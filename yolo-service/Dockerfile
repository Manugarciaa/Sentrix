FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

# Información del mantenedor
LABEL maintainer="dengue-detection-project"
LABEL description="YOLOv11 Dengue Breeding Site Detection System"

# Variables de entorno
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    unzip \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p data/images/{train,val,test} \
    data/labels/{train,val,test} \
    models \
    results/reports

# Exponer puerto para Jupyter/LabelStudio
EXPOSE 8080 8888

# Comando por defecto
CMD ["python", "main.py"]