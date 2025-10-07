"""
YOLO Training Script for IC Text Detection
Creates and trains a custom YOLOv8 model specifically for IC text detection

This script implements:
1. Dataset preparation for IC text detection
2. Data augmentation using albumentations
3. Custom YOLO training for IC markings
4. Model evaluation and validation
5. Export for production use

Based on research papers and IC-specific requirements
"""

import os
import cv2
import numpy as np
import yaml
import json
import shutil
from pathlib import Path
from typing import List, Tuple, Dict
import albumentations as A
from ultralytics import YOLO
from sklearn.model_selection import train_test_split
import torch

class ICTextDatasetCreator:
    """
    Creates training dataset for IC text detection
    Generates synthetic data and augmentations
    """
    
    def __init__(self, output_dir: str = "ic_text_dataset"):
        self.output_dir = Path(output_dir)
        self.setup_directories()
        self.setup_augmentations()
        
    def setup_directories(self):
        """Create dataset directory structure"""
        directories = [
            self.output_dir / "images" / "train",
            self.output_dir / "images" / "val",
            self.output_dir / "images" / "test",
            self.output_dir / "labels" / "train",
            self.output_dir / "labels" / "val", 
            self.output_dir / "labels" / "test"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        print(f"✓ Created dataset directories in {self.output_dir}")
    
    def setup_augmentations(self):
        """Setup augmentation pipeline for IC images"""
        self.augmentation_pipeline = A.Compose([
            # Geometric transformations
            A.Rotate(limit=15, p=0.5),
            A.Perspective(scale=(0.05, 0.1), p=0.3),
            A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.2, rotate_limit=10, p=0.5),
            
            # Lighting and contrast (IC specific)
            A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=0.7),
            A.CLAHE(clip_limit=4.0, tile_grid_size=(4, 4), p=0.5),
            A.GaussianBlur(blur_limit=(1, 3), p=0.3),
            
            # Noise and artifacts (manufacturing variations)
            A.GaussNoise(var_limit=(10, 50), p=0.3),
            A.ISONoise(color_shift=(0.01, 0.05), intensity=(0.1, 0.5), p=0.2),
            A.RandomGamma(gamma_limit=(80, 120), p=0.3),
            
            # IC-specific distortions
            A.OpticalDistortion(distort_limit=0.1, p=0.2),
            A.GridDistortion(distort_limit=0.1, p=0.2),
            
        ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))
    
    def generate_synthetic_ic_data(self, num_samples: int = 1000):
        """
        Generate synthetic IC images with text annotations
        Creates diverse IC-like images with various text patterns
        """
        print(f"🎨 Generating {num_samples} synthetic IC images...")
        
        # IC text patterns (common IC markings)
        ic_patterns = [
            # Microcontrollers
            "ATMEGA328P", "ATMEGA32U4", "ATMEGA2560", "STM32F103", "STM32F407",
            "PIC16F877A", "PIC18F4550", "ESP32", "ESP8266", "Arduino",
            
            # Memory chips
            "AT24C32", "AT24C64", "25LC256", "W25Q32", "W25Q64",
            
            # Logic chips  
            "SN74HC00", "SN74HC04", "SN74HC595", "CD4017", "NE555",
            
            # Power management
            "LM317", "LM7805", "AMS1117", "LP2950", "TPS7233",
            
            # Date codes
            "0723", "1223", "0824", "1124", "0622", "1022", "0323", "0923"
        ]
        
        manufacturers = ["ATMEL", "ST", "MICROCHIP", "TI", "ESPRESSIF", "ARDUINO"]
        
        generated_count = 0
        
        for i in range(num_samples):
            try:
                # Create synthetic IC image
                image, annotations = self._create_synthetic_ic_image(ic_patterns, manufacturers)
                
                if image is not None and annotations:
                    # Save image
                    image_name = f"synthetic_ic_{i:06d}.jpg"
                    image_path = self.output_dir / "images" / "train" / image_name
                    cv2.imwrite(str(image_path), image)
                    
                    # Save annotations
                    label_name = f"synthetic_ic_{i:06d}.txt"
                    label_path = self.output_dir / "labels" / "train" / label_name
                    
                    with open(label_path, 'w') as f:
                        for ann in annotations:
                            f.write(f"{ann['class']} {ann['x_center']} {ann['y_center']} {ann['width']} {ann['height']}\n")
                    
                    generated_count += 1
                    
                    if (i + 1) % 100 == 0:
                        print(f"  Generated {i + 1}/{num_samples} images")
                        
            except Exception as e:
                print(f"Error generating image {i}: {e}")
                continue
        
        print(f"✓ Successfully generated {generated_count} synthetic IC images")
        return generated_count
    
    def _create_synthetic_ic_image(self, ic_patterns: List[str], manufacturers: List[str]) -> Tuple[np.ndarray, List[Dict]]:
        """Create a single synthetic IC image with text"""
        # Random image size (simulating different resolutions)
        width = np.random.randint(200, 800)
        height = np.random.randint(150, 600)
        
        # Create base IC-like image
        image = self._create_ic_background(width, height)
        
        annotations = []
        
        # Add 1-4 text regions
        num_texts = np.random.randint(1, 5)
        
        for _ in range(num_texts):
            # Choose text content
            if np.random.random() < 0.7:
                text = np.random.choice(ic_patterns)
            else:
                text = np.random.choice(manufacturers)
            
            # Random position and size
            text_annotation = self._add_text_to_image(image, text)
            if text_annotation:
                annotations.append(text_annotation)
        
        return image, annotations
    
    def _create_ic_background(self, width: int, height: int) -> np.ndarray:
        """Create IC-like background"""
        # Random IC color (black, gray, dark green, etc.)
        colors = [
            (20, 20, 20),      # Black IC
            (60, 60, 60),      # Gray IC  
            (30, 50, 30),      # Dark green
            (40, 35, 25),      # Brown
        ]
        
        base_color = np.random.choice(colors)
        
        # Create base image
        image = np.full((height, width, 3), base_color, dtype=np.uint8)
        
        # Add some texture/noise
        noise = np.random.normal(0, 10, (height, width, 3))
        image = np.clip(image + noise, 0, 255).astype(np.uint8)
        
        # Add some IC-like features (pins, edges, etc.)
        if np.random.random() < 0.3:
            # Add rectangular outline (IC package)
            cv2.rectangle(image, (10, 10), (width-10, height-10), (100, 100, 100), 2)
        
        if np.random.random() < 0.2:
            # Add pin-like lines
            pin_color = (80, 80, 80)
            for i in range(0, width, 20):
                cv2.line(image, (i, 0), (i, 10), pin_color, 1)
                cv2.line(image, (i, height-10), (i, height), pin_color, 1)
        
        return image
    
    def _add_text_to_image(self, image: np.ndarray, text: str) -> Dict:
        """Add text to image and return annotation"""
        height, width = image.shape[:2]
        
        # Random text properties
        font_scale = np.random.uniform(0.3, 1.2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = np.random.randint(1, 3)
        
        # Text color (usually white or light on dark IC)
        text_colors = [(255, 255, 255), (220, 220, 220), (200, 200, 200), (180, 180, 180)]
        text_color = np.random.choice(text_colors)
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Random position (ensure text fits)
        margin = 10
        if text_width + 2*margin > width or text_height + 2*margin > height:
            return None
        
        x = np.random.randint(margin, width - text_width - margin)
        y = np.random.randint(text_height + margin, height - baseline - margin)
        
        # Draw text
        cv2.putText(image, text, (x, y), font, font_scale, text_color, thickness)
        
        # Create YOLO annotation (normalized coordinates)
        x_center = (x + text_width / 2) / width
        y_center = (y - text_height / 2) / height
        norm_width = text_width / width
        norm_height = text_height / height
        
        return {
            'class': 0,  # Text class
            'x_center': x_center,
            'y_center': y_center,
            'width': norm_width,
            'height': norm_height
        }
    
    def augment_existing_images(self, source_dir: str, target_split: str = "train"):
        """
        Augment existing IC images and create annotations
        Uses existing images from test_images directory
        """
        source_path = Path(source_dir)
        if not source_path.exists():
            print(f"⚠️  Source directory not found: {source_dir}")
            return 0
        
        image_files = list(source_path.glob("*.png")) + list(source_path.glob("*.jpg")) + list(source_path.glob("*.jpeg"))
        
        if not image_files:
            print(f"⚠️  No images found in {source_dir}")
            return 0
        
        print(f"🖼️  Augmenting {len(image_files)} existing images...")
        
        augmented_count = 0
        
        for image_file in image_files:
            try:
                # Load image
                image = cv2.imread(str(image_file))
                if image is None:
                    continue
                
                # Create multiple augmented versions
                for aug_idx in range(5):  # 5 augmentations per image
                    try:
                        # For now, create simple bounding box annotation
                        # In production, you would manually annotate or use pre-annotated data
                        annotations = self._create_fullimage_annotation()
                        
                        # Apply augmentation
                        augmented = self.augmentation_pipeline(
                            image=image,
                            bboxes=[[ann['x_center'] - ann['width']/2, 
                                   ann['y_center'] - ann['height']/2,
                                   ann['x_center'] + ann['width']/2,
                                   ann['y_center'] + ann['height']/2] for ann in annotations],
                            class_labels=[ann['class'] for ann in annotations]
                        )
                        
                        aug_image = augmented['image']
                        aug_bboxes = augmented['bboxes']
                        
                        # Save augmented image
                        image_name = f"aug_{image_file.stem}_{aug_idx}.jpg"
                        image_path = self.output_dir / "images" / target_split / image_name
                        cv2.imwrite(str(image_path), aug_image)
                        
                        # Save annotations
                        label_name = f"aug_{image_file.stem}_{aug_idx}.txt"
                        label_path = self.output_dir / "labels" / target_split / label_name
                        
                        with open(label_path, 'w') as f:
                            for i, bbox in enumerate(aug_bboxes):
                                x1, y1, x2, y2 = bbox
                                x_center = (x1 + x2) / 2
                                y_center = (y1 + y2) / 2
                                width = x2 - x1
                                height = y2 - y1
                                f.write(f"0 {x_center} {y_center} {width} {height}\n")
                        
                        augmented_count += 1
                        
                    except Exception as e:
                        print(f"Error augmenting {image_file} (version {aug_idx}): {e}")
                        continue
                        
            except Exception as e:
                print(f"Error processing {image_file}: {e}")
                continue
        
        print(f"✓ Created {augmented_count} augmented images")
        return augmented_count
    
    def _create_fullimage_annotation(self) -> List[Dict]:
        """Create annotation for full image (fallback when manual annotation not available)"""
        return [{
            'class': 0,
            'x_center': 0.5,
            'y_center': 0.5,
            'width': 0.8,
            'height': 0.6
        }]
    
    def create_dataset_config(self):
        """Create YAML config file for YOLO training"""
        config = {
            'path': str(self.output_dir.absolute()),
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test',
            'nc': 1,  # Number of classes
            'names': ['text']  # Class names
        }
        
        config_path = self.output_dir / "dataset.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"✓ Dataset config saved to {config_path}")
        return config_path


class ICTextYOLOTrainer:
    """
    YOLO trainer specifically for IC text detection
    """
    
    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
    def train_model(self, epochs: int = 100, batch_size: int = 16, image_size: int = 640):
        """Train YOLO model for IC text detection"""
        print(f"🚀 Starting YOLO training for IC text detection")
        print(f"📊 Epochs: {epochs}, Batch Size: {batch_size}, Image Size: {image_size}")
        
        # Load YOLOv8 nano model (lightweight for text detection)
        model = YOLO('yolov8n.pt')
        
        # Dataset config
        dataset_config = self.dataset_path / "dataset.yaml"
        
        if not dataset_config.exists():
            print(f"❌ Dataset config not found: {dataset_config}")
            return None
        
        # Training arguments
        train_args = {
            'data': str(dataset_config),
            'epochs': epochs,
            'batch': batch_size,
            'imgsz': image_size,
            'project': str(self.models_dir),
            'name': 'ic_text_detection',
            'device': 0 if torch.cuda.is_available() else 'cpu',
            'workers': 4,
            'patience': 20,
            'save': True,
            'plots': True,
            'verbose': True
        }
        
        print(f"🔧 Training arguments: {train_args}")
        
        try:
            # Start training
            results = model.train(**train_args)
            
            # Save the trained model
            best_model_path = self.models_dir / "ic_text_detection" / "weights" / "best.pt"
            final_model_path = self.models_dir / "ic_text_detection.pt"
            
            if best_model_path.exists():
                shutil.copy(best_model_path, final_model_path)
                print(f"✓ Best model saved to: {final_model_path}")
            
            return results
            
        except Exception as e:
            print(f"❌ Training failed: {e}")
            return None
    
    def evaluate_model(self, model_path: str):
        """Evaluate trained model"""
        print(f"📊 Evaluating model: {model_path}")
        
        if not os.path.exists(model_path):
            print(f"❌ Model not found: {model_path}")
            return None
        
        model = YOLO(model_path)
        dataset_config = self.dataset_path / "dataset.yaml"
        
        try:
            # Validation
            results = model.val(data=str(dataset_config))
            
            print(f"✓ Model evaluation completed")
            print(f"📈 mAP50: {results.box.map50:.3f}")
            print(f"📈 mAP50-95: {results.box.map:.3f}")
            
            return results
            
        except Exception as e:
            print(f"❌ Evaluation failed: {e}")
            return None


def main():
    """Main training pipeline"""
    print("🤖 YOLO IC Text Detection Training Pipeline")
    print("=" * 60)
    
    # Step 1: Create dataset
    print("📦 Step 1: Creating training dataset")
    dataset_creator = ICTextDatasetCreator()
    
    # Generate synthetic data
    synthetic_count = dataset_creator.generate_synthetic_ic_data(num_samples=1000)
    
    # Augment existing images
    existing_count = dataset_creator.augment_existing_images("test_images", "train")
    
    # Create validation split from some training data
    validation_count = dataset_creator.generate_synthetic_ic_data(num_samples=200)
    
    # Create dataset config
    config_path = dataset_creator.create_dataset_config()
    
    print(f"✓ Dataset created:")
    print(f"  Synthetic images: {synthetic_count}")
    print(f"  Augmented images: {existing_count}")
    print(f"  Validation images: {validation_count}")
    
    # Step 2: Train model
    print(f"\n🚀 Step 2: Training YOLO model")
    trainer = ICTextYOLOTrainer("ic_text_dataset")
    
    # Train with different configurations
    print(f"🔧 Starting training (this may take a while)...")
    
    results = trainer.train_model(
        epochs=50,  # Reduced for testing
        batch_size=8,  # Smaller batch for lower memory usage
        image_size=416  # Smaller image size for faster training
    )
    
    if results:
        print(f"✅ Training completed successfully!")
        
        # Step 3: Evaluate model
        print(f"\n📊 Step 3: Evaluating trained model")
        model_path = "models/ic_text_detection.pt"
        
        if os.path.exists(model_path):
            eval_results = trainer.evaluate_model(model_path)
            
            if eval_results:
                print(f"✅ Model evaluation completed!")
            else:
                print(f"⚠️  Model evaluation failed")
        else:
            print(f"⚠️  Trained model not found at {model_path}")
    
    else:
        print(f"❌ Training failed!")
    
    print(f"\n🎯 Training pipeline completed!")
    print(f"💡 Next steps:")
    print(f"  1. Test the trained model with test_yolo_system.py")
    print(f"  2. Fine-tune training parameters if needed")
    print(f"  3. Add more manually annotated data for better accuracy")


if __name__ == "__main__":
    main()