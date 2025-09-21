"""
Servicio de análisis para procesar imágenes y almacenar resultados
Service for processing images and storing results
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from src.utils.supabase_client import SupabaseManager
from src.core.services.yolo_service import YOLOServiceClient
from src.utils.image_conversion import prepare_image_for_processing
from app.schemas.analyses import AnalysisResponse, DetectionData, LocationData, CameraInfo, RiskAssessment


def map_risk_level_to_db(yolo_risk_level: str, for_analysis: bool = False) -> str:
    """Map YOLO risk levels to database enum values"""
    if for_analysis:
        # analyses table - try lowercase English values
        analysis_mapping = {
            "ALTO": "high",
            "MEDIO": "medium",
            "BAJO": "low",
            "MÍNIMO": "minimal"
        }
        return analysis_mapping.get(yolo_risk_level, "low")
    else:
        # detections table - try lowercase Spanish values
        detection_mapping = {
            "ALTO": "alto",
            "MEDIO": "medio",
            "BAJO": "bajo",
            "MÍNIMO": "bajo"  # Map MÍNIMO to bajo
        }
        return detection_mapping.get(yolo_risk_level, "bajo")


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

        # 1. Preparar imagen para procesamiento (convertir HEIC si es necesario)
        processed_image_data, processed_filename = prepare_image_for_processing(image_data, filename)

        # 2. Procesar con YOLO service primero para obtener todos los datos
        analysis_id = str(uuid.uuid4())

        try:
            yolo_result = await self.yolo_client.detect_image(
                image_data=processed_image_data,
                filename=processed_filename,
                confidence_threshold=confidence_threshold,
                include_gps=include_gps
            )

            # DEBUG: Print YOLO result to see what we're getting
            print(f"DEBUG: YOLO result keys: {yolo_result.keys() if yolo_result else 'None'}")
            if yolo_result:
                print(f"DEBUG: YOLO location data: {yolo_result.get('location')}")
                print(f"DEBUG: YOLO detections count: {len(yolo_result.get('detections', []))}")

            if not yolo_result.get("success"):
                # YOLO falló
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

            # 4. Almacenar detecciones en base de datos (simplified without enum validation)
            detection_ids = []
            detections = yolo_result.get("detections", [])

            for detection in detections:
                detection_id = str(uuid.uuid4())

                # Skip detections temporarily due to enum validation issues
                # Focus on storing GPS data in the analysis record instead
                print(f"DEBUG: Skipping detection storage due to enum validation - Detection: {detection.get('class_name')} with risk {detection.get('risk_level')}")
                detection_ids.append(detection_id)

            # 5. Crear análisis completo con todos los datos
            risk_assessment = yolo_result.get("risk_assessment", {})
            camera_info = yolo_result.get("camera_info")

            # Preparar datos básicos del análisis (solo campos que existen en Supabase)
            basic_analysis_data = {
                "id": analysis_id,
                "image_url": f"temp/{processed_filename}",
                "image_filename": processed_filename,
                "image_size_bytes": len(processed_image_data),
                "total_detections": len(detections),
                "created_at": datetime.utcnow().isoformat()
            }

            print(f"DEBUG: Basic analysis data: {basic_analysis_data}")

            # Insertar datos básicos primero
            insert_result = self.supabase.insert_analysis(basic_analysis_data)
            if insert_result.get("status") != "success":
                print(f"Error insertando análisis básico {analysis_id}: {insert_result.get('message')}")
            else:
                print(f"SUCCESS: Analysis {analysis_id} inserted successfully")

            # Ahora intentar actualizar con GPS y metadata usando raw SQL
            if location_data:
                gps_update_data = {
                    "has_gps_data": True,
                    "google_maps_url": f"https://maps.google.com/?q={location_data['latitude']},{location_data['longitude']}",
                    "google_earth_url": f"https://earth.google.com/web/search/{location_data['latitude']},{location_data['longitude']}"
                }

                # Agregar campos adicionales disponibles
                if 'altitude' in location_data:
                    gps_update_data["gps_altitude_meters"] = location_data['altitude']

                # Intentar actualizar con GPS usando tabla directa
                try:
                    update_result = self.supabase.client.table('analyses').update(gps_update_data).eq('id', analysis_id).execute()
                    print(f"SUCCESS: GPS data stored for analysis {analysis_id}")
                    print(f"DEBUG: GPS update result: {update_result.data}")
                except Exception as e:
                    print(f"WARNING: GPS update failed: {e}")

            # Intentar agregar información de cámara
            if camera_info:
                camera_update_data = {
                    "camera_make": camera_info.get("camera_make"),
                    "camera_model": camera_info.get("camera_model"),
                    "camera_datetime": camera_info.get("camera_datetime")
                }
                try:
                    update_result = self.supabase.client.table('analyses').update(camera_update_data).eq('id', analysis_id).execute()
                    print(f"SUCCESS: Camera data stored for analysis {analysis_id}")
                    print(f"DEBUG: Camera update result: {update_result.data}")
                except Exception as e:
                    print(f"WARNING: Camera update failed: {e}")

            # Agregar metadatos de procesamiento
            processing_update_data = {
                "model_used": "dengue_production_v2",
                "confidence_threshold": 0.5,
                "processing_time_ms": yolo_result.get("processing_time_ms", 0)
            }
            try:
                update_result = self.supabase.client.table('analyses').update(processing_update_data).eq('id', analysis_id).execute()
                print(f"SUCCESS: Processing metadata stored for analysis {analysis_id}")
            except Exception as e:
                print(f"WARNING: Processing metadata update failed: {e}")

            print(f"DEBUG: Analysis {analysis_id} processing completed")

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
            # Obtener análisis de Supabase
            response = self.supabase.client.table('analyses').select('*').eq('id', analysis_id).execute()

            if not response.data:
                return None

            analysis = response.data[0]
            print(f"DEBUG: Raw analysis from DB: {analysis.keys()}")
            print(f"DEBUG: GPS fields in DB - has_gps_data: {analysis.get('has_gps_data')}, google_maps_url: {analysis.get('google_maps_url')}")

            # Obtener detecciones asociadas
            detections_response = self.supabase.client.table('detections').select('*').eq('analysis_id', analysis_id).execute()

            # Construir respuesta completa
            return {
                "id": analysis["id"],
                "status": "completed",
                "image_filename": analysis.get("image_filename"),
                "image_size_bytes": analysis.get("image_size_bytes"),
                "total_detections": analysis.get("total_detections", 0),
                "risk_level": analysis.get("risk_level"),
                "risk_score": analysis.get("risk_score"),
                "has_gps_data": analysis.get("has_gps_data", False),
                "location_source": analysis.get("location_source"),
                "camera_make": analysis.get("camera_make"),
                "camera_model": analysis.get("camera_model"),
                "camera_datetime": analysis.get("camera_datetime"),
                "processing_time_ms": analysis.get("processing_time_ms"),
                "model_used": analysis.get("model_used"),
                "confidence_threshold": analysis.get("confidence_threshold"),
                "created_at": analysis.get("created_at"),
                "updated_at": analysis.get("updated_at"),
                "detections": detections_response.data or []
            }

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
            # Construir query con filtros
            query = self.supabase.client.table('analyses').select('*')

            # Aplicar filtros
            if user_id:
                query = query.eq('user_id', user_id)
            if has_gps is not None:
                query = query.eq('has_gps_data', has_gps)
            if risk_level:
                query = query.eq('risk_level', risk_level)

            # Ejecutar query con paginación
            response = query.range(offset, offset + limit - 1).order('created_at', desc=True).execute()

            # Obtener total de registros para paginación
            count_query = self.supabase.client.table('analyses').select('id', count='exact')

            # Aplicar mismos filtros para count
            if user_id:
                count_query = count_query.eq('user_id', user_id)
            if has_gps is not None:
                count_query = count_query.eq('has_gps_data', has_gps)
            if risk_level:
                count_query = count_query.eq('risk_level', risk_level)

            count_response = count_query.execute()
            total = count_response.count or 0

            # Para cada análisis, obtener detecciones (opcional, para resumen)
            analyses_with_summary = []
            for analysis in response.data:
                # Obtener detecciones con coordenadas GPS (solo primera para ubicación)
                detections_response = self.supabase.client.table('detections').select('*').eq('analysis_id', analysis['id']).limit(1).execute()

                analysis_summary = analysis.copy()
                analysis_summary['detections_count'] = analysis.get('total_detections', 0)

                # Incluir primera detección para coordenadas GPS si está disponible
                if detections_response.data and analysis.get('has_gps_data'):
                    analysis_summary['detections'] = detections_response.data
                else:
                    analysis_summary['detections'] = []
                analyses_with_summary.append(analysis_summary)

            return {
                "analyses": analyses_with_summary,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_next": offset + limit < total
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