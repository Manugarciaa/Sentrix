from ultralytics import YOLO
import cv2
import os
import json
from datetime import datetime

from configs.classes import DENGUE_CLASSES, HIGH_RISK_CLASSES, MEDIUM_RISK_CLASSES

def train_dengue_model(model_path='models/yolo11n.pt', data_config='configs/dataset.yaml', epochs=100):
    """Train YOLOv11 model for dengue breeding site detection"""
    model = YOLO(model_path)
    results = model.train(
        data=data_config, 
        epochs=epochs, 
        imgsz=640,
        project='models',
        name='dengue_detection'
    )
    return results

def validate_dengue_model(model_path='models/dengue_detection/weights/best.pt', data_config='configs/dataset.yaml'):
    """Validate dengue detection model"""
    model = YOLO(model_path)
    results = model.val(data=data_config, project='results', name='validation')
    return results

def detect_breeding_sites(model_path='models/dengue_detection/weights/best.pt', source='data/images/test.jpg', 
                         conf_threshold=0.5, save_results=True):
    """Detect dengue breeding sites in image/video"""
    model = YOLO(model_path)
    results = model(source, conf=conf_threshold, save=save_results, project='results', name='detections')
    
    # Process detections
    detections = []
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = DENGUE_CLASSES.get(class_id, "unknown")
            
            detections.append({
                'class': class_name,
                'confidence': confidence,
                'bbox': box.xyxy[0].tolist(),
                'timestamp': datetime.now().isoformat()
            })
    
    # Save detection report
    if save_results and detections:
        save_detection_report(detections, source)
    
    return results, detections

def save_detection_report(detections, source_path):
    """Save detection results to JSON report"""
    os.makedirs('results/reports', exist_ok=True)
    
    report = {
        'source': source_path,
        'total_detections': len(detections),
        'timestamp': datetime.now().isoformat(),
        'detections': detections,
        'risk_assessment': assess_dengue_risk(detections)
    }
    
    filename = f"results/reports/detection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Detection report saved: {filename}")

def assess_dengue_risk(detections):
    """Assess dengue risk based on detections"""
    high_risk_classes = ['charco_agua', 'recipiente_agua', 'neumatico', 'desague']
    medium_risk_classes = ['basural', 'contenedor_basura', 'botellas']
    
    high_risk_count = sum(1 for d in detections if d['class'] in high_risk_classes)
    medium_risk_count = sum(1 for d in detections if d['class'] in medium_risk_classes)
    
    if high_risk_count >= 3:
        risk_level = "ALTO"
    elif high_risk_count >= 1 or medium_risk_count >= 3:
        risk_level = "MEDIO"
    elif medium_risk_count >= 1:
        risk_level = "BAJO"
    else:
        risk_level = "MÍNIMO"
    
    return {
        'level': risk_level,
        'high_risk_sites': high_risk_count,
        'medium_risk_sites': medium_risk_count,
        'recommendations': get_risk_recommendations(risk_level)
    }

def get_risk_recommendations(risk_level):
    """Get recommendations based on risk level"""
    recommendations = {
        'ALTO': [
            "Intervención inmediata requerida",
            "Eliminar agua estancada inmediatamente",
            "Limpiar basurales y desagües",
            "Inspección frecuente del área"
        ],
        'MEDIO': [
            "Monitoreo regular necesario",
            "Limpiar recipientes con agua",
            "Mantener área libre de basura",
            "Revisar drenajes"
        ],
        'BAJO': [
            "Mantenimiento preventivo",
            "Limpieza regular del área",
            "Monitoreo periódico"
        ],
        'MÍNIMO': [
            "Continuar con vigilancia rutinaria"
        ]
    }
    return recommendations.get(risk_level, [])

if __name__ == "__main__":
    print("Sistema de Detección de Focos de Dengue - YOLOv11")
    print("=" * 50)
    print("Funciones disponibles:")
    print("- train_dengue_model(): Entrenar modelo para detección de focos")
    print("- validate_dengue_model(): Validar modelo entrenado")
    print("- detect_breeding_sites(): Detectar focos de reproducción del dengue")
    print("- assess_dengue_risk(): Evaluar nivel de riesgo")