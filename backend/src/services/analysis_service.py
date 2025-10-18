"""
Servicio de análisis para procesar imágenes y almacenar resultados
Service for processing images and storing results
"""

import uuid
import sys
import os
from datetime import datetime
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
        timestamp = kwargs.get('analysis_timestamp', datetime.utcnow())
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
            'timestamp': datetime.utcnow().isoformat()
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
        Procesar imagen completa: YOLO + almacenamiento dual en BD + nomenclatura estandarizada

        Args:
            image_data: Datos binarios de la imagen
            filename: Nombre del archivo
            confidence_threshold: Umbral de confianza
            include_gps: Extraer GPS automáticamente
            manual_latitude: Latitud manual (opcional)
            manual_longitude: Longitud manual (opcional)

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

            if manual_latitude and manual_longitude:
                location_data = {
                    "has_location": True,
                    "latitude": manual_latitude,
                    "longitude": manual_longitude,
                    "location_source": "MANUAL"
                }
                gps_data = {"has_gps": True, "latitude": manual_latitude, "longitude": manual_longitude}
            elif yolo_location and yolo_location.get("has_location"):
                location_data = {
                    "has_location": True,
                    "latitude": yolo_location.get("latitude"),
                    "longitude": yolo_location.get("longitude"),
                    "altitude_meters": yolo_location.get("altitude_meters"),
                    "location_source": yolo_location.get("location_source", "EXIF_GPS")
                }
                gps_data = {"has_gps": True, "latitude": yolo_location.get("latitude"), "longitude": yolo_location.get("longitude")}

            # 5. Generar nombres de archivo estandarizados
            timestamp = datetime.utcnow()
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
            processed_image_data_from_yolo = yolo_result.get("processed_image_data")  # TODO: Implementar en YOLO service

            # 7. Almacenar ambas imágenes en Supabase Storage
            image_upload_result = None
            if processed_image_data_from_yolo:
                # Almacenamiento dual
                image_upload_result = self.supabase.upload_dual_images(
                    original_data=processed_image_data,
                    processed_data=processed_image_data_from_yolo,
                    base_filename=standardized_filename
                )
            else:
                # Solo imagen original por ahora
                image_upload_result = self.supabase.upload_image(
                    image_data=processed_image_data,
                    filename=f"original_{standardized_filename}",
                    bucket_name="images"
                )

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
            basic_analysis_data = {
                "id": analysis_id,
                "image_url": image_url,
                "processed_image_url": processed_image_url,
                "image_filename": image_filename,
                "processed_image_filename": processed_image_filename,
                "original_filename": filename,
                "image_size_bytes": len(processed_image_data),
                "total_detections": len(detections),
                "created_at": timestamp.isoformat()
            }

            logger.debug("creating analysis with standardized naming",
                        analysis_id=analysis_id,
                        filename=image_filename)

            # Insertar análisis básico
            insert_result = self.supabase.insert_analysis(basic_analysis_data)
            if insert_result.get("status") != "success":
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
                    logger.info("gps data stored for analysis", analysis_id=analysis_id)
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
                "confidence_threshold": 0.5,
                "processing_time_ms": yolo_result.get("processing_time_ms", 0)
            }
            try:
                update_result = self.supabase.client.table('analyses').update(processing_update_data).eq('id', analysis_id).execute()
                logger.info("processing metadata stored for analysis", analysis_id=analysis_id)
            except Exception as e:
                logger.warning("processing metadata update failed", analysis_id=analysis_id, error=str(e))

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
            # Query for recent analyses with content hashes
            response = self.supabase.client.table('analyses').select(
                'id, content_hash, image_size_bytes, camera_make, camera_model, '
                'has_gps_data, gps_latitude, gps_longitude, image_url, processed_image_url, created_at'
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
        timestamp = datetime.utcnow()

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
            "original_filename": original_filename,
            "image_filename": standardized_filename,
            "processed_image_filename": filename_variations["processed"],
            "image_url": duplicate_check["reference_image_url"],
            "processed_image_url": duplicate_check["reference_image_url"].replace("original_", "processed_"),
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

            # Construir query con filtros
            query = self.supabase.client.table("analyses")\
                .select("id, google_maps_url, risk_level, total_detections, created_at")\
                .not_.is_("google_maps_url", "null")\
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
                return {
                    "total_analyses": 0,
                    "total_detections": 0,
                    "data": []
                }

            # Fetch analyses from database
            analyses = self.supabase.client.table("analyses")\
                .select("risk_level, total_detections, google_maps_url, created_at")\
                .execute()

            if not analyses.data:
                return {
                    "total_analyses": 0,
                    "total_detections": 0,
                    "data": []
                }

            return {
                "status": "success",
                "data": analyses.data,
                "total_analyses": len(analyses.data),
                "total_detections": sum(a.get("total_detections", 0) for a in analyses.data)
            }

        except (OSError, ConnectionError) as e:
            # Handle DNS/network errors gracefully (e.g., Supabase not reachable)
            logger.warning("supabase_connection_error", error=str(e), message="Supabase connection failed, returning empty stats")
            return {
                "total_analyses": 0,
                "total_detections": 0,
                "data": []
            }
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
                return {
                    "total_analyses": 0,
                    "total_detections": 0,
                    "data": []
                }
            logger.error("map_stats_fetch_error", error=str(e), exc_info=True)
            raise DatabaseException(f"Error fetching map statistics: {str(e)}", operation="fetch_map_stats")


# Instancia singleton
analysis_service = AnalysisService()