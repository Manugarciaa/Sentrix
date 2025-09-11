import os
import json
from datetime import datetime
import torch
from ultralytics import YOLO
from configs.classes import DENGUE_CLASSES, HIGH_RISK_CLASSES, MEDIUM_RISK_CLASSES
from utils import detect_device, validate_file_exists, validate_model_file, ensure_directory, cleanup_unwanted_downloads

def train_dengue_model(model_path='yolo11n-seg.pt', 
                      data_config='configs/dataset.yaml', 
                      epochs=100,
                      experiment_name=None):
    """Entrena modelo YOLOv11-seg para detección de criaderos"""
    # Validar archivos usando funciones utilitarias
    if os.path.exists(model_path):
        validate_model_file(model_path)
    validate_file_exists(data_config, "Configuración de dataset")
    
    # Detectar dispositivo automáticamente
    device = detect_device()
    
    # Generar nombre del experimento
    if experiment_name is None:
        from datetime import datetime
        model_size = 'unknown'
        model_name = os.path.basename(model_path).lower()
        
        for size in ['n', 's', 'm', 'l', 'x']:
            if f'{size}-seg' in model_name:
                model_size = size
                break
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        experiment_name = f"dengue_seg_{model_size}_{epochs}ep_{timestamp}"
    
    try:
        print(f"Iniciando entrenamiento con {model_path}...")
        print(f"Experimento: {experiment_name}")
        # Evitar descargas innecesarias de YOLO
        os.environ['YOLO_VERBOSE'] = 'False'
        os.environ['YOLO_AUTODOWNLOAD'] = 'False'
        
        model = YOLO(model_path)
        results = model.train(
            data=data_config, 
            task='segment',
            epochs=epochs, 
            imgsz=640,
            batch=1,
            device=device,
            patience=50,
            project='models',
            name=experiment_name,
            lr0=0.001,
            weight_decay=0.001,
            mosaic=0.5,
            copy_paste=0.3,
            amp=False  # Deshabilitar AMP para evitar descargas
        )
        print("Entrenamiento completado exitosamente")
        # Limpiar descargas no deseadas inmediatamente
        cleanup_unwanted_downloads()
        return results
    except Exception as e:
        print(f"Error durante el entrenamiento: {e}")
        raise

def detect_breeding_sites(model_path, source, conf_threshold=0.5):
    """Detecta sitios de cría en imágenes usando modelo entrenado"""
    validate_model_file(model_path)
    validate_file_exists(source, "Imagen/directorio")
    
    try:
        os.environ['YOLO_VERBOSE'] = 'False'
        model = YOLO(model_path)
        results = model(source, conf=conf_threshold, task='segment')
        
        detections = []
        for result in results:
            if result.masks is not None:
                for i, mask in enumerate(result.masks):
                    class_id = int(result.boxes.cls[i])
                    polygon_coords = mask.xy[0].tolist()
                    detections.append({
                        'class': DENGUE_CLASSES.get(class_id, f"Clase_{class_id}"),
                        'class_id': class_id,
                        'confidence': float(result.boxes.conf[i]),
                        'polygon': polygon_coords,
                        'mask_area': float(mask.data.sum())
                    })
        return detections
    except Exception as e:
        print(f"Error durante la detección: {e}")
        raise
    finally:
        # Limpiar descargas no deseadas
        cleanup_unwanted_downloads()

def assess_dengue_risk(detections):
    """Evalúa riesgo epidemiológico basado en detecciones"""
    if not isinstance(detections, list):
        raise ValueError("Las detecciones deben ser una lista")
    
    high_risk_count = sum(1 for d in detections 
                         if d.get('class') in HIGH_RISK_CLASSES)
    medium_risk_count = sum(1 for d in detections 
                           if d.get('class') in MEDIUM_RISK_CLASSES)
    
    if high_risk_count >= 3:
        risk_level = "ALTO"
        recommendations = [
            "Intervención inmediata requerida",
            "Eliminar agua estancada inmediatamente"
        ]
    elif high_risk_count >= 1 or medium_risk_count >= 3:
        risk_level = "MEDIO"
        recommendations = [
            "Monitoreo regular necesario",
            "Limpiar recipientes y contenedores"
        ]
    elif medium_risk_count >= 1:
        risk_level = "BAJO"
        recommendations = [
            "Mantenimiento preventivo",
            "Limpieza regular del área"
        ]
    else:
        risk_level = "MÍNIMO"
        recommendations = ["Vigilancia rutinaria"]
    
    return {
        'level': risk_level,
        'high_risk_sites': high_risk_count,
        'medium_risk_sites': medium_risk_count,
        'recommendations': recommendations
    }

def generate_report(source, detections):
    """Genera reporte JSON con detecciones y evaluación de riesgo"""
    risk_assessment = assess_dengue_risk(detections)
    
    report = {
        'source': os.path.basename(source),
        'total_detections': len(detections),
        'timestamp': datetime.now().isoformat(),
        'detections': detections,
        'risk_assessment': risk_assessment
    }
    
    return report

def save_report(report, output_path='results/detection_report.json'):
    """Guarda reporte en archivo JSON"""
    ensure_directory(os.path.dirname(output_path))
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # Ejemplo de uso
    print("Sistema de Detección de Criaderos de Dengue - YOLOv11")
    
    # Entrenar modelo
    # train_results = train_dengue_model()
    
    # Detectar en imagen
    # detections = detect_breeding_sites('models/best.pt', 'path/to/image.jpg')
    # report = generate_report('path/to/image.jpg', detections)
    # save_report(report)
    # print(f"Detecciones: {len(detections)}")
    # print(f"Riesgo: {report['risk_assessment']['level']}")