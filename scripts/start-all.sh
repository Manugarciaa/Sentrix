#!/bin/bash

# Script para iniciar todos los servicios de Sentrix
# Autor: Equipo Sentrix
# Fecha: 2025-01-06

set -e  # Exit on error

echo "======================================"
echo "🚀 Iniciando Servicios de Sentrix"
echo "======================================"
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -d "backend" ] || [ ! -d "frontend" ] || [ ! -d "yolo-service" ]; then
    # Intentar encontrar el directorio raíz
    if [ -f "../start-all.sh" ] && [ -d "../backend" ] && [ -d "../frontend" ] && [ -d "../yolo-service" ]; then
        print_warning "Detectado que estás en un subdirectorio. Cambiando al directorio raíz..."
        cd ..
        print_success "Cambiado al directorio raíz de Sentrix"
    else
        print_error "Error: Debes ejecutar este script desde el directorio raíz de Sentrix"
        print_error "Directorio actual: $(pwd)"
        print_error "Directorios encontrados: $(ls -la)"
        exit 1
    fi
fi

print_status "Verificando dependencias..."

# Verificar Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js no está instalado. Instala Node.js 18+ primero."
    exit 1
fi
print_success "Node.js $(node --version) encontrado"

# Verificar Python
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    print_error "Python no está instalado. Instala Python 3.9+ primero."
    exit 1
fi

PYTHON_CMD=$(command -v python3 || command -v python)
print_success "Python $($PYTHON_CMD --version) encontrado"

# Verificar npm
if ! command -v npm &> /dev/null; then
    print_error "npm no está instalado"
    exit 1
fi
print_success "npm $(npm --version) encontrado"

echo ""
print_status "Preparando entorno..."

# Verificar archivo .env
if [ ! -f ".env" ]; then
    print_warning "Archivo .env no encontrado, copiando desde .env.example..."
    cp .env.example .env
    print_success "Archivo .env creado. Por favor, configura tus variables de entorno."
    print_warning "Presiona Enter para continuar después de configurar .env..."
    read
fi

# Crear directorio de logs si no existe
mkdir -p logs

echo ""
print_status "Instalando dependencias del frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
    print_success "Dependencias del frontend instaladas"
else
    print_success "Dependencias del frontend ya instaladas"
fi
cd ..

echo ""
print_status "Configurando entorno virtual de Python para backend..."
cd backend

# Crear virtual environment si no existe
if [ ! -d "venv" ]; then
    print_status "Creando virtual environment..."
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment creado"
fi

# Activar virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

print_success "Virtual environment activado"

# Instalar dependencias del backend
if [ ! -d "venv/lib" ] && [ ! -d "venv/Lib" ]; then
    print_status "Instalando dependencias del backend..."
    pip install -r requirements.txt
    print_success "Dependencias del backend instaladas"
else
    print_success "Dependencias del backend ya instaladas"
fi
cd ..

echo ""
print_status "Configurando entorno virtual de Python para yolo-service..."
cd yolo-service

# Crear virtual environment si no existe
if [ ! -d "venv" ]; then
    print_status "Creando virtual environment..."
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment creado"
fi

# Activar virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

print_success "Virtual environment activado"

# Instalar dependencias del yolo-service
if [ ! -d "venv/lib" ] && [ ! -d "venv/Lib" ]; then
    print_status "Instalando dependencias del YOLO service..."
    pip install -r requirements.txt
    print_success "Dependencias del YOLO service instaladas"
else
    print_success "Dependencias del YOLO service ya instaladas"
fi
cd ..

echo ""
echo "======================================"
print_success "Todas las dependencias están listas"
echo "======================================"
echo ""

print_status "Iniciando servicios en segundo plano..."
echo ""

# Función para manejar SIGINT (Ctrl+C)
cleanup() {
    echo ""
    echo ""
    print_warning "Deteniendo todos los servicios..."

    # Matar procesos en segundo plano
    jobs -p | xargs -r kill 2>/dev/null

    print_success "Servicios detenidos correctamente"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Iniciar Backend
print_status "Iniciando Backend API (Puerto 8000)..."
cd backend
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
uvicorn app:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
print_success "Backend iniciado (PID: $BACKEND_PID)"

# Esperar un poco para que el backend inicie
sleep 3

# Iniciar YOLO Service
print_status "Iniciando YOLO Service (Puerto 8001)..."
cd yolo-service
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
uvicorn server:app --host 0.0.0.0 --port 8001 --reload > ../logs/yolo-service.log 2>&1 &
YOLO_PID=$!
cd ..
print_success "YOLO Service iniciado (PID: $YOLO_PID)"

# Esperar un poco para que el YOLO service inicie
sleep 3

# Iniciar Frontend
print_status "Iniciando Frontend (Puerto 3000)..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
print_success "Frontend iniciado (PID: $FRONTEND_PID)"

echo ""
echo "======================================"
print_success "¡Todos los servicios están corriendo!"
echo "======================================"
echo ""
echo -e "${GREEN}Servicios disponibles:${NC}"
echo ""
echo -e "  ${BLUE}Frontend:${NC}     http://localhost:3000"
echo -e "  ${BLUE}Backend API:${NC}  http://localhost:8000"
echo -e "  ${BLUE}YOLO Service:${NC} http://localhost:8001"
echo ""
echo -e "  ${BLUE}API Docs:${NC}     http://localhost:8000/docs"
echo -e "  ${BLUE}YOLO Docs:${NC}    http://localhost:8001/docs"
echo ""
echo -e "${YELLOW}Logs en tiempo real:${NC}"
echo ""
echo -e "  ${BLUE}Backend:${NC}      tail -f logs/backend.log"
echo -e "  ${BLUE}YOLO:${NC}         tail -f logs/yolo-service.log"
echo -e "  ${BLUE}Frontend:${NC}     tail -f logs/frontend.log"
echo ""
echo -e "${RED}Presiona Ctrl+C para detener todos los servicios${NC}"
echo ""

# Esperar indefinidamente (hasta Ctrl+C)
wait
