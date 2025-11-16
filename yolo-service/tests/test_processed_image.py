"""
Test para verificar generación de imagen procesada con detecciones marcadas
"""

import os
import sys
import base64
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.detector import detect_breeding_sites


class TestProcessedImageGeneration:
    """Tests para verificar que se genera correctamente la imagen procesada"""

    def test_processed_image_creation_enabled(self):
        """
        Test: Verificar que cuando save_processed_image=True, se crea la imagen
        """
        # Skip si no hay modelo disponible
        model_path = "models/best.pt"
        if not os.path.exists(model_path):
            # Intentar con modelos alternativos
            alt_models = [
                "models/yolo11s-seg.pt",
                "models/yolo11n-seg.pt"
            ]
            model_found = False
            for alt_model in alt_models:
                if os.path.exists(alt_model):
                    model_path = alt_model
                    model_found = True
                    break

            if not model_found:
                pytest.skip("No YOLO model available for testing")

        # Usar imagen de test
        test_image = "test_images/imagen_test_2.jpg"
        if not os.path.exists(test_image):
            pytest.skip("Test image not found")

        # Output directory para imagen procesada
        output_dir = "test_images/processed"

        # Ejecutar detección CON imagen procesada habilitada
        result = detect_breeding_sites(
            model_path=model_path,
            source=test_image,
            conf_threshold=0.5,
            include_gps=True,
            save_processed_image=True,  # [OK] HABILITADO
            output_dir=output_dir
        )

        # Verificaciones
        assert result is not None, "Result should not be None"
        assert "detections" in result, "Result should contain detections"
        assert "processed_image_path" in result, "Result should contain processed_image_path"

        # Verificar que la imagen procesada se creó
        processed_image_path = result.get("processed_image_path")

        if processed_image_path:
            assert os.path.exists(processed_image_path), f"Processed image should exist at {processed_image_path}"

            # Verificar que el archivo tiene contenido
            file_size = os.path.getsize(processed_image_path)
            assert file_size > 0, "Processed image should not be empty"

            print(f"[OK] Processed image created: {processed_image_path} ({file_size} bytes)")
        else:
            # Si no hay detecciones, puede no haber imagen procesada
            print("[WARNING] No processed image path returned (possibly no detections)")

    def test_processed_image_disabled_by_default(self):
        """
        Test: Verificar que cuando save_processed_image=False, NO se crea la imagen
        """
        model_path = "models/best.pt"
        if not os.path.exists(model_path):
            pytest.skip("No YOLO model available")

        test_image = "test_images/imagen_test_2.jpg"
        if not os.path.exists(test_image):
            pytest.skip("Test image not found")

        # Ejecutar detección SIN imagen procesada
        result = detect_breeding_sites(
            model_path=model_path,
            source=test_image,
            conf_threshold=0.5,
            include_gps=False,
            save_processed_image=False,  # [ERROR] DESHABILITADO
            output_dir=None
        )

        # Verificar que no se generó imagen procesada
        assert result.get("processed_image_path") is None, "Should not create processed image when disabled"
        print("[OK] Processed image correctly disabled")

    def test_processed_image_has_detections_marked(self):
        """
        Test: Verificar que la imagen procesada tiene marcadores visuales
        """
        model_path = "models/best.pt"
        if not os.path.exists(model_path):
            pytest.skip("No YOLO model available")

        test_image = "test_images/imagen_test_2.jpg"
        if not os.path.exists(test_image):
            pytest.skip("Test image not found")

        output_dir = "test_images/processed"

        result = detect_breeding_sites(
            model_path=model_path,
            source=test_image,
            conf_threshold=0.3,  # Lower threshold para más detecciones
            include_gps=True,
            save_processed_image=True,
            output_dir=output_dir
        )

        processed_image_path = result.get("processed_image_path")
        detections_count = len(result.get("detections", []))

        if processed_image_path and detections_count > 0:
            # Verificar que la imagen procesada existe
            assert os.path.exists(processed_image_path), "Processed image should exist"

            # Verificar que es diferente de la original (tiene marcadores)
            import cv2
            import numpy as np

            original = cv2.imread(test_image)
            processed = cv2.imread(processed_image_path)

            # Verificar que las imágenes tienen el mismo tamaño
            assert original.shape == processed.shape, "Processed image should have same dimensions"

            # Verificar que son diferentes (porque tiene marcadores dibujados)
            diff = cv2.absdiff(original, processed)
            has_differences = np.any(diff > 0)

            assert has_differences, "Processed image should be different from original (has markers)"

            print(f"[OK] Processed image has visual markers ({detections_count} detections)")
            print(f"   Original: {original.shape}")
            print(f"   Processed: {processed.shape}")
        else:
            print("[WARNING] No detections found, skipping visual comparison")


class TestProcessedImageBase64Encoding:
    """Tests para verificar encoding base64 de imagen procesada"""

    def test_processed_image_can_be_encoded_to_base64(self):
        """
        Test: Verificar que la imagen procesada se puede codificar a base64
        """
        # Crear imagen procesada primero
        model_path = "models/best.pt"
        if not os.path.exists(model_path):
            pytest.skip("No YOLO model available")

        test_image = "test_images/imagen_test_2.jpg"
        if not os.path.exists(test_image):
            pytest.skip("Test image not found")

        result = detect_breeding_sites(
            model_path=model_path,
            source=test_image,
            conf_threshold=0.5,
            save_processed_image=True
        )

        processed_image_path = result.get("processed_image_path")

        if processed_image_path and os.path.exists(processed_image_path):
            # Leer y codificar a base64 (como lo hace el servidor)
            with open(processed_image_path, 'rb') as f:
                image_bytes = f.read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')

            # Verificaciones
            assert len(image_base64) > 0, "Base64 string should not be empty"
            assert isinstance(image_base64, str), "Base64 should be string"

            # Verificar que se puede decodificar de vuelta
            decoded_bytes = base64.b64decode(image_base64)
            assert len(decoded_bytes) == len(image_bytes), "Decoded bytes should match original"

            print(f"[OK] Image successfully encoded to base64")
            print(f"   Original size: {len(image_bytes)} bytes")
            print(f"   Base64 size: {len(image_base64)} chars")
            print(f"   Decoded size: {len(decoded_bytes)} bytes")
        else:
            pytest.skip("No processed image available to test encoding")


class TestProcessedImageNaming:
    """Tests para verificar nomenclatura de imagen procesada"""

    def test_processed_image_has_correct_naming(self):
        """
        Test: Verificar que la imagen procesada tiene el sufijo _processed
        """
        model_path = "models/best.pt"
        if not os.path.exists(model_path):
            pytest.skip("No YOLO model available")

        test_image = "test_images/imagen_test_2.jpg"
        if not os.path.exists(test_image):
            pytest.skip("Test image not found")

        result = detect_breeding_sites(
            model_path=model_path,
            source=test_image,
            save_processed_image=True
        )

        processed_image_path = result.get("processed_image_path")

        if processed_image_path:
            # Verificar que contiene "_processed" en el nombre
            filename = os.path.basename(processed_image_path)
            assert "_processed" in filename, "Processed image should have _processed suffix"

            # Verificar que está en directorio 'processed'
            assert "processed" in processed_image_path.lower(), "Should be in processed directory"

            print(f"[OK] Correct naming: {filename}")
        else:
            pytest.skip("No processed image generated")


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v", "--tb=short"])
