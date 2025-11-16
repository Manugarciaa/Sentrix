"""
Performance Verification Script
Verifies that Phase 1 optimizations are working correctly
"""
import time
from sqlalchemy import text
from src.database.connection import SessionLocal, get_database_url
import sys

def verify_indexes():
    """Verify that all performance indexes were created"""
    print("=" * 80)
    print("1. VERIFICANDO ÍNDICES DE PERFORMANCE")
    print("=" * 80)

    db = SessionLocal()
    try:
        query = text("""
            SELECT
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND (indexname LIKE 'idx_analyses_%' OR indexname LIKE 'idx_detections_%')
            ORDER BY tablename, indexname;
        """)

        result = db.execute(query)
        indexes = result.fetchall()

        expected_indexes = [
            'idx_analyses_created_at_desc',
            'idx_analyses_user_id',
            'idx_analyses_risk_level',
            'idx_analyses_user_created',
            'idx_analyses_has_gps',
            'idx_detections_analysis_id',
            'idx_detections_risk_level',
            'idx_detections_breeding_site',
            'idx_detections_analysis_risk'
        ]

        found_indexes = [idx[2] for idx in indexes]

        print(f"\n[OK] Índices encontrados: {len(found_indexes)}/9")
        for idx_name in found_indexes:
            status = "[OK]" if idx_name in expected_indexes else "[WARNING]"
            print(f"  {status} {idx_name}")

        missing = set(expected_indexes) - set(found_indexes)
        if missing:
            print(f"\n[ERROR] Índices faltantes:")
            for idx_name in missing:
                print(f"  [ERROR] {idx_name}")
            return False

        print("\n[OK] Todos los índices están creados correctamente")
        return True
    finally:
        db.close()


def measure_query_performance():
    """Measure performance of critical queries"""
    print("\n" + "=" * 80)
    print("2. MIDIENDO PERFORMANCE DE QUERIES")
    print("=" * 80)

    db = SessionLocal()
    try:
        # Test 1: List analyses (most common query)
        print("\n📊 Test 1: GET /api/v1/analyses (list with pagination)")
        query = text("""
            SELECT COUNT(*) FROM analyses;
        """)
        result = db.execute(query)
        total_analyses = result.scalar()
        print(f"  Total de análisis en BD: {total_analyses}")

        if total_analyses == 0:
            print("  [WARNING] No hay datos para medir performance")
            print("  💡 Sube algunas imágenes para análisis primero")
            return

        # Measure list query
        query = text("""
            SELECT
                id, created_at, image_path, risk_level, user_id
            FROM analyses
            ORDER BY created_at DESC
            LIMIT 20;
        """)

        start = time.time()
        result = db.execute(query)
        rows = result.fetchall()
        duration = (time.time() - start) * 1000  # Convert to ms

        print(f"  ⏱️ Tiempo de query: {duration:.2f}ms")
        print(f"  📄 Resultados: {len(rows)} registros")

        if duration < 100:
            print("  [OK] EXCELENTE: <100ms")
        elif duration < 500:
            print("  [OK] BUENO: <500ms (objetivo Phase 1)")
        elif duration < 1000:
            print("  [WARNING] ACEPTABLE: <1s")
        else:
            print("  [ERROR] LENTO: >1s (revisar índices)")

        # Test 2: User-specific query
        print("\n📊 Test 2: Queries filtradas por usuario")
        query = text("""
            SELECT
                id, created_at, risk_level
            FROM analyses
            WHERE user_id IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 20;
        """)

        start = time.time()
        result = db.execute(query)
        rows = result.fetchall()
        duration = (time.time() - start) * 1000

        print(f"  ⏱️ Tiempo de query: {duration:.2f}ms")
        print(f"  📄 Resultados: {len(rows)} registros")

        if duration < 50:
            print("  [OK] EXCELENTE: <50ms (índice compuesto funcionando)")
        elif duration < 200:
            print("  [OK] BUENO: <200ms")
        else:
            print("  [WARNING] Revisar índice idx_analyses_user_created")

        # Test 3: Detections join (heatmap queries)
        print("\n📊 Test 3: JOIN con detecciones (heatmap)")
        query = text("""
            SELECT
                a.id, a.created_at, d.risk_level, d.breeding_site_type
            FROM analyses a
            LEFT JOIN detections d ON d.analysis_id = a.id
            WHERE a.has_gps_data = true
            LIMIT 100;
        """)

        start = time.time()
        result = db.execute(query)
        rows = result.fetchall()
        duration = (time.time() - start) * 1000

        print(f"  ⏱️ Tiempo de query: {duration:.2f}ms")
        print(f"  📄 Resultados: {len(rows)} registros")

        if duration < 200:
            print("  [OK] EXCELENTE: <200ms")
        elif duration < 500:
            print("  [OK] BUENO: <500ms")
        else:
            print("  [WARNING] Considerar optimizaciones adicionales")
    finally:
        db.close()


def check_database_stats():
    """Check database statistics"""
    print("\n" + "=" * 80)
    print("3. ESTADÍSTICAS DE LA BASE DE DATOS")
    print("=" * 80)

    db = SessionLocal()
    try:
        # Table sizes
        query = text("""
            SELECT
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                pg_total_relation_size(schemaname||'.'||tablename) AS bytes
            FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename IN ('analyses', 'detections', 'users')
            ORDER BY bytes DESC;
        """)

        result = db.execute(query)
        tables = result.fetchall()

        print("\n📊 Tamaño de tablas:")
        for table in tables:
            print(f"  • {table[1]}: {table[2]}")

        # Index usage stats (if available)
        print("\n📊 Conteo de registros:")
        for table_name in ['analyses', 'detections', 'users']:
            query = text(f"SELECT COUNT(*) FROM {table_name};")
            result = db.execute(query)
            count = result.scalar()
            print(f"  • {table_name}: {count:,} registros")
    finally:
        db.close()


def main():
    """Run all verification checks"""
    print("\n" + "=" * 80)
    print("VERIFICACIÓN DE OPTIMIZACIONES - PHASE 1")
    print("=" * 80)
    db_url = get_database_url()
    print(f"Database: {db_url[:50]}...")
    print("")

    try:
        # 1. Verify indexes
        indexes_ok = verify_indexes()

        # 2. Measure performance
        measure_query_performance()

        # 3. Database stats
        check_database_stats()

        # Summary
        print("\n" + "=" * 80)
        print("RESUMEN")
        print("=" * 80)

        if indexes_ok:
            print("[OK] Índices: CORRECTOS")
        else:
            print("[ERROR] Índices: FALTAN ALGUNOS")

        print("\n💡 PRÓXIMOS PASOS:")
        print("  1. Si la performance es <500ms: [OK] Phase 1 completa")
        print("  2. Ejecutar tests: pytest backend/tests -v")
        print("  3. Phase 2: Implementar caché de Redis")

        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\n[ERROR] Error durante verificación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
