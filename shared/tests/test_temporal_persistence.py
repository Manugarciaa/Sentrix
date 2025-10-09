"""
Tests for Temporal Persistence Module
Tests para el Módulo de Persistencia Temporal

Tests for breeding site detection validity calculation and expiration management.
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
parent_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, parent_dir)

# Import from shared package
import temporal_persistence as tp
from temporal_persistence import (
    PersistenceTypeEnum,
    WeatherConditionEnum,
    get_persistence_type,
    calculate_validity_period,
    calculate_expiration_date,
    is_detection_expired,
    get_remaining_validity_days,
    get_validity_status,
    should_send_expiration_alert,
    get_current_season_weather,
    get_detection_metadata,
    BREEDING_SITE_PERSISTENCE,
    DEFAULT_VALIDITY_DAYS
)
import data_models
from data_models import BreedingSiteTypeEnum, DetectionRiskEnum


class TestPersistenceClassification:
    """Test persistence type classification for breeding sites"""

    def test_charcos_is_transient(self):
        """Charcos should be classified as TRANSIENT"""
        persistence = get_persistence_type(BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA)
        assert persistence == PersistenceTypeEnum.TRANSIENT

    def test_basura_is_short_term(self):
        """Basura should be classified as SHORT_TERM"""
        persistence = get_persistence_type(BreedingSiteTypeEnum.BASURA)
        assert persistence == PersistenceTypeEnum.SHORT_TERM

    def test_huecos_is_medium_term(self):
        """Huecos should be classified as MEDIUM_TERM"""
        persistence = get_persistence_type(BreedingSiteTypeEnum.HUECOS)
        assert persistence == PersistenceTypeEnum.MEDIUM_TERM

    def test_calles_is_long_term(self):
        """Calles mal hechas should be classified as LONG_TERM"""
        persistence = get_persistence_type(BreedingSiteTypeEnum.CALLES_MAL_HECHAS)
        assert persistence == PersistenceTypeEnum.LONG_TERM

    def test_default_persistence_for_unknown(self):
        """Unknown breeding sites should default to MEDIUM_TERM"""
        # Create a mock enum value
        class MockBreedingSite:
            pass

        persistence = get_persistence_type(MockBreedingSite())
        assert persistence == PersistenceTypeEnum.MEDIUM_TERM


class TestValidityCalculation:
    """Test validity period calculation"""

    def test_base_validity_for_transient(self):
        """Transient sites should have short base validity"""
        days = calculate_validity_period(
            breeding_site=BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA,
            risk_level=DetectionRiskEnum.MEDIO,
            confidence=0.8,
            is_validated=False
        )
        # Should be around 2 days (base for TRANSIENT)
        assert 1 <= days <= 4

    def test_base_validity_for_long_term(self):
        """Long-term sites should have extended base validity"""
        days = calculate_validity_period(
            breeding_site=BreedingSiteTypeEnum.CALLES_MAL_HECHAS,
            risk_level=DetectionRiskEnum.MEDIO,
            confidence=0.8,
            is_validated=False
        )
        # Should be around 180 days (base for LONG_TERM)
        assert 150 <= days <= 220

    def test_high_risk_extends_validity(self):
        """High risk detections should have extended validity"""
        days_high = calculate_validity_period(
            breeding_site=BreedingSiteTypeEnum.HUECOS,
            risk_level=DetectionRiskEnum.ALTO,
            confidence=0.8,
            is_validated=False
        )

        days_medium = calculate_validity_period(
            breeding_site=BreedingSiteTypeEnum.HUECOS,
            risk_level=DetectionRiskEnum.MEDIO,
            confidence=0.8,
            is_validated=False
        )

        assert days_high > days_medium

    def test_weather_affects_transient_sites(self):
        """Weather should affect validity of transient sites"""
        days_sunny = calculate_validity_period(
            breeding_site=BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA,
            risk_level=DetectionRiskEnum.MEDIO,
            weather_condition=WeatherConditionEnum.SUNNY,
            confidence=0.8,
            is_validated=False
        )

        days_rainy = calculate_validity_period(
            breeding_site=BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA,
            risk_level=DetectionRiskEnum.MEDIO,
            weather_condition=WeatherConditionEnum.RAINY,
            confidence=0.8,
            is_validated=False
        )

        # Rainy should extend validity more than sunny
        assert days_rainy > days_sunny

    def test_weather_does_not_affect_long_term_sites(self):
        """Weather should not significantly affect long-term sites"""
        days_sunny = calculate_validity_period(
            breeding_site=BreedingSiteTypeEnum.CALLES_MAL_HECHAS,
            risk_level=DetectionRiskEnum.MEDIO,
            weather_condition=WeatherConditionEnum.SUNNY,
            confidence=0.8,
            is_validated=False
        )

        days_rainy = calculate_validity_period(
            breeding_site=BreedingSiteTypeEnum.CALLES_MAL_HECHAS,
            risk_level=DetectionRiskEnum.MEDIO,
            weather_condition=WeatherConditionEnum.RAINY,
            confidence=0.8,
            is_validated=False
        )

        # Should be the same (weather doesn't affect structural issues)
        assert days_sunny == days_rainy

    def test_low_confidence_reduces_validity(self):
        """Low confidence should reduce validity period"""
        days_high_conf = calculate_validity_period(
            breeding_site=BreedingSiteTypeEnum.HUECOS,
            risk_level=DetectionRiskEnum.MEDIO,
            confidence=0.95,
            is_validated=False
        )

        days_low_conf = calculate_validity_period(
            breeding_site=BreedingSiteTypeEnum.HUECOS,
            risk_level=DetectionRiskEnum.MEDIO,
            confidence=0.65,
            is_validated=False
        )

        assert days_low_conf < days_high_conf

    def test_validation_extends_validity(self):
        """Validated detections should have extended validity"""
        days_not_validated = calculate_validity_period(
            breeding_site=BreedingSiteTypeEnum.HUECOS,
            risk_level=DetectionRiskEnum.MEDIO,
            confidence=0.8,
            is_validated=False
        )

        days_validated = calculate_validity_period(
            breeding_site=BreedingSiteTypeEnum.HUECOS,
            risk_level=DetectionRiskEnum.MEDIO,
            confidence=0.8,
            is_validated=True
        )

        assert days_validated > days_not_validated

    def test_minimum_validity_is_one_day(self):
        """Validity should never be less than 1 day"""
        days = calculate_validity_period(
            breeding_site=BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA,
            risk_level=DetectionRiskEnum.MINIMO,
            weather_condition=WeatherConditionEnum.SUNNY,
            confidence=0.5,
            is_validated=False
        )

        assert days >= 1


class TestExpirationCalculation:
    """Test expiration date calculation"""

    def test_expiration_date_is_future(self):
        """Expiration date should be in the future"""
        detection_date = datetime.now()
        expires_at = calculate_expiration_date(
            detection_date=detection_date,
            breeding_site=BreedingSiteTypeEnum.HUECOS,
            risk_level=DetectionRiskEnum.MEDIO,
            confidence=0.8,
            is_validated=False
        )

        assert expires_at > detection_date

    def test_expiration_date_matches_validity_period(self):
        """Expiration date should match calculated validity period"""
        detection_date = datetime.now()

        validity_days = calculate_validity_period(
            breeding_site=BreedingSiteTypeEnum.HUECOS,
            risk_level=DetectionRiskEnum.MEDIO,
            confidence=0.8,
            is_validated=False
        )

        expires_at = calculate_expiration_date(
            detection_date=detection_date,
            breeding_site=BreedingSiteTypeEnum.HUECOS,
            risk_level=DetectionRiskEnum.MEDIO,
            confidence=0.8,
            is_validated=False
        )

        expected_expiration = detection_date + timedelta(days=validity_days)

        # Allow 1 second tolerance for execution time
        assert abs((expires_at - expected_expiration).total_seconds()) < 1


class TestExpirationChecking:
    """Test expiration detection"""

    def test_future_date_is_not_expired(self):
        """Future expiration dates should not be expired"""
        expires_at = datetime.now() + timedelta(days=7)
        assert not is_detection_expired(expires_at)

    def test_past_date_is_expired(self):
        """Past expiration dates should be expired"""
        expires_at = datetime.now() - timedelta(days=1)
        assert is_detection_expired(expires_at)

    def test_current_time_is_expired(self):
        """Current time should be considered expired"""
        expires_at = datetime.now()
        # Small delay to ensure it's in the past
        import time
        time.sleep(0.01)
        assert is_detection_expired(expires_at)


class TestRemainingDays:
    """Test remaining validity days calculation"""

    def test_remaining_days_for_future_expiration(self):
        """Should correctly calculate remaining days"""
        expires_at = datetime.now() + timedelta(days=7)
        remaining = get_remaining_validity_days(expires_at)

        # Should be 6 or 7 depending on current time
        assert 6 <= remaining <= 7

    def test_remaining_days_for_expired_is_zero(self):
        """Expired detections should have 0 remaining days"""
        expires_at = datetime.now() - timedelta(days=1)
        remaining = get_remaining_validity_days(expires_at)

        assert remaining == 0


class TestValidityStatus:
    """Test validity status determination"""

    def test_valid_status_for_long_validity(self):
        """Long validity should return VALID status"""
        expires_at = datetime.now() + timedelta(days=10)
        status = get_validity_status(expires_at)

        assert status['status'] == 'VALID'
        assert not status['is_expired']
        assert not status['is_expiring_soon']
        assert status['validity_percentage'] == 100

    def test_expiring_soon_status(self):
        """Detections expiring within 1 day should be marked as expiring soon"""
        expires_at = datetime.now() + timedelta(hours=12)
        status = get_validity_status(expires_at)

        assert status['is_expiring_soon']
        assert not status['is_expired']
        assert status['requires_revalidation']

    def test_expired_status(self):
        """Expired detections should return EXPIRED status"""
        expires_at = datetime.now() - timedelta(days=1)
        status = get_validity_status(expires_at)

        assert status['status'] == 'EXPIRED'
        assert status['is_expired']
        assert status['validity_percentage'] == 0
        assert status['requires_revalidation']


class TestExpirationAlerts:
    """Test expiration alert logic"""

    def test_should_alert_one_day_before(self):
        """Should send alert 1 day before expiration"""
        expires_at = datetime.now() + timedelta(days=1, hours=1)
        should_alert = should_send_expiration_alert(expires_at)

        assert should_alert

    def test_should_not_alert_if_already_expired(self):
        """Should not send alert if already expired"""
        expires_at = datetime.now() - timedelta(days=1)
        should_alert = should_send_expiration_alert(expires_at)

        assert not should_alert

    def test_should_not_alert_if_recently_sent(self):
        """Should not spam alerts if one was recently sent"""
        expires_at = datetime.now() + timedelta(days=1, hours=1)
        last_alert = datetime.now() - timedelta(hours=1)

        should_alert = should_send_expiration_alert(
            expires_at,
            last_alert_sent=last_alert
        )

        assert not should_alert

    def test_should_alert_if_last_alert_was_long_ago(self):
        """Should send alert if last one was more than 24h ago"""
        expires_at = datetime.now() + timedelta(days=1, hours=1)
        last_alert = datetime.now() - timedelta(days=2)

        should_alert = should_send_expiration_alert(
            expires_at,
            last_alert_sent=last_alert
        )

        assert should_alert


class TestSeasonDetection:
    """Test Argentina season detection"""

    def test_summer_months_are_wet_season(self):
        """December, January, February should be wet season"""
        assert get_current_season_weather(12) == WeatherConditionEnum.WET_SEASON
        assert get_current_season_weather(1) == WeatherConditionEnum.WET_SEASON
        assert get_current_season_weather(2) == WeatherConditionEnum.WET_SEASON

    def test_winter_months_are_dry_season(self):
        """June, July, August should be dry season"""
        assert get_current_season_weather(6) == WeatherConditionEnum.DRY_SEASON
        assert get_current_season_weather(7) == WeatherConditionEnum.DRY_SEASON
        assert get_current_season_weather(8) == WeatherConditionEnum.DRY_SEASON

    def test_spring_fall_are_moderate(self):
        """Spring and fall should be moderate (CLOUDY)"""
        assert get_current_season_weather(3) == WeatherConditionEnum.CLOUDY  # March
        assert get_current_season_weather(9) == WeatherConditionEnum.CLOUDY  # September


class TestDetectionMetadata:
    """Test detection metadata generation"""

    def test_metadata_includes_all_fields(self):
        """Metadata should include all expected fields"""
        metadata = get_detection_metadata(
            breeding_site=BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA,
            risk_level=DetectionRiskEnum.ALTO
        )

        assert 'breeding_site' in metadata
        assert 'risk_level' in metadata
        assert 'persistence_type' in metadata
        assert 'base_validity_days' in metadata
        assert 'is_weather_dependent' in metadata
        assert 'typical_lifespan' in metadata
        assert 'requires_frequent_monitoring' in metadata
        assert 'requires_structural_intervention' in metadata

    def test_transient_requires_frequent_monitoring(self):
        """Transient sites should require frequent monitoring"""
        metadata = get_detection_metadata(
            breeding_site=BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA,
            risk_level=DetectionRiskEnum.MEDIO
        )

        assert metadata['requires_frequent_monitoring']

    def test_long_term_requires_structural_intervention(self):
        """Long-term sites should require structural intervention"""
        metadata = get_detection_metadata(
            breeding_site=BreedingSiteTypeEnum.CALLES_MAL_HECHAS,
            risk_level=DetectionRiskEnum.MEDIO
        )

        assert metadata['requires_structural_intervention']


class TestDefaultValues:
    """Test default validity values are reasonable"""

    def test_all_persistence_types_have_defaults(self):
        """All persistence types should have default validity values"""
        for persistence_type in PersistenceTypeEnum:
            assert persistence_type in DEFAULT_VALIDITY_DAYS

    def test_validity_increases_with_persistence(self):
        """Validity should increase with persistence type"""
        transient = DEFAULT_VALIDITY_DAYS[PersistenceTypeEnum.TRANSIENT]
        short_term = DEFAULT_VALIDITY_DAYS[PersistenceTypeEnum.SHORT_TERM]
        medium_term = DEFAULT_VALIDITY_DAYS[PersistenceTypeEnum.MEDIUM_TERM]
        long_term = DEFAULT_VALIDITY_DAYS[PersistenceTypeEnum.LONG_TERM]
        permanent = DEFAULT_VALIDITY_DAYS[PersistenceTypeEnum.PERMANENT]

        assert transient < short_term < medium_term < long_term < permanent


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
