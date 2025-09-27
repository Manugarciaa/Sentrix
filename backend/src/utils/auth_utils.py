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


