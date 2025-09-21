"""
Database connection utilities for Sentrix Backend
Utilidades de conexión de base de datos para Sentrix Backend

Based on original app/database.py but following yolo-service patterns
Basado en app/database.py original pero siguiendo patrones de yolo-service
"""

import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..utils.paths import get_database_url_from_env


def get_database_url():
    """
    Get database URL with automatic configuration
    Obtener URL de base de datos con configuración automática
    """
    return get_database_url_from_env()


def create_database_engine(database_url: str = None):
    """
    Create database engine with optimized settings
    Crear motor de base de datos con configuraciones optimizadas
    """
    if not database_url:
        database_url = get_database_url()

    # Production settings
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "echo": os.getenv("DEBUG", "false").lower() == "true"
    }

    # Test environment settings
    if "test" in database_url or os.getenv("TESTING"):
        engine_kwargs.update({
            "poolclass": StaticPool,
            "connect_args": {"check_same_thread": False} if "sqlite" in database_url else {}
        })

    engine = create_engine(database_url, **engine_kwargs)

    # Enable PostGIS extension on PostgreSQL
    if "postgresql" in database_url:
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            if hasattr(dbapi_connection, 'execute'):
                # Enable PostGIS if available
                try:
                    dbapi_connection.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
                except Exception:
                    pass  # Extension might already exist or not available

    return engine


def create_session_maker(engine=None):
    """
    Create session maker
    Crear creador de sesiones
    """
    if not engine:
        engine = create_database_engine()

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    return SessionLocal


# Global engine and session maker (following FastAPI patterns)
engine = create_database_engine()
SessionLocal = create_session_maker(engine)

# Base for model declarations
Base = declarative_base()


def get_db():
    """
    Dependency for getting database session in FastAPI
    Dependencia para obtener sesión de base de datos en FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """
    Test database connection
    Probar conexión a base de datos
    """
    try:
        db = SessionLocal()
        # Simple query to test connection
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"ERROR: Error de conexión a la base de datos: {e}")
        return False


def get_database_info():
    """
    Get database information for system diagnostics
    Obtener información de base de datos para diagnósticos del sistema
    """
    try:
        db = SessionLocal()

        # Get database version
        result = db.execute(text("SELECT version()")).fetchone()
        version = result[0] if result else "Unknown"

        # Check PostGIS availability (for PostgreSQL)
        postgis_available = False
        try:
            result = db.execute(
                text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'postgis')")
            ).fetchone()
            postgis_available = result[0] if result else False
        except Exception:
            pass  # Not PostgreSQL or PostGIS not available

        db.close()

        return {
            "database_url": get_database_url(),
            "version": version,
            "postgis_available": postgis_available,
            "connection_valid": True
        }

    except Exception as e:
        return {
            "database_url": get_database_url(),
            "error": str(e),
            "connection_valid": False
        }