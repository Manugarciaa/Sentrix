"""
Report Generation Service
Servicio de generación de reportes
"""

import io
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from uuid import UUID

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image as RLImage
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from ..database.models.models import Analysis, Detection, UserProfile


class ReportService:
    """Service for generating reports in various formats"""

    def __init__(self, db: Session):
        self.db = db
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12
        ))
        self.styles.add(ParagraphStyle(
            name='RiskHigh',
            parent=self.styles['Normal'],
            textColor=colors.red,
            fontSize=12,
            fontName='Helvetica-Bold'
        ))

    def generate_pdf_report(
        self,
        report_type: str,
        filters: Dict[str, Any],
        user_id: UUID
    ) -> io.BytesIO:
        """
        Generate PDF report

        Args:
            report_type: Type of report (summary, detailed, statistics)
            filters: Filters to apply (date_from, date_to, risk_level, etc.)
            user_id: User requesting the report

        Returns:
            BytesIO buffer with PDF content
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch)
        story = []

        # Title
        title = self._get_report_title(report_type)
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Metadata
        story.extend(self._generate_metadata_section(filters, user_id))
        story.append(Spacer(1, 0.2*inch))

        # Content based on report type
        if report_type == 'summary':
            story.extend(self._generate_summary_content(filters))
        elif report_type == 'detailed':
            story.extend(self._generate_detailed_content(filters))
        elif report_type == 'statistics':
            story.extend(self._generate_statistics_content(filters))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def _get_report_title(self, report_type: str) -> str:
        """Get report title based on type"""
        titles = {
            'summary': 'Sentrix - Reporte Ejecutivo de Análisis',
            'detailed': 'Sentrix - Reporte Detallado de Detecciones',
            'statistics': 'Sentrix - Reporte Estadístico',
            'map': 'Sentrix - Reporte Geográfico'
        }
        return titles.get(report_type, 'Sentrix - Reporte de Análisis')

    def _generate_metadata_section(
        self,
        filters: Dict[str, Any],
        user_id: UUID
    ) -> List:
        """Generate report metadata section"""
        elements = []

        # Get user info
        user = self.db.query(UserProfile).filter(UserProfile.id == user_id).first()

        # Metadata table
        metadata_data = [
            ['Generado por:', user.display_name or user.email if user else 'N/A'],
            ['Fecha de generación:', datetime.now().strftime('%d/%m/%Y %H:%M')],
        ]

        if filters.get('date_from'):
            metadata_data.append(['Fecha desde:', filters['date_from']])
        if filters.get('date_to'):
            metadata_data.append(['Fecha hasta:', filters['date_to']])
        if filters.get('risk_level'):
            metadata_data.append(['Nivel de riesgo:', filters['risk_level']])

        metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(metadata_table)
        return elements

    def _generate_summary_content(self, filters: Dict[str, Any]) -> List:
        """Generate summary report content"""
        elements = []

        # Get summary statistics
        stats = self._get_summary_statistics(filters)

        # Summary heading
        elements.append(Paragraph('Resumen Ejecutivo', self.styles['CustomHeading']))
        elements.append(Spacer(1, 0.15*inch))

        # Statistics table
        stats_data = [
            ['Métrica', 'Valor'],
            ['Total de Análisis', str(stats['total_analyses'])],
            ['Total de Detecciones', str(stats['total_detections'])],
            ['Detecciones de Alto Riesgo', str(stats['high_risk_count'])],
            ['Detecciones de Riesgo Medio', str(stats['medium_risk_count'])],
            ['Promedio de Detecciones por Análisis', f"{stats['avg_detections']:.2f}"],
        ]

        stats_table = Table(stats_data, colWidths=[3.5*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        elements.append(stats_table)
        elements.append(Spacer(1, 0.3*inch))

        # Risk distribution
        elements.append(Paragraph('Distribución de Riesgo', self.styles['CustomHeading']))
        elements.append(Spacer(1, 0.15*inch))

        risk_data = [
            ['Nivel de Riesgo', 'Cantidad', 'Porcentaje'],
        ]

        total = stats['total_detections'] or 1  # Avoid division by zero
        for risk_level, count in stats['risk_distribution'].items():
            percentage = (count / total) * 100 if total > 0 else 0
            risk_data.append([risk_level, str(count), f"{percentage:.1f}%"])

        risk_table = Table(risk_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
        ]))

        elements.append(risk_table)

        return elements

    def _generate_detailed_content(self, filters: Dict[str, Any]) -> List:
        """Generate detailed report content"""
        elements = []

        # Get detailed analyses
        analyses = self._get_filtered_analyses(filters, limit=50)

        elements.append(Paragraph('Análisis Detallados', self.styles['CustomHeading']))
        elements.append(Spacer(1, 0.15*inch))

        for idx, analysis in enumerate(analyses, 1):
            # Analysis header
            analysis_title = f"Análisis #{idx} - {analysis.image_filename or 'Sin nombre'}"
            elements.append(Paragraph(analysis_title, self.styles['Heading3']))

            # Analysis details table
            details_data = [
                ['Fecha:', analysis.created_at.strftime('%d/%m/%Y %H:%M') if analysis.created_at else 'N/A'],
                ['Nivel de Riesgo:', analysis.risk_level or 'N/A'],
                ['Total Detecciones:', str(analysis.total_detections or 0)],
                ['Umbral de Confianza:', f"{float(analysis.confidence_threshold or 0):.0%}" if analysis.confidence_threshold else 'N/A'],
            ]

            if analysis.has_gps_data:
                details_data.append(['Ubicación:', 'GPS disponible'])

            details_table = Table(details_data, colWidths=[2*inch, 4*inch])
            details_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ]))

            elements.append(details_table)
            elements.append(Spacer(1, 0.2*inch))

            # Page break every 3 analyses
            if idx % 3 == 0 and idx < len(analyses):
                elements.append(PageBreak())

        return elements

    def _generate_statistics_content(self, filters: Dict[str, Any]) -> List:
        """Generate statistics report content"""
        elements = []

        stats = self._get_detailed_statistics(filters)

        elements.append(Paragraph('Estadísticas Detalladas', self.styles['CustomHeading']))
        elements.append(Spacer(1, 0.15*inch))

        # Various statistical tables and charts would go here
        # For brevity, showing main stats

        stats_sections = [
            ('Estadísticas Generales', stats['general']),
            ('Por Nivel de Riesgo', stats['by_risk_level']),
            ('Por Tipo de Criadero', stats['by_breeding_site']),
        ]

        for section_title, section_data in stats_sections:
            elements.append(Paragraph(section_title, self.styles['Heading3']))
            elements.append(Spacer(1, 0.1*inch))

            table_data = [['Métrica', 'Valor']]
            for key, value in section_data.items():
                table_data.append([key, str(value)])

            table = Table(table_data, colWidths=[3.5*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 0.2*inch))

        return elements

    def generate_csv_report(
        self,
        report_type: str,
        filters: Dict[str, Any]
    ) -> io.StringIO:
        """
        Generate CSV report

        Args:
            report_type: Type of report
            filters: Filters to apply

        Returns:
            StringIO buffer with CSV content
        """
        buffer = io.StringIO()
        writer = csv.writer(buffer)

        # Get data based on report type
        if report_type == 'summary':
            data = self._get_summary_csv_data(filters)
        elif report_type == 'detailed':
            data = self._get_detailed_csv_data(filters)
        else:
            data = self._get_statistics_csv_data(filters)

        # Write headers and rows
        if data:
            writer.writerow(data['headers'])
            writer.writerows(data['rows'])

        buffer.seek(0)
        return buffer

    def _get_summary_csv_data(self, filters: Dict[str, Any]) -> Dict:
        """Get summary data for CSV export"""
        stats = self._get_summary_statistics(filters)

        return {
            'headers': ['Métrica', 'Valor'],
            'rows': [
                ['Total de Análisis', stats['total_analyses']],
                ['Total de Detecciones', stats['total_detections']],
                ['Detecciones de Alto Riesgo', stats['high_risk_count']],
                ['Detecciones de Riesgo Medio', stats['medium_risk_count']],
                ['Promedio de Detecciones', f"{stats['avg_detections']:.2f}"],
            ]
        }

    def _get_detailed_csv_data(self, filters: Dict[str, Any]) -> Dict:
        """Get detailed data for CSV export"""
        analyses = self._get_filtered_analyses(filters, limit=1000)

        headers = [
            'ID', 'Archivo', 'Fecha', 'Nivel de Riesgo',
            'Total Detecciones', 'Alto Riesgo', 'Riesgo Medio',
            'Umbral Confianza', 'Tiene GPS'
        ]

        rows = []
        for analysis in analyses:
            rows.append([
                str(analysis.id),
                analysis.image_filename or '',
                analysis.created_at.strftime('%Y-%m-%d %H:%M:%S') if analysis.created_at else '',
                analysis.risk_level or '',
                analysis.total_detections or 0,
                analysis.high_risk_count or 0,
                analysis.medium_risk_count or 0,
                float(analysis.confidence_threshold or 0),
                'Sí' if analysis.has_gps_data else 'No'
            ])

        return {'headers': headers, 'rows': rows}

    def _get_statistics_csv_data(self, filters: Dict[str, Any]) -> Dict:
        """Get statistics data for CSV export"""
        # Similar to detailed but with aggregated data
        return self._get_summary_csv_data(filters)

    def _get_summary_statistics(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary statistics from database"""
        query = self.db.query(Analysis)

        # Apply filters
        query = self._apply_filters(query, filters)

        # Get totals
        total_analyses = query.count()
        total_detections = query.with_entities(
            func.sum(Analysis.total_detections)
        ).scalar() or 0

        high_risk_count = query.with_entities(
            func.sum(Analysis.high_risk_count)
        ).scalar() or 0

        medium_risk_count = query.with_entities(
            func.sum(Analysis.medium_risk_count)
        ).scalar() or 0

        # Risk distribution
        risk_dist = query.with_entities(
            Analysis.risk_level,
            func.count(Analysis.id)
        ).group_by(Analysis.risk_level).all()

        risk_distribution = {level: count for level, count in risk_dist if level}

        avg_detections = total_detections / total_analyses if total_analyses > 0 else 0

        return {
            'total_analyses': total_analyses,
            'total_detections': int(total_detections),
            'high_risk_count': int(high_risk_count),
            'medium_risk_count': int(medium_risk_count),
            'avg_detections': avg_detections,
            'risk_distribution': risk_distribution
        }

    def _get_detailed_statistics(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed statistics"""
        query = self.db.query(Analysis)
        query = self._apply_filters(query, filters)

        # General stats
        general = {
            'Total Análisis': query.count(),
            'Con GPS': query.filter(Analysis.has_gps_data == True).count(),
        }

        # By risk level
        by_risk = query.with_entities(
            Analysis.risk_level,
            func.count(Analysis.id)
        ).group_by(Analysis.risk_level).all()

        by_risk_level = {level: count for level, count in by_risk if level}

        # By breeding site (would need to join detections)
        by_breeding_site = {'Total': query.count()}  # Simplified

        return {
            'general': general,
            'by_risk_level': by_risk_level,
            'by_breeding_site': by_breeding_site
        }

    def _get_filtered_analyses(
        self,
        filters: Dict[str, Any],
        limit: int = 100
    ) -> List[Analysis]:
        """Get filtered analyses"""
        query = self.db.query(Analysis)
        query = self._apply_filters(query, filters)
        return query.order_by(Analysis.created_at.desc()).limit(limit).all()

    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to query"""
        if filters.get('date_from'):
            query = query.filter(
                Analysis.created_at >= datetime.fromisoformat(filters['date_from'])
            )
        if filters.get('date_to'):
            query = query.filter(
                Analysis.created_at <= datetime.fromisoformat(filters['date_to'])
            )
        if filters.get('risk_level'):
            query = query.filter(Analysis.risk_level == filters['risk_level'])
        if filters.get('has_gps'):
            query = query.filter(Analysis.has_gps_data == True)

        return query
