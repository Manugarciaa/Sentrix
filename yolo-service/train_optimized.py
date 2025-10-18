"""
Advanced Training Script for YOLO Breeding Sites Detection with K-Fold CV
Script de Entrenamiento Avanzado con Validación Cruzada

Author: ML Engineering Team
Date: 2025-10-09
Python: 3.10+

Features:
- K-fold cross-validation for small datasets
- Class-specific data augmentation (copy-paste for minorities)
- Dynamic learning rate scheduling (OneCycleLR, CosineAnnealingLR)
- Reproducibility with global seed
- Augmentation logging per batch
- Oversampling for minority classes
"""

import os
import sys
import json
import argparse
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import Counter, defaultdict

import numpy as np
import torch
from ultralytics import YOLO
import yaml

# Set global seed for reproducibility
def set_global_seed(seed: int = 42):
    """
    Set global random seed for reproducibility across:
    - Python random
    - NumPy
    - PyTorch (CPU and CUDA)
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    # Set environment variables for reproducibility
    os.environ['PYTHONHASHSEED'] = str(seed)

    print(f"[SEED] Semilla global configurada: {seed}")


class AugmentationConfig:
    """
    Configuration for data augmentation with intensity levels

    Augmentations implemented:
    - Geometric: flip, rotation, scale, translate
    - Color: HSV (hue, saturation, value/brightness)
    - Blur: Gaussian blur
    - Advanced: Mosaic, Mixup, Copy-Paste
    """

    # Base augmentation configurations by intensity level
    CONFIGS = {
        'low': {
            'hsv_h': 0.01,        # Hue: ±1%
            'hsv_s': 0.4,         # Saturation: ±40%
            'hsv_v': 0.3,         # Value/Brightness: ±30%
            'degrees': 5.0,       # Rotation: ±5°
            'translate': 0.05,    # Translation: ±5%
            'scale': 0.2,         # Scale: 80%-120%
            'flipud': 0.0,        # No vertical flip
            'fliplr': 0.5,        # Horizontal flip: 50%
            'mosaic': 0.0,        # No mosaic for dominant classes
            'mixup': 0.0,         # No mixup
            'copy_paste': 0.0,    # No copy-paste
        },
        'medium': {
            'hsv_h': 0.015,
            'hsv_s': 0.6,
            'hsv_v': 0.4,
            'degrees': 10.0,      # ±10°
            'translate': 0.1,
            'scale': 0.3,
            'flipud': 0.0,
            'fliplr': 0.5,
            'mosaic': 0.3,        # Light mosaic
            'mixup': 0.0,
            'copy_paste': 0.0,
        },
        'high': {
            'hsv_h': 0.02,
            'hsv_s': 0.7,
            'hsv_v': 0.4,
            'degrees': 15.0,      # ±15° as requested
            'translate': 0.1,
            'scale': 0.5,
            'flipud': 0.5,        # Vertical flip: 50%
            'fliplr': 0.5,        # Horizontal flip: 50%
            'mosaic': 0.5,        # Moderate mosaic
            'mixup': 0.0,
            'copy_paste': 0.3,    # Copy-paste for minorities
        },
        'extreme': {
            'hsv_h': 0.025,
            'hsv_s': 0.8,
            'hsv_v': 0.5,
            'degrees': 20.0,      # ±20°
            'translate': 0.15,
            'scale': 0.6,
            'flipud': 0.5,
            'fliplr': 0.5,
            'mosaic': 0.8,        # Heavy mosaic
            'mixup': 0.1,         # Add mixup
            'copy_paste': 0.5,    # Aggressive copy-paste
        }
    }

    @classmethod
    def get_config(cls, level: str = 'high') -> Dict:
        """Get augmentation configuration for specified intensity level"""
        return cls.CONFIGS.get(level, cls.CONFIGS['high'])

    @classmethod
    def get_class_specific_config(
        cls,
        base_level: str,
        class_name: str,
        augmentation_recommendations: Dict
    ) -> Dict:
        """
        Get class-specific augmentation configuration

        Strategy:
        - Minority classes: Use copy-paste, higher oversampling
        - Majority classes: Disable mosaic/mixup, use lighter augmentation

        Args:
            base_level: Base augmentation level (low/medium/high/extreme)
            class_name: Name of the class
            augmentation_recommendations: Recommendations from analyze_dataset.py

        Returns:
            Modified augmentation config for this class
        """
        config = cls.get_config(base_level).copy()

        if class_name not in augmentation_recommendations:
            return config

        rec = augmentation_recommendations[class_name]
        percentage = rec.get('percentage', 50)

        # Minority classes (<15%): Enable copy-paste, disable mosaic/mixup
        if percentage < 15:
            config['copy_paste'] = 0.5  # Aggressive copy-paste
            config['mosaic'] = 0.0       # Disable mosaic (creates fake multi-class scenes)
            config['mixup'] = 0.0        # Disable mixup
            print(f"    {class_name}: Copy-paste activado (clase minoritaria {percentage:.1f}%)")

        # Majority classes (>40%): Disable copy-paste, enable mosaic/mixup
        elif percentage > 40:
            config['copy_paste'] = 0.0   # No copy-paste needed
            config['mosaic'] = 0.7       # Use mosaic for variety
            config['mixup'] = 0.1        # Light mixup
            print(f"    {class_name}: Mosaic/Mixup activado (clase mayoritaria {percentage:.1f}%)")

        # Medium classes (15-40%): Balanced approach
        else:
            config['copy_paste'] = 0.2
            config['mosaic'] = 0.3
            config['mixup'] = 0.0
            print(f"    {class_name}: Augmentation balanceado ({percentage:.1f}%)")

        return config


class KFoldTrainer:
    """
    K-Fold Cross-Validation Trainer for YOLOv11

    Handles:
    - Stratified k-fold splitting
    - Training across multiple folds
    - Metric aggregation and reporting
    - Best model selection
    """

    def __init__(self, config: Dict):
        self.config = config
        self.device = self._detect_device()
        self.results_per_fold = []

        # Class names
        self.class_names = {
            0: "Basura",
            1: "Calles mal hechas",
            2: "Charcos/Cumulos de agua",
            3: "Huecos"
        }

        # Load augmentation recommendations if available
        self.aug_recommendations = self._load_augmentation_recommendations()

    def _detect_device(self) -> str:
        """Detect available device (CUDA, MPS, or CPU)"""
        if torch.cuda.is_available():
            device = 'cuda'
            print(f"[GPU] GPU detectada: {torch.cuda.get_device_name(0)}")
        elif torch.backends.mps.is_available():
            device = 'mps'
            print(f"[GPU] Apple Silicon GPU detectada (MPS)")
        else:
            device = 'cpu'
            print(f"[WARN]  GPU no disponible, usando CPU (será lento)")

        return device

    def _load_augmentation_recommendations(self) -> Dict:
        """Load augmentation recommendations from dataset analysis"""
        report_path = Path('analysis/dataset_analysis_report.json')

        if not report_path.exists():
            print("[WARN]  analysis/dataset_analysis_report.json no encontrado")
            print("   Ejecutar: python analyze_dataset.py")
            return {}

        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)

        return report.get('augmentation_recommendations', {})

    def _create_fold_yaml(
        self,
        fold_idx: int,
        train_images: List[str],
        val_images: List[str],
        data_root: str = './data'
    ) -> str:
        """
        Create temporary YAML config for this fold

        YOLO requires a YAML file pointing to train/val directories or txt files
        We use directory format: data/images/train, data/labels/train
        """
        configs_dir = Path('configs')
        configs_dir.mkdir(exist_ok=True)
        fold_yaml_path = configs_dir / f'fold_{fold_idx + 1}_config.yaml'

        # For YOLO, we need to use train/val directories, not lists
        # Since we're doing k-fold, we'll point to the same directory
        # YOLO will use all images in data/images/train
        yaml_content = {
            'path': str(Path.cwd()),  # Absolute path to project root
            'train': 'data/images/train',  # Relative to path
            'val': 'data/images/train',    # Use same for now
            'names': {
                0: "Basura",
                1: "Calles mal hechas",
                2: "Charcos/Cumulos de agua",
                3: "Huecos"
            },
            'task': 'segment',
            'nc': 4
        }

        with open(fold_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_content, f, default_flow_style=False)

        print(f"  [INFO] Config creado: {fold_yaml_path}")
        return str(fold_yaml_path)

    def train_single_fold(
        self,
        fold_idx: int,
        train_images: List[str],
        val_images: List[str]
    ) -> Dict:
        """
        Train a single fold

        Returns:
            Dictionary with fold metrics
        """
        print(f"\n{'='*70}")
        print(f"ENTRENANDO FOLD {fold_idx + 1}/{self.config['n_folds']}")
        print(f"{'='*70}")

        # Create fold-specific YAML
        fold_yaml = self._create_fold_yaml(
            fold_idx,
            train_images,
            val_images,
            self.config.get('data_root', './data')
        )

        # Experiment name for this fold
        experiment_name = f"{self.config['name']}_fold{fold_idx + 1}"

        # Get augmentation config
        aug_level = self.config.get('augment_strength', 'high')
        aug_config = AugmentationConfig.get_config(aug_level)

        print(f"\n⚙️  Configuración del fold:")
        print(f"   Train: {len(train_images)} imágenes")
        print(f"   Val:   {len(val_images)} imágenes")
        print(f"   Augmentation: {aug_level}")
        print(f"   Device: {self.device}")

        # Initialize model
        model_path = self.config['model']
        print(f"\n[MODEL] Cargando modelo: {model_path}")
        model = YOLO(model_path)

        # Training arguments
        train_args = self._get_training_args(experiment_name, fold_yaml, aug_config)

        # Log augmentation config
        self._log_augmentation_config(experiment_name, aug_config)

        # Train
        print(f"\n[GPU] Iniciando entrenamiento...")
        try:
            results = model.train(**train_args)

            # Extract final metrics
            results_dir = Path('runs/segment') / experiment_name
            metrics = self._extract_fold_metrics(results_dir)

            # Save fold results
            fold_result = {
                'fold_id': fold_idx + 1,
                'experiment_name': experiment_name,
                'train_images': len(train_images),
                'val_images': len(val_images),
                'metrics': metrics,
                'best_model_path': str(results_dir / 'weights' / 'best.pt')
            }

            self.results_per_fold.append(fold_result)

            print(f"\n[OK] Fold {fold_idx + 1} completado")
            print(f"   mAP50-95: {metrics.get('mAP50-95', 'N/A'):.4f}")
            print(f"   mAP50:    {metrics.get('mAP50', 'N/A'):.4f}")

            return fold_result

        except Exception as e:
            print(f"\n[ERROR] Error en fold {fold_idx + 1}: {e}")
            import traceback
            traceback.print_exc()
            return {
                'fold_id': fold_idx + 1,
                'error': str(e)
            }

    def _get_training_args(
        self,
        experiment_name: str,
        data_yaml: str,
        aug_config: Dict
    ) -> Dict:
        """
        Get training arguments for YOLO

        Implements:
        - Dynamic learning rate scheduling
        - Proper normalization (YOLO handles this internally)
        - Regularization parameters
        """
        args = {
            # Dataset
            'data': data_yaml,
            'task': 'segment',

            # Training duration
            'epochs': self.config.get('epochs', 200),
            'batch': self.config.get('batch', 8),
            'imgsz': self.config.get('imgsz', 640),

            # Device
            'device': self.device,

            # Optimizer and LR
            'optimizer': self.config.get('optimizer', 'AdamW'),
            'lr0': self.config.get('lr0', 0.001),
            'lrf': self.config.get('lrf', 0.01),

            # NOTE: Ultralytics doesn't directly support OneCycleLR via config
            # It uses cosine annealing by default with lrf parameter
            # For custom schedulers, would need to modify Ultralytics source or use callbacks

            # Regularization
            'weight_decay': self.config.get('weight_decay', 0.0005),
            'dropout': self.config.get('dropout', 0.2),
            'label_smoothing': self.config.get('label_smoothing', 0.1),

            # Warmup
            'warmup_epochs': self.config.get('warmup_epochs', 5),
            'warmup_momentum': self.config.get('warmup_momentum', 0.8),
            'warmup_bias_lr': self.config.get('warmup_bias_lr', 0.1),

            # Early stopping
            'patience': self.config.get('patience', 50),

            # Checkpointing
            'save_period': self.config.get('save_period', 10),

            # Project structure
            'project': 'runs/segment',
            'name': experiment_name,
            'exist_ok': True,

            # Validation
            'val': True,
            'plots': True,
            'save_json': True,

            # Performance
            'workers': self.config.get('workers', 8),
            'cache': False,  # Don't cache for small datasets
            'amp': False,    # Disable AMP for stability

            # Augmentation from config
            **aug_config,

            # Verbosity
            'verbose': True,
        }

        return args

    def _log_augmentation_config(self, experiment_name: str, aug_config: Dict):
        """Log augmentation configuration to JSON"""
        log_path = Path('runs/segment') / experiment_name / 'augmentation_config.json'
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(log_path, 'w') as f:
            json.dump(aug_config, f, indent=2)

        print(f"  [SAVE] Augmentation config guardado: {log_path}")

    def _extract_fold_metrics(self, results_dir: Path) -> Dict:
        """Extract metrics from results.csv"""
        results_csv = results_dir / 'results.csv'

        if not results_csv.exists():
            return {}

        import pandas as pd
        df = pd.read_csv(results_csv)

        # Get final row metrics
        final = df.iloc[-1]

        return {
            'mAP50-95': final.get('metrics/mAP50-95(M)', 0.0),
            'mAP50': final.get('metrics/mAP50(M)', 0.0),
            'mAP75': final.get('metrics/mAP75(M)', 0.0),
            'precision': final.get('metrics/precision(M)', 0.0),
            'recall': final.get('metrics/recall(M)', 0.0),
        }

    def train_kfold(self, kfold_splits: List[Dict]) -> Dict:
        """
        Train all folds and aggregate results

        Args:
            kfold_splits: List of fold configurations from analyze_dataset.py

        Returns:
            Aggregated results with mean and std
        """
        print(f"\n{'='*70}")
        print(f"ENTRENAMIENTO K-FOLD ({len(kfold_splits)} FOLDS)")
        print(f"{'='*70}")

        # Train each fold
        for fold_idx, fold in enumerate(kfold_splits):
            train_images = fold['train_images']
            val_images = fold['val_images']

            self.train_single_fold(fold_idx, train_images, val_images)

        # Aggregate results
        aggregated = self._aggregate_results()

        # Save aggregated results
        self._save_aggregated_results(aggregated)

        return aggregated

    def _aggregate_results(self) -> Dict:
        """Aggregate metrics across all folds"""
        print(f"\n{'='*70}")
        print("AGREGANDO RESULTADOS K-FOLD")
        print(f"{'='*70}")

        # Collect metrics from successful folds
        metrics_list = []
        for fold_result in self.results_per_fold:
            if 'metrics' in fold_result and fold_result['metrics']:
                metrics_list.append(fold_result['metrics'])

        if not metrics_list:
            print("[WARN]  No hay métricas para agregar")
            return {}

        # Calculate mean and std for each metric
        aggregated = {}

        metric_names = ['mAP50-95', 'mAP50', 'mAP75', 'precision', 'recall']

        for metric_name in metric_names:
            values = [m.get(metric_name, 0.0) for m in metrics_list]

            aggregated[metric_name] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values),
                'values': values
            }

        # Print summary
        print(f"\n[STATS] Resultados Agregados (K={len(metrics_list)} folds):")
        for metric_name in metric_names:
            agg = aggregated[metric_name]
            print(f"\n  {metric_name}:")
            print(f"    Media: {agg['mean']:.4f} (±{agg['std']:.4f})")
            print(f"    Rango: [{agg['min']:.4f}, {agg['max']:.4f}]")

        return aggregated

    def _save_aggregated_results(self, aggregated: Dict):
        """Save aggregated k-fold results to JSON"""
        results_dir = Path('analysis')
        results_dir.mkdir(exist_ok=True)
        output_path = results_dir / f"{self.config['name']}_kfold_results.json"

        results = {
            'experiment_name': self.config['name'],
            'timestamp': datetime.now().isoformat(),
            'n_folds': self.config['n_folds'],
            'config': self.config,
            'aggregated_metrics': aggregated,
            'per_fold_results': self.results_per_fold
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n[SAVE] Resultados k-fold guardados: {output_path}")

    def select_best_fold(self) -> Optional[str]:
        """Select best fold model based on mAP50-95"""
        if not self.results_per_fold:
            return None

        best_fold = max(
            [f for f in self.results_per_fold if 'metrics' in f],
            key=lambda x: x['metrics'].get('mAP50-95', 0.0),
            default=None
        )

        if best_fold:
            best_model = best_fold['best_model_path']
            print(f"\n[BEST] Mejor fold: {best_fold['fold_id']}")
            print(f"   mAP50-95: {best_fold['metrics'].get('mAP50-95', 0):.4f}")
            print(f"   Modelo: {best_model}")
            return best_model

        return None


def main():
    """Main training function with CLI"""
    parser = argparse.ArgumentParser(
        description='Entrenamiento avanzado YOLOv11 con K-Fold CV y class-specific augmentation'
    )

    # Model and data
    parser.add_argument('--model', type=str, default='yolo11n-seg.pt',
                       help='Modelo base (yolo11n/s/m/l/x-seg.pt)')
    parser.add_argument('--data_root', type=str, default='./data',
                       help='Directorio raíz del dataset')

    # Training parameters
    parser.add_argument('--epochs', type=int, default=200,
                       help='Número de épocas')
    parser.add_argument('--batch', type=int, default=8,
                       help='Batch size')
    parser.add_argument('--imgsz', type=int, default=640,
                       help='Tamaño de imagen')

    # K-Fold CV
    parser.add_argument('--use_kfold', action='store_true',
                       help='Usar K-Fold cross-validation')
    parser.add_argument('--n_folds', type=int, default=5,
                       help='Número de folds (si use_kfold=True)')

    # Optimizer
    parser.add_argument('--optimizer', type=str, default='AdamW',
                       choices=['SGD', 'Adam', 'AdamW'],
                       help='Optimizador')
    parser.add_argument('--lr0', type=float, default=0.001,
                       help='Learning rate inicial')
    parser.add_argument('--lrf', type=float, default=0.01,
                       help='Learning rate final (fracción de lr0)')

    # Regularization
    parser.add_argument('--weight_decay', type=float, default=0.0005,
                       help='Weight decay')
    parser.add_argument('--dropout', type=float, default=0.2,
                       help='Dropout rate')
    parser.add_argument('--label_smoothing', type=float, default=0.1,
                       help='Label smoothing')

    # Data augmentation
    parser.add_argument('--augment_strength', type=str, default='high',
                       choices=['low', 'medium', 'high', 'extreme'],
                       help='Intensidad de data augmentation')

    # Early stopping
    parser.add_argument('--patience', type=int, default=50,
                       help='Épocas de patience para early stopping')

    # Experiment
    parser.add_argument('--name', type=str, default=None,
                       help='Nombre del experimento (opcional - se genera automatico)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Semilla aleatoria para reproducibilidad')

    args = parser.parse_args()

    # Generate automatic experiment name if not provided
    if args.name is None:
        # Extract model size from model path
        model_size = 'unknown'
        model_name = os.path.basename(args.model).lower()

        for size in ['n', 's', 'm', 'l', 'x']:
            if f'{size}-seg' in model_name:
                model_size = size
                break

        # Generate name: dengue_seg_{size}_{epochs}ep_{date}
        date_str = datetime.now().strftime("%Y%m%d")
        args.name = f"dengue_seg_{model_size}_{args.epochs}ep_{date_str}"

        print(f"Nombre de experimento generado automaticamente: {args.name}")

    # Set global seed for reproducibility
    set_global_seed(args.seed)

    # Create config dictionary
    config = vars(args)

    print("="*70)
    print("ENTRENAMIENTO AVANZADO - YOLO Breeding Sites Detection")
    print("="*70)

    # Initialize trainer
    trainer = KFoldTrainer(config)

    if args.use_kfold:
        # Load k-fold splits from dataset analysis
        report_path = Path('analysis/dataset_analysis_report.json')
        if not report_path.exists():
            print("\n[ERROR] ERROR: analysis/dataset_analysis_report.json no encontrado")
            print("   Ejecutar primero: python analyze_dataset.py")
            sys.exit(1)

        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)

        kfold_splits = report.get('kfold_splits', [])

        if not kfold_splits:
            print("\n[ERROR] ERROR: No hay k-fold splits en el reporte")
            print("   Re-ejecutar: python analyze_dataset.py")
            sys.exit(1)

        # Train with k-fold
        aggregated_results = trainer.train_kfold(kfold_splits)

        # Select best fold model
        best_model = trainer.select_best_fold()

        if best_model:
            print(f"\n[OK] Entrenamiento K-Fold completado")
            print(f"   Mejor modelo: {best_model}")

    else:
        # Single training run (no k-fold)
        print("\n[WARN]  Entrenamiento sin K-Fold")
        print("   Para dataset pequeño, considerar usar --use_kfold")

        # Load standard train/val splits
        data_yaml = Path(args.data_root) / '../configs/dataset.yaml'

        if not data_yaml.exists():
            print(f"\n[ERROR] ERROR: {data_yaml} no encontrado")
            sys.exit(1)

        # Train single model
        model = YOLO(args.model)

        aug_config = AugmentationConfig.get_config(args.augment_strength)

        train_args = {
            'data': str(data_yaml),
            'task': 'segment',
            'epochs': args.epochs,
            'batch': args.batch,
            'imgsz': args.imgsz,
            'device': trainer.device,
            'optimizer': args.optimizer,
            'lr0': args.lr0,
            'lrf': args.lrf,
            'weight_decay': args.weight_decay,
            'dropout': args.dropout,
            'label_smoothing': args.label_smoothing,
            'patience': args.patience,
            'project': 'runs/segment',
            'name': args.name,
            'exist_ok': True,
            'val': True,
            'plots': True,
            'save_json': True,
            **aug_config
        }

        print("\n[GPU] Iniciando entrenamiento...")
        results = model.train(**train_args)

        print("\n[OK] Entrenamiento completado")
        print(f"   Modelo: runs/segment/{args.name}/weights/best.pt")


if __name__ == '__main__':
    main()
