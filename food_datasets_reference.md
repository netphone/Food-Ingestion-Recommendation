# Food Image Dataset Reference Guide

> **Purpose:** A comprehensive reference for building a high-quality dataset of JPEG/PNG food photos enhanced with descriptive food-tag metadata and structured labels. Intended as a reliable source for testing food recognition or analysis systems.
>
> **Last reviewed:** April 2026

---

## Table of Contents

1. [Core Dataset Platforms & Repositories](#1-core-dataset-platforms--repositories)
2. [Specific Benchmark Datasets](#2-specific-benchmark-datasets)
3. [Specialized Metadata & Nutrition Repositories](#3-specialized-metadata--nutrition-repositories)
4. [Large-Scale Community Hubs](#4-large-scale-community-hubs)
5. [Region-Specific & Academic Benchmarks](#5-region-specific--academic-benchmarks)
6. [Access Methods](#6-access-methods)
7. [License & Source Quick Reference](#7-license--source-quick-reference)
8. [Platform Access Summary](#8-platform-access-summary)
9. [Known Corrections & Caveats](#9-known-corrections--caveats)
10. [Accessibility Investigation (April 2026)](#10-accessibility-investigation-april-2026)

---

## 1. Core Dataset Platforms & Repositories

### Dataset Ninja
- **URL:** https://datasetninja.com
- **Description:** A primary directory for annotated food datasets with filterable metadata (annotation type, license, image count, class count). Aggregates datasets from research and academic sources into a unified browseable catalog.
- **Access:** Free, no account required for browsing; dataset exports may require sign-in.

### AIcrowd — Food Recognition Benchmark
- **URL:** https://www.aicrowd.com/challenges/food-recognition-benchmark-2022
- **Description:** Hosts the official *Food Recognition 2022* competition and data files. The benchmark spans three yearly editions (2019–2022) and uses the MyFoodRepo dataset sampled from a Swiss digital cohort called *Food & You*. Both competition rounds are now completed but the dataset files remain accessible.
- **Data statistics (v2.1, Round 2):**
  - Training set: 54,392 images, 100,256 annotations, 323 food classes
  - Validation set: 946 images, 1,708 annotations, 323 food classes
  - Annotation format: MS-COCO JSON (segmentation masks + bounding boxes)
- **Data statistics (v2.0, Round 1):** 39,962 images, 76,491 annotations, 498 food classes
- **Access:** Free account required to download from the dataset files page.
- **Organizer:** Seerave Foundation; contact: mohanty@aicrowd.com
- **Source app:** Images are collected from Swiss volunteers via the **MyFoodRepo** smartphone app (*Food & You* digital cohort). Starter kits and documentation are maintained at https://gitlab.aicrowd.com. The GitHub organisation contains parser scripts and documentation only — not the images themselves.

### Kaggle — Food Recognition 2022
- **URL:** https://www.kaggle.com/datasets
- **Description:** Provides mirrors and repackaged versions of official datasets (including Food-101 and Food Recognition competition data) for easier cloud-based analysis. Supports Kaggle API download and notebook integration.
- **Access:** Free Kaggle account + API key or direct web download.

### Open Food Facts
- **URL:** https://world.openfoodfacts.org
- **Description:** A global, crowdsourced database of barcoded packaged products (3M+ products worldwide). Covers ingredient lists, nutrition labels, allergens, Nutri-Score, NOVA classification, and product images.
- **AWS Open Data:** Hosted on the AWS Registry of Open Data; product images and CSV dumps can be retrieved via the AWS CLI from the Open Food Facts S3 bucket.
- **License:** Data — Open Database License (ODbL); Product images — CC BY-SA 4.0
- **Access:** No AWS account required for basic `s3 cp` commands targeting their public bucket. Full dataset dump available at https://static.openfoodfacts.org/data/openfoodfacts-mongodbdump.gz

### ResearchGate
- **URL:** https://www.researchgate.net
- **Description:** A hub for research papers and table-based comparisons of food dataset specifications. Useful for finding dataset papers, author contacts, and comparative surveys (e.g., surveys on food recognition benchmarks).

---

## 2. Specific Benchmark Datasets

### Food-101
| Attribute | Value |
|-----------|-------|
| **Images** | 101,000 (101 categories × 1,000 images each) |
| **Split** | 750 training + 250 test per class |
| **Image size** | Max side length 512 px (rescaled) |
| **Annotation** | Class labels only (no bounding boxes) |
| **Note** | Training images are intentionally noisy (intense colors, occasional wrong labels); test images are manually verified |
| **Source URL** | https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/ |
| **Download** | Direct `.tar.gz` (~5 GB) from ETH Zurich |
| **TF Datasets** | Also available via `tensorflow_datasets` (`tfds.load('food101')`) |
| **License** | Images sourced from Foodspotting; use beyond scientific fair use must be negotiated with picture owners per Foodspotting Terms of Use |
| **Citation** | Bossard et al., ECCV 2014, *"Food-101 — Mining Discriminative Components with Random Forests"* |

### Food2K / Food1K
| Attribute | Value |
|-----------|-------|
| **Images** | ~1,036,564 images across 2,000 food classes (Food2K); subset ~500K for Food1K |
| **Description** | High-volume large-scale datasets for fine-grained food category recognition; claimed to exceed prior food datasets by one order of magnitude in both categories and images |
| **Paper** | Min et al., IEEE TPAMI 2023, *"Large Scale Visual Food Recognition"* — arXiv:2103.16107 |
| **Paper URL** | https://arxiv.org/abs/2103.16107 |
| **Access** | Dataset available via request; contact authors through the paper (no stable public download URL confirmed as of April 2026) |
| **License** | Research use; check paper for specific terms |

### UEC Food-256 / UEC Food-100
| Attribute | Value |
|-----------|-------|
| **Images (256)** | ~31,000 photos across 256 food categories |
| **Images (100)** | ~14,000 photos across 100 food categories |
| **Annotation** | Bounding boxes per food item (stored in `bb_info.txt` per class directory) |
| **Focus** | Popular Japanese and international foods; designed for real-time recognition on Android |
| **Source URL (256)** | http://foodcam.mobi/dataset256.html |
| **Source URL (100)** | http://foodcam.mobi/dataset.html |
| **Download** | Direct ZIP download from foodcam.mobi |
| **Institution** | Department of Informatics, The University of Electro-Communications, Tokyo, Japan |
| **License** | **Non-commercial research use only.** Commercial use requires contacting the authors (food-group@mm.cs.uec.ac.jp) |
| **Citation** | Kawano & Yanai, ECCV Workshop TASK-CV, 2014 |

### Nutrition5k
| Attribute | Value |
|-----------|-------|
| **Plates** | 5,006 realistic plates of food |
| **Capture setup** | 4 Raspberry Pi cameras (side-angle videos at 30°/60° elevation, 90° apart) + Intel RealSense overhead RGB-D images |
| **Annotations** | Per-ingredient mass, total dish mass, total calories, fat, protein, carbohydrates |
| **Download size** | 181.4 GB |
| **Source URL** | https://github.com/google-research-datasets/Nutrition5k |
| **GCS bucket** | `gs://nutrition5k_dataset/` |
| **Download command** | `gsutil -m cp -r "gs://nutrition5k_dataset/nutrition5k_dataset/{FILE_OR_DIR}" .` |
| **Direct download** | https://storage.cloud.google.com/nutrition5k_dataset/nutrition5k_dataset.tar.gz |
| **Institution** | Google Research (cafeteria data from California, USA) |
| **License** | **CC BY 4.0** (not Apache 2.0) — free to share and adapt, including for commercial use, with attribution |
| **Citation** | Thames et al., CVPR 2021, *"Nutrition5k: Towards Automatic Nutritional Understanding of Generic Food"* |
| **Contact** | nutrition5k@google.com |

### Vireo Food-172
| Attribute | Value |
|-----------|-------|
| **Images** | ~110,241 images across 172 food categories |
| **Focus** | Chinese cuisine; ingredient recognition with ingredient-level labels |
| **Source URL** | http://vireo.cs.cityu.edu.hk/VireoFood172/ |
| **Institution** | Visual Information Research (VIREO) group, City University of Hong Kong |
| **License** | Research use; contact authors for terms |
| **⚠️ Accessibility** | URL returns no content during verification (April 2026). The domain resolves but the page may be offline. Contact the VIREO group directly if access is needed |

### MAFood-121
| Attribute | Value |
|-----------|-------|
| **Categories** | 121 food categories drawn from the top 11 world cuisines (ranked by Google Trends popularity) |
| **Images** | ~21,175 images |
| **Focus** | Multi-cuisine coverage including American, Chinese, French, Indian, Italian, Japanese, Mexican, Spanish, Thai, Greek, and Turkish cuisines |
| **Source** | Kaggle dataset repository |
| **License** | Check individual Kaggle listing for terms |

### ISIA Food-500
| Attribute | Value |
|-----------|-------|
| **Categories** | 500 food categories |
| **Images** | ~399,726 images |
| **Focus** | Large-scale dataset spanning Asian, European, and African food types |
| **Source URL** | http://123.57.42.89/Dataset_ict/iFood-500.html |
| **Institution** | Institute of Computing Technology, Chinese Academy of Sciences |
| **License** | Research use |
| **⚠️ Accessibility** | URL is a raw IP address with no associated domain name, making it fragile and potentially unstable long-term |

### FooDB
| Attribute | Value |
|-----------|-------|
| **Description** | The world's most comprehensive database on food constituents, chemistry, and biology. Contains data on over 1,000 raw or minimally processed foods, with full chemical composition including macronutrients, micronutrients, phytochemicals, and metabolites |
| **Source URL** | https://foodb.ca |
| **Format** | Downloadable as XML/CSV/JSON and SDF (structure data files) |
| **License** | Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0) |
| **Note** | Primarily a chemical/nutritional database, not an image dataset |

---

## 3. Specialized Metadata & Nutrition Repositories

### SNAPMe Database (USDA)
| Attribute | Value |
|-----------|-------|
| **Full name** | Snack and Meal Photo and Eating Occasion Study |
| **Images** | 3,311 food photos |
| **Linked records** | 275 ASA24 (Automated Self-Administered 24-Hour Dietary Assessment Tool) food records |
| **Use case** | High-quality real-world data for automated dietary assessment; links photos directly to verified nutrient intake records |
| **Source URL** | https://agdatacommons.nal.usda.gov |
| **Institution** | USDA Agricultural Research Service |
| **License** | **CC BY 4.0** — freely usable with attribution |
| **Access** | Direct download from Ag Data Commons (free, no account required) |

### MM-Food-100K
| Attribute | Value |
|-----------|-------|
| **Images** | 100,000 food images |
| **Description** | Large-scale multi-modal dataset pairing food images with tabular nutrition facts and text descriptions. Often used for image-to-text and visual question answering tasks |
| **Source** | Hugging Face Hub |
| **Access** | `pip install datasets` then `from datasets import load_dataset; ds = load_dataset("...")` |
| **License** | OpenRail / Public Research license (verify on the specific Hugging Face dataset card) |

### NutriGreen Image Dataset
| Attribute | Value |
|-----------|-------|
| **Images** | 10,472 images of branded packaged food products |
| **Focus** | Detection of standardized food packaging labels: Nutri-Score (grades A–E), EU BIO organic logo, and V-label (vegan/vegetarian) |
| **Annotations** | YOLO-format bounding box segmentation masks per label; semi-automatic pipeline (expert manual + fine-tuned YOLOv5) |
| **Use case** | Training segmentation models to identify front-of-pack nutrition and sustainability labels |
| **Source URL** | https://zenodo.org/records/8374047 |
| **Paper DOI** | https://doi.org/10.3389/fnut.2024.1342823 (Frontiers in Nutrition, March 2024) |
| **License** | **CC BY 4.0** — open access; attribution required |
| **Note** | Images sourced from Open Food Facts (CC BY-SA). Dataset is about *packaging label detection*, not food type or ingredient recognition |

### Daily Food & Nutrition Dataset
| Attribute | Value |
|-----------|-------|
| **Description** | Records everyday food consumption items paired with macro- and micronutrient values (calories, protein, carbs, fat, fiber, sugars, sodium, cholesterol) and meal context (breakfast/lunch/dinner/snack) |
| **Source (Kaggle)** | https://www.kaggle.com/datasets/adilshamim8/daily-food-and-nutrition-dataset |
| **Source (HuggingFace)** | https://huggingface.co/datasets/adilshamim8/daily-food-and-nutrition-dataset |
| **Format** | CSV; no food images |
| **License** | Check individual dataset card (typically CC0 or CC BY for this type) |
| **⚠️ Important note** | The most widely linked Kaggle version is **synthetically generated** (not real dietary records). Verify the provenance of any specific version before using in research |

---

## 4. Large-Scale Community Hubs

### Roboflow Universe — Food Category
| Attribute | Value |
|-----------|-------|
| **URL** | https://universe.roboflow.com/browse/food |
| **Description** | A public repository with thousands of food-related computer vision datasets contributed by the community. Includes object detection, instance segmentation, and classification datasets |
| **Notable datasets** | Food Image Segmentation (YOLOv5 format), Indian Food Detection, Food Calorie Estimation (~6.68k images), Food Recognition Challenge (~1.27k images), Food Waste Detection (~2.72k images) |
| **Export formats** | 50+ formats including COCO JSON, YOLO (v5/v8), Pascal VOC, TFRecord, CSV |
| **Access** | Free Roboflow account required for dataset export |
| **License** | Varies per dataset; check individual dataset cards |

### Kaggle — Global Food & Nutrition Database 2026
| Attribute | Value |
|-----------|-------|
| **URL** | https://www.kaggle.com/datasets/ahsanneural/global-food-and-nutrition-database-2026 |
| **Records** | 44,997 foods (40,000 from USDA FoodData Central + ~5,000 from Open Food Facts branded products) |
| **Metadata** | Nutri-Score grades (A–E), NOVA classification (1–4), Eco-Score, allergen flags (gluten, dairy, nuts, soy, eggs, fish), custom health scores (0–100) |
| **Files** | 5 CSV files: `comprehensive_foods_usda.csv`, `foods_health_scores_allergens.csv`, `foods_allergens.csv`, `foods_dietary_restrictions.csv`, `healthy_foods_database.csv` |
| **Note** | **Nutrition/metadata only — does not include food images.** Use as a taxonomy reference or label source paired with image datasets |
| **Created** | February 2026 |
| **License** | **CC BY-SA 4.0** (derivative datasets must be shared under the same license) |

### USDA FoodData Central
| Attribute | Value |
|-----------|-------|
| **URL** | https://fdc.nal.usda.gov |
| **Description** | Authoritative nutritional database from the U.S. Department of Agriculture. Covers Foundation Foods, SR Legacy, Branded Foods, and Experimental Foods with full nutrient profiles |
| **Format** | Bulk CSV and JSON downloads (full database snapshots updated periodically) |
| **API** | REST API available at https://api.nal.usda.gov/fdc/v1/ with free API key |
| **Note** | Primarily nutritional data, no images. Serves as the "ground truth" taxonomy for many visual food datasets |
| **License** | Public domain (U.S. government works) |

---

## 5. Region-Specific & Academic Benchmarks

### UNICT-FD889
| Attribute | Value |
|-----------|-------|
| **Images** | 3,583 images (multiple images per food plate) |
| **Categories** | 889 distinct food plates/classes |
| **Focus** | Benchmark for studying the representation of food images |
| **Annotation** | Class labels for each food plate |
| **Source URL** | https://iplab.dmi.unict.it/UNICT-FD889/ |
| **Direct download** | https://iplab.dmi.unict.it/legacy/UNICT-FD889/Info_&_Dataset_UNICT-FD889.zip |
| **Institution** | Image Processing Lab (IPLab), University of Catania (UNICT), Italy |
| **Contact** | gfarinella@dmi.unict.it |
| **Citation** | Farinella et al., ECCV Workshop ACVR 2014 |
| **License** | Research use |

### VIPER-FoodNet
| Attribute | Value |
|-----------|-------|
| **Images** | 14,991 images |
| **Categories** | 82 food classes |
| **Focus** | Multiethnic and culturally diverse food recognition |
| **License** | Research use |
| **⚠️ Accessibility** | No confirmed public URL found as of April 2026. The GitHub repo and IPLab page both return 404. Contact IPLab UNICT (gfarinella@dmi.unict.it) if access is needed |

### UNIMIB2016
| Attribute | Value |
|-----------|-------|
| **Images** | 1,027 images |
| **Context** | Cafeteria / canteen tray setting; multiple food items per image |
| **Annotation** | Polygon segmentation masks (multi-food annotations per image) |
| **Source** | Kaggle repository |
| **Institution** | University of Milano-Bicocca (UNIMIB), Italy |
| **License** | Research use; free Kaggle account required |

### Food-11 (MMSPG-EPFL)
| Attribute | Value |
|-----------|-------|
| **Images** | 16,643 |
| **Categories** | 11 major food groups: Bread, Dairy product, Dessert, Egg, Fried food, Meat, Noodles/Pasta, Rice, Seafood, Soup, Vegetable/Fruit |
| **Split** | Training, validation, and evaluation sets |
| **Naming convention** | `{ClassID}_{ImageID}.jpg` (ClassID 0–10) |
| **Source URL** | https://www.epfl.ch/labs/mmspg/downloads/food-image-datasets/ |
| **Institution** | Multimedia Signal Processing Group (MMSPG), EPFL, Switzerland |
| **Download** | FTP: host `tremplin.epfl.ch`, user `datasets@mmspgdata.epfl.ch`, password `ohsh9jah4T`, port 21. Navigate to `/FoodImage/` |
| **Download size** | ~1.16 GB |
| **License** | Permitted for research purposes only; not for commercial redistribution |

### Food-5K (MMSPG-EPFL)
| Attribute | Value |
|-----------|-------|
| **Images** | 5,000 (2,500 food + 2,500 non-food) |
| **Task** | Binary food / non-food image classification |
| **Split** | Training, validation, and evaluation sets |
| **Naming convention** | `{ClassID}_{ImageID}.jpg` (ClassID 0 = non-food, 1 = food) |
| **Source URL** | https://www.epfl.ch/labs/mmspg/downloads/food-image-datasets/ |
| **Download** | Same FTP server as Food-11 (see above), navigate to `/FoodImage/` |
| **Download size** | ~446.9 MB |
| **License** | Research purposes only; not for commercial redistribution |

### FoodBD
| Attribute | Value |
|-----------|-------|
| **Source** | Mendeley Data |
| **Access** | Direct web download |
| **⚠️ Accessibility** | No valid Mendeley DOI or stable URL could be confirmed as of April 2026. Multiple candidate Mendeley dataset IDs return "Dataset Not Found". The dataset may have been removed or is no longer publicly hosted |

---

## 6. Access Methods

### Direct Downloads (ZIP / CSV / JSON)

The simplest method to get JPEG/PNG images paired with sidecar metadata is through research hubs:

| Dataset | Method | URL |
|---------|--------|-----|
| **Nutrition5k** | `gsutil` OR direct `.tar.gz` link | `gsutil -m cp -r "gs://nutrition5k_dataset/..."` |
| **Food Recognition 2022** | Web download (AIcrowd dataset page) | https://www.aicrowd.com/challenges/food-recognition-benchmark-2022/dataset_files |
| **Food-101** | Direct `.tar.gz` (~5 GB) | http://data.vision.ee.ethz.ch/cvl/food-101.tar.gz |
| **Food-11 / Food-5K** | FTP (see credentials above) | `tremplin.epfl.ch` |
| **SNAPMe** | Direct download | https://agdatacommons.nal.usda.gov |
| **UEC Food-256** | Direct ZIP | http://foodcam.mobi/dataset256.zip |

#### Nutrition5k — gsutil command example
```bash
# Install gsutil: https://cloud.google.com/storage/docs/gsutil
gsutil -m cp -r "gs://nutrition5k_dataset/nutrition5k_dataset/metadata" .
gsutil -m cp -r "gs://nutrition5k_dataset/nutrition5k_dataset/imagery/realsense_overhead" .
```

#### Food-101 — TensorFlow Datasets
```python
import tensorflow_datasets as tfds
ds = tfds.load('food101', split='train', as_supervised=True)
```

---

### Large-Scale Cloud Access

For massive datasets, cloud providers host data with free-egress access:

| Dataset | Platform | Command / Method |
|---------|----------|-----------------|
| **Open Food Facts** | AWS Open Data (S3) | `aws s3 cp s3://openfoodfacts-images/...` (public bucket) |
| **MM-Food-100K** | Hugging Face | `from datasets import load_dataset` |
| **USDA FoodData Central** | Direct API / bulk download | https://fdc.nal.usda.gov/download-foods.html |

#### Open Food Facts — AWS CLI
```bash
# List available prefixes (no AWS account needed for public access)
aws s3 ls s3://openfoodfacts-images/ --no-sign-request
```

#### MM-Food-100K — Hugging Face
```python
pip install datasets
from datasets import load_dataset
ds = load_dataset("mm-food-100k")  # verify exact dataset name on Hugging Face
```

---

### Community-Driven Repositories

**Roboflow Universe:** Search at https://universe.roboflow.com/browse/food for thousands of user-contributed food datasets. Export in 50+ formats (COCO JSON, YOLO, etc.) after creating a free account.

---

## 7. License & Source Quick Reference

| Dataset | Source URL | Primary License | Commercial Use? |
|---------|-----------|-----------------|-----------------|
| **Nutrition5k** | https://github.com/google-research-datasets/Nutrition5k | **CC BY 4.0** ✅ | Yes, with attribution |
| **Food Recognition 2022** | https://www.aicrowd.com/challenges/food-recognition-benchmark-2022 | CC0 1.0 (verify on dataset page) | Public domain |
| **Food-101** | https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/ | Foodspotting Terms of Use | Research / fair use only |
| **MM-Food-100K** | Hugging Face Hub | OpenRail / Public Research | Verify on dataset card |
| **Open Food Facts** | https://world.openfoodfacts.org | ODbL (data) / CC BY-SA 4.0 (images) | Yes (with share-alike) |
| **SNAPMe** | https://agdatacommons.nal.usda.gov | **CC BY 4.0** ✅ | Yes, with attribution |
| **UEC Food-256/100** | http://foodcam.mobi/dataset256.html | Non-commercial research only ⚠️ | No |
| **Food-11 / Food-5K** | https://www.epfl.ch/labs/mmspg/downloads/food-image-datasets/ | Research only ⚠️ | No |
| **Vireo Food-172** | http://vireo.cs.cityu.edu.hk/VireoFood172/ | Research use | Contact authors |
| **USDA FoodData Central** | https://fdc.nal.usda.gov | Public domain ✅ | Yes |
| **Kaggle Global F&N 2026** | Kaggle (see URL above) | CC BY-SA 4.0 | Yes (with share-alike) |
| **FooDB** | https://foodb.ca | CC BY-NC 4.0 ⚠️ | Non-commercial only |
| **ISIA Food-500** | http://123.57.42.89/Dataset_ict/iFood-500.html | Research use | Contact authors |

---

## 8. Platform Access Summary

| Platform | Key Datasets Hosted | Access Requirements |
|----------|---------------------|---------------------|
| **ETH Zurich** | Food-101 | Direct web download (no account) |
| **AIcrowd** | Food Recognition 2022 (MyFoodRepo) | Free account; dataset files page |
| **Kaggle** | Food-101 (mirror), UNIMIB2016, MAFood-121, Global F&N 2026 | Free Kaggle account + API or web download |
| **Roboflow Universe** | Indian Food, UECFood-256 (repackaged), segmentation datasets | Free account; COCO, YOLO, or CSV export |
| **EPFL MMSPG** | Food-11, Food-5K | FTP credentials (see §5); use FileZilla or FireFTP |
| **Mendeley Data** | FoodBD | Direct web download |
| **AWS Open Data** | Open Food Facts | AWS CLI (`--no-sign-request` for public access) |
| **Hugging Face** | MM-Food-100K | `pip install datasets`; free account for large downloads |
| **Ag Data Commons (USDA)** | SNAPMe | Direct download; free account may be needed |
| **Google Cloud Storage / GitHub** | Nutrition5k | `gsutil cp` or direct `.tar.gz`; free GCP account for large downloads |
| **foodcam.mobi (UEC)** | UEC Food-256, UEC Food-100 | Direct ZIP download; non-commercial research only |

---

## 9. Known Corrections & Caveats

The following are factual corrections and important caveats relative to commonly cited summaries of these datasets:

### License Corrections
- **Nutrition5k**: Licensed under **CC BY 4.0**, not Apache 2.0. You may use it commercially with attribution.
- **UEC Food-256 / 100**: These datasets are **non-commercial research only**. This is explicitly stated on the download page. Any use outside research requires written permission from the University of Electro-Communications.
- **Food-101**: Images were originally scraped from Foodspotting. Scientific fair use is generally accepted, but broader commercial use requires negotiation with the respective picture owners per Foodspotting's terms. It is **not** a permissively licensed dataset.
- **Kaggle Global Food & Nutrition Database 2026**: Licensed under **CC BY-SA 4.0**, not CC0 or public domain. Derivative databases must maintain the same license due to the inclusion of Open Food Facts data (ODbL).

### Size / Scale Corrections
- **Nutrition5k download size**: 181.4 GB (commonly rounded to "180 GB" in secondary sources).
- **Food Recognition 2022 v2.1**: Exactly 54,392 training images and 100,256 annotations across 323 classes (v2.0 has 39,962 images, 76,491 annotations over 498 classes — the two versions are not interchangeable).
- **Food-101**: The 750 training images per class are **intentionally noisy** (wrong labels, extreme colors). Only the 250 test images per class are manually verified.

### Access Method Corrections
- **EPFL Food-11 / Food-5K**: Access is via **FTP**, not a simple server link. Requires an FTP client (FileZilla, FireFTP). Credentials: host `tremplin.epfl.ch`, user `datasets@mmspgdata.epfl.ch`, password `ohsh9jah4T`, port 21.

### Missing Datasets (Not Mentioned in Original Summary)
- **Food-5K** (EPFL MMSPG): Binary food/non-food classification dataset (5,000 images), hosted alongside Food-11 on the same EPFL FTP server (~446.9 MB). Suitable for pre-filtering pipelines.
- **Food2K/Food1K**: Multi-million image datasets for large-scale recognition at 1,000–2,000 class granularity; available via research paper supplementary materials.

### Dataset-Platform Relationship Clarifications
- **myFoodRepo** is the *source application* collecting data for the **Food Recognition 2022 AIcrowd benchmark**. The app is used by Swiss volunteers in the *Food & You* digital cohort. The GitHub organization contains documentation and parser scripts, not the images themselves.
- **USDA FoodData Central** is a *nutritional taxonomy* and does not include food photographs. It is best used as a label/ingredient reference alongside visual datasets.
- **Kaggle's Global Food & Nutrition Database 2026** is a *metadata-only* CSV dataset (no images). It combines USDA FoodData Central and Open Food Facts into a single structured file with added health scoring metrics.
- **Dataset Ninja** is a *catalog/index* (datasetninja.com), not a primary data host. It links to original sources.

---

## 10. Accessibility Investigation (April 2026)

This section documents the results of a URL and access verification pass conducted on all 24 datasets in this reference, performed in April 2026.

### Summary Table

| # | Dataset | Status | Notes |
|---|---------|--------|-------|
| 1 | Food Recognition 2022 (MyFoodRepo) | ✅ Accessible | Free AIcrowd account required |
| 2 | Open Food Facts | ✅ Accessible | AWS CLI (`--no-sign-request`); no account needed for public bucket |
| 3 | Food-101 | ✅ Accessible | Direct `.tar.gz` from ETH Zurich or `tensorflow_datasets` |
| 4 | Food2K | ⚠️ Request-only | No stable public download URL; access via author contact (arXiv:2103.16107) |
| 5 | Food1K | ⚠️ Request-only | Same as Food2K |
| 6 | UEC Food-256 | ✅ Accessible | Direct ZIP from foodcam.mobi |
| 7 | UEC Food-100 | ✅ Accessible | Direct ZIP from foodcam.mobi |
| 8 | Nutrition5k | ✅ Accessible | `gsutil` or direct `.tar.gz` from Google Cloud |
| 9 | Vireo Food-172 | ⚠️ URL unresponsive | http://vireo.cs.cityu.edu.hk/VireoFood172/ resolves but returns no content |
| 10 | MAFood-121 | ✅ Accessible | Free Kaggle account required |
| 11 | ISIA Food-500 | ⚠️ Fragile URL | Raw IP address (`http://123.57.42.89/...`); no domain name — unstable long-term |
| 12 | FooDB | ✅ Accessible | foodb.ca publicly accessible (rate-limited under heavy load) |
| 13 | SNAPMe | ✅ Accessible | Direct download from USDA Ag Data Commons |
| 14 | MM-Food-100K | ✅ Accessible | Hugging Face `datasets` library |
| 15 | NutriGreen | ✅ Accessible | Zenodo record: https://zenodo.org/records/8374047 (CC BY 4.0) |
| 16 | Daily Food & Nutrition | ✅ Accessible | Kaggle and Hugging Face; ⚠️ popular version is **synthetically generated** |
| 17 | Kaggle Global Food & Nutrition Database 2026 | ✅ Accessible | Free Kaggle account required |
| 18 | USDA FoodData Central | ✅ Accessible | Public domain; direct bulk download + free REST API |
| 19 | UNICT-FD889 | ✅ Accessible | Direct ZIP: https://iplab.dmi.unict.it/legacy/UNICT-FD889/Info_&_Dataset_UNICT-FD889.zip |
| 20 | VIPER-FoodNet | ❌ Not found | GitHub repo and IPLab page both return 404; may be offline |
| 21 | UNIMIB2016 | ✅ Accessible | Free Kaggle account required |
| 22 | Food-11 | ✅ Accessible | FTP credentials provided in §5 |
| 23 | Food-5K | ✅ Accessible | Same FTP server as Food-11 (see §5) |
| 24 | FoodBD | ❌ Not found | Mendeley Data — no valid DOI or URL confirmed; may have been removed |

### Accessibility Counts

| Category | Count |
|----------|-------|
| ✅ Clearly accessible (direct URL or documented method) | **17** |
| ⚠️ Conditionally accessible (fragile URL, author request, or caveat) | **5** |
| ❌ Not accessible (confirmed offline or no URL found) | **2** |

### Action Recommendations

| Dataset | Recommended Action |
|---------|--------------|
| **Food2K / Food1K** | Email corresponding author Weiqing Min (see arXiv:2103.16107) to request access |
| **Vireo Food-172** | Try the URL directly in a browser; if still down, contact the VIREO group at City University of Hong Kong |
| **ISIA Food-500** | Download immediately if needed — raw IP URLs are unreliable. Alternatively, search for a mirrored copy |
| **VIPER-FoodNet** | Contact IPLab UNICT (gfarinella@dmi.unict.it); dataset may have been folded into a later release |
| **FoodBD** | Search Mendeley Data with keyword "FoodBD" or search for citing papers to find a current mirror |
| **Daily Food & Nutrition** | Confirm whether a real (non-synthetic) version exists before using in research; USDA FoodData Central is a robust alternative |
