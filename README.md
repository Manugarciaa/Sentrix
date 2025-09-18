# Sentrix - Plataforma de Detección de Vectores de Enfermedad con IA

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![YOLO v11](https://img.shields.io/badge/YOLO-v11-brightgreen.svg)](https://github.com/ultralytics/ultralytics)

Sentrix es una plataforma integral para la detección automatizada y evaluación de riesgo de criaderos de mosquitos del dengue, utilizando inteligencia artificial, análisis ambiental y participación ciudadana para la prevención de enfermedades vectoriales.

## Descripción General

Sentrix combina visión por computadora avanzada con análisis ambiental contextual para identificar y evaluar sitios de reproducción del mosquito *Aedes aegypti*. La plataforma procesa imágenes aéreas (drones) y terrestres (usuarios), calcula índices de riesgo basados en variables meteorológicas, y proporciona herramientas de visualización y alerta temprana para autoridades de salud pública y comunidades.

### Problema que Resuelve

La detección tradicional de criaderos de dengue depende de inspecciones manuales limitadas en cobertura y velocidad de respuesta. Sentrix automatiza este proceso mediante:

- **Análisis masivo** de imágenes aéreas y terrestres
- **Evaluación contextual** con datos meteorológicos en tiempo real
- **Geolocalización precisa** de focos identificados
- **Índices de riesgo** personalizados por zona geográfica
- **Participación ciudadana** activa en la prevención

## Arquitectura

Sentrix está construido como una plataforma modular con tres componentes principales:

```
sentrix/
├── yolo-service/              # Servicio de Detección IA
├── backend/                   # Backend API (Próximamente)
├── frontend/                  # Interfaz Web (Próximamente)
├── docs/                      # Documentación
└── README.md                  # Este archivo
```

### Servicio YOLO

El servicio central de IA para detección por visión por computadora y evaluación de riesgo.

**Características:**
- Modelos de segmentación de instancias YOLOv11
- Evaluación automatizada de riesgo epidemiológico
- Soporte de aceleración GPU
- Interfaces CLI y programáticas
- Capacidades de procesamiento por lotes

[**Ver documentación del servicio YOLO**](./yolo-service/README.md)

### Backend API *(Próximamente)*

Servicio API RESTful para integrar Sentrix en sistemas más grandes.

**Características Planificadas:**
- Endpoints de API REST para integración con sistemas municipales
- Autenticación de usuarios con roles (administrador, experto, técnico, usuario)
- Base de datos PostgreSQL + PostGIS para datos geoespaciales
- Gestión de almacenamiento de imágenes con metadatos EXIF
- Integración con APIs meteorológicas (OpenWeatherMap, ClimaCell)
- Procesamiento de trabajos por lotes y colas de tareas

### Interfaz Frontend *(Próximamente)*

Interfaz de usuario basada en web para interacción fácil con la plataforma.

**Características Planificadas:**
- Mapas interactivos con capas de riesgo y detecciones
- Carga manual de imágenes por usuarios con geolocalización
- Mapas de calor para visualización de zonas críticas
- Dashboards con estadísticas y series temporales
- Sistema de alertas tempranas basado en índices de riesgo
- Exportación de reportes en PDF/CSV
- Participación ciudadana con validación comunitaria

## Quick Start

Currently, the YOLO service is fully functional. To get started:

```bash
git clone https://github.com/yourusername/sentrix.git
cd sentrix/yolo-service
pip install -r requirements.txt

# Run detection on an image
python main.py detect --model yolo11s-seg.pt --source your_image.jpg
```

For detailed instructions, see the [YOLO Service README](./yolo-service/README.md).

## Detection Capabilities

| Class | Risk Level | Description |
|-------|------------|-------------|
| Trash/Debris | Medium | Waste accumulation with water retention potential |
| Deteriorated Streets | High | Irregular surfaces facilitating puddle formation |
| Water Accumulations | High | Visible stagnant water, direct breeding habitat |
| Holes/Depressions | High | Cavities that retain rainwater |

## Risk Assessment

The platform evaluates epidemiological risk based on detected breeding sites:

- **HIGH**: ≥3 high-risk sites OR ≥1 high-risk + ≥3 medium-risk sites
- **MEDIUM**: ≥1 high-risk site OR ≥3 medium-risk sites
- **LOW**: ≥1 medium-risk site
- **MINIMAL**: No risk sites detected

## Estado de Desarrollo

| Componente | Estado | Descripción | Cronograma |
|-----------|--------|-------------|------------|
| **Servicio YOLO** | **Completo** | Detección IA con YOLOv11 funcional | ✅ Julio-Agosto 2024 |
| **Backend API** | **En Desarrollo** | API REST + base de datos geoespacial | 🚧 Septiembre 2024 |
| **Frontend Web** | **Planificado** | Mapas interactivos y dashboards | 📋 Octubre 2024 |
| **Integración Meteorológica** | **Planificado** | APIs clima + índices de riesgo | 📋 Octubre 2024 |
| **App Móvil** | **Futuro** | Aplicación para trabajo de campo | 🔮 2025 |

### Roadmap del Proyecto

**Fase 1 (Completa):** Core IA - Detección automatizada de criaderos
**Fase 2 (En Progreso):** Plataforma Web - Visualización y gestión de datos
**Fase 3 (Planificada):** Análisis Contextual - Integración meteorológica y alertas
**Fase 4 (Futura):** Escalamiento - Apps móviles y participación ciudadana masiva

## Investigación y Uso Académico

Sentrix fue desarrollado como proyecto de investigación aplicada en inteligencia artificial para salud pública, enfocado en la prevención del dengue mediante tecnología accesible y escalable.

### Objetivos de Investigación

**Objetivo General:** Desarrollar e implementar un sistema de inteligencia artificial y plataforma web para la detección, geolocalización y análisis de focos de *Aedes aegypti* en zonas urbanas.

**Objetivos Específicos:**
- Implementar modelos YOLOv11/YOLOv12 para detección de criaderos
- Integrar variables ambientales (temperatura, humedad, precipitaciones)
- Desarrollar índices de riesgo contextualizados por zona geográfica
- Validar el sistema mediante comparación con inspecciones humanas
- Crear herramientas de participación ciudadana efectivas

### Metodología de Investigación

1. **Recolección de Datos:** Imágenes aéreas (drones) y terrestres con diversidad de condiciones
2. **Entrenamiento IA:** Arquitecturas CNN con técnicas de data augmentation
3. **Integración Ambiental:** APIs meteorológicas para calcular índices de riesgo
4. **Validación en Campo:** Comparación con inspecciones manuales de expertos
5. **Implementación Piloto:** Pruebas en zonas urbanas reales

### Publicaciones y Citas

Al usar Sentrix en trabajo académico, por favor cita:

```bibtex
@software{sentrix2025,
  title={Sentrix: AI-Powered Disease Vector Detection Platform},
  author={[Your Name]},
  year={2025},
  url={https://github.com/yourusername/sentrix}
}
```

### Limitaciones y Consideraciones

- **Especificidad Geográfica**: Modelos entrenados con datos regionales específicos
- **Tamaño del Dataset**: Datos de entrenamiento limitados (73 imágenes total)
- **Dependencia Climática**: Restricciones legales y meteorológicas para uso de drones
- **Validación Requerida**: Los resultados necesitan verificación por especialistas en salud pública
- **Cobertura Logística**: Limitada a zonas con acceso para captura o carga de datos
- **Calidad de Imágenes**: El rendimiento varía con condiciones de iluminación y clima

### Resultados Esperados

- Modelo de IA con alta precisión para detección de superficies con agua estancada
- Índice de riesgo contextualizado para anticipar zonas de alta probabilidad de proliferación
- Plataforma web intuitiva para difusión de información y toma de decisiones
- Sistema validado en condiciones reales, listo para implementación piloto
- Herramientas de participación ciudadana para involucramiento comunitario

## Contribuciones

¡Damos la bienvenida a contribuciones en cualquier componente de la plataforma Sentrix!

- **Mejoras AI/ML**: Mejorar modelos de detección y algoritmos
- **Desarrollo Backend**: Ayudar a construir el servicio API
- **Desarrollo Frontend**: Crear interfaces web amigables
- **Documentación**: Mejorar guías y tutoriales
- **Testing**: Agregar cobertura de pruebas y validación

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para guías detalladas.

## Impacto en Salud Pública

Sentrix busca apoyar:

- **Vigilancia automatizada** de sitios de reproducción de vectores de enfermedad
- **Sistemas de alerta temprana** para brotes de enfermedades
- **Optimización de recursos** para intervenciones de salud pública
- **Toma de decisiones basada en datos** en planificación urbana
- **Conciencia y educación** en salud comunitaria

## Licencia

Este proyecto está licenciado bajo la Licencia MIT con términos adicionales para uso académico. Ver [LICENSE](LICENSE) para detalles.

## Contacto y Soporte

- **Issues y Bugs**: [GitHub Issues](https://github.com/yourusername/sentrix/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/yourusername/sentrix/discussions)
- **Colaboración Académica**: [your.email@institution.edu]
- **Documentación**: [Project Wiki](https://github.com/yourusername/sentrix/wiki)

## Agradecimientos

- Equipo de Ultralytics por el framework YOLOv11
- Organizaciones de salud pública que proporcionan experiencia en el dominio
- Comunidades de investigación en visión por computadora y epidemiología
- Contribuidores y colaboradores de código abierto

---

**Versión Actual**: 2.0.0 (Servicio YOLO)
**Estado del Proyecto**: Fase 1 completa, desarrollando Fase 2 (Backend + Frontend)
**Cronograma**: Julio 2024 - Octubre 2024 (4 meses de desarrollo)
**Última Actualización**: Enero 2025

### Cronograma de Desarrollo

| Mes | Actividad Principal |
|-----|-------------------|
| **Julio 2024** | ✅ Organización dataset + diseño modelo IA |
| **Agosto 2024** | ✅ Entrenamiento modelo + desarrollo inicial web |
| **Septiembre 2024** | 🚧 Integración IA + plataforma + pruebas preliminares |
| **Octubre 2024** | 📋 Validación + mejoras + documentación final |