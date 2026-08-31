##################USEAGE EXAMPLE. #####################
# python ~/meal-image-insights/exploration/mds_543_error_analysis_and_evaluation_of_currenr_model/inference_classifier_model.py \
# --config-name ~/meal-image-insights/exploration/mds_506_text_classification_prototype/classification_training/images/configs/config_food_type_tags_v4.json \
# --checkpoint-path ~/meal-image-insights/exploration/mds_506_text_classification_prototype/classification_training/images/models/extracted/model.pth \
# --output-path ~/ \
# --batch-size 16 --hidden-layer-size 256
#######################################################
import argparse
import json
import os
from typing import Dict, List

import torch
import pandas as pd
from torchvision import transforms
from torchmetrics.classification import (
    MultilabelAccuracy,
    MultilabelAUROC,
    MultilabelAveragePrecision,
    MultilabelF1Score,
    MultilabelPrecision,
    MultilabelRecall,
)

from meal_insights.core.logging import get_logger
from meal_insights.data.data_handler import DataHandler
from meal_insights.data.preprocessor import Preprocessor
from meal_insights.data_models import (
    AnnotationPaths,
    ClassificationModelConfig,
    DataloaderSettings,
    DatasetConfig,
    DatasetSettings,
    ImagePaths,
    OntologySettings,
)
from meal_insights.models.classification.meal_image_classifier import (
    EfficientNetMealImageClassifier,
)
from meal_insights.training.trainers.generate_dataloaders import create_dataloader, align_categories

logger = get_logger(__name__)

