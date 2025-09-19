#!/usr/bin/env python3
"""
Script de mantenimiento de base de datos para Sentrix Backend
Proporciona utilidades para limpieza, optimización y análisis de datos
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# Agregar directorio raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, func
from app.database import get_db_session
from app.models.models import Analysis, Detection, UserProfile
from app.models.enums import ValidationStatusEnum


def imprimir_encabezado(titulo):
    """Imprime encabezado formateado"""
    print(f"\n{'='*60}")
    print(f" {titulo}")
    print('='*60)


def limpiar_analisis_antiguos(dias=30):
    """Limpia análisis y detecciones más antiguos que N días"""
    imprimir_encabezado(f"LIMPIEZA DE ANÁLISIS ANTIGUOS ({dias} días)")

    fecha_limite = datetime.utcnow() - timedelta(days=dias)

    with get_db_session() as db:
        # Contar análisis a eliminar
        count_analisis = db.query(Analysis).filter(
            Analysis.created_at < fecha_limite
        ).count()

        if count_analisis == 0:
            print("✓ No hay análisis antiguos para eliminar")
            return

        print(f"⚠️  Se eliminarán {count_analisis} análisis anteriores al {fecha_limite.date()}")

        # Confirmar acción
        respuesta = input("¿Continuar? (s/N): ").lower()
        if respuesta != 's':
            print("❌ Operación cancelada")
            return

        # Eliminar análisis (las detecciones se eliminan por cascade)
        eliminados = db.query(Analysis).filter(
            Analysis.created_at < fecha_limite
        ).delete()

        db.commit()
        print(f"✅ {eliminados} análisis eliminados exitosamente")


def optimizar_base_datos():
    """Ejecuta comandos de optimización de PostgreSQL"""
    imprimir_encabezado("OPTIMIZACIÓN DE BASE DE DATOS")

    with get_db_session() as db:
        try:
            # Análisis de tablas
            print("🔍 Ejecutando ANALYZE en todas las tablas...")
            db.execute(text("ANALYZE;"))

            # Vacuum para recuperar espacio
            print("🧹 Ejecutando VACUUM...")
            db.execute(text("VACUUM;"))

            # Reindexar si es necesario
            print("📇 Reindexando tablas principales...")
            db.execute(text("REINDEX TABLE analyses;"))
            db.execute(text("REINDEX TABLE detections;"))

            db.commit()
            print("✅ Optimización completada")

        except Exception as e:
            print(f"❌ Error durante optimización: {e}")
            db.rollback()


def generar_estadisticas():
    """Genera estadísticas de uso de la base de datos"""
    imprimir_encabezado("ESTADÍSTICAS DE BASE DE DATOS")

    with get_db_session() as db:
        # Estadísticas generales
        total_usuarios = db.query(UserProfile).count()
        total_analisis = db.query(Analysis).count()
        total_detecciones = db.query(Detection).count()

        print(f"📊 Usuarios registrados: {total_usuarios}")
        print(f"📊 Total análisis: {total_analisis}")
        print(f"📊 Total detecciones: {total_detecciones}")

        # Análisis por mes (últimos 6 meses)
        print("\n📈 Análisis por mes (últimos 6 meses):")
        resultado = db.query(
            func.date_trunc('month', Analysis.created_at).label('mes'),
            func.count(Analysis.id).label('cantidad')
        ).filter(
            Analysis.created_at >= datetime.utcnow() - timedelta(days=180)
        ).group_by(
            func.date_trunc('month', Analysis.created_at)
        ).order_by('mes').all()

        for mes, cantidad in resultado:
            print(f"  {mes.strftime('%Y-%m')}: {cantidad} análisis")

        # Detecciones por tipo
        print("\n🦟 Detecciones por tipo de sitio de cría:")
        resultado = db.query(
            Detection.breeding_site_type,
            func.count(Detection.id).label('cantidad')
        ).group_by(
            Detection.breeding_site_type
        ).order_by('cantidad DESC').all()

        for tipo, cantidad in resultado:
            if tipo:
                print(f"  {tipo.value}: {cantidad} detecciones")

        # Estado de validaciones
        print("\n✅ Estado de validaciones:")
        resultado = db.query(
            Detection.validation_status,
            func.count(Detection.id).label('cantidad')
        ).group_by(
            Detection.validation_status
        ).all()

        for estado, cantidad in resultado:
            print(f"  {estado.value}: {cantidad} detecciones")


def verificar_integridad():
    """Verifica la integridad de los datos"""
    imprimir_encabezado("VERIFICACIÓN DE INTEGRIDAD")

    with get_db_session() as db:
        errores = []

        # Verificar análisis huérfanos (sin usuario)
        analisis_huerfanos = db.query(Analysis).filter(
            ~Analysis.user_id.in_(
                db.query(UserProfile.id)
            )
        ).count()

        if analisis_huerfanos > 0:
            errores.append(f"❌ {analisis_huerfanos} análisis sin usuario válido")

        # Verificar detecciones huérfanas (sin análisis)
        detecciones_huerfanas = db.query(Detection).filter(
            ~Detection.analysis_id.in_(
                db.query(Analysis.id)
            )
        ).count()

        if detecciones_huerfanas > 0:
            errores.append(f"❌ {detecciones_huerfanas} detecciones sin análisis válido")

        # Verificar consistencia de conteos
        for analisis in db.query(Analysis).limit(100):
            detecciones_reales = db.query(Detection).filter_by(
                analysis_id=analisis.id
            ).count()

            if analisis.total_detections != detecciones_reales:
                errores.append(
                    f"❌ Análisis {analisis.id}: cuenta {analisis.total_detections} "
                    f"pero tiene {detecciones_reales} detecciones"
                )

        if not errores:
            print("✅ No se encontraron problemas de integridad")
        else:
            print("⚠️  Problemas encontrados:")
            for error in errores[:10]:  # Mostrar solo los primeros 10
                print(f"  {error}")

            if len(errores) > 10:
                print(f"  ... y {len(errores) - 10} problemas más")


def main():
    """Función principal del script"""
    print("🔧 Script de Mantenimiento de Base de Datos - Sentrix Backend")
    print("=" * 60)

    opciones = {
        "1": ("Limpiar análisis antiguos", limpiar_analisis_antiguos),
        "2": ("Optimizar base de datos", optimizar_base_datos),
        "3": ("Generar estadísticas", generar_estadisticas),
        "4": ("Verificar integridad", verificar_integridad),
        "5": ("Ejecutar todo", None)
    }

    print("\n📋 Opciones disponibles:")
    for clave, (descripcion, _) in opciones.items():
        print(f"  {clave}. {descripcion}")

    print("  0. Salir")

    while True:
        try:
            opcion = input("\n🔽 Seleccionar opción (0-5): ").strip()

            if opcion == "0":
                print("👋 ¡Hasta luego!")
                break
            elif opcion == "5":
                # Ejecutar todo
                for clave in ["2", "4", "3"]:  # Optimizar, verificar, estadísticas
                    _, funcion = opciones[clave]
                    if funcion:
                        funcion()
                print("\n🎉 Mantenimiento completo terminado")
            elif opcion in opciones:
                descripcion, funcion = opciones[opcion]
                if funcion:
                    if opcion == "1":
                        # Pedir días para limpieza
                        try:
                            dias = int(input("📅 Días de antigüedad (default 30): ") or "30")
                            funcion(dias)
                        except ValueError:
                            print("❌ Número de días inválido")
                    else:
                        funcion()
                else:
                    print("❌ Opción no implementada")
            else:
                print("❌ Opción inválida. Intente nuevamente.")

        except KeyboardInterrupt:
            print("\n\n👋 Operación cancelada por el usuario")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()