from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Configuracion
INPUT_DIR = Path("../docs/imagenes/ejemplos_yolo")
OUTPUT_FILE = Path("../docs/imagenes/figura_8_1_grid_detecciones.png")

# Cargar las 8 imagenes
casos = ['a', 'b', 'c', 'd']
imagenes = []

print("=" * 60)
print("CREANDO GRID 2x2 PARA FIGURA 8.1")
print("=" * 60)

# Cargar imagenes en orden: caso_a_original, caso_a_procesada, caso_b_original, etc.
for caso in casos:
    original_path = INPUT_DIR / f"caso_{caso}_original.jpg"
    procesada_path = INPUT_DIR / f"caso_{caso}_procesada.jpg"

    if not original_path.exists() or not procesada_path.exists():
        print(f"[ERROR] Faltan imagenes para caso {caso}")
        exit(1)

    img_original = Image.open(original_path)
    img_procesada = Image.open(procesada_path)

    imagenes.append((img_original, img_procesada, caso))
    print(f"[OK] Cargadas imagenes caso {caso}: {img_original.size}")

# Redimensionar todas las imagenes a un tamano uniforme
TARGET_WIDTH = 800
TARGET_HEIGHT = 600

imagenes_resized = []
for img_orig, img_proc, caso in imagenes:
    orig_resized = img_orig.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    proc_resized = img_proc.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    imagenes_resized.append((orig_resized, proc_resized, caso))

print(f"\n[OK] Imagenes redimensionadas a {TARGET_WIDTH}x{TARGET_HEIGHT}")

# Crear el grid 2x2 (4 filas x 2 columnas)
# Fila 1: caso_a_original | caso_a_procesada
# Fila 2: caso_b_original | caso_b_procesada
# Fila 3: caso_c_original | caso_c_procesada
# Fila 4: caso_d_original | caso_d_procesada

MARGIN = 10
LABEL_HEIGHT = 40

grid_width = TARGET_WIDTH * 2 + MARGIN * 3
grid_height = (TARGET_HEIGHT + LABEL_HEIGHT) * 4 + MARGIN * 5

# Crear imagen blanca para el grid
grid = Image.new('RGB', (grid_width, grid_height), 'white')
draw = ImageDraw.Draw(grid)

# Intentar cargar una fuente, si no usar la default
try:
    font = ImageFont.truetype("arial.ttf", 28)
except:
    font = ImageFont.load_default()

print(f"[OK] Grid creado: {grid_width}x{grid_height}")

# Colocar imagenes en el grid
for i, (img_orig, img_proc, caso) in enumerate(imagenes_resized):
    row = i

    # Posicion columna izquierda (original)
    x_orig = MARGIN
    y_orig = MARGIN + row * (TARGET_HEIGHT + LABEL_HEIGHT + MARGIN) + LABEL_HEIGHT

    # Posicion columna derecha (procesada)
    x_proc = MARGIN * 2 + TARGET_WIDTH
    y_proc = y_orig

    # Pegar imagenes
    grid.paste(img_orig, (x_orig, y_orig))
    grid.paste(img_proc, (x_proc, y_proc))

    # Agregar etiquetas
    y_label = y_orig - LABEL_HEIGHT + 5

    draw.text((x_orig + 10, y_label), f"({caso}) Original", fill='black', font=font)
    draw.text((x_proc + 10, y_label), f"({caso}) Procesada", fill='black', font=font)

    print(f"[OK] Colocado caso {caso} en fila {row+1}")

# Guardar
grid.save(OUTPUT_FILE, quality=90)

print(f"\n[OK] Grid guardado: {OUTPUT_FILE.absolute()}")
print(f"    Dimensiones: {grid_width}x{grid_height} px")
print(f"    Tamano archivo: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")

print("\n" + "=" * 60)
print("GRID COMPLETADO!")
print("=" * 60)
print(f"\nPuedes insertar la imagen en la tesis con:")
print(f'![Figura 8.1](./imagenes/figura_8_1_grid_detecciones.png)')
print("=" * 60)