def generate_dataloaders(
    config: DatasetConfig,
    ontology: Dict,
    data_df: pd.DataFrame,
    data_img_dir: str = "test",
    batch_size: int = None
) -> torch.utils.data.DataLoader:
    """Generate DataLoader for inference without data augmentation."""
    # Extract settings directly from DatasetConfig
    batch_size = batch_size if batch_size is not None else config.dataloader_settings.batch_size
    img_size = config.dataloader_settings.image_size
    num_workers = config.dataloader_settings.num_workers

    # Align datasets with ontology
    logger.info("Aligning test dataset with ontology...")
    data_df, data_category_columns = align_categories(data_df, ontology)
    
    # Define image transformations (test/inference transformations - no augmentation)
    data_transform = transforms.Compose([
        transforms.Resize(img_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Create dataloader
    logger.info("Creating DataLoader")
    data_image_dir = config.dataloader_settings.image_dirs[data_img_dir]
    data_loader = create_dataloader(
        metadata=data_df,
        image_dir=data_image_dir,
        category_columns=data_category_columns,
        transform=data_transform,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
    )
    
    return data_loader

def load_model(model_config: ClassificationModelConfig, checkpoint_path: str) -> EfficientNetMealImageClassifier:
    """Load trained model from checkpoint file."""
    logger.info(f"Loading model from: {checkpoint_path}")

    # print(model_config)
    model = EfficientNetMealImageClassifier(config=model_config)
    # Load checkpoint
    checkpoint = torch.load(checkpoint_path, map_location=model_config.device)
    model.load_state_dict(checkpoint)
    # model.eval()  # Set to evaluation mode
    
    logger.info("Model loaded successfully.")
    return model

def run_inference(
    model: EfficientNetMealImageClassifier,
    dataloader: torch.utils.data.DataLoader,
    device: torch.device,
    ontology: List,
) -> pd.DataFrame:
    """Run model inference and compute evaluation metrics."""
    logger.info("Running inference...")
    predictions = []
    image_ids = []
    labels = []
    
    model.eval()
    num_labels = len(ontology)

    # Initialize TorchMetrics metrics
    metrics = {
        "Multilabel AUROC": MultilabelAUROC(num_labels=num_labels).to(device),
        "mAP": MultilabelAveragePrecision(num_labels=num_labels).to(device),
        "F1 Micro": MultilabelF1Score(num_labels=num_labels, average="micro").to(device),
        "F1 Macro": MultilabelF1Score(num_labels=num_labels, average="macro").to(device),
        "Precision Micro": MultilabelPrecision(num_labels=num_labels, average="micro").to(device),
        "Precision Macro": MultilabelPrecision(num_labels=num_labels, average="macro").to(device),
        "Multilabel Recall Micro": MultilabelRecall(num_labels=num_labels, average="micro").to(device),
        "Multilabel Recall Macro": MultilabelRecall(num_labels=num_labels, average="macro").to(device),
        "Accuracy Micro": MultilabelAccuracy(num_labels=num_labels, average="micro").to(device),
        "Accuracy Macro": MultilabelAccuracy(num_labels=num_labels, average="macro").to(device),
    }

    with torch.no_grad():
        for batch_idx, (batch, batch_labels) in enumerate(dataloader):
            images = batch.to(device)  # First element is typically images
            _, labels_int = batch_labels  # Unpack labels
            labels_int = labels_int.to(device)  # Int labels for metrics
            batch_image_ids = [f"batch_{batch_idx}_img_{i}" for i in range(len(images))]
            # Forward pass
            outputs = model(images)
            # Convert outputs to predictions (assuming multi-label classification)
            probs = outputs if model.config.output == "probability" else torch.sigmoid(outputs)
            # Update metrics with integer labels
            for metric in metrics.values():
                metric.update(probs, labels_int)
            # Store predictions
            predictions.extend(probs.cpu().numpy())
            labels.extend(labels_int.cpu().numpy())
            image_ids.extend(batch_image_ids)
            
            if (batch_idx + 1) % 10 == 0:
                print(f"Processed {(batch_idx + 1) * dataloader.batch_size} images...")
    
    # Compute final metrics
    metrics_results = {name: metric.compute().item() for name, metric in metrics.items()}
    logger.info(f"Metrics: {metrics_results}")
    # Create DataFrame with predictions
    category_names = [cat for cat in ontology]
    results_df = pd.DataFrame(predictions, columns=category_names)
    results_df.insert(0, "label", labels)
    results_df.insert(0, "image_id", image_ids)
    
    logger.info(f"Inference complete. Processed {len(predictions)} images.")
    return results_df, metrics_results


def main(args):
    """Run inference pipeline on validation and test datasets."""
    # Step 1: Load Configurations
    config_path = args.config_name
    print(f"Loading configuration from: {config_path}")
    
    with open(config_path) as f:
        config = json.load(f)

    dataset_config = DatasetConfig(
        annotation_paths=AnnotationPaths(
            train="",
            val=config["annotation_paths"]["val"],
            test=config["annotation_paths"]["test"]),
        image_paths=ImagePaths(**config["image_paths"]),
        output_location=config["output_location"],
        dataset_settings=DatasetSettings(**config.get("dataset_settings", {})),
        dataloader_settings=DataloaderSettings(**config["dataloader_settings"]),
        ontology_settings=OntologySettings(**config["ontology_settings"]),
    )
    
    # Override local image directories if provided (SageMaker compatibility)
    if args.inference_image_dir:
        # For inference, use test dataset
        dataset_config.dataloader_settings.image_dirs["test"] = args.inference_image_dir
    
    # Load ontology
    with open(dataset_config.ontology_settings.ontology_path) as f:
        ontology = json.load(f)
    
    # Extract and validate model configuration
    raw_model_cfg = config["model"]
    model_config = ClassificationModelConfig(
        num_categories=len(ontology),
        hidden_layer_size=args.hidden_layer_size if args.hidden_layer_size is not None else raw_model_cfg.get("hidden_layer_size", 512),
        efficientnet_size=raw_model_cfg.get("efficientnet_size", "b0"),
        device=str(torch.device("cuda" if torch.cuda.is_available() else "cpu")),
        freezing_strategy=raw_model_cfg.get("freezing_strategy", "base"),
        prior_prob=raw_model_cfg.get("prior_prob", "default"),
        output=raw_model_cfg.get("output", "probability"),
        local_checkpoint_path=args.checkpoint_path,  # Use CLI-provided checkpoint
        pretrained=False,  # Don't need pretrained weights for inference
    )
    
    device = torch.device(model_config.device)
    logger.info(f"Using device: {device}")
    
    # Step 2: Load Dataset
    logger.info("\nLoading test dataset for inference...")
    data_handler = DataHandler()
    
    val_df = data_handler.load_dataset(dataset_config.annotation_paths.val)
    test_df = data_handler.load_dataset(dataset_config.annotation_paths.test)
    
    # Step 3: Preprocess Dataset
    logger.info("\nPreprocessing dataset...")
    preprocessor = Preprocessor(
        replace_columns=dataset_config.dataset_settings.replace_columns
    )
    
    local_image_dirs = dataset_config.dataloader_settings.image_dirs
    val_df = preprocessor.preprocess_dataset(val_df, "val", local_image_dirs)
    test_df = preprocessor.preprocess_dataset(test_df, "test", local_image_dirs)
    
    # print("\nSample remapped URIs:")
    # print(val_df["uri"].head())
    # print(test_df["uri"].head())

    # Step 4: Generate DataLoader
    logger.info("Generating DataLoader...")
    # Only use the val/ test loader for inference
    val_loader = generate_dataloaders(
        dataset_config, ontology, 
        data_df=val_df,
        data_img_dir='val',
        batch_size=args.batch_size
    )
    test_loader = generate_dataloaders(
        dataset_config, ontology,
        data_df=test_df, 
        data_img_dir='test',
        batch_size=args.batch_size
    )
    
    logger.info("DataLoader successfully created.")
    
    # Step 5: Load Model
    model = load_model(model_config, args.checkpoint_path).to(device)

    # Step 6: Run Inference
    val_results_df, _ = run_inference(model, val_loader, device, ontology)
    test_results_df, _ = run_inference(model, test_loader, device, ontology)
    for d in ["val", "test"]:    
        # # Step 7: Save Results
        output_path = os.path.join(
            args.output_path or dataset_config.output_location, 
            f"{d}_inference_results.csv"
        )
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if d == "val":
            val_results_df.to_csv(output_path, index=False)
            logger.info(f"Inference complete! Results saved to {output_path}")
            logger.info(f"Total predictions: {len(val_results_df)}")
        else:
            test_results_df.to_csv(output_path, index=False)
            logger.info(f"Inference complete! Results saved to {output_path}")
            logger.info(f"Total predictions: {len(test_results_df)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run inference with a trained meal image classification model."
    )
    
    parser.add_argument("--config-name", type=str, required=True,
                        help="Path to configuration JSON file")
    parser.add_argument("--checkpoint-path", type=str, required=True,
                        help="Path to model checkpoint (.pth file)")
    parser.add_argument("--inference_image_dir", type=str, default=None,
                        help="Override image directory from config")
    parser.add_argument("--output-path", type=str, default=None,
                        help="Directory to save inference results")
    parser.add_argument("--batch-size", type=int, default=None,
                        help="Override batch size from config")
    parser.add_argument("--hidden-layer-size", type=int, default=None,
                        help="Override hidden layer size from config")

    # SageMaker compatibility (optional)
    parser.add_argument("--modeldir", type=str,
        default=os.environ.get("SM_MODEL_DIR", None),
        help="SageMaker model directory (if running in SageMaker)."
    )
    
    args = parser.parse_args()
    main(args)