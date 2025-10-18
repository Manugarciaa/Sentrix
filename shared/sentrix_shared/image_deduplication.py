"""
Image deduplication system for Sentrix
Sistema de deduplicación de imágenes para Sentrix

Prevents storage overflow by detecting and handling duplicate image content
Previene desbordamiento de almacenamiento detectando y manejando contenido duplicado
"""

import hashlib
import os
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
from pathlib import Path


def calculate_image_hash(image_data: bytes, algorithm: str = 'sha256') -> str:
    """
    Calculate hash of image content for deduplication
    Calcular hash del contenido de imagen para deduplicación

    Args:
        image_data: Binary image data
        algorithm: Hash algorithm ('sha256', 'md5')

    Returns:
        Hex string of hash
    """
    if algorithm == 'sha256':
        hasher = hashlib.sha256()
    elif algorithm == 'md5':
        hasher = hashlib.md5()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    hasher.update(image_data)
    return hasher.hexdigest()


def calculate_content_signature(image_data: bytes) -> Dict[str, str]:
    """
    Calculate multiple signatures for robust duplicate detection
    Calcular múltiples firmas para detección robusta de duplicados

    Returns:
        Dict with different hash algorithms
    """
    return {
        'sha256': calculate_image_hash(image_data, 'sha256'),
        'md5': calculate_image_hash(image_data, 'md5'),
        'size_bytes': len(image_data)
    }


