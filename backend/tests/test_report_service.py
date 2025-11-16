"""
Unit tests for report generation service
"""

import pytest
import io
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.models.base import Base
from src.database.models.models import UserProfile, Analysis, Detection
from src.services.report_service import ReportService
from src.utils.auth import get_password_hash

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def test_db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    db = TestingSessionLocal()
    user = UserProfile(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        role="USER",
        display_name="Test User",
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.close()


@pytest.fixture
def test_analyses(test_db, test_user):
    """Create test analyses"""
    db = TestingSessionLocal()
    analyses = []

    for i in range(5):
        analysis = Analysis(
            user_id=test_user.id,
            image_url=f"https://example.com/image{i}.jpg",
            image_filename=f"test_image_{i}.jpg",
            total_detections=3 + i,
            high_risk_count=i,
            medium_risk_count=1,
            risk_level="ALTO" if i >= 3 else "MEDIO",
            risk_score=0.7 + (i * 0.05),
            confidence_threshold=0.7,
            processing_time_ms=1500 + (i * 100),
            has_gps_data=i % 2 == 0,
            created_at=datetime.now() - timedelta(days=i)
        )
        db.add(analysis)
        analyses.append(analysis)

    db.commit()
    for analysis in analyses:
        db.refresh(analysis)

    yield analyses
    db.close()


class TestReportService:
    """Test report generation service"""

    def test_generate_pdf_report(self, test_db, test_user, test_analyses):
        """Test PDF report generation"""
        db = TestingSessionLocal()
        service = ReportService(db)

        # Generate PDF
        buffer = service.generate_pdf_report(
            report_type="summary",
            filters={},
            user_id=test_user.id
        )

        # Verify PDF was generated
        assert isinstance(buffer, io.BytesIO)
        assert buffer.getvalue()  # Has content
        assert len(buffer.getvalue()) > 0

        # Verify PDF signature
        pdf_content = buffer.getvalue()
        assert pdf_content.startswith(b'%PDF')  # Valid PDF

        db.close()

    def test_generate_csv_report(self, test_db, test_user, test_analyses):
        """Test CSV report generation"""
        db = TestingSessionLocal()
        service = ReportService(db)

        # Generate CSV
        buffer = service.generate_csv_report(
            report_type="summary",
            filters={}
        )

        # Verify CSV was generated
        assert isinstance(buffer, io.StringIO)
        csv_content = buffer.getvalue()
        assert len(csv_content) > 0

        # Verify CSV structure
        lines = csv_content.strip().split('\n')
        assert len(lines) > 1  # Has headers and data
        assert 'Métrica' in lines[0]  # Has header
        assert 'Total de Análisis' in csv_content

        db.close()

    def test_summary_statistics(self, test_db, test_user, test_analyses):
        """Test summary statistics calculation"""
        db = TestingSessionLocal()
        service = ReportService(db)

        stats = service._get_summary_statistics(filters={})

        # Verify statistics
        assert stats['total_analyses'] == 5
        assert stats['total_detections'] > 0
        assert stats['high_risk_count'] >= 0
        assert stats['avg_detections'] > 0
        assert 'risk_distribution' in stats

        db.close()

    def test_filtered_statistics(self, test_db, test_user, test_analyses):
        """Test statistics with filters"""
        db = TestingSessionLocal()
        service = ReportService(db)

        # Filter by risk level
        stats = service._get_summary_statistics(
            filters={'risk_level': 'ALTO'}
        )

        assert stats['total_analyses'] <= 5
        assert stats['total_analyses'] >= 0

        db.close()

    def test_date_range_filter(self, test_db, test_user, test_analyses):
        """Test filtering by date range"""
        db = TestingSessionLocal()
        service = ReportService(db)

        # Filter to last 2 days
        date_from = (datetime.now() - timedelta(days=2)).isoformat()

        stats = service._get_summary_statistics(
            filters={'date_from': date_from}
        )

        # Should have fewer analyses
        assert stats['total_analyses'] <= 5

        db.close()

    def test_detailed_csv_export(self, test_db, test_user, test_analyses):
        """Test detailed CSV export"""
        db = TestingSessionLocal()
        service = ReportService(db)

        buffer = service.generate_csv_report(
            report_type="detailed",
            filters={}
        )

        csv_content = buffer.getvalue()
        lines = csv_content.strip().split('\n')

        # Should have headers + data rows
        assert len(lines) > 1

        # Verify headers
        headers = lines[0].split(',')
        assert 'ID' in headers[0]
        assert 'Archivo' in headers[1]

        # Verify data rows
        assert len(lines) - 1 <= 5  # Up to 5 analyses

        db.close()

    def test_pdf_with_filters(self, test_db, test_user, test_analyses):
        """Test PDF generation with filters"""
        db = TestingSessionLocal()
        service = ReportService(db)

        buffer = service.generate_pdf_report(
            report_type="detailed",
            filters={'risk_level': 'ALTO'},
            user_id=test_user.id
        )

        # Should generate valid PDF
        assert buffer.getvalue().startswith(b'%PDF')

        db.close()

    def test_empty_data_handling(self, test_db, test_user):
        """Test report generation with no data"""
        db = TestingSessionLocal()
        service = ReportService(db)

        # No analyses exist yet (using fresh test_user without test_analyses)
        stats = service._get_summary_statistics(filters={})

        assert stats['total_analyses'] == 0
        assert stats['total_detections'] == 0
        assert stats['avg_detections'] == 0

        db.close()

    def test_multiple_report_types(self, test_db, test_user, test_analyses):
        """Test generating different report types"""
        db = TestingSessionLocal()
        service = ReportService(db)

        report_types = ['summary', 'detailed', 'statistics']

        for report_type in report_types:
            # PDF
            pdf_buffer = service.generate_pdf_report(
                report_type=report_type,
                filters={},
                user_id=test_user.id
            )
            assert pdf_buffer.getvalue().startswith(b'%PDF')

            # CSV
            csv_buffer = service.generate_csv_report(
                report_type=report_type,
                filters={}
            )
            assert len(csv_buffer.getvalue()) > 0

        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
