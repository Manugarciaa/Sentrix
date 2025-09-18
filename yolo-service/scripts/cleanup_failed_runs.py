#!/usr/bin/env python3
"""
Script para limpiar entrenamientos fallidos o incompletos
"""
import os
import shutil
import argparse
from datetime import datetime

def is_training_complete(run_dir):
    """Verifica si un entrenamiento se completó exitosamente"""
    weights_dir = os.path.join(run_dir, 'weights')

    if not os.path.exists(weights_dir):
        return False

    # Verificar que existan both best.pt y last.pt
    best_path = os.path.join(weights_dir, 'best.pt')
    last_path = os.path.join(weights_dir, 'last.pt')

    return os.path.exists(best_path) and os.path.exists(last_path)

def get_run_size(run_dir):
    """Obtiene el tamaño de una carpeta de entrenamiento en MB"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(run_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(file_path)
            except (OSError, IOError):
                pass
    return total_size / (1024 * 1024)  # Convert to MB

def cleanup_failed_runs(models_dir='models', dry_run=False):
    """Limpia entrenamientos fallidos"""
    print("LIMPIEZA DE ENTRENAMIENTOS FALLIDOS")
    print("=" * 50)

    if not os.path.exists(models_dir):
        print(f"ERROR: Directorio {models_dir} no existe")
        return

    # Buscar carpetas de entrenamiento
    training_dirs = []
    for item in os.listdir(models_dir):
        item_path = os.path.join(models_dir, item)
        if os.path.isdir(item_path) and item.startswith('dengue_seg_'):
            training_dirs.append(item)

    if not training_dirs:
        print("No se encontraron carpetas de entrenamiento")
        return

    print(f"Encontradas {len(training_dirs)} carpetas de entrenamiento\n")

    failed_runs = []
    completed_runs = []

    for run_dir in training_dirs:
        full_path = os.path.join(models_dir, run_dir)
        is_complete = is_training_complete(full_path)
        size_mb = get_run_size(full_path)

        status = "[COMPLETO]" if is_complete else "[FALLIDO]"
        print(f"{status} | {run_dir} | {size_mb:.1f} MB")

        if is_complete:
            completed_runs.append((run_dir, full_path, size_mb))
        else:
            failed_runs.append((run_dir, full_path, size_mb))

    print(f"\nRESUMEN:")
    print(f"   Entrenamientos completos: {len(completed_runs)}")
    print(f"   Entrenamientos fallidos: {len(failed_runs)}")

    if failed_runs:
        total_failed_size = sum(size for _, _, size in failed_runs)
        print(f"   Espacio a liberar: {total_failed_size:.1f} MB")

        if dry_run:
            print(f"\nMODO DRY-RUN - No se eliminaran archivos")
            print("Carpetas que se eliminarian:")
            for run_dir, _, size_mb in failed_runs:
                print(f"   - {run_dir} ({size_mb:.1f} MB)")
        else:
            print(f"\nELIMINANDO ENTRENAMIENTOS FALLIDOS...")
            for run_dir, full_path, size_mb in failed_runs:
                try:
                    shutil.rmtree(full_path)
                    print(f"   [OK] Eliminado: {run_dir} ({size_mb:.1f} MB)")
                except Exception as e:
                    print(f"   [ERROR] Error eliminando {run_dir}: {e}")

            print(f"\nLimpieza completada")
    else:
        print(f"\nNo hay entrenamientos fallidos que limpiar")

def main():
    parser = argparse.ArgumentParser(description='Limpia entrenamientos YOLO fallidos')
    parser.add_argument('--models-dir', default='models',
                       help='Directorio de modelos (default: models)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Solo mostrar qué se eliminaría sin eliminar')

    args = parser.parse_args()

    cleanup_failed_runs(args.models_dir, args.dry_run)

if __name__ == "__main__":
    main()