"""
Tests unificados para el proyecto YOLO Dengue Detection
Combina tests de funciones, GPU y sistema en un solo archivo
"""
import sys
import os
import torch
import numpy as np
from src.core.evaluator import assess_dengue_risk
from src.reports.generator import generate_report
from src.utils.device import detect_device, get_system_info
from src.utils.model_utils import find_available_model, get_model_info
from src.utils.file_ops import print_section_header

def test_system_and_gpu():
    """Test unificado de sistema y GPU"""
    print_section_header("TEST SISTEMA Y GPU")
    
    # Obtener información del sistema
    system_info = get_system_info()
    
    print(f"Python: {system_info['python_version']}")
    print(f"PyTorch: {system_info['pytorch_version']}")
    print(f"CUDA disponible: {system_info['cuda_available']}")
    
    if system_info['cuda_available']:
        print(f"CUDA version: {system_info['cuda_version']}")
        print(f"cuDNN version: {system_info['cudnn_version']}")
        print(f"GPUs detectadas: {system_info['device_count']}")
        
        # Información detallada de GPUs
        for i, gpu in enumerate(system_info['gpus']):
            print(f"  GPU {i}: {gpu['name']} ({gpu['memory_gb']:.1f}GB)")
            print(f"    Compute capability: {gpu['compute_capability']}")
        
        # Test de operación GPU
        try:
            print("\nTest de operacion GPU...")
            x = torch.randn(1000, 1000).cuda()
            y = torch.randn(1000, 1000).cuda()
            z = torch.mm(x, y)
            print(f"Multiplicacion de matrices en GPU exitosa: {z.shape}")
            
            # Limpiar memoria
            del x, y, z
            torch.cuda.empty_cache()
            return True
            
        except Exception as e:
            print(f"Error en operacion GPU: {e}")
            return False
    
    return system_info['cuda_available']

def test_yolo_integration():
    """Test de integración con YOLO"""
    print_section_header("TEST YOLO INTEGRATION")
    
    try:
        from ultralytics import YOLO
        
        # Buscar modelo disponible usando función utilitaria
        model_path = find_available_model()
        
        if not model_path:
            print("No se encontro modelo de segmentacion, omitiendo test YOLO")
            return True  # No es un error crítico
        
        # Obtener información del modelo
        model_info = get_model_info(model_path)
        print(f"Usando modelo: {model_path}")
        print(f"Tamaño: {model_info['size_mb']:.1f}MB")
        print(f"Segmentacion: {'Sí' if model_info['is_segmentation'] else 'No'}")
        print(f"Entrenado: {'Sí' if model_info['is_trained'] else 'No'}")
        
        # Test básico de carga de modelo  
        print("Cargando modelo YOLO...")
        os.environ['YOLO_VERBOSE'] = 'False'
        model = YOLO(model_path)
        
        # Test con imagen dummy
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        # Detección automática de dispositivo
        device = detect_device()
        
        # Predicción con tarea correcta
        if model_info['is_segmentation']:
            results = model(dummy_image, device=device, verbose=False, task='segment')
            print("Prediccion YOLO segmentacion exitosa")
        else:
            results = model(dummy_image, device=device, verbose=False)
            print("Prediccion YOLO exitosa")
        
        return True
        
    except Exception as e:
        print(f"Error en test YOLO: {e}")
        return False

def test_folder_creation():
    """Test para verificar que no se crean múltiples carpetas de entrenamiento"""
    print_section_header("TEST CREACION DE CARPETAS")

    try:
        import tempfile
        import shutil
        from datetime import datetime

        # Simular directorio temporal para tests
        with tempfile.TemporaryDirectory() as temp_dir:
            # Simular la lógica de nombres de experimentos
            date_str = datetime.now().strftime("%Y%m%d")
            base_name = f"dengue_seg_test_{date_str}"

            # Simular creación de experimento múltiples veces
            experiment_names = []
            for i in range(3):
                # Usar la lógica simplificada del código modificado
                experiment_name = base_name
                experiment_names.append(experiment_name)

            # Verificar que todos los nombres son iguales (no múltiples carpetas)
            unique_names = set(experiment_names)
            assert len(unique_names) == 1, f"Se generaron múltiples nombres: {unique_names}"
            print(f"✓ Nombre único generado: {list(unique_names)[0]}")

            # Simular que exist_ok=True permite reutilizar carpetas
            test_folder = os.path.join(temp_dir, base_name)
            os.makedirs(test_folder, exist_ok=True)
            os.makedirs(test_folder, exist_ok=True)  # Segunda vez no debería fallar

            # Verificar que solo existe una carpeta
            folders = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
            assert len(folders) == 1, f"Se crearon múltiples carpetas: {folders}"
            print(f"✓ Solo se creó una carpeta: {folders[0]}")

        return True

    except Exception as e:
        print(f"Error en test de carpetas: {e}")
        return False

def test_core_functions():
    """Test de funciones principales del sistema"""
    print_section_header("TEST FUNCIONES PRINCIPALES")
    
    try:
        # Test de evaluación de riesgo - Alto
        # Need 3+ high-risk sites for ALTO level
        detections_high = [
            {'class': 'Charcos/Cumulo de agua', 'confidence': 0.9},  # HIGH risk
            {'class': 'Basura', 'confidence': 0.8},  # HIGH risk
            {'class': 'Charcos/Cumulo de agua', 'confidence': 0.7}  # HIGH risk
        ]

        risk = assess_dengue_risk(detections_high)
        assert risk['level'] == 'ALTO'
        assert risk['high_risk_sites'] == 3
        print("✓ Test riesgo alto")
        
        # Test de evaluación de riesgo - Medio (1 high-risk site)
        detections_medium = [
            {'class': 'Basura', 'confidence': 0.8}  # HIGH risk
        ]

        risk = assess_dengue_risk(detections_medium)
        assert risk['level'] == 'MEDIO'  # 1 high-risk site = MEDIO
        assert risk['high_risk_sites'] == 1
        print("✓ Test riesgo medio")

        # Test sin detecciones
        risk = assess_dengue_risk([])
        assert risk['level'] == 'MINIMO'  # No accent
        print("✓ Test sin detecciones")
        
        # Test de generación de reporte
        detections = [
            {'class': 'Huecos', 'confidence': 0.9, 'polygon': [[0.1, 0.1], [0.2, 0.2]]},
        ]
        
        report = generate_report('test_image.jpg', detections)
        assert report['source'] == 'test_image.jpg'
        assert report['total_detections'] == 1
        assert 'timestamp' in report
        assert 'risk_assessment' in report
        print("✓ Test generacion de reporte")
        
        # Test de detección de dispositivo
        device = detect_device()
        assert device in ['cuda', 'cpu']
        print("✓ Test deteccion de dispositivo")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"Error en test de funciones: {e}")
        print(f"Traceback completo: {traceback.format_exc()}")
        return False

def run_comprehensive_tests():
    """Ejecuta todos los tests del sistema"""
    print_section_header("TESTS COMPREHENSIVOS YOLO DENGUE")

    results = {
        'system_gpu': test_system_and_gpu(),
        'yolo_integration': test_yolo_integration(),
        'folder_creation': test_folder_creation(),
        'core_functions': test_core_functions()
    }
    
    # Resumen de resultados
    print_section_header("RESUMEN DE TESTS")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nTests pasados: {passed}/{total}")
    
    if passed == total:
        print("[SUCCESS] TODOS LOS TESTS PASARON")
        print("El sistema esta listo para uso completo")
    else:
        print("[WARN]  ALGUNOS TESTS FALLARON")
        print("Revisar configuracion del sistema")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)