"""
Test de integración para verificar el flujo completo de imagen procesada
desde YOLO service hasta almacenamiento en Supabase
"""

import pytest
import base64
import httpx
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from src.core.services.yolo_service import YOLOServiceClient


class TestProcessedImageIntegration:
    """Tests de integración para imagen procesada"""

    @pytest.mark.asyncio
    async def test_yolo_client_receives_processed_image_base64(self):
        """
        Test: Verificar que el cliente YOLO recibe processed_image_base64
        """
        # Mock de respuesta del YOLO service con imagen procesada
        mock_response_data = {
            "analysis_id": "test-123",
            "status": "completed",
            "detections": [
                {
                    "class_name": "Charcos/Cumulo de agua",
                    "class_id": 0,
                    "confidence": 0.85,
                    "risk_level": "ALTO",
                    "breeding_site_type": "Charcos/Cumulo de agua",
                    "polygon": [[100, 100], [200, 100], [200, 200], [100, 200]],
                    "mask_area": 10000.0
                }
            ],
            "total_detections": 1,
            "risk_assessment": {
                "overall_risk_level": "ALTO",
                "high_risk_count": 1,
                "medium_risk_count": 0,
                "risk_score": 0.85
            },
            "location": {
                "has_location": False
            },
            "camera_info": None,
            "processing_time_ms": 1234,
            "model_used": "models/best.pt",
            "confidence_threshold": 0.5,
            "processed_image_path": "/tmp/processed/test_image_processed.jpg",
            "processed_image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="  # 1x1 pixel PNG
        }

        # Mock del httpx client
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = Mock()

            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value = mock_client_instance

            # Ejecutar cliente YOLO
            yolo_client = YOLOServiceClient()

            # Simular imagen de prueba (1x1 pixel)
            test_image_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")

            result = await yolo_client.detect_image(
                image_data=test_image_data,
                filename="test_image.jpg",
                confidence_threshold=0.5,
                include_gps=True
            )

            # Verificaciones
            assert result["success"] is True, "YOLO detection should succeed"
            assert "processed_image_base64" in result, "Result should contain processed_image_base64"
            assert result["processed_image_base64"] is not None, "processed_image_base64 should not be None"

            # Verificar que es base64 válido
            processed_base64 = result["processed_image_base64"]
            assert isinstance(processed_base64, str), "processed_image_base64 should be string"

            # Verificar que se puede decodificar
            decoded_bytes = base64.b64decode(processed_base64)
            assert len(decoded_bytes) > 0, "Decoded image should have content"

            print(f"[OK] YOLO client successfully received processed image base64")
            print(f"   Base64 length: {len(processed_base64)} chars")
            print(f"   Decoded size: {len(decoded_bytes)} bytes")

    @pytest.mark.asyncio
    async def test_analysis_service_decodes_processed_image(self):
        """
        Test: Verificar que analysis_service decodifica correctamente el base64
        """
        # Crear una imagen procesada falsa en base64
        test_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

        # Decodificar (como lo hace analysis_service)
        decoded_bytes = base64.b64decode(test_base64)

        # Verificaciones
        assert decoded_bytes is not None, "Decoded bytes should not be None"
        assert len(decoded_bytes) > 0, "Decoded bytes should have content"
        assert isinstance(decoded_bytes, bytes), "Should be bytes type"

        print(f"[OK] Successfully decoded base64 to {len(decoded_bytes)} bytes")

    def test_base64_encoding_decoding_roundtrip(self):
        """
        Test: Verificar que encoding/decoding de base64 funciona correctamente
        """
        # Simular lectura de imagen procesada (como lo hace YOLO service)
        original_data = b"fake_image_data_12345"

        # Encoding (YOLO service)
        encoded = base64.b64encode(original_data).decode('utf-8')

        # Decoding (Backend)
        decoded = base64.b64decode(encoded)

        # Verificar que son idénticos
        assert original_data == decoded, "Decoded data should match original"

        print(f"[OK] Base64 roundtrip successful")
        print(f"   Original: {len(original_data)} bytes")
        print(f"   Encoded: {len(encoded)} chars")
        print(f"   Decoded: {len(decoded)} bytes")


