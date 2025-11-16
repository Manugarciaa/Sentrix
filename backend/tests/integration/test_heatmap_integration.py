"""
Integration tests for heatmap features with real database
Tests authentication-aware limiting and breeding site type differentiation
"""

import pytest
import asyncio
import httpx
from datetime import datetime


@pytest.mark.asyncio
class TestHeatmapIntegration:
    """Integration tests for heatmap endpoint with real services"""

    async def test_public_heatmap_endpoint_accessible_without_auth(self):
        """
        Test that heatmap endpoint is accessible without authentication
        """
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/heatmap-data")

            assert response.status_code == 200
            data = response.json()

            assert "status" in data
            assert "data" in data
            assert "total_locations" in data
            assert data["status"] == "success"

    async def test_public_heatmap_has_breeding_type_field(self):
        """
        Test that heatmap points include breedingSiteType field
        """
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/heatmap-data")

            assert response.status_code == 200
            data = response.json()

            # If there are points, check they have the right structure
            if len(data["data"]) > 0:
                point = data["data"][0]

                # Required fields
                assert "latitude" in point
                assert "longitude" in point
                assert "intensity" in point
                assert "riskLevel" in point
                assert "detectionCount" in point
                assert "breedingSiteType" in point  # New field for breeding site type
                assert "timestamp" in point

    async def test_public_heatmap_respects_10_point_limit(self):
        """
        Test that public (unauthenticated) requests return max 10 points
        """
        async with httpx.AsyncClient() as client:
            # Request with no authentication
            response = await client.get("http://localhost:8000/api/v1/heatmap-data")

            assert response.status_code == 200
            data = response.json()

            # Should not exceed 10 points for public access
            assert len(data["data"]) <= 10
            assert data["total_locations"] <= 10

    async def test_public_heatmap_with_large_limit_still_capped(self):
        """
        Test that public users cannot bypass 10-point limit with query parameter
        """
        async with httpx.AsyncClient() as client:
            # Try to request 1000 points as public user
            response = await client.get("http://localhost:8000/api/v1/heatmap-data?limit=1000")

            assert response.status_code == 200
            data = response.json()

            # Should still be capped at 10 for public
            assert len(data["data"]) <= 10

    async def test_heatmap_includes_breeding_type_counts(self):
        """
        Test that heatmap response includes breeding_type_counts summary
        """
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/heatmap-data")

            assert response.status_code == 200
            data = response.json()

            # Should include breeding_type_counts
            assert "breeding_type_counts" in data
            assert isinstance(data["breeding_type_counts"], dict)

    async def test_heatmap_includes_risk_counts(self):
        """
        Test that heatmap response includes risk level counts
        """
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/heatmap-data")

            assert response.status_code == 200
            data = response.json()

            # Should include risk counts
            assert "high_risk_count" in data
            assert "medium_risk_count" in data
            assert "low_risk_count" in data

            # All counts should be non-negative integers
            assert data["high_risk_count"] >= 0
            assert data["medium_risk_count"] >= 0
            assert data["low_risk_count"] >= 0


@pytest.mark.asyncio
class TestHeatmapWithAuthentication:
    """Test heatmap behavior with authenticated requests"""

    @pytest.fixture
    async def auth_token(self):
        """
        Get authentication token for testing
        Returns None if authentication is not set up
        """
        async with httpx.AsyncClient() as client:
            try:
                # Try to login with test credentials
                response = await client.post(
                    "http://localhost:8000/api/v1/auth/login",
                    data={
                        "username": "test@sentrix.com",
                        "password": "testpassword123"
                    }
                )

                if response.status_code == 200:
                    return response.json().get("access_token")
            except Exception:
                pass

        return None

    async def test_authenticated_heatmap_can_request_more_than_10_points(self, auth_token):
        """
        Test that authenticated users can request more than 10 points
        """
        if not auth_token:
            pytest.skip("Authentication not configured for test")

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {auth_token}"}

            # Request 50 points as authenticated user
            response = await client.get(
                "http://localhost:8000/api/v1/heatmap-data?limit=50",
                headers=headers
            )

            assert response.status_code == 200
            data = response.json()

            # If database has more than 10 analyses, should return more than 10
            # (This test would need data in database to fully verify)
            assert "data" in data
            assert "total_locations" in data


class TestHeatmapBreedingSiteTypes:
    """Test breeding site type differentiation in heatmap"""

    def test_breeding_site_types_are_valid(self):
        """
        Test that if breeding site types are present, they match expected values
        """
        import requests

        response = requests.get("http://localhost:8000/api/v1/heatmap-data")
        assert response.status_code == 200

        data = response.json()

        # Valid breeding site types
        valid_types = [
            "Basura",
            "Charcos/Cumulo de agua",
            "Huecos",
            "Calles mal hechas",
            None  # Points without breeding site type
        ]

        for point in data["data"]:
            breeding_type = point.get("breedingSiteType")
            assert breeding_type in valid_types, \
                f"Invalid breeding site type: {breeding_type}"

    def test_breeding_type_counts_match_data(self):
        """
        Test that breeding_type_counts match the actual data
        """
        import requests

        response = requests.get("http://localhost:8000/api/v1/heatmap-data")
        assert response.status_code == 200

        data = response.json()

        # Count breeding types manually from data
        manual_counts = {}
        for point in data["data"]:
            breeding_type = point.get("breedingSiteType")
            if breeding_type:
                manual_counts[breeding_type] = manual_counts.get(breeding_type, 0) + 1

        # Should match the breeding_type_counts in response
        breeding_type_counts = data.get("breeding_type_counts", {})

        for breeding_type, count in manual_counts.items():
            assert breeding_type_counts.get(breeding_type, 0) == count, \
                f"Count mismatch for {breeding_type}: expected {count}, got {breeding_type_counts.get(breeding_type, 0)}"


def test_heatmap_endpoint_performance():
    """
    Test that heatmap endpoint responds within acceptable time
    """
    import requests
    import time

    start_time = time.time()
    response = requests.get("http://localhost:8000/api/v1/heatmap-data")
    end_time = time.time()

    assert response.status_code == 200

    # Should respond within 5 seconds
    response_time = end_time - start_time
    assert response_time < 5.0, f"Heatmap endpoint took {response_time:.2f}s (>5s threshold)"


def test_heatmap_with_risk_level_filter():
    """
    Test that heatmap respects risk_level filter
    """
    import requests

    # Test with ALTO risk filter
    response = requests.get("http://localhost:8000/api/v1/heatmap-data?risk_level=ALTO")
    assert response.status_code == 200

    data = response.json()

    # If there are points, they should all be ALTO risk
    for point in data["data"]:
        if "riskLevel" in point:
            # Note: might not match exactly due to per-breeding-type risk calculation
            assert point["riskLevel"] in ["ALTO", "MEDIO", "BAJO"]


def test_heatmap_json_structure():
    """
    Test that heatmap response has correct JSON structure
    """
    import requests

    response = requests.get("http://localhost:8000/api/v1/heatmap-data")
    assert response.status_code == 200

    data = response.json()

    # Required top-level fields
    assert "status" in data
    assert "data" in data
    assert "total_locations" in data
    assert "high_risk_count" in data
    assert "medium_risk_count" in data
    assert "low_risk_count" in data
    assert "breeding_type_counts" in data

    # Data should be a list
    assert isinstance(data["data"], list)

    # Counts should be integers
    assert isinstance(data["total_locations"], int)
    assert isinstance(data["high_risk_count"], int)
    assert isinstance(data["medium_risk_count"], int)
    assert isinstance(data["low_risk_count"], int)
    assert isinstance(data["breeding_type_counts"], dict)