class ImageDeduplicationManager:
    """
    Manages image deduplication and smart storage
    Gestiona deduplicación de imágenes y almacenamiento inteligente
    """

    def __init__(self):
        self.duplicate_threshold_hours = 24  # Consider duplicates within 24h

    def check_for_duplicates(
        self,
        image_hash: str,
        image_size: int,
        camera_info: Optional[Dict] = None,
        gps_data: Optional[Dict] = None,
        existing_analyses: List[Dict] = None
    ) -> Dict[str, any]:
        """
        Check if image is a duplicate based on content and metadata
        Verificar si la imagen es duplicada basándose en contenido y metadatos

        Args:
            image_hash: SHA-256 hash of image content
            image_size: Size in bytes
            camera_info: Camera metadata
            gps_data: GPS metadata
            existing_analyses: List of existing analyses to check against

        Returns:
            Dict with duplicate status and reference info
        """
        result = {
            'is_duplicate': False,
            'duplicate_analysis_id': None,
            'duplicate_type': None,
            'should_store_separately': True,
            'reference_image_url': None,
            'confidence': 0.0
        }

        if not existing_analyses:
            return result

        # Check for exact content matches
        exact_matches = self._find_exact_content_matches(
            image_hash, image_size, existing_analyses
        )

        if exact_matches:
            # Found exact content match
            best_match = self._select_best_duplicate_match(
                exact_matches, camera_info, gps_data
            )

            result.update({
                'is_duplicate': True,
                'duplicate_analysis_id': best_match['id'],
                'duplicate_type': 'exact_content',
                'should_store_separately': False,  # Reuse existing storage
                'reference_image_url': best_match.get('image_url'),
                'confidence': best_match['confidence']
            })

        return result

    def _find_exact_content_matches(
        self,
        image_hash: str,
        image_size: int,
        existing_analyses: List[Dict]
    ) -> List[Dict]:
        """Find analyses with exact same content hash and size"""
        matches = []

        for analysis in existing_analyses:
            if (analysis.get('content_hash') == image_hash and
                analysis.get('image_size_bytes') == image_size):
                matches.append(analysis)

        return matches

    def _select_best_duplicate_match(
        self,
        matches: List[Dict],
        camera_info: Optional[Dict],
        gps_data: Optional[Dict]
    ) -> Dict[str, any]:
        """
        Select the best duplicate match based on metadata similarity
        Seleccionar la mejor coincidencia duplicada basada en similitud de metadatos
        """
        if not matches:
            return None

        best_match = matches[0]
        best_score = 0.0

        for match in matches:
            score = self._calculate_similarity_score(match, camera_info, gps_data)

            if score > best_score:
                best_score = score
                best_match = match

        best_match['confidence'] = best_score
        return best_match

    def _calculate_similarity_score(
        self,
        analysis: Dict,
        camera_info: Optional[Dict],
        gps_data: Optional[Dict]
    ) -> float:
        """
        Calculate similarity score between 0.0 and 1.0
        Calcular puntuación de similitud entre 0.0 y 1.0
        """
        score = 0.0
        factors = 0

        # Content is already identical (that's why we're here)
        score += 0.4  # Base score for identical content
        factors += 1

        # Camera similarity
        if camera_info and analysis.get('camera_make'):
            if (camera_info.get('camera_make') == analysis.get('camera_make') and
                camera_info.get('camera_model') == analysis.get('camera_model')):
                score += 0.3
            factors += 1

        # GPS similarity (within reasonable distance)
        if gps_data and gps_data.get('has_gps') and analysis.get('has_gps_data'):
            gps_distance = self._calculate_gps_distance(
                gps_data.get('latitude', 0),
                gps_data.get('longitude', 0),
                analysis.get('gps_latitude', 0),
                analysis.get('gps_longitude', 0)
            )

            # Consider same location if within 100 meters
            if gps_distance < 0.1:  # km
                score += 0.3
            factors += 1

        return score / factors if factors > 0 else 0.0

    def _calculate_gps_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two GPS points in kilometers
        Calcular distancia entre dos puntos GPS en kilómetros
        """
        import math

        # Simple haversine formula for small distances
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (math.sin(dlat/2) * math.sin(dlat/2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon/2) * math.sin(dlon/2))

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = 6371 * c  # Earth radius in km

        return distance

    def create_duplicate_reference(
        self,
        original_analysis_id: str,
        new_analysis_data: Dict,
        duplicate_info: Dict
    ) -> Dict[str, any]:
        """
        Create a reference to existing image instead of storing duplicate
        Crear referencia a imagen existente en lugar de almacenar duplicado
        """
        return {
            'analysis_id': new_analysis_data['analysis_id'],
            'storage_type': 'reference',
            'reference_analysis_id': original_analysis_id,
            'original_filename': new_analysis_data['original_filename'],
            'standardized_filename': new_analysis_data['standardized_filename'],
            'image_url': duplicate_info['reference_image_url'],
            'processed_image_url': duplicate_info['reference_image_url'].replace('original_', 'processed_'),
            'duplicate_confidence': duplicate_info['confidence'],
            'storage_saved_bytes': new_analysis_data.get('image_size_bytes', 0),
            'metadata': {
                'is_duplicate_reference': True,
                'duplicate_detected_at': datetime.utcnow().isoformat(),
                'duplicate_type': duplicate_info['duplicate_type']
            }
        }


def estimate_storage_savings(duplicate_analyses: List[Dict]) -> Dict[str, any]:
    """
    Estimate storage savings from deduplication
    Estimar ahorro de almacenamiento por deduplicación
    """
    total_original_size = sum(a.get('image_size_bytes', 0) for a in duplicate_analyses)
    total_duplicates = len([a for a in duplicate_analyses if a.get('is_duplicate_reference', False)])
    saved_bytes = sum(
        a.get('storage_saved_bytes', 0)
        for a in duplicate_analyses
        if a.get('is_duplicate_reference', False)
    )

    return {
        'total_analyses': len(duplicate_analyses),
        'unique_images': len(duplicate_analyses) - total_duplicates,
        'duplicate_references': total_duplicates,
        'storage_saved_bytes': saved_bytes,
        'storage_saved_mb': round(saved_bytes / (1024 * 1024), 2),
        'deduplication_rate': round(total_duplicates / len(duplicate_analyses) * 100, 1) if duplicate_analyses else 0
    }


# Global deduplication manager
_deduplication_manager = None


def get_deduplication_manager() -> ImageDeduplicationManager:
    """Get or create global deduplication manager instance"""
    global _deduplication_manager
    if _deduplication_manager is None:
        _deduplication_manager = ImageDeduplicationManager()
    return _deduplication_manager


# Convenience functions
def check_image_duplicate(image_data: bytes, existing_analyses: List[Dict], **metadata) -> Dict[str, any]:
    """
    Convenience function to check if image is duplicate
    Función de conveniencia para verificar si imagen es duplicada
    """
    signature = calculate_content_signature(image_data)
    manager = get_deduplication_manager()

    return manager.check_for_duplicates(
        image_hash=signature['sha256'],
        image_size=signature['size_bytes'],
        existing_analyses=existing_analyses,
        **metadata
    )


def should_store_image(duplicate_check_result: Dict[str, any]) -> bool:
    """
    Determine if image should be stored or referenced
    Determinar si imagen debe almacenarse o referenciarse
    """
    return duplicate_check_result.get('should_store_separately', True)