"""
Database utilities for Sentrix Backend
Utilidades de base de datos para Sentrix Backend
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from .paths import get_database_url_from_env


def get_db_session():
    """
    Get database session
    Obtener sesión de base de datos
    """
    database_url = get_database_url_from_env()
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


@contextmanager
def get_db_context():
    """
    Database session context manager
    Manejador de contexto para sesiones de base de datos
    """
    session = get_db_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def validate_connection():
    """
    Validate database connection
    Validar conexión a la base de datos
    """
    try:
        database_url = get_database_url_from_env()
        engine = create_engine(database_url)

        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return result.fetchone() is not None

    except SQLAlchemyError as e:
        print(f"❌ Error de conexión a la base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def get_system_info():
    """
    Get database system information
    Obtener información del sistema de base de datos
    """
    info = {
        "database_url": get_database_url_from_env(),
        "connection_valid": validate_connection()
    }

    if info["connection_valid"]:
        try:
            database_url = get_database_url_from_env()
            engine = create_engine(database_url)

            with engine.connect() as connection:
                # Get PostgreSQL version
                result = connection.execute(text("SELECT version()"))
                info["database_version"] = result.fetchone()[0]

                # Check PostGIS extension
                result = connection.execute(text(
                    "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'postgis')"
                ))
                info["postgis_available"] = result.fetchone()[0]

        except Exception as e:
            info["error"] = str(e)

    return info