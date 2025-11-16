"""
Advanced Dataset Analysis for YOLO Breeding Sites Detection
Análisis Avanzado del Dataset para Detección de Criaderos

Author: ML Engineering Team
Date: 2025-10-09
Python: 3.10+

This script provides comprehensive dataset analysis including:
- Class distribution and imbalance metrics
- Image quality statistics
- Stratified split recommendations for k-fold cross-validation
- Data augmentation strategy recommendations
"""

import os
import json
import yaml
import random
import argparse
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional

import numpy as np
from PIL import Image

# Try to import matplotlib for visualization (optional)
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("[WARN]  matplotlib no disponible - gráficos deshabilitados")


class AdvancedDatasetAnalyzer:
    """
    Advanced analyzer with k-fold split generation and augmentation recommendations
    """

    def __init__(self, data_root: str = './data'):
        self.data_root = Path(data_root)
        self.class_names = {
            0: "Basura",
            1: "Calles mal hechas",
            2: "Charcos/Cumulos de agua",
            3: "Huecos"
        }

        # Statistics storage
        self.stats = {
            'train': defaultdict(int),
            'val': defaultdict(int),
            'test': defaultdict(int)
        }

        # Image-level information for k-fold splitting
        self.image_annotations = []  # List of (image_path, class_ids)

    def analyze_split(self, split_name: str) -> Tuple[Counter, List[int]]:
        """
        Analyze a specific dataset split

        Returns:
            class_counts: Counter of class occurrences
            instances_per_image: List of instance counts per image
        """
        print(f"\n{'='*70}")
        print(f"Analizando {split_name.upper()} set")
        print(f"{'='*70}")

        images_dir = self.data_root / 'images' / split_name
        labels_dir = self.data_root / 'labels' / split_name

        # Count images
        images = list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.png'))
        print(f"Total de imágenes: {len(images)}")

        # Analyze labels
        class_counts = Counter()
        instances_per_image = []
        annotation_areas = []
        image_sizes = []

        for label_file in labels_dir.glob('*.txt'):
            with open(label_file, 'r') as f:
                lines = f.readlines()

                # Filter empty lines
                lines = [l for l in lines if l.strip()]
                instances_per_image.append(len(lines))

                # Extract class IDs for this image
                image_classes = []

                for line in lines:
                    parts = line.strip().split()
                    if len(parts) == 0:
                        continue

                    class_id = int(parts[0])
                    class_counts[class_id] += 1
                    image_classes.append(class_id)

                    # Calculate approximate area from segmentation polygon
                    if len(parts) > 5:  # Segmentation format
                        coords = [float(x) for x in parts[1:]]
                        xs = coords[0::2]
                        ys = coords[1::2]
                        if xs and ys:
                            width = max(xs) - min(xs)
                            height = max(ys) - min(ys)
                            annotation_areas.append(width * height)

                # Store for k-fold splitting (only train split matters)
                if split_name == 'train':
                    img_path = images_dir / (label_file.stem + '.jpg')
                    if not img_path.exists():
                        img_path = images_dir / (label_file.stem + '.png')

                    if img_path.exists():
                        self.image_annotations.append((str(img_path), image_classes))

        # Analyze image dimensions (sample)
        sample_size = min(20, len(images))
        for img_path in random.sample(list(images), sample_size):
            try:
                with Image.open(img_path) as img:
                    image_sizes.append(img.size)
            except Exception as e:
                print(f"[WARN]  Error leyendo {img_path.name}: {e}")

        # Print statistics
        self._print_split_statistics(
            split_name, class_counts, instances_per_image,
            annotation_areas, image_sizes
        )

        return class_counts, instances_per_image

    def _print_split_statistics(
        self,
        split_name: str,
        class_counts: Counter,
        instances_per_image: List[int],
        annotation_areas: List[float],
        image_sizes: List[Tuple[int, int]]
    ):
        """Print detailed statistics for a split"""

        print(f"\n[STATS] Distribución de clases:")
        total_instances = sum(class_counts.values())

        for class_id in sorted(self.class_names.keys()):
            class_name = self.class_names[class_id]
            count = class_counts.get(class_id, 0)
            percentage = (count / total_instances * 100) if total_instances > 0 else 0

            # Store for overall analysis
            self.stats[split_name][class_name] = count

            # Visual indicator
            bar = '█' * int(percentage / 2)
            print(f"  {class_id}: {class_name:25s} - {count:4d} instancias ({percentage:5.1f}%) {bar}")

        if instances_per_image:
            print(f"\n[DATA] Instancias por imagen:")
            print(f"  Promedio: {np.mean(instances_per_image):.2f}")
            print(f"  Mínimo:   {min(instances_per_image)}")
            print(f"  Máximo:   {max(instances_per_image)}")
            print(f"  Mediana:  {np.median(instances_per_image):.2f}")

        if annotation_areas:
            print(f"\n[SIZE] Tamaño de anotaciones (normalizado):")
            print(f"  Promedio: {np.mean(annotation_areas):.4f}")
            print(f"  Mínimo:   {min(annotation_areas):.4f}")
            print(f"  Máximo:   {max(annotation_areas):.4f}")

        if image_sizes:
            widths = [s[0] for s in image_sizes]
            heights = [s[1] for s in image_sizes]
            print(f"\n[IMG]  Dimensiones de imágenes (muestra de {len(image_sizes)}):")
            print(f"  Ancho:  {np.mean(widths):.0f}px (±{np.std(widths):.0f})")
            print(f"  Alto:   {np.mean(heights):.0f}px (±{np.std(heights):.0f})")

    def calculate_class_imbalance(self) -> Tuple[Counter, float]:
        """
        Calculate overall class imbalance metrics

        Returns:
            total_counts: Aggregated class counts across all splits
            imbalance_ratio: Ratio between most and least common class
        """
        print(f"\n{'='*70}")
        print("ANÁLISIS DE DESBALANCE DE CLASES")
        print(f"{'='*70}")

        # Aggregate counts
        total_counts = Counter()
        for split in ['train', 'val', 'test']:
            for class_name, count in self.stats[split].items():
                total_counts[class_name] += count

        if not total_counts:
            print("[WARN]  No se encontraron instancias")
            return total_counts, 0.0

        # Calculate imbalance ratio
        counts_only = [c for c in total_counts.values() if c > 0]
        if len(counts_only) < 2:
            imbalance_ratio = 1.0
        else:
            max_count = max(counts_only)
            min_count = min(counts_only)
            imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')

        print(f"\n[GRAPH] Ratio de desbalance: {imbalance_ratio:.2f}x")

        # Provide recommendations
        self._print_imbalance_recommendations(imbalance_ratio)

        # Print detailed distribution
        print(f"\n[STATS] Distribución total por clase:")
        total = sum(total_counts.values())
        for class_name in sorted(total_counts.keys(), key=lambda x: total_counts[x], reverse=True):
            count = total_counts[class_name]
            percentage = (count / total * 100) if total > 0 else 0
            bar = '█' * int(percentage / 2)
            print(f"  {class_name:25s}: {count:4d} ({percentage:5.1f}%) {bar}")

        return total_counts, imbalance_ratio

    def _print_imbalance_recommendations(self, imbalance_ratio: float):
        """Print recommendations based on imbalance severity"""

        print(f"\n[TARGET] Estrategia de balanceo recomendada:")

        if imbalance_ratio > 30:
            print("  [WARN]  DESBALANCE EXTREMO (>30x)")
            print("  → Estrategia AGRESIVA:")
            print("     1. Copy-paste augmentation exclusivo para clases minoritarias")
            print("     2. Oversampling 10x-20x de clases minoritarias")
            print("     3. Class weights: inversamente proporcional a frecuencia")
            print("     4. Focal Loss (γ=2.0) para reducir peso de clases fáciles")
            print("     5. CRÍTICO: Recolectar más datos de clases ausentes/minoritarias")

        elif imbalance_ratio > 10:
            print("  [WARN]  DESBALANCE CRÍTICO (10-30x)")
            print("  → Estrategia MODERADA-ALTA:")
            print("     1. Copy-paste para clases con <5% de ejemplos")
            print("     2. Oversampling 5x-10x de clases minoritarias")
            print("     3. Class weights con factor 0.5-2.0")
            print("     4. Augmentation intenso solo en minoritarias")

        elif imbalance_ratio > 3:
            print("  [WARN]  DESBALANCE MODERADO (3-10x)")
            print("  → Estrategia BALANCEADA:")
            print("     1. Copy-paste selectivo para clases <10%")
            print("     2. Oversampling 2x-3x de clases minoritarias")
            print("     3. Class weights suaves")

        else:
            print("  [OK] DESBALANCE ACEPTABLE (<3x)")
            print("  → Estrategia ESTÁNDAR:")
            print("     1. Augmentation uniforme")
            print("     2. Sin oversampling necesario")

    def generate_kfold_splits(self, n_folds: int = 5, seed: int = 42) -> List[Dict]:
        """
        Generate stratified k-fold splits

        Strategy:
        - Stratify by primary class (first class in each image)
        - Ensure each fold has similar class distribution

        Args:
            n_folds: Number of folds
            seed: Random seed for reproducibility

        Returns:
            List of fold configurations, each with train/val image lists
        """
        print(f"\n{'='*70}")
        print(f"GENERANDO {n_folds}-FOLD CROSS-VALIDATION SPLITS")
        print(f"{'='*70}")

        if not self.image_annotations:
            print("[WARN]  No hay imágenes para dividir (ejecutar analyze_split('train') primero)")
            return []

        # Set seed for reproducibility
        random.seed(seed)
        np.random.seed(seed)

        # Group images by primary class (first class in annotation)
        class_to_images = defaultdict(list)
        for img_path, class_ids in self.image_annotations:
            if class_ids:
                primary_class = class_ids[0]  # Use first class as primary
                class_to_images[primary_class].append((img_path, class_ids))

        # Shuffle images within each class
        for class_id in class_to_images:
            random.shuffle(class_to_images[class_id])

        # Create folds with stratification
        folds = [{'train': [], 'val': []} for _ in range(n_folds)]

        for class_id, images in class_to_images.items():
            n_images = len(images)
            fold_size = n_images // n_folds

            for fold_idx in range(n_folds):
                # Validation images for this fold
                start_idx = fold_idx * fold_size
                end_idx = start_idx + fold_size if fold_idx < n_folds - 1 else n_images

                val_images = images[start_idx:end_idx]
                train_images = images[:start_idx] + images[end_idx:]

                folds[fold_idx]['val'].extend([img[0] for img in val_images])
                folds[fold_idx]['train'].extend([img[0] for img in train_images])

        # Print fold statistics
        print(f"\n[DIR] Estadísticas de los folds:")
        for fold_idx, fold in enumerate(folds):
            print(f"\n  Fold {fold_idx + 1}:")
            print(f"    Train: {len(fold['train'])} imágenes")
            print(f"    Val:   {len(fold['val'])} imágenes")

        return folds

    def recommend_augmentation_strategy(self, total_counts: Counter) -> Dict:
        """
        Recommend augmentation strategy based on class distribution

        Returns:
            Dictionary with augmentation recommendations per class
        """
        print(f"\n{'='*70}")
        print("ESTRATEGIA DE AUGMENTATION RECOMENDADA")
        print(f"{'='*70}")

        if not total_counts:
            return {}

        total_instances = sum(total_counts.values())
        max_count = max(total_counts.values())

        recommendations = {}

        for class_name, count in total_counts.items():
            percentage = (count / total_instances * 100) if total_instances > 0 else 0

            # Determine strategy based on representation
            if count == 0:
                strategy = "CRÍTICO: Recolectar datos"
                aug_level = "N/A"
                copy_paste = False
                oversampling = 0

            elif percentage < 5:
                strategy = "AGRESIVO"
                aug_level = "extreme"
                copy_paste = True
                oversampling = max(10, int(max_count / count))  # Oversample to match majority

            elif percentage < 15:
                strategy = "ALTO"
                aug_level = "high"
                copy_paste = True
                oversampling = max(3, int(max_count / (count * 2)))

            elif percentage < 30:
                strategy = "MODERADO"
                aug_level = "medium"
                copy_paste = False
                oversampling = 2

            else:
                strategy = "ESTÁNDAR"
                aug_level = "low"
                copy_paste = False
                oversampling = 1

            recommendations[class_name] = {
                'count': count,
                'percentage': percentage,
                'strategy': strategy,
                'aug_level': aug_level,
                'copy_paste': copy_paste,
                'oversampling_factor': oversampling
            }

            print(f"\n  {class_name}:")
            print(f"    Instancias: {count} ({percentage:.1f}%)")
            print(f"    Estrategia: {strategy}")
            print(f"    Nivel Aug: {aug_level}")
            print(f"    Copy-Paste: {'[OK]' if copy_paste else '[X]'}")
            print(f"    Oversampling: {oversampling}x")

        return recommendations

    def generate_report(self, output_file: str = 'analysis/dataset_analysis_report.json') -> Dict:
        """Generate comprehensive JSON report"""

        # Ensure output directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        # Calculate overall metrics
        total_counts, imbalance_ratio = self.calculate_class_imbalance()

        # Get augmentation recommendations
        aug_recommendations = self.recommend_augmentation_strategy(total_counts)

        # Generate k-fold splits
        kfold_splits = self.generate_kfold_splits(n_folds=5, seed=42)

        report = {
            'dataset_root': str(self.data_root),
            'class_names': self.class_names,
            'splits': {},
            'total_instances_by_class': dict(total_counts),
            'imbalance_ratio': imbalance_ratio,
            'augmentation_recommendations': aug_recommendations,
            'kfold_splits': [
                {
                    'fold_id': idx + 1,
                    'train_images': fold['train'],
                    'val_images': fold['val'],
                    'train_count': len(fold['train']),
                    'val_count': len(fold['val'])
                }
                for idx, fold in enumerate(kfold_splits)
            ],
            'recommendations': []
        }

        # Add split information
        for split in ['train', 'val', 'test']:
            images_dir = self.data_root / 'images' / split
            images = list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.png'))

            report['splits'][split] = {
                'total_images': len(images),
                'class_distribution': dict(self.stats[split])
            }

        # Generate recommendations
        if imbalance_ratio > 10:
            report['recommendations'].append({
                'priority': 'CRITICAL',
                'type': 'class_imbalance',
                'description': f'Desbalance crítico ({imbalance_ratio:.1f}x). Usar copy-paste y oversampling para clases minoritarias.'
            })

        train_size = report['splits']['train']['total_images']
        if train_size < 200:
            report['recommendations'].append({
                'priority': 'HIGH',
                'type': 'dataset_size',
                'description': f'Dataset pequeño ({train_size} imágenes). Aplicar data augmentation intensivo y considerar k-fold CV.'
            })

        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n[SAVE] Reporte guardado en: {output_file}")
        return report

    def plot_distribution(self, output_file: str = 'analysis/class_distribution.png'):
        """Generate visualization of class distribution"""

        if not MATPLOTLIB_AVAILABLE:
            print("[WARN]  matplotlib no disponible - saltando generación de gráfico")
            return

        # Ensure output directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        try:
            fig, axes = plt.subplots(1, 3, figsize=(18, 5))
            fig.suptitle('Distribución de Clases por Split', fontsize=16, fontweight='bold')

            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']

            for idx, split in enumerate(['train', 'val', 'test']):
                if self.stats[split]:
                    # Sort by class ID (0, 1, 2, 3)
                    class_order = sorted(self.stats[split].keys(),
                                        key=lambda x: [k for k, v in self.class_names.items() if v == x][0])
                    counts = [self.stats[split][cls] for cls in class_order]

                    bars = axes[idx].bar(range(len(class_order)), counts, color=colors[:len(class_order)])
                    axes[idx].set_title(f'{split.upper()} Set ({sum(counts)} instancias)',
                                       fontweight='bold')
                    axes[idx].set_xlabel('Clase', fontweight='bold')
                    axes[idx].set_ylabel('Cantidad de Instancias', fontweight='bold')
                    axes[idx].set_xticks(range(len(class_order)))
                    axes[idx].set_xticklabels([c[:20] for c in class_order], rotation=45, ha='right')
                    axes[idx].grid(axis='y', alpha=0.3, linestyle='--')

                    # Add value labels on bars
                    for bar in bars:
                        height = bar.get_height()
                        if height > 0:
                            axes[idx].text(bar.get_x() + bar.get_width()/2., height,
                                         f'{int(height)}',
                                         ha='center', va='bottom', fontweight='bold')

            plt.tight_layout()
            plt.savefig(output_file, dpi=150, bbox_inches='tight')
            print(f"[STATS] Gráfico guardado en: {output_file}")
            plt.close()

        except Exception as e:
            print(f"[WARN]  Error generando gráfico: {e}")


