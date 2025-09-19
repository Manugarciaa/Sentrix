"""
Authentication utilities for Sentrix Backend
Utilidades de autenticación para Sentrix Backend
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token
    Verificar token JWT
    """
    try:
        # In production, use proper JWT secret from environment
        secret_key = os.getenv("JWT_SECRET_KEY", "development-secret-key")

        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create access token
    Crear token de acceso
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)

    to_encode.update({"exp": expire})

    secret_key = os.getenv("JWT_SECRET_KEY", "development-secret-key")
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")

    return encoded_jwt


def get_current_user(token: str) -> Dict[str, Any]:
    """
    Get current user from token
    Obtener usuario actual del token
    """
    payload = verify_token(token)

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    return {
        "id": user_id,
        "email": payload.get("email"),
        "role": payload.get("role", "user")
    }


def validate_supabase_token(token: str) -> Dict[str, Any]:
    """
    Validate Supabase JWT token
    Validar token JWT de Supabase
    """
    try:
        # Supabase JWT validation logic
        supabase_jwt_secret = os.getenv("SUPABASE_JWT_SECRET")

        if not supabase_jwt_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase JWT secret not configured"
            )

        payload = jwt.decode(token, supabase_jwt_secret, algorithms=["HS256"])
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Supabase token"
        )