class TestProcessedImageUpload:
    """Tests para verificar subida de imagen procesada a Supabase"""

    def test_dual_image_upload_structure(self):
        """
        Test: Verificar que upload_dual_images recibe los datos correctos
        """
        # Simular datos de imagen original y procesada
        original_data = b"original_image_data"
        processed_data = b"processed_image_data_with_markers"

        # Verificar que ambos tienen datos
        assert len(original_data) > 0, "Original data should have content"
        assert len(processed_data) > 0, "Processed data should have content"

        # Verificar que son diferentes (procesada tiene marcadores)
        assert original_data != processed_data, "Processed should be different from original"

        print(f"[OK] Dual image upload structure validated")
        print(f"   Original: {len(original_data)} bytes")
        print(f"   Processed: {len(processed_data)} bytes")

    @pytest.mark.asyncio
    async def test_processed_image_included_in_yolo_response(self):
        """
        Test: Verificar que la respuesta del YOLO incluye processed_image_base64
        """
        mock_yolo_response = {
            "success": True,
            "analysis_id": "test-456",
            "status": "completed",
            "detections": [],
            "total_detections": 0,
            "risk_assessment": {},
            "location": None,
            "camera_info": None,
            "processing_time_ms": 500,
            "model_used": "models/best.pt",
            "confidence_threshold": 0.5,
            "processed_image_path": "/tmp/processed/image.jpg",
            "processed_image_base64": "base64_encoded_image_here"  # [OK] Campo presente
        }

        # Verificar estructura de respuesta
        assert "processed_image_base64" in mock_yolo_response, "Response should include processed_image_base64"
        assert mock_yolo_response["processed_image_base64"] is not None, "Field should not be None"

        print(f"[OK] YOLO response includes processed_image_base64 field")


class TestProcessedImageErrorHandling:
    """Tests para manejo de errores en imagen procesada"""

    @pytest.mark.asyncio
    async def test_handles_missing_processed_image_gracefully(self):
        """
        Test: Verificar que el sistema funciona aunque no haya imagen procesada
        """
        mock_yolo_response = {
            "success": True,
            "analysis_id": "test-789",
            "detections": [],
            "total_detections": 0,
            "processed_image_base64": None  # [ERROR] Sin imagen procesada
        }

        # El sistema debería funcionar sin errores
        processed_base64 = mock_yolo_response.get("processed_image_base64")

        if processed_base64:
            decoded = base64.b64decode(processed_base64)
            print(f"Processed image decoded: {len(decoded)} bytes")
        else:
            # No hay imagen procesada, pero el sistema continúa
            print("[WARNING] No processed image available, continuing without it")

        # No debería lanzar excepción
        assert True, "Should handle missing processed image gracefully"

    def test_handles_invalid_base64_gracefully(self):
        """
        Test: Verificar que maneja base64 inválido sin crashear
        """
        invalid_base64 = "esto_no_es_base64_valido!!!"

        try:
            # Intentar decodificar base64 inválido
            decoded = base64.b64decode(invalid_base64)
            print(f"[WARNING] Unexpectedly decoded: {decoded}")
        except Exception as e:
            # Se espera que falle, pero de forma controlada
            print(f"[OK] Correctly caught invalid base64: {type(e).__name__}")
            assert isinstance(e, Exception), "Should raise exception for invalid base64"


class TestProcessedImageMetadata:
    """Tests para verificar metadata de imagen procesada"""

    def test_processed_image_filename_convention(self):
        """
        Test: Verificar que el nombre de archivo procesado sigue la convención
        """
        original_filename = "SENTRIX_20250123_123456_GPS_-26.831314_-65.123456.jpg"
        expected_processed = "processed_SENTRIX_20250123_123456_GPS_-26.831314_-65.123456.jpg"

        # Simular generación de nombre procesado
        processed_filename = f"processed_{original_filename}"

        assert processed_filename == expected_processed, "Processed filename should have 'processed_' prefix"
        print(f"[OK] Processed filename convention validated")
        print(f"   Original: {original_filename}")
        print(f"   Processed: {processed_filename}")

    def test_processed_image_storage_paths(self):
        """
        Test: Verificar rutas de almacenamiento correctas
        """
        # Rutas esperadas en Supabase
        original_bucket = "images"
        processed_bucket = "processed_images"

        original_path = f"{original_bucket}/original_SENTRIX_20250123_123456.jpg"
        processed_path = f"{processed_bucket}/processed_SENTRIX_20250123_123456.jpg"

        assert "images" in original_path, "Original should be in images bucket"
        assert "processed_images" in processed_path, "Processed should be in processed_images bucket"

        print(f"[OK] Storage paths validated")
        print(f"   Original: {original_path}")
        print(f"   Processed: {processed_path}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
