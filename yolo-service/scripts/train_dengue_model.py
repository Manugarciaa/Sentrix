import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import train_dengue_model
from utils import print_section_header, find_all_yolo_seg_models, get_yolo_model_specs, get_model_info, get_system_info

def show_available_models():
    """Muestra modelos disponibles y permite seleccionar"""
    print_section_header("MODELOS YOLO-SEG DISPONIBLES")
    
    available_models = find_all_yolo_seg_models()
    
    if not available_models:
        print("No se encontraron modelos YOLO-seg en el proyecto")
        print("\nPuedes descargar modelos base desde:")
        print("https://github.com/ultralytics/assets/releases/")
        return None, None
    
    print(f"Se encontraron {len(available_models)} modelo(s):")
    print()
    
    specs = get_yolo_model_specs()
    
    for i, model_path in enumerate(available_models, 1):
        model_info = get_model_info(model_path)
        model_name = os.path.basename(model_path)
        
        # Detectar tamaño del modelo
        model_size = 'unknown'
        for size in specs.keys():
            if f'{size}-seg' in model_name.lower():
                model_size = size
                break
        
        print(f"{i}. {model_path}")
        print(f"   Tamaño archivo: {model_info['size_mb']:.1f} MB")
        
        if model_size in specs:
            spec = specs[model_size]
            print(f"   Tipo: {spec['name']} ({spec['speed']}, {spec['accuracy']} precisión)")
            print(f"   Parámetros: {spec['params']}")
            print(f"   Recomendado para: {spec['recommended_for']}")
        
        print()
    
    return available_models, specs

def select_model_interactive():
    """Permite seleccionar modelo interactivamente"""
    available_models, specs = show_available_models()
    
    if not available_models:
        return None
    
    print("Selecciona un modelo:")
    print("0. Automático (recomendado según tu GPU)")
    
    while True:
        try:
            choice = input(f"\nIngresa tu opción (0-{len(available_models)}): ").strip()
            
            if choice == '0':
                # Selección automática basada en GPU
                system_info = get_system_info()
                
                if system_info['cuda_available'] and system_info['device_count'] > 0:
                    gpu_memory = system_info['gpus'][0]['memory_gb']
                    
                    if gpu_memory >= 8:
                        # GPU potente: usar modelo medium o large si está disponible
                        for model in available_models:
                            if 'l-seg' in model or 'm-seg' in model:
                                print(f"\nSeleccionado automáticamente: {model} (GPU potente detectada)")
                                return model
                    elif gpu_memory >= 4:
                        # GPU media: usar small o medium
                        for model in available_models:
                            if 's-seg' in model or 'm-seg' in model:
                                print(f"\nSeleccionado automáticamente: {model} (GPU media detectada)")
                                return model
                
                # Fallback: usar el primero disponible (más pequeño)
                print(f"\nSeleccionado automáticamente: {available_models[0]} (opción segura)")
                return available_models[0]
                
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(available_models):
                selected_model = available_models[choice_idx]
                print(f"\nSeleccionado: {selected_model}")
                return selected_model
            else:
                print(f"Por favor ingresa un número entre 0 y {len(available_models)}")
                
        except ValueError:
            print("Por favor ingresa un número válido")
        except KeyboardInterrupt:
            print("\nCancelado por el usuario")
            return None

