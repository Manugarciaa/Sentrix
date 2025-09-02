#!/usr/bin/env python3
"""
Script de entrenamiento especializado para detección de focos de dengue
"""
import sys
import os
from pathlib import Path
sys.path.append('..')

from main import train_dengue_model, validate_dengue_model

def train_with_monitoring(
    model_size='n',  # n, s, m, l, x
    epochs=100,
    batch_size=16,
    img_size=640,
    patience=10
):
    """
    Entrena el modelo con configuraciones optimizadas para detección de focos de dengue
    """
    model_path = f'yolo11{model_size}.pt'
    
    print("=== ENTRENAMIENTO MODELO DETECCIÓN DENGUE ===")
    print(f"Modelo base: {model_path}")
    print(f"Épocas: {epochs}")
    print(f"Tamaño de imagen: {img_size}")
    print(f"Tamaño de lote: {batch_size}")
    print("-" * 50)
    
    # Check if dataset exists
    data_config = 'configs/dataset.yaml'
    if not os.path.exists(data_config):
        print(f"Error: Dataset configuration not found: {data_config}")
        return None
    
    # Check if training data exists
    train_images = Path('data/images/train')
    if not train_images.exists() or not list(train_images.glob('*')):
        print("Error: No training images found in data/images/train/")
        print("Please add training images and labels before starting training.")
        return None
    
    try:
        # Start training
        from ultralytics import YOLO
        model = YOLO(model_path)
        
        results = model.train(
            data=data_config,
            epochs=epochs,
            imgsz=img_size,
            batch=batch_size,
            patience=patience,
            project='models',
            name='dengue_detection',
            save=True,
            save_period=10,  # Save checkpoint every 10 epochs
            # Augmentation parameters for better generalization
            hsv_h=0.015,
            hsv_s=0.7,
            hsv_v=0.4,
            degrees=0.0,
            translate=0.1,
            scale=0.9,
            shear=0.0,
            perspective=0.0,
            flipud=0.0,
            fliplr=0.5,
            mosaic=1.0,
            mixup=0.1
        )
        
        print("\n=== ENTRENAMIENTO COMPLETADO ===")
        print(f"Modelo guardado en: models/dengue_detection/weights/best.pt")
        
        # Validate the trained model
        print("\nIniciando validación del modelo...")
        val_results = validate_dengue_model()
        
        return results
        
    except Exception as e:
        print(f"Error durante el entrenamiento: {e}")
        return None

def resume_training(checkpoint_path, additional_epochs=50):
    """
    Reanuda el entrenamiento desde un checkpoint
    """
    if not os.path.exists(checkpoint_path):
        print(f"Error: Checkpoint not found: {checkpoint_path}")
        return None
    
    print(f"Reanudando entrenamiento desde: {checkpoint_path}")
    
    from ultralytics import YOLO
    model = YOLO(checkpoint_path)
    
    results = model.train(
        resume=True,
        epochs=additional_epochs,
        project='models',
        name='dengue_detection_resumed'
    )
    
    return results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train dengue detection model")
    parser.add_argument("--model", default="n", choices=['n', 's', 'm', 'l', 'x'],
                       help="Model size (n=nano, s=small, m=medium, l=large, x=xlarge)")
    parser.add_argument("--epochs", type=int, default=100, help="Number of epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--resume", help="Resume training from checkpoint")
    
    args = parser.parse_args()
    
    if args.resume:
        results = resume_training(args.resume)
    else:
        results = train_with_monitoring(
            model_size=args.model,
            epochs=args.epochs,
            batch_size=args.batch,
            img_size=args.imgsz
        )