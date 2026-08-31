from pathlib import Path
from abc import ABC, abstractmethod
from typing import List, Tuple, Callable

import rasterio
import numpy as np
from readers import bora_reader

# This library is developed by the framework team and needs
# to be installed separately until today (2024-01-15),
# it is only available for linux
from MultiResImagePy import MultiResImage

from src.utils.utils import apply_function
from src.utils.svs import get_resolution_svs
from src.utils.tissue import calculate_tissue_mask
from src.utils.bif import bif_reader, verify_bif, bif_writer
from src.utils.tif import get_resolution_tif, update_tiff_tag


class WSI(ABC):
    def __init__(self, image_path: Path, diplomat_path: Path = None) -> None:
        self.id = image_path.stem
        self._load(image_path)
        self.modifications = ""
        self.mask = None

        if diplomat_path is not None:
            self._load_diplomat(diplomat_path)
            print(self)

    def __repr__(self) -> str:
        repr = (
            f"{self.id} \n"
            f"\t* Dimension: {self.dimension} \n"
            f"\t* Invasive tumor: {np.sum(self.mask/255)*100/self.area:.2f}% \n"
            # f"\t* Cells: {len(np.unique(self.cell))-1} \n"
        )
        return repr

    @abstractmethod
    def _load(self, path: Path) -> None:
        """Loading the WSI"""
        pass

    @abstractmethod
    def save(self, dir_path: Path) -> None:
        """Saving the input array as WSI"""
        pass

    def _load_diplomat(self, path: Path) -> None:
        """
        Loading the diplomat H5 file including
            * Invasive tumor mask
            * Cell segmentation and statistics

        Parameters
        ----------
        - path (Path): The path to the diplomat file.

        Returns
        ------
            None
        """
        br = bora_reader.BoraReader()
        br.load_diplomat_file(path)

        # Epithelium mask is stored within the `predicted_region_mask_l0_1` key
        # not sure the meaning of the key
        masks = br.get_wsi_masks()
        self.mask = masks["predicted_region_mask_l0_1"]
        # ensuring the mask has the correct dimension
        # assert self.mask.shape[::-1] == self.dimension
        # Ideally, we want to perform the tissue detection on the highest resolution
        # however, it leads to out of memory on device with low memory
        # thus, we are performing the tissue detection on the higher resolutions
        # data = self.data[0] if isinstance(self.data, list) else self.data
        data = (
            self.data[self.nb_levels - 3] if isinstance(self.data, list) else self.data
        )
        calculate_tissue_mask(data, self.mask)

        # Unfortunately, Bora_Reader takes a long time to load the cell information
        # this is due to the fact that it is loading the data into 6 numpy arrays of size of data
        # we are skipping this step for now

        # Obtain the cell segmentation
        # Available information in cell stats:
        #   1. 'centers': the center of the cells
        #   2. 'nuclei': semantic segmentation information of the nuclei
        #   3. 'membrane': semantic segmentation information of the membrane
        #   4. 'cells': semantic segmentation information of the cells
        #   5. 'ODs' 6. 'subcell_ids' 7. 'subcell_classes' 8. 'stats'
        # thus, only accessing the `cells` will provide the cell information
        # cells = br.get_wsi_cells()
        # self.cell = cells["cells"]
        # # ensuring the mask has the correct dimension
        # assert self.cell.shape[::-1] == self.dimension

    @property
    def dimension(self) -> Tuple[int, int]:
        """
        WSI's dimension

        Returns
        ------
        - tuple (width, height)
        """
        data = self.data[0] if isinstance(self.data, list) else self.data
        # data is a numpy array which returns (H, W, C)
        # the interested output is (W, H)
        (width, height) = data.shape[:2][::-1]
        return (width, height)

    @property
    def area(self) -> int:
        """
        WSI's area

        Returns
        ------
        - int (area)
        """
        (width, height) = self.dimension
        return width * height

    def transform(self, transformations: List[Tuple[Callable, dict, str]]) -> None:
        """
        Applies a series of transformations to the dataset.

        Parameters
        ----------
        - transformations (List[tuple]): A list of tuples containing
            * the transformation function,
            * keyword arguments
            * name of the transformation.

        Returns
        ------
            None
        """
        for transformation, kwargs, name in transformations:
            kwargs["mask"] = self.mask
            kwargs["id"] = self.id
            self.data = apply_function(self.data, transformation, **kwargs)
            self.modifications += f"_{transformation.__name__}_{name}"


