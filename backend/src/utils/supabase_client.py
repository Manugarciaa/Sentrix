"""
Supabase client configuration for Sentrix Backend
Cliente de Supabase para Sentrix Backend
"""

import os
from typing import Optional
from supabase import create_client, Client
from configs.settings import get_settings


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

        if not supabase_url or not supabase_key:
            raise ValueError(
                "Supabase URL and Key must be provided in environment variables. "
                "Check SUPABASE_URL and SUPABASE_KEY in your .env file."
            )

        try:
            client = create_client(supabase_url, supabase_key)
            return client
        except Exception as e:
            raise ConnectionError(f"Failed to create Supabase client: {e}")

    def test_connection(self) -> dict:
        """
        Test Supabase connection
        Probar conexión a Supabase
        """
        try:
            # Test basic connectivity by making a simple query
            response = self.client.table('users').select('id').limit(1).execute()

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

    def insert_detection(self, detection_data: dict) -> dict:
        """
        Insert detection record into Supabase
        Insertar registro de detección en Supabase
        """
        try:
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