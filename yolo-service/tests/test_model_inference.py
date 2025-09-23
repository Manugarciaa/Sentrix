"""
Test suite for YOLO model inference with trained model
Tests para inferencia del modelo YOLO entrenado
"""

import pytest
import os
import sys
import tempfile
import requests
from pathlib import Path

# Add project root and src to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.core.detector import detect_breeding_sites
from src.core.evaluator import assess_dengue_risk


class TestModelInference:
    """Test trained model inference capabilities"""

    @classmethod
    def setup_class(cls):
        """Set up test class with model and test image"""
        cls.model_path = "models/best.pt"
        cls.test_image = "test_images/imagen_test.jpg"

        # Verify model exists
        if not os.path.exists(cls.model_path):
            pytest.skip("Trained model not found - run training first")

        # Verify test image exists
        if not os.path.exists(cls.test_image):
            pytest.skip("Test image not found")

    def test_model_loads_successfully(self):
        """Test that trained model loads without errors"""
        from ultralytics import YOLO

        model = YOLO(self.model_path)
        assert model is not None
        assert hasattr(model, 'predict')

    def test_model_inference_on_test_image(self):
        """Test model inference on test image"""
        detections = detect_breeding_sites(
            model_path=self.model_path,
            source=self.test_image,
            conf_threshold=0.3,
            include_gps=True
        )

        # Model should return results (even if empty)
        assert isinstance(detections, list)

        # If detections found, verify structure
        if detections:
            detection = detections[0]
            required_keys = ['class', 'class_id', 'confidence', 'polygon', 'mask_area', 'risk_level']
            for key in required_keys:
                assert key in detection

            # Verify class is one of our trained classes (allow both singular and plural forms)
            valid_classes = ["Basura", "Calles mal hechas", "Charcos/Cumulos de agua", "Charcos/Cumulo de agua", "Huecos"]
            assert detection['class'] in valid_classes

            # Verify confidence is in valid range
            assert 0.0 <= detection['confidence'] <= 1.0

            # Verify risk level is valid
            assert detection['risk_level'] in ["ALTO", "MEDIO", "BAJO"]

    def test_model_different_confidence_thresholds(self):
        """Test model with different confidence thresholds"""
        thresholds = [0.1, 0.3, 0.5, 0.7, 0.9]
        previous_count = float('inf')

        for threshold in thresholds:
            detections = detect_breeding_sites(
                model_path=self.model_path,
                source=self.test_image,
                conf_threshold=threshold,
                include_gps=False
            )

            # Higher threshold should result in fewer or equal detections
            current_count = len(detections)
            assert current_count <= previous_count
            previous_count = current_count

    def test_risk_assessment_integration(self):
        """Test risk assessment with model detections"""
        detections = detect_breeding_sites(
            model_path=self.model_path,
            source=self.test_image,
            conf_threshold=0.3,
            include_gps=False
        )

        risk_assessment = assess_dengue_risk(detections)

        # Verify risk assessment structure
        required_keys = ['overall_risk', 'risk_score', 'level', 'total_detections', 'recommendations']
        for key in required_keys:
            assert key in risk_assessment

        # Verify risk level is valid
        assert risk_assessment['level'] in ["ALTO", "MEDIO", "BAJO", "MÍNIMO"]

        # Verify risk score is numeric and in range
        assert isinstance(risk_assessment['risk_score'], (int, float))
        assert 0.0 <= risk_assessment['risk_score'] <= 1.0

        # Verify total detections matches
        assert risk_assessment['total_detections'] == len(detections)

    def test_gps_metadata_extraction(self):
        """Test GPS metadata extraction functionality"""
        detections = detect_breeding_sites(
            model_path=self.model_path,
            source=self.test_image,
            conf_threshold=0.5,
            include_gps=True
        )

        # Check that location data structure is present
        if detections:
            detection = detections[0]
            assert 'location' in detection
            location = detection['location']

            # Verify location structure
            assert 'has_location' in location
            assert isinstance(location['has_location'], bool)

            if location['has_location']:
                assert 'latitude' in location
                assert 'longitude' in location
                assert 'coordinates' in location

    def test_model_performance_metrics(self):
        """Test model performance on test image"""
        import time

        start_time = time.time()
        detections = detect_breeding_sites(
            model_path=self.model_path,
            source=self.test_image,
            conf_threshold=0.5,
            include_gps=True
        )
        end_time = time.time()

        inference_time = end_time - start_time

        # Model should complete inference within reasonable time (< 5 seconds)
        assert inference_time < 5.0, f"Inference took too long: {inference_time:.2f}s"

        print(f"Inference time: {inference_time:.3f}s")
        print(f"Detections found: {len(detections)}")

    def test_batch_processing(self):
        """Test batch processing with multiple images"""
        # Create temporary copies of test image for batch test
        temp_dir = tempfile.mkdtemp()
        test_images = []

        try:
            # Copy test image multiple times
            for i in range(3):
                temp_path = os.path.join(temp_dir, f"test_image_{i}.jpg")
                import shutil
                shutil.copy2(self.test_image, temp_path)
                test_images.append(temp_path)

            # Test batch processing
            detections = detect_breeding_sites(
                model_path=self.model_path,
                source=temp_dir,
                conf_threshold=0.5,
                include_gps=False
            )

            # Should process all images in directory
            assert isinstance(detections, list)

        finally:
            # Clean up temporary files
            import shutil
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])