def main():
    """Main analysis function"""

    parser = argparse.ArgumentParser(
        description='Análisis avanzado de dataset para YOLOv11'
    )
    parser.add_argument('--data_root', type=str, default='./data',
                       help='Directorio raíz del dataset')
    parser.add_argument('--output_json', type=str, default='analysis/dataset_analysis_report.json',
                       help='Archivo de salida JSON')
    parser.add_argument('--output_plot', type=str, default='analysis/class_distribution.png',
                       help='Archivo de salida PNG')
    parser.add_argument('--n_folds', type=int, default=5,
                       help='Número de folds para cross-validation')
    parser.add_argument('--seed', type=int, default=42,
                       help='Semilla aleatoria para reproducibilidad')

    args = parser.parse_args()

    print("="*70)
    print("ANÁLISIS AVANZADO DE DATASET - YOLO Breeding Sites Detection")
    print("="*70)

    # Initialize analyzer
    analyzer = AdvancedDatasetAnalyzer(args.data_root)

    # Analyze each split
    for split in ['train', 'val', 'test']:
        analyzer.analyze_split(split)

    # Calculate overall imbalance
    analyzer.calculate_class_imbalance()

    # Generate report with k-fold splits and recommendations
    report = analyzer.generate_report(args.output_json)

    # Generate visualization
    analyzer.plot_distribution(args.output_plot)

    # Print summary
    print(f"\n{'='*70}")
    print("RESUMEN Y PRÓXIMOS PASOS")
    print(f"{'='*70}")
    print("\n[OK] Análisis completado")
    print(f"\n[LIST] Archivos generados:")
    print(f"  • {args.output_json} - Reporte completo con k-fold splits")
    print(f"  • {args.output_plot} - Visualización de distribución")
    print(f"\n[TARGET] Usar este análisis para:")
    print(f"  → Configurar train_optimized.py con augmentations apropiadas")
    print(f"  → Entrenar con k-fold cross-validation para dataset pequeño")
    print(f"  → Aplicar oversampling/copy-paste a clases minoritarias")


if __name__ == '__main__':
    main()
