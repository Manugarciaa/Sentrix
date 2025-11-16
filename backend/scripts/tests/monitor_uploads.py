"""
Monitor de uploads en tiempo real a Supabase Storage
"""
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Cargar .env
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print("=== MONITOR DE UPLOADS EN TIEMPO REAL ===")
print(f"Supabase URL: {SUPABASE_URL}")
print(f"Presiona Ctrl+C para detener\n")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    buckets = ['sentrix-images', 'sentrix-processed']

    previous_counts = {}

    while True:
        for bucket in buckets:
            try:
                files = supabase.storage.from_(bucket).list()
                current_count = len(files)

                if bucket not in previous_counts:
                    previous_counts[bucket] = current_count
                    print(f"[INICIO] {bucket}: {current_count} archivos")
                elif current_count != previous_counts[bucket]:
                    diff = current_count - previous_counts[bucket]
                    symbol = "📥" if diff > 0 else "🗑️"
                    print(f"\n{symbol} [{time.strftime('%H:%M:%S')}] {bucket}: {previous_counts[bucket]} -> {current_count} ({diff:+d})")

                    # Mostrar nuevos archivos
                    if diff > 0:
                        print("   Nuevos archivos:")
                        for f in files[-abs(diff):]:
                            name = f.get('name') if isinstance(f, dict) else f.name
                            # Generar URL pública
                            public_url = f"https://bnllcqmcwfuauithwgkw.supabase.co/storage/v1/object/public/{bucket}/{name}"
                            print(f"   • {name}")
                            print(f"     URL: {public_url}")

                    previous_counts[bucket] = current_count

            except Exception as e:
                print(f"Error en {bucket}: {e}")

        time.sleep(2)  # Verificar cada 2 segundos

except KeyboardInterrupt:
    print("\n\n=== MONITOR DETENIDO ===")
    print("\nResumen final:")
    for bucket, count in previous_counts.items():
        print(f"  {bucket}: {count} archivos")

except Exception as e:
    print(f"\nError: {e}")