class TIF(WSI):
    def __repr__(self) -> str:
        repr = super().__repr__() + f"\t* Resolution: {self.resolution} \n"
        return repr

    def _load(self, path: Path) -> None:
        """
        Load the data from the given path.

        Parameters
        ----------
        - path (Path): The path to the data.
        """
        tif = rasterio.open(path)
        self.profile = tif.profile
        self.resolution = get_resolution_tif(path)
        self.data = tif.read().transpose((1, 2, 0))

    def save(self, dir_path: Path) -> None:
        """
        Save the modified data to a file.
        """
        # Path to save the modified data
        # the iAnalytics currently handles SVS properly
        # one concern is that the original BIF data has multiple data directory, but SVS has one
        path = dir_path / f"{self.id + self.modifications}.svs"

        # Updating the profile to be compatible with the modified data
        profile = self.profile
        (width, height) = self.dimension
        image_description = update_tiff_tag(
            self.profile, self.dimension, self.resolution, path
        )
        profile.update(
            height=height,
            width=width,
            desc=image_description,
        )

        # rasterio expect the format of data while writing to be (C, H, W)
        data = self.data.transpose(2, 0, 1)
        with rasterio.open(path, "w", **profile) as dst:
            dst.write(data)
            dst.update_tags(TIFFTAG_IMAGEDESCRIPTION=image_description)


class BIF(WSI):
    def _load(self, path: Path) -> None:
        """
        Load the data from the given path.

        Parameters
        ----------
        - path (Path): The path to the data.
        """
        image = MultiResImage(str(path))
        self.pixels_per_cm_max_res, self.pixels_per_micron = verify_bif(image, path)

        # Ensure base magnification is set to 20x as per QCS production requirements
        max_mag = int(image.getMaxMagnification())
        self.base_mag = 20 if max_mag != 20 else max_mag
        self.nb_levels = image.getNumResolutionLevels() - (1 if self.base_mag != max_mag else 0)

        if self.base_mag != max_mag:
            self.pixels_per_cm_max_res /= max_mag / self.base_mag
            self.pixels_per_micron *= max_mag / self.base_mag

        # This function attemps to load the entire image, which is not feasible in some images with high dimension
        # therefore, we are using the following function to load the data section by section
        # height, width = image.getHeightWidthForResolution(0)
        # self.data = image.getTile(0, (0, 0), (height, width), "none")
        # self.data = bif_reader(image, 0, "none")

        # In addition, we are interested to extracting all the levels of the image
        self.data = []
        for level in range(1 if self.base_mag != max_mag else 0, image.getNumResolutionLevels()):
            data = bif_reader(image, level, "none")
            self.data.append(data)

    def save(self, dir_path: Path) -> None:
        """
        Save the modified data to a file.
        """
        path = dir_path / f"{self.id + self.modifications}.bif"
        bif_writer(str(path), self.data, self.base_mag,
                   num_levels=self.nb_levels,
                   pixels_per_micron=self.pixels_per_micron,
                   pixels_per_cm_max_res=self.pixels_per_cm_max_res)


class SVS(TIF):
    def _load(self, path: Path) -> None:
        """
        Load the data from the given path.

        Parameters
        ----------
        - path (Path): The path to the data.
        """
        tif = rasterio.open(path)
        self.profile = tif.profile
        self.resolution = get_resolution_svs(tif.tags())
        self.data = tif.read().transpose((1, 2, 0))
