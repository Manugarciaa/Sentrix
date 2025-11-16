"""
Simple script to verify indexes in Supabase
"""
import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

# Get DATABASE_URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in .env file")
    exit(1)

print("=" * 80)
print("VERIFICACION DE INDICES DE PERFORMANCE - PHASE 1")
print("=" * 80)
print(f"\nDatabase: {DATABASE_URL[:60]}...")

try:
    # Connect to database
    print("\n[1] Conectando a Supabase...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    print("    OK - Conectado")

    # Query to get all indexes
    print("\n[2] Verificando indices creados...")
    query = """
        SELECT
            schemaname,
            tablename,
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND (indexname LIKE 'idx_analyses_%' OR indexname LIKE 'idx_detections_%')
        ORDER BY tablename, indexname;
    """

    cursor.execute(query)
    indexes = cursor.fetchall()

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

    print(f"\nIndices encontrados: {len(found_indexes)}/9")
    print("-" * 80)

    for idx_name in expected_indexes:
        if idx_name in found_indexes:
            print(f"  OK   {idx_name}")
        else:
            print(f"  FALTA {idx_name}")

    missing = set(expected_indexes) - set(found_indexes)

    print("\n" + "=" * 80)
    if not missing:
        print("RESULTADO: TODOS LOS INDICES CREADOS CORRECTAMENTE")
        print("=" * 80)

        # Get table stats
        print("\n[3] Estadisticas de las tablas:")
        print("-" * 80)

        for table in ['analyses', 'detections']:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count:,} registros")

        # Note about empty tables
        if all(cursor.execute(f"SELECT COUNT(*) FROM {table};") or cursor.fetchone()[0] == 0 for table in ['analyses', 'detections']):
            print("\n  NOTA: No hay datos en las tablas aun.")
            print("        Sube algunas imagenes para analisis para medir performance real.")

        print("\n" + "=" * 80)
        print("PROXIMOS PASOS:")
        print("=" * 80)
        print("1. Ejecutar tests: cd backend && pytest tests -v")
        print("2. Medir performance del backend en uso real")
        print("3. Phase 2: Implementar cache de Redis")

    else:
        print(f"RESULTADO: FALTAN {len(missing)} INDICES")
        print("=" * 80)
        print("\nIndices faltantes:")
        for idx in missing:
            print(f"  - {idx}")
        print("\nRevisar la migracion 006_add_performance_indexes.sql")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
