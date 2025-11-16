"""
Advanced Model Evaluation Script for YOLO Breeding Sites Detection
Script de Evaluación Avanzada del Modelo

Author: ML Engineering Team
Date: 2025-10-09
Python: 3.10+

Features:
- Detailed per-class metrics
- K-fold results aggregation
- Automatic recommendations for data collection
- JSON export for tracking
- Statistical analysis (mean, std, confidence intervals)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

import numpy as np
from ultralytics import YOLO


class AdvancedModelEvaluator:
    """
    Comprehensive model evaluation with statistical analysis
    """

    def __init__(self, model_path: str, data_config: Optional[str] = None):
        self.model_path = Path(model_path)
        self.data_config = data_config

        if not self.model_path.exists():
            print(f"ERROR: Modelo no encontrado: {model_path}")
            sys.exit(1)

        self.model = YOLO(str(model_path))

        self.class_names = {
            0: "Basura",
            1: "Calles mal hechas",
            2: "Charcos/Cumulos de agua",
            3: "Huecos"
        }

    def evaluate(
        self,
        split: str = 'test',
        save_results: Optional[str] = None,
        conf_threshold: float = 0.25
    ) -> Dict:
        """
        Evaluate model on specified split

        Args:
            split: Dataset split to evaluate (train/val/test)
            save_results: Path to save results JSON
            conf_threshold: Confidence threshold for detections

        Returns:
            Dictionary with evaluation metrics
        """
        print("="*70)
        print(f"EVALUACION FINAL - {split.upper()} SET")
        print("="*70)

        print(f"\nModelo: {self.model_path}")
        print(f"Dataset config: {self.data_config or 'default'}")
        print(f"Split: {split}")
        print(f"Confidence threshold: {conf_threshold}")

        # Run validation
        print(f"\nEjecutando evaluacion...")

        try:
            results = self.model.val(
                data=self.data_config,
                split=split,
                batch=1,
                imgsz=640,
                conf=conf_threshold,
                iou=0.6,
                save_json=True,
                plots=True,
                verbose=True
            )

            # Extract and analyze metrics
            metrics = self._extract_metrics(results)

            # Print results
            self._print_results(metrics)

            # Provide recommendations
            self._provide_recommendations(metrics)

            # Save results if requested
            if save_results:
                self._save_results(metrics, save_results)

            return metrics

        except Exception as e:
            print(f"\nERROR durante evaluacion: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def evaluate_kfold_results(
        self,
        kfold_results_path: str,
        save_summary: Optional[str] = None
    ) -> Dict:
        """
        Evaluate aggregated k-fold results

        Args:
            kfold_results_path: Path to k-fold results JSON
            save_summary: Path to save summary JSON

        Returns:
            Statistical summary of k-fold results
        """
        print("="*70)
        print("EVALUACION K-FOLD RESULTS")
        print("="*70)

        results_path = Path(kfold_results_path)
        if not results_path.exists():
            print(f"\nERROR: Archivo no encontrado: {kfold_results_path}")
            sys.exit(1)

        with open(results_path, 'r', encoding='utf-8') as f:
            kfold_data = json.load(f)

        # Extract metrics from each fold
        fold_metrics = []
        for fold_result in kfold_data.get('per_fold_results', []):
            if 'metrics' in fold_result:
                fold_metrics.append(fold_result['metrics'])

        if not fold_metrics:
            print("\nERROR: No hay metricas en los resultados k-fold")
            sys.exit(1)

        # Statistical analysis
        summary = self._analyze_kfold_statistics(fold_metrics)

        # Print summary
        self._print_kfold_summary(summary, kfold_data)

        # Save summary if requested
        if save_summary:
            output = {
                'experiment_name': kfold_data.get('experiment_name', 'unknown'),
                'timestamp': datetime.now().isoformat(),
                'n_folds': len(fold_metrics),
                'statistical_summary': summary,
                'source_file': str(results_path)
            }

            with open(save_summary, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)

            print(f"\nResumen guardado: {save_summary}")

        return summary

    def _extract_metrics(self, results) -> Dict:
        """Extract metrics from YOLO results object"""
        metrics = {
            'evaluation_date': datetime.now().isoformat(),
            'model_path': str(self.model_path),
            'overall': {},
            'per_class': {}
        }

        # Overall segmentation metrics
        if hasattr(results, 'seg'):
            seg = results.seg
            metrics['overall']['mask'] = {
                'mAP50-95': float(seg.map) if hasattr(seg, 'map') else 0.0,
                'mAP50': float(seg.map50) if hasattr(seg, 'map50') else 0.0,
                'mAP75': float(seg.map75) if hasattr(seg, 'map75') else 0.0,
                'precision': float(seg.mp) if hasattr(seg, 'mp') else 0.0,
                'recall': float(seg.mr) if hasattr(seg, 'mr') else 0.0,
            }

            # Per-class metrics (masks)
            if hasattr(seg, 'maps') and seg.maps is not None:
                for idx, map_val in enumerate(seg.maps):
                    if idx in self.class_names:
                        class_name = self.class_names[idx]
                        if class_name not in metrics['per_class']:
                            metrics['per_class'][class_name] = {}
                        metrics['per_class'][class_name]['mask_mAP50-95'] = float(map_val)

        # Overall box detection metrics
        if hasattr(results, 'box'):
            box = results.box
            metrics['overall']['box'] = {
                'mAP50-95': float(box.map) if hasattr(box, 'map') else 0.0,
                'mAP50': float(box.map50) if hasattr(box, 'map50') else 0.0,
                'mAP75': float(box.map75) if hasattr(box, 'map75') else 0.0,
                'precision': float(box.mp) if hasattr(box, 'mp') else 0.0,
                'recall': float(box.mr) if hasattr(box, 'mr') else 0.0,
            }

            # Per-class metrics (boxes)
            if hasattr(box, 'maps') and box.maps is not None:
                for idx, map_val in enumerate(box.maps):
                    if idx in self.class_names:
                        class_name = self.class_names[idx]
                        if class_name not in metrics['per_class']:
                            metrics['per_class'][class_name] = {}
                        metrics['per_class'][class_name]['box_mAP50-95'] = float(map_val)

        return metrics

    def _print_results(self, metrics: Dict):
        """Print formatted results"""
        print("\n" + "="*70)
        print("RESULTADOS DE EVALUACION")
        print("="*70)

        # Overall metrics
        if 'mask' in metrics['overall']:
            mask = metrics['overall']['mask']
            print("\nMetricas Globales (Segmentacion):")
            print(f"   mAP50-95: {mask['mAP50-95']:.4f}")
            print(f"   mAP50:    {mask['mAP50']:.4f}")
            print(f"   mAP75:    {mask['mAP75']:.4f}")
            print(f"   Precision: {mask['precision']:.4f}")
            print(f"   Recall:    {mask['recall']:.4f}")

        if 'box' in metrics['overall']:
            box = metrics['overall']['box']
            print("\nMetricas Globales (Bounding Boxes):")
            print(f"   mAP50-95: {box['mAP50-95']:.4f}")
            print(f"   mAP50:    {box['mAP50']:.4f}")

        # Per-class metrics
        if metrics['per_class']:
            print("\nMetricas por Clase:")
            for class_name in sorted(metrics['per_class'].keys()):
                class_metrics = metrics['per_class'][class_name]
                print(f"\n   {class_name}:")
                if 'mask_mAP50-95' in class_metrics:
                    print(f"      Mask mAP50-95: {class_metrics['mask_mAP50-95']:.4f}")
                if 'box_mAP50-95' in class_metrics:
                    print(f"      Box mAP50-95:  {class_metrics['box_mAP50-95']:.4f}")

    def _provide_recommendations(self, metrics: Dict):
        """Provide actionable recommendations based on results"""
        print("\n" + "="*70)
        print("RECOMENDACIONES")
        print("="*70)

        if 'mask' not in metrics['overall']:
            print("\nNo hay metricas de segmentacion disponibles")
            return

        mask = metrics['overall']['mask']
        map50_95 = mask['mAP50-95']
        precision = mask['precision']
        recall = mask['recall']

        # Overall assessment
        print(f"\nEvaluacion General:")
        if map50_95 >= 0.60:
            print("   [EXCELENTE] Modelo listo para produccion")
        elif map50_95 >= 0.45:
            print("   [BUENO] Modelo aceptable, puede mejorarse")
        elif map50_95 >= 0.30:
            print("   [REGULAR] Requiere mejoras significativas")
        else:
            print("   [INSUFICIENTE] Necesita reentrenamiento con mas datos")

        # Specific recommendations
        print(f"\nRecomendaciones Especificas:")

        if precision < 0.65:
            print("\n   [PRECISION BAJA] Muchos falsos positivos")
            print("   -> Aumentar confidence threshold en produccion (0.5 -> 0.6)")
            print("   -> Revisar data augmentation (puede estar generando ruido)")
            print("   -> Considerar focal loss para reducir falsos positivos")

        if recall < 0.60:
            print("\n   [RECALL BAJO] Muchos falsos negativos")
            print("   -> Recolectar mas ejemplos de clases dificiles")
            print("   -> Aumentar data augmentation")
            print("   -> Reducir confidence threshold (si precision lo permite)")

        # Per-class recommendations
        if metrics['per_class']:
            weak_classes = []
            for class_name, class_metrics in metrics['per_class'].items():
                map_val = class_metrics.get('mask_mAP50-95', 0)
                if map_val < 0.30:
                    weak_classes.append((class_name, map_val))

            if weak_classes:
                print(f"\n   [CLASES DEBILES] Bajo rendimiento detectado:")
                for class_name, map_val in weak_classes:
                    print(f"      {class_name}: mAP={map_val:.4f}")
                print("   -> CRITICO: Recolectar 30-50+ imagenes de estas clases")
                print("   -> Aplicar copy-paste augmentation exclusivamente a estas clases")
                print("   -> Considerar oversampling 10x-20x durante entrenamiento")

    def _analyze_kfold_statistics(self, fold_metrics: List[Dict]) -> Dict:
        """Analyze k-fold metrics statistically"""
        metric_names = ['mAP50-95', 'mAP50', 'mAP75', 'precision', 'recall']

        summary = {}

        for metric_name in metric_names:
            values = [m.get(metric_name, 0.0) for m in fold_metrics]

            # Calculate statistics
            mean = np.mean(values)
            std = np.std(values)
            sem = std / np.sqrt(len(values))  # Standard error of mean

            # 95% confidence interval
            ci_95 = 1.96 * sem

            summary[metric_name] = {
                'mean': float(mean),
                'std': float(std),
                'sem': float(sem),
                'ci_95_lower': float(mean - ci_95),
                'ci_95_upper': float(mean + ci_95),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'median': float(np.median(values)),
                'values': [float(v) for v in values]
            }

        return summary

    def _print_kfold_summary(self, summary: Dict, kfold_data: Dict):
        """Print k-fold statistical summary"""
        print(f"\nExperimento: {kfold_data.get('experiment_name', 'unknown')}")
        print(f"Numero de folds: {kfold_data.get('n_folds', 'unknown')}")

        print("\nEstadisticas Agregadas (K-Fold):")

        for metric_name, stats in summary.items():
            print(f"\n   {metric_name}:")
            print(f"      Media: {stats['mean']:.4f} (±{stats['std']:.4f})")
            print(f"      IC 95%: [{stats['ci_95_lower']:.4f}, {stats['ci_95_upper']:.4f}]")
            print(f"      Rango: [{stats['min']:.4f}, {stats['max']:.4f}]")
            print(f"      Mediana: {stats['median']:.4f}")

        # Assess stability (low std = more stable model)
        map_std = summary.get('mAP50-95', {}).get('std', 0)
        print("\nEstabilidad del Modelo:")
        if map_std < 0.05:
            print("   [EXCELENTE] Desviacion baja - modelo estable")
        elif map_std < 0.10:
            print("   [BUENO] Desviacion moderada - modelo razonablemente estable")
        else:
            print("   [PREOCUPANTE] Desviacion alta - modelo inestable")
            print("   -> Dataset puede ser demasiado pequeno o desbalanceado")
            print("   -> Considerar recolectar mas datos")

    def _save_results(self, metrics: Dict, output_path: str):
        """Save results to JSON file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

        print(f"\nResultados guardados: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Evaluacion avanzada de modelo YOLOv11 con analisis estadistico'
    )

    parser.add_argument('--model', type=str, required=True,
                       help='Ruta al modelo entrenado (.pt)')
    parser.add_argument('--data', type=str, default='configs/dataset.yaml',
                       help='Configuracion del dataset')
    parser.add_argument('--split', type=str, default='test',
                       choices=['train', 'val', 'test'],
                       help='Split a evaluar')
    parser.add_argument('--conf', type=float, default=0.25,
                       help='Confidence threshold')
    parser.add_argument('--save_results', type=str, default=None,
                       help='Archivo de salida para resultados JSON')

    # K-fold evaluation
    parser.add_argument('--kfold_results', type=str, default=None,
                       help='Evaluar resultados k-fold desde JSON')
    parser.add_argument('--save_kfold_summary', type=str, default=None,
                       help='Guardar resumen k-fold en JSON')

    args = parser.parse_args()

    print("="*70)
    print("EVALUACION AVANZADA - YOLO Breeding Sites Detection")
    print("="*70)

    if args.kfold_results:
        # Evaluate k-fold results
        evaluator = AdvancedModelEvaluator(args.model, args.data)
        summary = evaluator.evaluate_kfold_results(
            args.kfold_results,
            args.save_kfold_summary
        )

    else:
        # Standard single-model evaluation
        evaluator = AdvancedModelEvaluator(args.model, args.data)
        metrics = evaluator.evaluate(
            split=args.split,
            save_results=args.save_results,
            conf_threshold=args.conf
        )

    print("\n" + "="*70)
    print("EVALUACION COMPLETADA")
    print("="*70)


if __name__ == '__main__':
    main()
