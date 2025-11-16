"""
Servicio de análisis para procesar imágenes y almacenar resultados
Service for processing images and storing results
"""

import uuid
import sys
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import httpx

from ..logging_config import get_logger
from ..exceptions import (
    ImageProcessingException,
    YOLOServiceException,
    YOLOTimeoutException,
    DatabaseException,
    GPSExtractionException
)

logger = get_logger(__name__)

# Try to import shared functionality
try:
    from sentrix_shared.file_utils import generate_standardized_filename, create_filename_variations
    from sentrix_shared.image_deduplication import (
        calculate_content_signature,
        check_image_duplicate,
        should_store_image,
        get_deduplication_manager
    )
    SHARED_AVAILABLE = True
    DEDUPLICATION_AVAILABLE = True
    # Only log in non-testing mode
    if not os.getenv('TESTING_MODE', 'false').lower() == 'true':
        logger.info("shared library loaded successfully")
except ImportError as e:
    # Only log warnings in non-testing mode
    if not os.getenv('TESTING_MODE', 'false').lower() == 'true':
        logger.info("using fallback implementation", error=str(e))
    SHARED_AVAILABLE = False
    DEDUPLICATION_AVAILABLE = False

    # Fallback minimal implementation
    def generate_standardized_filename(original_filename, **kwargs):
        timestamp = kwargs.get('analysis_timestamp', datetime.now(timezone.utc))
        unique_id = str(uuid.uuid4())[:8]
        ext = Path(original_filename).suffix or '.jpg'
        return f"SENTRIX_{timestamp.strftime('%Y%m%d_%H%M%S')}_FALLBACK_{unique_id}{ext}"

    def create_filename_variations(base_filename, **kwargs):
        standardized = generate_standardized_filename(base_filename, **kwargs)
        return {
            'original': base_filename,
            'standardized': standardized,
            'processed': standardized.replace('SENTRIX_', 'SENTRIX_PROC_'),
            'thumbnail': standardized.replace(Path(standardized).suffix, '_thumb.jpg'),
            'analysis_id': str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    # Fallback deduplication functions
    def calculate_content_signature(image_data):
        import hashlib
        return {
            'sha256': hashlib.sha256(image_data).hexdigest(),
            'size_bytes': len(image_data)
        }

    def check_image_duplicate(image_data, existing_analyses=None, **kwargs):
        return {
            'is_duplicate': False,
            'should_store_separately': True
        }

    def should_store_image(duplicate_result):
        return duplicate_result.get('should_store_separately', True)

    def get_deduplication_manager():
        class FallbackManager:
            def estimate_storage_savings(self, analyses):
                return {'deduplication_rate': 0, 'storage_saved_mb': 0}
        return FallbackManager()

# Handle backend imports gracefully
try:
    from ..utils.supabase_client import SupabaseManager
    from ..core.services.yolo_service import YOLOServiceClient
    from ..utils.image_conversion import prepare_image_for_processing
    from ..schemas.analyses import AnalysisResponse, DetectionResponse, LocationResponse, CameraInfoResponse, RiskAssessmentResponse
except ImportError:
    # Try absolute imports
    try:
        from utils.supabase_client import SupabaseManager
        from core.services.yolo_service import YOLOServiceClient
        from utils.image_conversion import prepare_image_for_processing
        from schemas.analyses import AnalysisResponse, DetectionResponse, LocationResponse, CameraInfoResponse, RiskAssessmentResponse
    except ImportError as e:
        # Only log warnings in non-testing mode
        if not os.getenv('TESTING_MODE', 'false').lower() == 'true':
            logger.info("using mock backend modules", error=str(e))
        # Create minimal mock classes for basic functionality
        class SupabaseManager:
            def __init__(self): pass
            def upload_image(self, *args, **kwargs):
                return {"status": "error", "message": "Supabase not available"}
            def upload_dual_images(self, *args, **kwargs):
                return {"status": "error", "message": "Supabase not available"}
            def insert_analysis(self, *args, **kwargs):
                return {"status": "error", "message": "Supabase not available"}

        class YOLOServiceClient:
            def __init__(self): pass
            async def detect_image(self, *args, **kwargs):
                return {"success": False, "error": "YOLO client not available"}

        def prepare_image_for_processing(image_data, filename):
            return image_data, filename

        # Mock schema classes
        AnalysisResponse = DetectionResponse = LocationResponse = CameraInfoResponse = RiskAssessmentResponse = dict


def map_risk_level_to_db(yolo_risk_level: str, for_analysis: bool = False) -> str:
    """Map YOLO risk levels to database enum values"""
    if for_analysis:
        # analyses table - lowercase English values
        analysis_mapping = {
            "ALTO": "high",
            "MEDIO": "medium",
            "BAJO": "low",
            "MÍNIMO": "minimal"
        }
        return analysis_mapping.get(yolo_risk_level, "low")
    else:
        # detections table - UPPERCASE Spanish values (detection_risk_enum)
        detection_mapping = {
            "ALTO": "ALTO",
            "MEDIO": "MEDIO",
            "BAJO": "BAJO",
            "MÍNIMO": "BAJO"
        }
        return detection_mapping.get(yolo_risk_level, "BAJO")


def map_class_name_to_breeding_site_type(class_name: str) -> str:
    """Map YOLO class names to BreedingSiteTypeEnum values"""
    # Exact values from BreedingSiteTypeEnum
    mapping = {
        "Basura": "Basura",
        "Calles mal hechas": "Calles mal hechas",
        "Charcos/Cumulo de agua": "Charcos/Cumulo de agua",
        "Huecos": "Huecos",
        # Variations and fallbacks
        "BASURA": "Basura",
        "basura": "Basura",
        "CALLES": "Calles mal hechas",
        "calles": "Calles mal hechas",
        "CHARCOS": "Charcos/Cumulo de agua",
        "charcos": "Charcos/Cumulo de agua",
        "HUECOS": "Huecos",
        "huecos": "Huecos",
    }
    return mapping.get(class_name, "Basura")  # Default to Basura if unknown


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
        manual_longitude: Optional[float] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Procesar imagen completa: YOLO + almacenamiento dual en BD + nomenclatura estandarizada

        Args:
            image_data: Datos binarios de la imagen
            filename: Nombre del archivo
            confidence_threshold: Umbral de confianza
            include_gps: Extraer GPS automáticamente
            manual_latitude: Latitud manual (opcional)
            manual_longitude: Longitud manual (opcional)
            user_id: ID del usuario que crea el análisis (requerido para RLS)

        Returns:
            Dict con ID de análisis, URLs de imágenes y estado
        """

        # 1. Preparar imagen para procesamiento (convertir HEIC si es necesario)
        processed_image_data, processed_filename = prepare_image_for_processing(image_data, filename)

        # 2. Calcular signature de contenido para deduplicación
        content_signature = calculate_content_signature(processed_image_data)
        logger.debug("content signature calculated",
                    sha256_prefix=content_signature['sha256'][:12],
                    size_bytes=content_signature['size_bytes'])

        # 3. Verificar duplicados antes de procesar
        if DEDUPLICATION_AVAILABLE:
            # Obtener análisis recientes para comparar
            existing_analyses = await self._get_recent_analyses_for_deduplication()

            duplicate_check = check_image_duplicate(
                image_data=processed_image_data,
                existing_analyses=existing_analyses,
                camera_info=None,  # Se obtendrá del YOLO
                gps_data=None      # Se obtendrá del YOLO
            )

            logger.debug("duplicate check completed", is_duplicate=duplicate_check['is_duplicate'])

            if duplicate_check['is_duplicate'] and not should_store_image(duplicate_check):
                # Es un duplicado, crear referencia en lugar de procesar
                return await self._handle_duplicate_image(
                    duplicate_check,
                    filename,
                    processed_filename,
                    content_signature
                )

        # 4. Procesar con YOLO service (solo si no es duplicado)
        analysis_id = str(uuid.uuid4())

        try:
            yolo_result = await self.yolo_client.detect_image(
                image_data=processed_image_data,
                filename=processed_filename,
                confidence_threshold=confidence_threshold,
                include_gps=include_gps
            )

            if not yolo_result.get("success"):
                return {
                    "analysis_id": analysis_id,
                    "status": "failed",
                    "error": "YOLO processing failed"
                }

            # 3. Extraer información de YOLO result
            detections = yolo_result.get("detections", [])
            yolo_location = yolo_result.get("location")
            camera_info = yolo_result.get("camera_info")

            # 4. Procesar coordenadas (manual vs automática)
            location_data = None
            gps_data = None

            logger.info(f"[GPS DEBUG BACKEND] yolo_location received: {yolo_location}")
            logger.info(f"[GPS DEBUG BACKEND] manual coords: lat={manual_latitude}, lng={manual_longitude}")

            if manual_latitude and manual_longitude:
                logger.info("[GPS DEBUG BACKEND] Using MANUAL coordinates")
                location_data = {
                    "has_location": True,
                    "latitude": manual_latitude,
                    "longitude": manual_longitude,
                    "location_source": "MANUAL"
                }
                gps_data = {"has_gps": True, "latitude": manual_latitude, "longitude": manual_longitude}
            elif yolo_location and yolo_location.get("has_location"):
                logger.info(f"[GPS DEBUG BACKEND] Using YOLO GPS: lat={yolo_location.get('latitude')}, lng={yolo_location.get('longitude')}")
                location_data = {
                    "has_location": True,
                    "latitude": yolo_location.get("latitude"),
                    "longitude": yolo_location.get("longitude"),
                    "altitude_meters": yolo_location.get("altitude_meters"),
                    "location_source": yolo_location.get("location_source", "EXIF_GPS")
                }
                gps_data = {"has_gps": True, "latitude": yolo_location.get("latitude"), "longitude": yolo_location.get("longitude")}
            else:
                logger.info("[GPS DEBUG BACKEND] NO GPS DATA AVAILABLE")

            logger.info(f"[GPS DEBUG BACKEND] Final location_data: {location_data}")

            # 5. Generar nombres de archivo estandarizados
            timestamp = datetime.now(timezone.utc)
            standardized_filename = generate_standardized_filename(
                original_filename=processed_filename,
                camera_info=camera_info,
                gps_data=gps_data,
                analysis_timestamp=timestamp
            )

            filename_variations = create_filename_variations(
                base_filename=processed_filename,
                camera_info=camera_info,
                gps_data=gps_data
            )

            logger.debug("generated standardized filename", filename=standardized_filename)

            # 6. Obtener imagen procesada de YOLO (si está disponible)
            processed_image_data_from_yolo = None
            processed_image_base64 = yolo_result.get("processed_image_base64")

            if processed_image_base64:
                # Decodificar imagen procesada desde base64
                try:
                    import base64
                    processed_image_data_from_yolo = base64.b64decode(processed_image_base64)
                    logger.info("processed_image_decoded", size=len(processed_image_data_from_yolo))
                except Exception as e:
                    logger.warning("failed_to_decode_processed_image", error=str(e))
                    processed_image_data_from_yolo = None

            # 7. Almacenar ambas imágenes en Supabase Storage
            image_upload_result = None
            logger.info(f"[UPLOAD DEBUG] Has processed image: {processed_image_data_from_yolo is not None}, Size: {len(processed_image_data_from_yolo) if processed_image_data_from_yolo else 0}")
            if processed_image_data_from_yolo:
                # Almacenamiento dual
                logger.info(f"[UPLOAD DEBUG] Calling upload_dual_images with base_filename: {standardized_filename}")
                image_upload_result = self.supabase.upload_dual_images(
                    original_data=processed_image_data,
                    processed_data=processed_image_data_from_yolo,
                    base_filename=standardized_filename
                )
                logger.info(f"[UPLOAD DEBUG] Upload result: {image_upload_result}")
            else:
                # Solo imagen original por ahora
                logger.info(f"[UPLOAD DEBUG] No processed image, uploading only original")
                image_upload_result = self.supabase.upload_image(
                    image_data=processed_image_data,
                    filename=f"original_{standardized_filename}"
                    # bucket_name usa el valor por defecto de settings
                )
                logger.info(f"[UPLOAD DEBUG] Upload result: {image_upload_result}")

            # 8. Preparar datos del análisis con URLs de imágenes
            if image_upload_result and image_upload_result["status"] == "success":
                if "original" in image_upload_result:
                    # Almacenamiento dual exitoso
                    image_url = image_upload_result["original"]["public_url"]
                    processed_image_url = image_upload_result["processed"]["public_url"]
                    image_filename = filename_variations["standardized"]
                    processed_image_filename = filename_variations["processed"]
                else:
                    # Solo imagen original
                    image_url = image_upload_result["public_url"]
                    processed_image_url = None
                    image_filename = filename_variations["standardized"]
                    processed_image_filename = None
            else:
                # Fallback temporal
                image_url = f"temp/{standardized_filename}"
                processed_image_url = None
                image_filename = standardized_filename
                processed_image_filename = None

            # 9. Crear registro de análisis en base de datos
            # Note: Don't include created_at/updated_at - Supabase handles these with server defaults
            basic_analysis_data = {
                "id": analysis_id,
                "user_id": user_id,  # Add user_id to allow RLS access
                "image_url": image_url,
                "image_filename": image_filename,
                "processed_image_url": processed_image_url,
                "processed_image_filename": processed_image_filename,
                "image_size_bytes": len(processed_image_data),
                "total_detections": len(detections),
                "risk_level": "BAJO",  # Default risk level, will be updated after detections
                "has_gps_data": False,  # Default, will be updated if GPS data provided
            }

            logger.debug("creating analysis with standardized naming",
                        analysis_id=analysis_id,
                        filename=image_filename)

            # Insertar análisis básico
            insert_result = self.supabase.insert_analysis(basic_analysis_data)
            if insert_result.get("status") != "success":
                logger.error(f"[GPS DEBUG] ERROR INSERTING ANALYSIS: {insert_result}")
                logger.error("error inserting analysis",
                           analysis_id=analysis_id,
                           message=insert_result.get('message'))
                # Clean up uploaded images if DB insert fails
                if image_upload_result and image_upload_result["status"] == "success":
                    if "original" in image_upload_result:
                        self.supabase.delete_image(image_upload_result["original"]["file_path"])
                        if "processed" in image_upload_result:
                            self.supabase.delete_image(image_upload_result["processed"]["file_path"])
                    else:
                        self.supabase.delete_image(image_upload_result["file_path"])

                return {
                    "analysis_id": analysis_id,
                    "status": "failed",
                    "error": "Database insertion failed"
                }

            # Ahora intentar actualizar con GPS y metadata usando raw SQL
            if location_data:
                lat = location_data['latitude']
                lng = location_data['longitude']

                gps_update_data = {
                    "has_gps_data": True,
                    "google_maps_url": f"https://maps.google.com/?q={lat},{lng}",
                    "google_earth_url": f"https://earth.google.com/web/search/{lat},{lng}"
                }

                # Agregar campos adicionales disponibles
                if 'altitude_meters' in location_data:
                    gps_update_data["gps_altitude_meters"] = location_data['altitude_meters']

                # Add location_source if available
                if 'location_source' in location_data:
                    gps_update_data["location_source"] = location_data['location_source']

                # Intentar actualizar con GPS usando tabla directa
                try:
                    # First update basic GPS fields
                    update_result = self.supabase.client.table('analyses').update(gps_update_data).eq('id', analysis_id).execute()
                    logger.info("gps metadata stored for analysis", analysis_id=analysis_id, lat=lat, lng=lng)

                    # Then update PostGIS location field using RPC
                    try:
                        # Use Supabase RPC to set the geography point
                        # PostGIS format: POINT(longitude latitude) - note the order!
                        from supabase import create_client

                        # Execute raw SQL to update location field
                        rpc_result = self.supabase.client.rpc(
                            'update_analysis_location',
                            {
                                'analysis_uuid': analysis_id,
                                'lat': lat,
                                'lng': lng
                            }
                        ).execute()
                        logger.info("postgis location updated", analysis_id=analysis_id)
                    except Exception as e:
                        # Fallback: try direct SQL update
                        logger.warning("rpc location update failed, trying direct SQL", error=str(e))
                        try:
                            # Direct PostGIS update using ST_SetSRID and ST_MakePoint
                            # Note: PostGIS uses (longitude, latitude) order
                            update_query = f"""
                                UPDATE analyses
                                SET location = ST_SetSRID(ST_MakePoint({lng}, {lat}), 4326)
                                WHERE id = '{analysis_id}'
                            """
                            # This won't work through Supabase client, so we'll skip for now
                            # The google_maps_url is enough for display
                            logger.info("location field skipped (requires RPC function)", analysis_id=analysis_id)
                        except Exception as e2:
                            logger.warning("direct sql location update failed", error=str(e2))

                    logger.debug("gps update result", data=update_result.data)
                except Exception as e:
                    logger.warning("gps update failed", analysis_id=analysis_id, error=str(e))

            # Intentar agregar información de cámara
            if camera_info:
                camera_update_data = {
                    "camera_make": camera_info.get("camera_make"),
                    "camera_model": camera_info.get("camera_model"),
                    "camera_datetime": camera_info.get("camera_datetime")
                }
                try:
                    update_result = self.supabase.client.table('analyses').update(camera_update_data).eq('id', analysis_id).execute()
                    logger.info("camera data stored for analysis", analysis_id=analysis_id)
                    logger.debug("camera update result", data=update_result.data)
                except Exception as e:
                    logger.warning("camera update failed", analysis_id=analysis_id, error=str(e))

            # Agregar metadatos de procesamiento
            processing_update_data = {
                "model_used": "dengue_production_v2",
                "confidence_threshold": confidence_threshold,
                "processing_time_ms": yolo_result.get("processing_time_ms", 0)
            }
            try:
                update_result = self.supabase.client.table('analyses').update(processing_update_data).eq('id', analysis_id).execute()
                logger.info("processing metadata stored for analysis", analysis_id=analysis_id)
            except Exception as e:
                logger.warning("processing metadata update failed", analysis_id=analysis_id, error=str(e))

            # Insertar detecciones en la base de datos
            if detections and len(detections) > 0:
                logger.info("inserting detections", count=len(detections), analysis_id=analysis_id)

                # Calculate overall risk level from detections
                highest_risk = "BAJO"
                risk_priority = {"ALTO": 3, "MEDIO": 2, "BAJO": 1, "MÍNIMO": 0}

                for detection in detections:
                    detection_risk = detection.get("risk_level", "BAJO")
                    if risk_priority.get(detection_risk, 0) > risk_priority.get(highest_risk, 0):
                        highest_risk = detection_risk

                for idx, detection in enumerate(detections):
                    try:
                        class_name = detection.get("class_name", "Basura")

                        detection_data = {
                            "id": str(uuid.uuid4()),
                            "analysis_id": analysis_id,
                            "class_name": class_name,
                            "breeding_site_type": map_class_name_to_breeding_site_type(class_name),
                            "confidence": float(detection.get("confidence", 0.0)),
                            "risk_level": map_risk_level_to_db(detection.get("risk_level", "BAJO"), for_analysis=False),
                            "created_at": timestamp.isoformat()
                        }

                        insert_detection_result = self.supabase.client.table('detections').insert(detection_data).execute()
                        logger.debug("detection inserted", detection_id=detection_data["id"], index=idx, class_name=class_name)
                    except Exception as e:
                        logger.warning("detection insert failed", analysis_id=analysis_id, index=idx, error=str(e))
                        # Continue with other detections even if one fails

                # Update analysis risk level
                try:
                    risk_update_data = {
                        "risk_level": map_risk_level_to_db(highest_risk, for_analysis=True)
                    }
                    self.supabase.client.table('analyses').update(risk_update_data).eq('id', analysis_id).execute()
                    logger.info("risk level updated", analysis_id=analysis_id, risk_level=highest_risk)
                except Exception as e:
                    logger.warning("risk level update failed", analysis_id=analysis_id, error=str(e))

            logger.debug("analysis processing completed", analysis_id=analysis_id)

            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "total_detections": len(detections),
                "processing_time_ms": yolo_result.get("processing_time_ms"),
                "has_gps_data": location_data is not None,
                "camera_detected": camera_info.get("camera_make") if camera_info else None,
                "image_urls": {
                    "original": image_url,
                    "processed": processed_image_url
                },
                "filenames": {
                    "original": filename,
                    "standardized": image_filename,
                    "processed": processed_image_filename
                },
                "filename_variations": filename_variations
            }

        except httpx.TimeoutException:
            logger.error("yolo_processing_timeout", analysis_id=analysis_id)
            raise YOLOTimeoutException(timeout_seconds=30.0)
        except httpx.HTTPStatusError as e:
            logger.error("yolo_http_error", analysis_id=analysis_id, status=e.response.status_code)
            raise YOLOServiceException(f"YOLO HTTP error: {e.response.status_code}")
        except httpx.HTTPError as e:
            logger.error("yolo_connection_error", analysis_id=analysis_id, error=str(e))
            raise YOLOServiceException(f"Failed to connect to YOLO service: {str(e)}")
        except KeyError as e:
            logger.error("missing_yolo_field", analysis_id=analysis_id, field=str(e), exc_info=True)
            raise YOLOServiceException(f"Missing required field in YOLO response: {e}")
        except ValueError as e:
            logger.error("invalid_processing_value", analysis_id=analysis_id, error=str(e), exc_info=True)
            raise ImageProcessingException(f"Invalid value during processing: {str(e)}")
        except Exception as e:
            logger.error("error processing analysis", analysis_id=analysis_id, error=str(e), exc_info=True)
            raise ImageProcessingException(f"Error procesando análisis: {str(e)}")

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
            logger.debug("raw analysis from db", fields=list(analysis.keys()))
            logger.debug("gps fields in db",
                        has_gps_data=analysis.get('has_gps_data'),
                        google_maps_url=analysis.get('google_maps_url'))

            # Obtener detecciones asociadas
            detections_response = self.supabase.client.table('detections').select('*').eq('analysis_id', analysis_id).execute()

            # Construir respuesta completa
            return {
                "id": analysis["id"],
                "status": "completed",
                "image_url": analysis.get("image_url"),
                "image_filename": analysis.get("image_filename"),
                "processed_image_url": analysis.get("processed_image_url"),
                "processed_image_filename": analysis.get("processed_image_filename"),
                "image_size_bytes": analysis.get("image_size_bytes"),
                "total_detections": analysis.get("total_detections", 0),
                "risk_level": analysis.get("risk_level"),
                "risk_score": analysis.get("risk_score"),
                "has_gps_data": analysis.get("has_gps_data", False),
                "google_maps_url": analysis.get("google_maps_url"),
                "google_earth_url": analysis.get("google_earth_url"),
                "gps_altitude_meters": analysis.get("gps_altitude_meters"),
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

        except KeyError as e:
            logger.error("missing_analysis_field", analysis_id=analysis_id, field=str(e), exc_info=True)
            raise DatabaseException(f"Missing required field in analysis data: {e}", operation="get_analysis")
        except Exception as e:
            logger.error("error getting analysis", analysis_id=analysis_id, error=str(e), exc_info=True)
            raise DatabaseException(f"Error retrieving analysis: {str(e)}", operation="get_analysis")

    async def _get_recent_analyses_for_deduplication(self, hours_back: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtener análisis recientes para verificar duplicados
        Get recent analyses to check for duplicates
        """
        try:
            # Query for recent analyses
            response = self.supabase.client.table('analyses').select(
                'id, image_size_bytes, camera_make, camera_model, '
                'has_gps_data, image_url, created_at'
            ).order('created_at', desc=True).limit(limit).execute()

            return response.data or []

        except Exception as e:
            logger.error("error getting recent analyses for deduplication", error=str(e), exc_info=True)
            # Return empty list instead of raising - deduplication is not critical
            return []

    async def _handle_duplicate_image(
        self,
        duplicate_check: Dict[str, Any],
        original_filename: str,
        processed_filename: str,
        content_signature: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Manejar imagen duplicada creando referencia en lugar de almacenar
        Handle duplicate image by creating reference instead of storing
        """
        analysis_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)

        # Generar nombres estandarizados para trazabilidad
        standardized_filename = generate_standardized_filename(
            original_filename=processed_filename,
            analysis_timestamp=timestamp
        )

        filename_variations = create_filename_variations(
            base_filename=processed_filename
        )

        logger.debug("creating duplicate reference", analysis_id=analysis_id)

        # Crear registro de análisis que referencia al original
        duplicate_analysis_data = {
            "id": analysis_id,
            "image_url": duplicate_check["reference_image_url"],
            "content_hash": content_signature["sha256"],
            "image_size_bytes": content_signature["size_bytes"],
            "is_duplicate_reference": True,
            "reference_analysis_id": duplicate_check["duplicate_analysis_id"],
            "duplicate_confidence": duplicate_check["confidence"],
            "duplicate_type": duplicate_check["duplicate_type"],
            "storage_saved_bytes": content_signature["size_bytes"],
            "created_at": timestamp.isoformat(),
            "total_detections": 0,  # Will be copied from referenced analysis
            "has_gps_data": False   # Will be updated if reference has GPS
        }

        # Insertar en base de datos
        insert_result = self.supabase.insert_analysis(duplicate_analysis_data)

        if insert_result.get("status") != "success":
            logger.error("error inserting duplicate reference",
                        analysis_id=analysis_id,
                        message=insert_result.get('message'))
            return {
                "analysis_id": analysis_id,
                "status": "failed",
                "error": "Database insertion failed for duplicate reference"
            }

        logger.info("duplicate reference created",
                   analysis_id=analysis_id,
                   storage_saved_bytes=content_signature['size_bytes'])

        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "is_duplicate": True,
            "duplicate_type": duplicate_check["duplicate_type"],
            "reference_analysis_id": duplicate_check["duplicate_analysis_id"],
            "storage_saved_bytes": content_signature["size_bytes"],
            "storage_saved_mb": round(content_signature["size_bytes"] / (1024 * 1024), 2),
            "duplicate_confidence": duplicate_check["confidence"],
            "image_urls": {
                "original": duplicate_check["reference_image_url"],
                "processed": duplicate_check["reference_image_url"].replace("original_", "processed_")
            },
            "filenames": {
                "original": original_filename,
                "standardized": standardized_filename,
                "processed": filename_variations["processed"]
            },
            "message": f"Duplicate detected - referenced existing analysis with {duplicate_check['confidence']:.1%} confidence"
        }

    def get_deduplication_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de deduplicación
        Get deduplication statistics
        """
        try:
            # Get total analyses
            total_response = self.supabase.client.table('analyses').select('id', count='exact').execute()
            total_analyses = total_response.count or 0

            # Get duplicate references
            duplicates_response = self.supabase.client.table('analyses').select(
                'id, storage_saved_bytes', count='exact'
            ).eq('is_duplicate_reference', True).execute()

            duplicate_references = duplicates_response.count or 0
            total_saved_bytes = sum(
                item.get('storage_saved_bytes', 0) for item in (duplicates_response.data or [])
            )

            deduplication_rate = (duplicate_references / total_analyses * 100) if total_analyses > 0 else 0

            return {
                "total_analyses": total_analyses,
                "unique_images": total_analyses - duplicate_references,
                "duplicate_references": duplicate_references,
                "deduplication_rate": round(deduplication_rate, 1),
                "storage_saved_bytes": total_saved_bytes,
                "storage_saved_mb": round(total_saved_bytes / (1024 * 1024), 2),
                "storage_saved_gb": round(total_saved_bytes / (1024 * 1024 * 1024), 3)
            }

        except Exception as e:
            logger.error("error getting deduplication stats", error=str(e), exc_info=True)
            # Return default stats instead of raising - stats are non-critical
            return {
                "error": str(e),
                "total_analyses": 0,
                "deduplication_rate": 0,
                "storage_saved_mb": 0
            }

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

            # Obtener todos los analysis_ids para fetch detecciones en una sola query
            analysis_ids = [analysis['id'] for analysis in response.data]

            # Fetch todas las detecciones en UNA SOLA query (optimización N+1)
            detections_map = {}
            if analysis_ids:
                all_detections_response = self.supabase.client.table('detections').select('*').in_('analysis_id', analysis_ids).execute()

                # Organizar detecciones por analysis_id
                for detection in (all_detections_response.data or []):
                    aid = detection['analysis_id']
                    if aid not in detections_map:
                        detections_map[aid] = []
                    detections_map[aid].append(detection)

            # Construir respuesta con detecciones ya cargadas
            analyses_with_summary = []
            for analysis in response.data:
                analysis_summary = analysis.copy()
                analysis_summary['detections_count'] = analysis.get('total_detections', 0)

                # Usar detecciones del mapa (ya cargadas)
                aid = analysis['id']
                if aid in detections_map and analysis.get('has_gps_data'):
                    # Tomar solo la primera detección para ubicación
                    analysis_summary['detections'] = detections_map[aid][:1]
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

        except KeyError as e:
            logger.error("missing_list_field", field=str(e), exc_info=True)
            raise DatabaseException(f"Missing required field in analysis list: {e}", operation="list_analyses")
        except ValueError as e:
            logger.error("invalid_list_value", error=str(e), exc_info=True)
            raise DatabaseException(f"Invalid value in analysis list: {str(e)}", operation="list_analyses")
        except Exception as e:
            logger.error("error listing analyses", error=str(e), exc_info=True)
            raise DatabaseException(f"Error listing analyses: {str(e)}", operation="list_analyses")

    async def get_heatmap_data(
        self,
        limit: int = 1000,
        risk_level: Optional[str] = None,
        since: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtener datos georeferenciados para visualización de mapa de calor

        Incluye información de tipo de criadero para diferenciación de colores

        Args:
            limit: Número máximo de análisis a retornar
            risk_level: Filtrar por nivel de riesgo (ALTO, MEDIO, BAJO)
            since: Filtrar análisis desde fecha ISO

        Returns:
            Dict con datos de ubicaciones para heatmap, incluyendo breeding_site_types
        """
        try:
            # Check if Supabase client is properly configured
            if not self.supabase or not hasattr(self.supabase, 'client') or not self.supabase.client:
                logger.warning("supabase_not_configured", message="Supabase not configured, returning empty heatmap data")
                return {
                    "status": "success",
                    "data": [],
                    "count": 0
                }

            # Check if we're using a mock client (development mode)
            from unittest.mock import MagicMock
            if isinstance(self.supabase.client, MagicMock):
                logger.info("using mock client, returning empty heatmap data")
                return {
                    "status": "success",
                    "data": [],
                    "count": 0
                }

            # Construir query con filtros - SOLO análisis con GPS válido
            # Include user_id to differentiate between own and community detections
            query = self.supabase.client.table("analyses")\
                .select("id, user_id, google_maps_url, risk_level, total_detections, created_at, location, has_gps_data")\
                .eq("has_gps_data", True)\
                .order("created_at", desc=True)\
                .limit(limit)

            if risk_level:
                query = query.eq("risk_level", risk_level.upper())
            if since:
                query = query.gte("created_at", since)

            result = query.execute()

            if not result.data:
                return {
                    "status": "success",
                    "data": [],
                    "count": 0
                }

            # Fetch detections for these analyses to get breeding site types
            analysis_ids = [analysis['id'] for analysis in result.data]

            detections_query = self.supabase.client.table("detections")\
                .select("analysis_id, breeding_site_type, risk_level")\
                .in_("analysis_id", analysis_ids)

            detections_result = detections_query.execute()

            # Group detections by analysis_id and breeding_site_type
            detections_by_analysis = {}
            for detection in (detections_result.data or []):
                aid = detection['analysis_id']
                if aid not in detections_by_analysis:
                    detections_by_analysis[aid] = []
                detections_by_analysis[aid].append(detection)

            # Enrich analysis data with detection types
            for analysis in result.data:
                aid = analysis['id']
                analysis['detections'] = detections_by_analysis.get(aid, [])

            return {
                "status": "success",
                "data": result.data,
                "count": len(result.data)
            }

        except (OSError, ConnectionError) as e:
            # Handle DNS/network errors gracefully (e.g., Supabase not reachable)
            logger.warning("supabase_connection_error", error=str(e), message="Supabase connection failed, returning empty data")
            return {
                "status": "success",
                "data": [],
                "count": 0
            }
        except KeyError as e:
            logger.error("heatmap_missing_field", field=str(e), exc_info=True)
            raise DatabaseException(f"Missing required field in heatmap data: {e}", operation="fetch_heatmap")
        except Exception as e:
            # Check if it's a network/DNS error
            error_str = str(e).lower()
            if 'getaddrinfo' in error_str or 'connection' in error_str or 'dns' in error_str:
                logger.warning("supabase_network_error", error=str(e), message="Network error accessing Supabase, returning empty data")
                return {
                    "status": "success",
                    "data": [],
                    "count": 0
                }
            logger.error("heatmap_fetch_error", error=str(e), exc_info=True)
            raise DatabaseException(f"Error fetching heatmap data: {str(e)}", operation="fetch_heatmap")

    async def get_map_statistics(self) -> Dict[str, Any]:
        """
        Obtener estadísticas agregadas para visualización de mapa

        Returns:
            Dict con estadísticas del sistema: total de análisis, detecciones,
            distribución de riesgo, área monitoreada
        """
        try:
            # Check if Supabase client is properly configured
            if not self.supabase or not hasattr(self.supabase, 'client') or not self.supabase.client:
                logger.warning("supabase_not_configured", message="Supabase not configured, returning empty statistics")
                return self._empty_stats()

            # Check if we're using a mock client (development mode)
            from unittest.mock import MagicMock
            if isinstance(self.supabase.client, MagicMock):
                logger.info("using mock client, returning empty map statistics")
                return self._empty_stats()

            # Fetch analyses from database
            analyses_response = self.supabase.client.table("analyses")\
                .select("id, risk_level, total_detections, google_maps_url, created_at, has_gps_data")\
                .execute()

            # Fetch detections for type distribution and area calculation
            detections_response = self.supabase.client.table("detections")\
                .select("breeding_site_type, created_at, mask_area, analysis_id")\
                .execute()

            if not analyses_response.data:
                return self._empty_stats()

            analyses = analyses_response.data
            detections = detections_response.data or []

            # Calculate statistics
            total_analyses = len(analyses)
            total_detections = sum(a.get("total_detections", 0) for a in analyses)

            # Risk distribution (map from DB enum values to frontend keys)
            risk_distribution = {"bajo": 0, "medio": 0, "alto": 0, "critico": 0}
            for analysis in analyses:
                risk_level = analysis.get("risk_level")
                if risk_level:  # Skip None values
                    risk = risk_level.lower()
                    if risk == "low" or risk == "minimal":
                        risk_distribution["bajo"] += 1
                    elif risk == "medium":
                        risk_distribution["medio"] += 1
                    elif risk == "high":
                        risk_distribution["alto"] += 1
                    elif risk == "critical":
                        risk_distribution["critico"] += 1

            # Detection types distribution
            detection_types_count = {}
            for detection in detections:
                dtype = detection.get("breeding_site_type", "Desconocido")
                detection_types_count[dtype] = detection_types_count.get(dtype, 0) + 1

            detection_types = [
                {"name": name, "value": count}
                for name, count in detection_types_count.items()
            ]

            # Debug logging
            logger.info(
                "map_stats_data_check",
                total_detections=len(detections),
                detection_types_count=detection_types_count,
                detection_types_result=detection_types,
                weekly_trend_will_be_calculated=True
            )

            # Weekly trend (last 7 days) - count detections per day
            now = datetime.now(timezone.utc)
            day_names_es = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
            weekly_trend = []

            for i in range(6, -1, -1):
                day = now - timedelta(days=i)
                day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)

                count = 0
                # Count detections for this day
                for d in detections:
                    created_at = d.get("created_at")
                    if created_at:
                        try:
                            # Parse datetime string to datetime object
                            if isinstance(created_at, str):
                                # Handle ISO format with Z or timezone
                                if created_at.endswith('Z'):
                                    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                elif '+' in created_at or '-' in created_at.split('T')[-1] if 'T' in created_at else False:
                                    created_dt = datetime.fromisoformat(created_at)
                                else:
                                    # No timezone, assume UTC
                                    created_dt = datetime.fromisoformat(created_at).replace(tzinfo=timezone.utc)
                            else:
                                # Already a datetime object
                                created_dt = created_at
                                if created_dt.tzinfo is None:
                                    created_dt = created_dt.replace(tzinfo=timezone.utc)

                            # Check if detection is in current day
                            if day_start <= created_dt < day_end:
                                count += 1
                        except (ValueError, AttributeError):
                            # Skip invalid dates
                            pass

                weekly_trend.append({
                    "day": day_names_es[day.weekday()],
                    "detections": count
                })

            # Active zones (analyses with GPS data)
            active_zones = sum(1 for a in analyses if a.get("has_gps_data"))

            # Calculate total area from all detections (sum of mask_area in square pixels)
            # Convert to square meters assuming typical phone camera resolution
            total_area_pixels = sum(d.get("mask_area", 0) for d in detections if d.get("mask_area"))
            # Rough conversion: 1 sq meter ≈ 10000 sq pixels (varies by camera distance)
            total_area_detected_m2 = total_area_pixels / 10000.0 if total_area_pixels > 0 else 0

            # Enrich analyses data with GPS flag and area
            enriched_analyses = []
            for analysis in analyses:
                enriched_analysis = dict(analysis)
                enriched_analysis["has_gps_data"] = analysis.get("has_gps_data", False)
                # Calculate area for this specific analysis
                analysis_id = analysis.get("id")
                if analysis_id:
                    analysis_area = sum(
                        d.get("mask_area", 0) for d in detections
                        if d.get("analysis_id") == analysis_id and d.get("mask_area")
                    )
                    enriched_analysis["total_area_detected_m2"] = analysis_area / 10000.0 if analysis_area > 0 else 0
                else:
                    enriched_analysis["total_area_detected_m2"] = 0
                enriched_analyses.append(enriched_analysis)

            result = {
                "status": "success",
                "total_analyses": total_analyses,
                "total_detections": total_detections,
                "area_monitored_km2": 0,  # TODO: Calculate from GPS coordinates
                "model_accuracy": 0.92,  # Placeholder
                "active_zones": active_zones,
                "risk_distribution": risk_distribution,
                "detection_types": detection_types,
                "weekly_trend": weekly_trend,
                "total_area_detected_m2": total_area_detected_m2,
                "data": enriched_analyses
            }

            # Debug log final result
            logger.info(
                "map_stats_final_result",
                has_detection_types=len(detection_types) > 0,
                detection_types_count=len(detection_types),
                has_weekly_trend=len(weekly_trend) > 0,
                weekly_trend_count=len(weekly_trend)
            )

            return result

        except (OSError, ConnectionError) as e:
            # Handle DNS/network errors gracefully (e.g., Supabase not reachable)
            logger.warning("supabase_connection_error", error=str(e), message="Supabase connection failed, returning empty stats")
            return self._empty_stats()
        except KeyError as e:
            logger.error("map_stats_missing_field", field=str(e), exc_info=True)
            raise DatabaseException(f"Missing required field in statistics: {e}", operation="fetch_map_stats")
        except ValueError as e:
            logger.error("map_stats_invalid_value", error=str(e), exc_info=True)
            raise DatabaseException(f"Invalid value in statistics calculation: {str(e)}", operation="fetch_map_stats")
        except Exception as e:
            # Check if it's a network/DNS error
            error_str = str(e).lower()
            if 'getaddrinfo' in error_str or 'connection' in error_str or 'dns' in error_str:
                logger.warning("supabase_network_error", error=str(e), message="Network error accessing Supabase, returning empty stats")
                return self._empty_stats()
            logger.error("map_stats_fetch_error", error=str(e), exc_info=True)
            raise DatabaseException(f"Error fetching map statistics: {str(e)}", operation="fetch_map_stats")

    def _empty_stats(self) -> Dict[str, Any]:
        """Return empty statistics structure"""
        return {
            "total_analyses": 0,
            "total_detections": 0,
            "area_monitored_km2": 0,
            "model_accuracy": 0,
            "active_zones": 0,
            "risk_distribution": {"bajo": 0, "medio": 0, "alto": 0, "critico": 0},
            "detection_types": [],
            "weekly_trend": [],
            "data": []
        }


# Instancia singleton
analysis_service = AnalysisService()