def main():
    parser = argparse.ArgumentParser(description='Entrenamiento especializado YOLOv11-seg para criaderos de dengue')
    parser.add_argument('--model', type=str, default=None,
                        help='Ruta específica del modelo o tamaño (n/s/m/l/x). Si no se especifica, se mostrará selector interactivo')
    parser.add_argument('--epochs', type=int, default=100,
                        help='Número de épocas de entrenamiento')
    parser.add_argument('--batch', type=int, default=1,
                        help='Tamaño del lote')
    parser.add_argument('--data', type=str, default='configs/dataset.yaml',
                        help='Archivo de configuración del dataset')
    parser.add_argument('--patience', type=int, default=50,
                        help='Paciencia para early stopping')
    parser.add_argument('--auto', action='store_true',
                        help='Selección automática del modelo según GPU')
    parser.add_argument('--name', type=str, default=None,
                        help='Nombre personalizado para el experimento')
    
    args = parser.parse_args()
    
    # Determinar modelo a usar
    if args.model:
        # Modelo especificado por usuario
        if args.model in ['n', 's', 'm', 'l', 'x']:
            # Tamaño especificado, buscar el archivo correspondiente
            possible_paths = [
                f'models/yolo11{args.model}-seg.pt',
                f'yolo11{args.model}-seg.pt'
            ]
            model_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    model_path = path
                    break
            
            if not model_path:
                print(f"ERROR: No se encontró modelo yolo11{args.model}-seg.pt")
                print(f"Buscar en: {', '.join(possible_paths)}")
                return
        else:
            # Ruta específica
            model_path = args.model
            if not os.path.exists(model_path):
                print(f"ERROR: Modelo no encontrado: {model_path}")
                return
    else:
        # Selección interactiva o automática
        if args.auto:
            print_section_header("SELECCIÓN AUTOMÁTICA DE MODELO")
            # Selección automática directa
            available_models = find_all_yolo_seg_models()
            
            if not available_models:
                print("ERROR: No se encontraron modelos YOLO-seg")
                return
            
            model_path = None
            system_info = get_system_info()
            
            if system_info['cuda_available'] and system_info['device_count'] > 0:
                gpu_memory = system_info['gpus'][0]['memory_gb']
                print(f"GPU detectada: {system_info['gpus'][0]['name']} ({gpu_memory:.1f}GB)")
                
                if gpu_memory >= 8:
                    # GPU potente: usar modelo large o medium
                    print("GPU potente detectada - buscando modelo Large/Medium...")
                    for model in available_models:
                        if 'l-seg' in model:
                            model_path = model
                            print(f"Seleccionado modelo Large: {model}")
                            break
                    if not model_path:
                        for model in available_models:
                            if 'm-seg' in model:
                                model_path = model
                                print(f"Seleccionado modelo Medium: {model}")
                                break
                elif gpu_memory >= 4:
                    # GPU media: usar small o medium
                    print("GPU media detectada - buscando modelo Small/Medium...")
                    for model in available_models:
                        if 's-seg' in model:
                            model_path = model
                            print(f"Seleccionado modelo Small: {model}")
                            break
                    if not model_path:
                        for model in available_models:
                            if 'm-seg' in model:
                                model_path = model
                                print(f"Seleccionado modelo Medium: {model}")
                                break
                else:
                    print("GPU básica detectada - usando modelo Nano...")
                    
            else:
                print("Sin GPU - usando modelo más pequeño (CPU)...")
            
            # Fallback: usar el primero disponible (más pequeño)
            if not model_path:
                model_path = available_models[0]
                print(f"Seleccionado modelo por defecto: {model_path}")
                
        else:
            # Selección interactiva
            model_path = select_model_interactive()
        
        if not model_path:
            print("No se seleccionó ningún modelo")
            return
    
    print_section_header("ENTRENAMIENTO YOLO DENGUE")
    print(f"Modelo: {model_path}")
    print(f"Epocas: {args.epochs}")
    print(f"Batch size: {args.batch}")
    print(f"Dataset: {args.data}")
    print(f"Patience: {args.patience}")
    print()
    
    try:
        results = train_dengue_model(
            model_path=model_path,
            data_config=args.data,
            epochs=args.epochs,
            experiment_name=args.name
        )
        print("Entrenamiento completado exitosamente")
        experiment_name = args.name
        if experiment_name is None:
            from datetime import datetime
            model_size = 'unknown'
            model_name = os.path.basename(model_path).lower()
            
            for size in ['n', 's', 'm', 'l', 'x']:
                if f'{size}-seg' in model_name:
                    model_size = size
                    break
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            experiment_name = f"dengue_seg_{model_size}_{args.epochs}ep_{timestamp}"
        
        print(f"Modelo guardado en: models/{experiment_name}/weights/best.pt")
        
    except Exception as e:
        print(f"Error durante el entrenamiento: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()