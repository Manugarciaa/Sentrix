"""
Servicio de análisis para procesar imágenes y almacenar resultados
Service for processing images and storing results
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from src.utils.supabase_client import SupabaseManager
from src.core.services.yolo_service import YOLOServiceClient
from app.schemas.analyses import AnalysisResponse, DetectionData, LocationData, CameraInfo, RiskAssessment


class AnalysisService:
    """Servicio principal para análisis de imágenes"""

    def __init__(self):
        self.supabase = SupabaseManager()
        self.yolo_client = YOLOServiceClient()

    async def process_image_analysis(
        self,
        image_data: bytes,
        filename: str,
        confidence_threshold: float = 0.5,
        include_gps: bool = True,
        manual_latitude: Optional[float] = None,
        manual_longitude: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Procesar imagen completa: YOLO + almacenamiento en BD

        Args:
            image_data: Datos binarios de la imagen
            filename: Nombre del archivo
            confidence_threshold: Umbral de confianza
            include_gps: Extraer GPS automáticamente
            manual_latitude: Latitud manual (opcional)
            manual_longitude: Longitud manual (opcional)

        Returns:
            Dict con ID de análisis y estado
        """

        # 1. Crear registro inicial en base de datos
        analysis_id = str(uuid.uuid4())

        try:
            # Insertar análisis inicial (solo campos que existen en la tabla)
            analysis_data = {
                "id": analysis_id,
                "image_url": f"temp/{filename}",  # Campo requerido
                "image_filename": filename,
                "image_size_bytes": len(image_data),
                "confidence_threshold": confidence_threshold,
                "total_detections": 0,
                "created_at": datetime.utcnow().isoformat()
            }

            # Insertar análisis inicial en Supabase
            insert_result = self.supabase.insert_analysis(analysis_data)
            if insert_result.get("status") != "success":
                raise Exception(f"Error insertando análisis: {insert_result.get('message')}")

            # 2. Procesar con YOLO service
            yolo_result = await self.yolo_client.detect_image(
                image_data=image_data,
                filename=filename,
                confidence_threshold=confidence_threshold,
                include_gps=include_gps
            )

            if not yolo_result.get("success"):
                # YOLO falló - no actualizar base de datos pues no hay campo status
                error_message = "YOLO processing failed"
                return {
                    "analysis_id": analysis_id,
                    "status": "failed",
                    "error": error_message
                }

            # 3. Procesar coordenadas (manual vs automática)
            location_data = None
            yolo_location = yolo_result.get("location")

            if manual_latitude and manual_longitude:
                # Usar coordenadas manuales
                location_data = {
                    "has_location": True,
                    "latitude": manual_latitude,
                    "longitude": manual_longitude,
                    "location_source": "MANUAL"
                }
            elif yolo_location and yolo_location.get("has_location"):
                # Usar coordenadas del EXIF
                location_data = {
                    "has_location": True,
                    "latitude": yolo_location.get("latitude"),
                    "longitude": yolo_location.get("longitude"),
                    "altitude_meters": yolo_location.get("altitude_meters"),
                    "location_source": yolo_location.get("location_source", "EXIF_GPS")
                }

            # 4. Almacenar detecciones en base de datos
            detection_ids = []
            detections = yolo_result.get("detections", [])

            for detection in detections:
                detection_id = str(uuid.uuid4())

                detection_record = {
                    "id": detection_id,
                    "analysis_id": analysis_id,
                    "class_id": detection.get("class_id"),
                    "class_name": detection.get("class_name"),
                    "confidence": detection.get("confidence"),
                    "risk_level": detection.get("risk_level"),
                    "breeding_site_type": detection.get("breeding_site_type"),
                    "polygon": detection.get("polygon"),
                    "mask_area": detection.get("mask_area"),
                    "created_at": datetime.utcnow().isoformat()
                }

                # Agregar ubicación si existe
                if location_data:
                    detection_record.update({
                        "detection_latitude": location_data["latitude"],
                        "detection_longitude": location_data["longitude"]
                    })

                # Insertar detección en Supabase
                detection_insert = self.supabase.insert_detection(detection_record)
                if detection_insert.get("status") != "success":
                    print(f"Warning: Error insertando detección {detection_id}: {detection_insert.get('message')}")
                detection_ids.append(detection_id)

            # 5. Actualizar análisis con resultados finales
            risk_assessment = yolo_result.get("risk_assessment", {})
            final_analysis_data = {
                "total_detections": len(detections),
                "risk_level": risk_assessment.get("overall_risk", "LOW"),
                "risk_score": risk_assessment.get("risk_score", 0.0),
                "processing_time_ms": yolo_result.get("processing_time_ms"),
                "model_used": yolo_result.get("model_used"),
                "updated_at": datetime.utcnow().isoformat()
            }

            # Agregar información de ubicación
            if location_data:
                final_analysis_data.update({
                    "has_gps_data": True,
                    "location_source": location_data["location_source"]
                })
                # Crear punto geográfico (POINT) para PostGIS
                if location_data.get("latitude") and location_data.get("longitude"):
                    final_analysis_data["location"] = f"POINT({location_data['longitude']} {location_data['latitude']})"

            # Agregar información de cámara
            camera_info = yolo_result.get("camera_info")
            if camera_info:
                final_analysis_data.update({
                    "camera_make": camera_info.get("camera_make"),
                    "camera_model": camera_info.get("camera_model"),
                    "camera_datetime": camera_info.get("camera_datetime"),
                    "camera_software": camera_info.get("camera_software")
                })

            # Actualizar análisis en Supabase
            update_result = self.supabase.update_analysis(analysis_id, final_analysis_data)
            if update_result.get("status") != "success":
                print(f"Warning: Error actualizando análisis {analysis_id}: {update_result.get('message')}")

            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "total_detections": len(detections),
                "processing_time_ms": yolo_result.get("processing_time_ms"),
                "has_gps_data": location_data is not None,
                "camera_detected": camera_info.get("camera_make") if camera_info else None
            }

        except Exception as e:
            # Log del error sin actualizar base de datos (no hay campo status/error_message)
            print(f"Error procesando análisis {analysis_id}: {str(e)}")
            raise Exception(f"Error procesando análisis: {str(e)}")

    async def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener análisis completo por ID

        Args:
            analysis_id: ID del análisis

        Returns:
            Dict con datos completos del análisis o None
        """

        try:
            # TODO: Implementar consulta a Supabase
            # analysis = self.supabase.get_analysis_with_detections(analysis_id)
            # return analysis

            # Por ahora retornamos None (mock)
            return None

        except Exception as e:
            print(f"Error obteniendo análisis {analysis_id}: {e}")
            return None

    async def list_analyses(
        self,
        limit: int = 20,
        offset: int = 0,
        user_id: Optional[str] = None,
        has_gps: Optional[bool] = None,
        risk_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Listar análisis con filtros

        Args:
            limit: Número máximo de resultados
            offset: Desplazamiento para paginación
            user_id: Filtrar por usuario (opcional)
            has_gps: Filtrar por disponibilidad de GPS (opcional)
            risk_level: Filtrar por nivel de riesgo (opcional)

        Returns:
            Dict con lista de análisis y metadata de paginación
        """

        try:
            # TODO: Implementar consulta a Supabase con filtros
            # analyses = self.supabase.list_analyses(
            #     limit=limit,
            #     offset=offset,
            #     filters={
            #         "user_id": user_id,
            #         "has_gps": has_gps,
            #         "risk_level": risk_level
            #     }
            # )

            # Por ahora retornamos lista vacía
            return {
                "analyses": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "has_next": False
            }

        except Exception as e:
            print(f"Error listando análisis: {e}")
            return {
                "analyses": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "has_next": False
            }


# Instancia singleton
analysis_service = AnalysisService()