"""
Simple YOLO Training Script - Fixed version without freezes
Script de Entrenamiento Simple y Confiable
"""

import os
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO

def train_model(
    model_path='models/yolo11s-seg.pt',
    epochs=100,
    batch=8,
    imgsz=640,
    name=None
):
    """
    Train YOLO model with reliable settings
    """
    # Auto-generate name if not provided
    if name is None:
        model_size = 'unknown'
        model_name = os.path.basename(model_path).lower()

        for size in ['n', 's', 'm', 'l', 'x']:
            if f'{size}-seg' in model_name:
                model_size = size
                break

        date_str = datetime.now().strftime("%Y%m%d")
        name = f"dengue_seg_{model_size}_{epochs}ep_{date_str}"

    print(f"="*70)
    print(f"YOLO Training - {name}")
    print(f"="*70)
    print(f"Model: {model_path}")
    print(f"Epochs: {epochs}")
    print(f"Batch: {batch}")
    print(f"="*70)

    # Load model
    model = YOLO(model_path)

    # Training arguments - simplified and stable
    train_args = {
        # Dataset
        'data': 'configs/dataset.yaml',
        'task': 'segment',

        # Training duration
        'epochs': epochs,
        'batch': batch,
        'imgsz': imgsz,

        # Device
        'device': 0,  # Use GPU 0

        # Optimizer
        'optimizer': 'AdamW',
        'lr0': 0.001,
        'lrf': 0.01,

        # Regularization
        'weight_decay': 0.0005,
        'dropout': 0.2,

        # Data Augmentation
        'hsv_h': 0.02,
        'hsv_s': 0.7,
        'hsv_v': 0.4,
        'degrees': 15.0,
        'translate': 0.1,
        'scale': 0.5,
        'flipud': 0.5,
        'fliplr': 0.5,
        'mosaic': 0.5,
        'mixup': 0.0,
        'copy_paste': 0.3,

        # Early stopping
        'patience': 50,

        # Checkpointing
        'save_period': -1,  # Only save best and last

        # Project structure
        'project': 'runs/segment',
        'name': name,
        'exist_ok': True,

        # Validation
        'val': True,
        'plots': False,  # Disable plots to avoid validation hangs
        'save_json': False,  # Disable JSON to speed up validation

        # Performance
        'workers': 4,  # Reduce workers to avoid bottlenecks
        'cache': False,
        'amp': True,  # Enable AMP for speed

        # Verbosity
        'verbose': True,
        'deterministic': True,
    }

    print("\nStarting training...")
    print("This may take 15-30 minutes depending on your GPU\n")

    # Train
    try:
        results = model.train(**train_args)

        print(f"\n{'='*70}")
        print("TRAINING COMPLETED SUCCESSFULLY!")
        print(f"{'='*70}")
        print(f"Best model: runs/segment/{name}/weights/best.pt")
        print(f"Last model: runs/segment/{name}/weights/last.pt")
        print(f"Results: runs/segment/{name}/results.csv")

        return results

    except Exception as e:
        print(f"\n[ERROR] Training failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Simple YOLO Training')
    parser.add_argument('--model', type=str, default='models/yolo11s-seg.pt')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch', type=int, default=8)
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--name', type=str, default=None)

    args = parser.parse_args()

    train_model(
        model_path=args.model,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        name=args.name
    )
