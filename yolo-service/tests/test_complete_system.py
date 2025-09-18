"""
Tests exhaustivos para verificar que todo el sistema funciona correctamente
Especialmente paths portables y resolución de modelos
"""

import os
import sys
import tempfile
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    get_project_root, get_models_dir, get_configs_dir, get_data_dir,
    resolve_path, resolve_model_path, ensure_project_directories,
    get_default_dataset_config, get_default_model_paths,
    find_all_yolo_seg_models, detect_device
)
from src.core import train_dengue_model, detect_breeding_sites, assess_dengue_risk
from src.reports import generate_report, save_report


def test_paths_portables():
    """Test que los paths se resuelven correctamente"""
    print("=== TEST PATHS PORTABLES ===")

    # Test 1: Directorio raíz del proyecto
    project_root = get_project_root()
    print(f"✓ Proyecto raíz: {project_root}")
    assert project_root.exists(), "El directorio raíz debe existir"
    assert (project_root / "main.py").exists(), "main.py debe existir en la raíz"

    # Test 2: Directorios principales
    dirs = {
        'models': get_models_dir(),
        'configs': get_configs_dir(),
        'data': get_data_dir()
    }

    for name, directory in dirs.items():
        print(f"✓ Directorio {name}: {directory}")
        assert str(project_root) in str(directory), f"Directorio {name} debe estar dentro del proyecto"

    # Test 3: Asegurar directorios
    created_dirs = ensure_project_directories()
    print(f"✓ Directorios asegurados: {len(created_dirs)}")
    for d in created_dirs:
        assert d.exists(), f"Directorio {d} debe existir después de ensure_project_directories"

    print("✅ PATHS PORTABLES: TODOS LOS TESTS PASARON\n")


def test_model_resolution():
    """Test que la resolución de modelos funciona correctamente"""
    print("=== TEST RESOLUCIÓN DE MODELOS ===")

    # Test 1: Modelos disponibles
    available_models = find_all_yolo_seg_models()
    print(f"✓ Modelos encontrados: {len(available_models)}")
    for model in available_models:
        print(f"  - {model}")
        assert Path(model).exists(), f"Modelo {model} debe existir"

    # Test 2: Resolución de paths de modelos
    test_models = ['yolo11n-seg.pt', 'yolo11s-seg.pt', 'yolo11m-seg.pt']
    models_dir = get_models_dir()

    for model_name in test_models:
        model_path = models_dir / model_name
        if model_path.exists():
            resolved = resolve_model_path(model_name)
            print(f"✓ {model_name} -> {resolved}")
            assert Path(resolved).exists(), f"Modelo resuelto {resolved} debe existir"
            assert str(models_dir) in str(resolved), f"Debe resolver a directorio models/"
        else:
            print(f"⚠️  {model_name} no existe, omitiendo test")

    # Test 3: Paths de modelos por defecto
    default_paths = get_default_model_paths()
    print(f"✓ Paths por defecto: {len(default_paths)}")
    existing_defaults = [p for p in default_paths if p.exists()]
    print(f"✓ Modelos por defecto existentes: {len(existing_defaults)}")

    print("✅ RESOLUCIÓN DE MODELOS: TODOS LOS TESTS PASARON\n")


def test_dataset_config():
    """Test configuración del dataset"""
    print("=== TEST CONFIGURACIÓN DATASET ===")

    # Test 1: Configuración por defecto
    default_config = get_default_dataset_config()
    print(f"✓ Config por defecto: {default_config}")
    assert default_config.exists(), "Configuración del dataset debe existir"

    # Test 2: Resolución de path relativo
    resolved_config = resolve_path("configs/dataset.yaml")
    print(f"✓ Config resuelta: {resolved_config}")
    assert resolved_config.exists(), "Config resuelta debe existir"
    assert str(default_config) == str(resolved_config), "Deben ser la misma config"

    print("✅ CONFIGURACIÓN DATASET: TODOS LOS TESTS PASARON\n")


