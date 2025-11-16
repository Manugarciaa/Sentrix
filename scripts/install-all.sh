#!/bin/bash
# Script de instalación completa para Sentrix
# Instala todas las dependencias de backend, yolo-service, shared y frontend
# Ejecutar desde la raíz del proyecto: ./scripts/install-all.sh

set -e  # Exit on error

echo "=========================================="
echo "Sentrix - Instalación Completa"
echo "=========================================="

# Cambiar a directorio raíz del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_step() {
    echo -e "\n${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Verificar Python
print_step "Verificando Python..."
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    print_error "Python no encontrado. Instale Python 3.8+ primero."
    exit 1
fi
PYTHON_CMD=$(command -v python3 || command -v python)
print_success "Python encontrado: $($PYTHON_CMD --version)"

# Verificar Node.js
print_step "Verificando Node.js..."
if ! command -v node &> /dev/null; then
    print_error "Node.js no encontrado. Instale Node.js 16+ primero."
    exit 1
fi
print_success "Node.js encontrado: $(node --version)"

# 1. Instalar Shared Library
print_step "Instalando Shared Library..."
cd shared
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
fi
source venv/bin/activate || . venv/Scripts/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
print_success "Shared library instalada"
deactivate
cd ..

# 2. Instalar Backend
print_step "Instalando Backend..."
cd backend
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
fi
source venv/bin/activate || . venv/Scripts/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ../shared
print_success "Backend instalado"
deactivate
cd ..

# 3. Instalar YOLO Service
print_step "Instalando YOLO Service..."
cd yolo-service
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
fi
source venv/bin/activate || . venv/Scripts/activate
pip install --upgrade pip
pip install -r requirements.txt
print_success "YOLO Service instalado"
deactivate
cd ..

# 4. Instalar Frontend
print_step "Instalando Frontend..."
cd frontend
npm install
print_success "Frontend instalado"
cd ..

# Mensaje final
echo ""
echo "=========================================="
echo -e "${GREEN}✓ Instalación completa exitosa${NC}"
echo "=========================================="
echo ""
echo "Próximos pasos:"
echo "1. Configura el archivo .env con tus credenciales"
echo "   cp .env.example .env"
echo ""
echo "2. Inicia Redis (Docker):"
echo "   docker run -d -p 6379:6379 --name sentrix-redis redis:7-alpine"
echo ""
echo "3. Ejecuta las migraciones de base de datos:"
echo "   cd backend && source venv/bin/activate"
echo "   alembic upgrade head"
echo ""
echo "4. Inicia todos los servicios:"
echo "   ./scripts/start-all.sh     # Linux/Mac"
echo "   .\\scripts\\start-all.ps1   # Windows PowerShell"
echo ""
