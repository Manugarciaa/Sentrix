import React from 'react'
import { CheckCircle, Database, Cpu, BarChart3, Users, BookOpen } from 'lucide-react'

const MethodologyPage: React.FC = () => {
  const methodology_steps = [
    {
      phase: "Fase 1",
      title: "Recolección y Preparación de Datos",
      items: [
        "Dataset de 858MB con imágenes de Tucumán y Yerba Buena",
        "Etiquetado manual con Label Studio: Basura, Calles mal hechas, Charcos/Cúmulo de agua, Huecos",
        "Gestión con Git LFS para archivos grandes"
      ]
    },
    {
      phase: "Fase 2",
      title: "Entrenamiento del Modelo IA",
      items: [
        "Configuración YOLOv11 con framework Ultralytics",
        "Múltiples arquitecturas (nano, small, medium, large)",
        "Métricas: mAP, precisión, recall, confianza por detección",
        "Segmentación de instancias para precisión pixel-level"
      ]
    },
    {
      phase: "Fase 3",
      title: "Desarrollo de Arquitectura de Sistema",
      items: [
        "Backend FastAPI con microservicios (puerto 8000)",
        "Servicio YOLO independiente (puerto 8001)",
        "Base de datos PostgreSQL con Supabase",
        "Frontend React con TypeScript (puerto 3000)"
      ]
    },
    {
      phase: "Fase 4",
      title: "Evaluación y Validación",
      items: [
        "Tests automatizados con pytest",
        "Validación de integración end-to-end",
        "Métricas de performance del sistema",
        "Evaluación de precisión epidemiológica"
      ]
    }
  ]

  const technical_specs = [
    {
      category: "Modelos de IA",
      specs: [
        "YOLOv11 para segmentación de instancias",
        "PyTorch + Ultralytics framework",
        "4 clases de detección entrenadas",
        "Soporte GPU/CPU automático"
      ]
    },
    {
      category: "Backend Architecture",
      specs: [
        "FastAPI + SQLAlchemy + Alembic",
        "PostgreSQL con Supabase hosting",
        "Arquitectura de microservicios",
        "API REST documentada con OpenAPI"
      ]
    },
    {
      category: "Frontend Technology",
      specs: [
        "React 18 + TypeScript + Vite",
        "Tailwind CSS + Headless UI",
        "Zustand + React Query",
        "React Leaflet para mapas"
      ]
    }
  ]

  return (
    <div className="bg-white">
      {/* Hero Section */}
      <section className="py-20 bg-gray-50">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="inline-flex items-center rounded-full bg-primary-50 px-4 py-1.5 text-sm font-medium text-primary-700 mb-8">
              <BookOpen className="h-4 w-4 mr-2" />
              Metodología de Investigación
            </div>
            <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl mb-8">
              Metodología Científica
            </h1>
            <p className="mx-auto max-w-3xl text-xl text-gray-600 leading-relaxed">
              Descripción detallada de la metodología empleada en el desarrollo del sistema Sentrix,
              desde la recolección de datos hasta la implementación y evaluación final.
            </p>
          </div>
        </div>
      </section>

      {/* Methodology Steps */}
      <section className="py-20">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">
              Fases de Desarrollo
            </h2>
            <p className="text-xl text-gray-600 text-center max-w-3xl mx-auto">
              Metodología iterativa de 4 fases que abarca desde la preparación de datos
              hasta la validación completa del sistema.
            </p>
          </div>

          <div className="space-y-12">
            {methodology_steps.map((step, index) => (
              <div key={index} className="flex flex-col lg:flex-row lg:items-start lg:gap-8">
                <div className="flex-shrink-0 mb-6 lg:mb-0">
                  <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-primary-100 text-primary-600 font-bold text-lg">
                    {step.phase}
                  </div>
                </div>
                <div className="flex-grow">
                  <div className="bg-white border border-gray-200 rounded-2xl p-8 shadow-sm">
                    <h3 className="text-2xl font-bold text-gray-900 mb-6">
                      {step.title}
                    </h3>
                    <ul className="space-y-3">
                      {step.items.map((item, itemIndex) => (
                        <li key={itemIndex} className="flex items-start">
                          <CheckCircle className="h-5 w-5 text-primary-600 mr-3 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-700 leading-relaxed">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Technical Specifications */}
      <section className="py-20 bg-gray-50">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              Especificaciones Técnicas
            </h2>
            <p className="mx-auto max-w-2xl text-xl text-gray-600">
              Tecnologías y frameworks utilizados en cada componente del sistema.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            {technical_specs.map((category, index) => {
              const icons = [Database, Cpu, Users]
              const Icon = icons[index]
              return (
                <div key={index} className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
                  <div className="flex items-center mb-6">
                    <div className="h-12 w-12 rounded-xl bg-primary-100 flex items-center justify-center mr-4">
                      <Icon className="h-6 w-6 text-primary-600" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900">
                      {category.category}
                    </h3>
                  </div>
                  <ul className="space-y-3">
                    {category.specs.map((spec, specIndex) => (
                      <li key={specIndex} className="flex items-start">
                        <div className="h-2 w-2 bg-primary-600 rounded-full mr-3 mt-2 flex-shrink-0" />
                        <span className="text-gray-700 text-sm leading-relaxed">{spec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Results Section */}
      <section className="py-20">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">
              Resultados Alcanzados
            </h2>
            <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4 mb-12">
              <div className="p-8 bg-white rounded-2xl shadow-lg border border-gray-100">
                <div className="text-4xl font-bold text-primary-600 mb-2">856MB</div>
                <div className="text-gray-600">Dataset Procesado</div>
              </div>
              <div className="p-8 bg-white rounded-2xl shadow-lg border border-gray-100">
                <div className="text-4xl font-bold text-primary-600 mb-2">4</div>
                <div className="text-gray-600">Tipos de Criaderos</div>
              </div>
              <div className="p-8 bg-white rounded-2xl shadow-lg border border-gray-100">
                <div className="text-4xl font-bold text-primary-600 mb-2">56.1%</div>
                <div className="text-gray-600">Cobertura GPS</div>
              </div>
              <div className="p-8 bg-white rounded-2xl shadow-lg border border-gray-100">
                <div className="text-4xl font-bold text-primary-600 mb-2">3</div>
                <div className="text-gray-600">Puertos del Sistema</div>
              </div>
            </div>

            <div className="bg-primary-50 rounded-2xl p-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Sistema Completamente Funcional
              </h3>
              <p className="text-gray-700 leading-relaxed max-w-3xl mx-auto">
                El proyecto resultó en un sistema completo y operacional que integra detección IA,
                backend robusto, interfaz web interactiva y algoritmos de evaluación epidemiológica,
                demostrando la viabilidad de la metodología propuesta para la detección automatizada
                de criaderos de <em>Aedes aegypti</em>.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default MethodologyPage