def test_core_functions():
    """Test funciones principales del core"""
    print("=== TEST FUNCIONES CORE ===")

    # Test 1: Evaluación de riesgo
    detections_test = [
        {'class': 'Huecos', 'confidence': 0.9},
        {'class': 'Basura', 'confidence': 0.8}
    ]

    risk = assess_dengue_risk(detections_test)
    print(f"✓ Evaluación de riesgo: {risk['level']}")
    assert 'level' in risk, "Debe retornar nivel de riesgo"
    assert 'recommendations' in risk, "Debe retornar recomendaciones"

    # Test 2: Generación de reportes
    report = generate_report('test_image.jpg', detections_test)
    print(f"✓ Reporte generado: {report['total_detections']} detecciones")
    assert report['source'] == 'test_image.jpg', "Debe incluir fuente correcta"
    assert report['total_detections'] == 2, "Debe contar detecciones correctamente"

    # Test 3: Detección de dispositivo
    device = detect_device()
    print(f"✓ Dispositivo detectado: {device}")
    assert device in ['cuda', 'cpu'], "Debe detectar cuda o cpu"

    print("✅ FUNCIONES CORE: TODOS LOS TESTS PASARON\n")


def test_imports_structure():
    """Test que los imports de la nueva estructura funcionan"""
    print("=== TEST IMPORTS ESTRUCTURA MODULAR ===")

    # Test 1: Imports desde src.core
    try:
        from src.core import train_dengue_model, detect_breeding_sites, assess_dengue_risk
        print("✓ Imports src.core: OK")
    except ImportError as e:
        raise AssertionError(f"Error importando src.core: {e}")

    # Test 2: Imports desde src.utils
    try:
        from src.utils import get_models_dir, resolve_model_path, detect_device
        print("✓ Imports src.utils: OK")
    except ImportError as e:
        raise AssertionError(f"Error importando src.utils: {e}")

    # Test 3: Imports desde src.reports
    try:
        from src.reports import generate_report, save_report
        print("✓ Imports src.reports: OK")
    except ImportError as e:
        raise AssertionError(f"Error importando src.reports: {e}")

    print("✅ IMPORTS ESTRUCTURA: TODOS LOS TESTS PASARON\n")


def test_model_path_integration():
    """Test integración completa de paths de modelos"""
    print("=== TEST INTEGRACIÓN PATHS MODELOS ===")

    # Simular exactamente lo que hace train_dengue_model
    model_name = 'yolo11s-seg.pt'
    models_dir = get_models_dir()
    expected_path = models_dir / model_name

    if expected_path.exists():
        print(f"✓ Modelo existe: {expected_path}")

        # Test resolución
        resolved = resolve_model_path(model_name)
        print(f"✓ Path resuelto: {resolved}")

        # Verificar que es el mismo archivo
        assert str(resolved) == str(expected_path), "Debe resolver al archivo correcto"
        assert Path(resolved).exists(), "Archivo resuelto debe existir"

        # Verificar tamaño (debe ser > 1MB)
        size_mb = Path(resolved).stat().st_size / (1024 * 1024)
        print(f"✓ Tamaño del modelo: {size_mb:.1f} MB")
        assert size_mb > 1, "Modelo debe ser > 1MB"

        print("✅ INTEGRACIÓN PATHS: TODOS LOS TESTS PASARON\n")
    else:
        print(f"⚠️  Modelo {model_name} no existe, omitiendo test de integración")


def run_all_tests():
    """Ejecuta todos los tests exhaustivos"""
    print("🧪 INICIANDO TESTS EXHAUSTIVOS DEL SISTEMA\n")

    tests = [
        test_imports_structure,
        test_paths_portables,
        test_model_resolution,
        test_dataset_config,
        test_core_functions,
        test_model_path_integration
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ ERROR en {test_func.__name__}: {e}\n")

    print("=" * 50)
    print(f"RESUMEN: {passed}/{total} tests pasaron")

    if passed == total:
        print("🎉 TODOS LOS TESTS PASARON - SISTEMA LISTO")
        return True
    else:
        print("⚠️  ALGUNOS TESTS FALLARON - REVISAR SISTEMA")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)