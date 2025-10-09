"""
Supabase client configuration for Sentrix Backend
Cliente de Supabase para Sentrix Backend
"""

import os
import uuid
from typing import Optional, Union
from pathlib import Path
from io import BytesIO
from supabase import create_client, Client

# Handle config import gracefully
try:
    from ..config import get_settings
except ImportError:
    try:
        from config import get_settings
    except ImportError:
        # Fallback for testing without warnings
        class MockSettings:
            def __init__(self):
                self.supabase_url = os.getenv('SUPABASE_URL', 'https://mock-supabase-url.com')
                self.supabase_key = os.getenv('SUPABASE_KEY', 'mock-supabase-key')

        def get_settings():
            return MockSettings()

        # Only show warning if not in testing mode
        if not os.getenv('TESTING_MODE', 'false').lower() == 'true':
            print("Info: Using mock configuration (set TESTING_MODE=true to suppress)")


class SupabaseManager:
    """
    Manager for Supabase connections and operations
    Gestor para conexiones y operaciones de Supabase
    """

    def __init__(self):
        self._client: Optional[Client] = None
        self._settings = get_settings()

    @property
    def client(self) -> Client:
        """Get or create Supabase client"""
        if self._client is None:
            self._client = self._create_client()
        return self._client

    def _create_client(self) -> Client:
        """Create Supabase client with configuration"""
        supabase_url = self._settings.supabase_url
        supabase_key = self._settings.supabase_key

        # Check if we're in testing mode or using mock URLs
        is_testing = os.getenv('TESTING_MODE', 'false').lower() == 'true'
        is_mock = 'mock' in supabase_url.lower() or not supabase_url or not supabase_key

        if is_mock and not is_testing:
            raise ValueError(
                "Supabase URL and Key must be provided in environment variables. "
                "Check SUPABASE_URL and SUPABASE_KEY in your .env file."
            )

        # In testing mode, create a mock client that will fail gracefully
        if is_mock:
            # Create a minimal mock client that won't actually connect
            from unittest.mock import MagicMock
            mock_client = MagicMock()
            mock_client.table = MagicMock(return_value=MagicMock())
            return mock_client

        try:
            client = create_client(supabase_url, supabase_key)
            return client
        except Exception as e:
            if is_testing:
                # In testing, return a mock instead of failing
                from unittest.mock import MagicMock
                mock_client = MagicMock()
                mock_client.table = MagicMock(return_value=MagicMock())
                return mock_client
            raise ConnectionError(f"Failed to create Supabase client: {e}")

    def test_connection(self) -> dict:
        """
        Test Supabase connection
        Probar conexión a Supabase
        """
        try:
            # Test basic connectivity by making a simple query to analyses table
            response = self.client.table('analyses').select('id').limit(1).execute()

            return {
                "status": "connected",
                "message": "Supabase connection successful",
                "url": self._settings.supabase_url,
                "data_available": len(response.data) > 0
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Supabase connection failed: {str(e)}",
                "url": self._settings.supabase_url,
                "error_type": type(e).__name__
            }

    def create_user(self, email: str, password: str, user_metadata: dict = None) -> dict:
        """
        Create a new user in Supabase Auth
        Crear un nuevo usuario en Supabase Auth
        """
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata or {}
                }
            })

            return {
                "status": "success",
                "user": response.user,
                "session": response.session
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def authenticate_user(self, email: str, password: str) -> dict:
        """
        Authenticate user with Supabase
        Autenticar usuario con Supabase
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            return {
                "status": "success",
                "user": response.user,
                "session": response.session
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def get_user_from_token(self, token: str) -> dict:
        """
        Get user from JWT token
        Obtener usuario desde token JWT
        """
        try:
            response = self.client.auth.get_user(token)

            return {
                "status": "success",
                "user": response.user
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def insert_analysis(self, analysis_data: dict) -> dict:
        """
        Insert analysis record into Supabase
        Insertar registro de análisis en Supabase
        """
        try:
            response = self.client.table('analyses').insert(analysis_data).execute()

            return {
                "status": "success",
                "data": response.data[0] if response.data else None
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def insert_detection(self, detection_data: dict, auto_calculate_validity: bool = True) -> dict:
        """
        Insert detection record into Supabase with temporal validity
        Insertar registro de detección en Supabase con validez temporal

        Args:
            detection_data: Detection data dictionary
            auto_calculate_validity: Automatically calculate and add validity fields (default: True)
        """
        try:
            # Enrich detection with validity fields if enabled
            if auto_calculate_validity:
                try:
                    from .temporal_validity import enrich_detection_with_validity
                    is_validated = detection_data.get("validation_status") == "validated"
                    detection_data = enrich_detection_with_validity(
                        detection_data,
                        is_validated=is_validated
                    )
                except ImportError:
                    # Temporal validity not available, proceed without it
                    pass

            response = self.client.table('detections').insert(detection_data).execute()

            return {
                "status": "success",
                "data": response.data[0] if response.data else None
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def update_analysis(self, analysis_id: str, update_data: dict) -> dict:
        """
        Update analysis record in Supabase
        Actualizar registro de análisis en Supabase
        """
        try:
            response = self.client.table('analyses').update(update_data).eq('id', analysis_id).execute()

            return {
                "status": "success",
                "data": response.data[0] if response.data else None
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def get_analyses(self, user_id: str = None, limit: int = 50) -> dict:
        """
        Get analyses from Supabase
        Obtener análisis desde Supabase
        """
        try:
            query = self.client.table('analyses').select('*')

            if user_id:
                query = query.eq('user_id', user_id)

            response = query.limit(limit).order('created_at', desc=True).execute()

            return {
                "status": "success",
                "data": response.data,
                "count": len(response.data)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def upload_image(self, image_data: Union[bytes, BytesIO], filename: str, bucket_name: str = "images") -> dict:
        """
        Upload image to Supabase Storage
        Subir imagen al almacenamiento de Supabase
        """
        try:
            # Prepare data
            if isinstance(image_data, BytesIO):
                file_data = image_data.getvalue()
            else:
                file_data = image_data

            # Generate unique filename to avoid conflicts
            file_ext = Path(filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_ext}"

            # Upload to storage
            response = self.client.storage.from_(bucket_name).upload(
                path=unique_filename,
                file=file_data,
                file_options={"content-type": self._get_content_type(file_ext)}
            )

            if response.status_code == 200:
                # Get public URL
                public_url = self.client.storage.from_(bucket_name).get_public_url(unique_filename)

                return {
                    "status": "success",
                    "file_path": unique_filename,
                    "public_url": public_url,
                    "size_bytes": len(file_data)
                }
            else:
                return {
                    "status": "error",
                    "message": f"Upload failed: {response.status_code}"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Upload error: {str(e)}"
            }

    def upload_dual_images(self, original_data: bytes, processed_data: bytes, base_filename: str) -> dict:
        """
        Upload both original and processed images
        Subir tanto imagen original como procesada
        """
        try:
            # Upload original image
            original_result = self.upload_image(
                original_data,
                f"original_{base_filename}",
                "images"
            )

            if original_result["status"] != "success":
                return original_result

            # Upload processed image
            processed_result = self.upload_image(
                processed_data,
                f"processed_{base_filename}",
                "images"
            )

            if processed_result["status"] != "success":
                # If processed upload fails, clean up original
                self.delete_image(original_result["file_path"])
                return processed_result

            return {
                "status": "success",
                "original": {
                    "file_path": original_result["file_path"],
                    "public_url": original_result["public_url"],
                    "size_bytes": original_result["size_bytes"]
                },
                "processed": {
                    "file_path": processed_result["file_path"],
                    "public_url": processed_result["public_url"],
                    "size_bytes": processed_result["size_bytes"]
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Dual upload error: {str(e)}"
            }

    def delete_image(self, file_path: str, bucket_name: str = "images") -> dict:
        """
        Delete image from Supabase Storage
        Eliminar imagen del almacenamiento de Supabase
        """
        try:
            response = self.client.storage.from_(bucket_name).remove([file_path])

            return {
                "status": "success" if response else "error",
                "message": "Image deleted successfully" if response else "Delete failed"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Delete error: {str(e)}"
            }

    def download_image(self, file_path: str, bucket_name: str = "images") -> dict:
        """
        Download image from Supabase Storage
        Descargar imagen del almacenamiento de Supabase
        """
        try:
            # Download file from storage
            response = self.client.storage.from_(bucket_name).download(file_path)

            if response:
                return {
                    "status": "success",
                    "data": response,
                    "content_type": self._get_content_type(Path(file_path).suffix)
                }
            else:
                return {
                    "status": "error",
                    "message": "File not found or download failed"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Download error: {str(e)}"
            }

    def get_image_url(self, file_path: str, bucket_name: str = "images") -> dict:
        """
        Get public URL for image in Supabase Storage
        Obtener URL pública para imagen en Supabase Storage
        """
        try:
            # Get public URL
            public_url = self.client.storage.from_(bucket_name).get_public_url(file_path)

            return {
                "status": "success",
                "public_url": public_url
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"URL generation error: {str(e)}"
            }

    def _get_content_type(self, file_extension: str) -> str:
        """Get content type based on file extension"""
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.tiff': 'image/tiff',
            '.bmp': 'image/bmp'
        }
        return content_types.get(file_extension.lower(), 'image/jpeg')


# Global Supabase manager instance
_supabase_manager: Optional[SupabaseManager] = None


def get_supabase_manager() -> SupabaseManager:
    """
    Get global Supabase manager instance
    Obtener instancia global del gestor de Supabase
    """
    global _supabase_manager

    if _supabase_manager is None:
        _supabase_manager = SupabaseManager()

    return _supabase_manager


def get_supabase_client() -> Client:
    """
    Get Supabase client directly
    Obtener cliente de Supabase directamente
    """
    return get_supabase_manager().client