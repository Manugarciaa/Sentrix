import React from 'react'
import { CheckCircle, Users, Zap, Shield, Award, Target } from 'lucide-react'

const AboutPage: React.FC = () => {
  const values = [
    {
      icon: Target,
      title: 'Precisión',
      description: 'Utilizamos tecnología de vanguardia para garantizar detecciones precisas y confiables.',
    },
    {
      icon: Users,
      title: 'Colaboración',
      description: 'Fomentamos la participación activa de la comunidad en la prevención del dengue.',
    },
    {
      icon: Zap,
      title: 'Rapidez',
      description: 'Análisis en tiempo real para respuestas inmediatas ante situaciones de riesgo.',
    },
    {
      icon: Shield,
      title: 'Protección',
      description: 'Nuestro objetivo es proteger la salud pública mediante la prevención efectiva.',
    },
  ]

  const features = [
    'Detección automática de criaderos usando IA',
    'Análisis de imágenes con geolocalización',
    'Sistema de alertas temprano',
    'Plataforma colaborativa para la comunidad',
    'Reportes epidemiológicos detallados',
    'Validación por expertos en salud pública',
  ]

  return (
    <div className="bg-white">
      {/* Hero Section */}
      <section className="py-20 bg-gray-50">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl mb-8">
              Proyecto de Investigación Sentrix
            </h1>
            <p className="mx-auto max-w-3xl text-xl text-gray-600 leading-relaxed">
              Sistema experimental de detección automatizada de criaderos de <em>Aedes aegypti</em> mediante
              modelos de inteligencia artificial YOLOv11, desarrollado como proyecto de tesis de grado
              en la Universidad Nacional de Tucumán.
            </p>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-20">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-2 lg:gap-16 lg:items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-8">
                Objetivos de la Investigación
              </h2>
              <div className="space-y-6">
                <p className="text-lg text-gray-600 leading-relaxed">
                  <strong>Objetivo General:</strong> Desarrollar un sistema basado en inteligencia artificial
                  para el reconocimiento de imágenes que permita identificar zonas de alto riesgo de
                  proliferación del mosquito <em>Aedes aegypti</em>, principal vector del virus del dengue.
                </p>
                <p className="text-lg text-gray-600 leading-relaxed">
                  <strong>Metodología:</strong> Implementación de modelos YOLOv11 para segmentación de instancias,
                  entrenados con dataset de 858MB de imágenes etiquetadas de Tucumán y Yerba Buena,
                  integrados en una arquitectura de microservicios para análisis epidemiológico automatizado.
                </p>
              </div>
            </div>
            <div className="mt-12 lg:mt-0">
              <div className="bg-primary-50 rounded-2xl p-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">
                  Componentes del Sistema Desarrollado
                </h3>
                <ul className="space-y-4">
                  <li className="flex items-start">
                    <CheckCircle className="h-6 w-6 text-primary-600 mr-3 mt-0.5" />
                    <span className="text-gray-700">Modelos YOLOv11 para detección de 4 tipos de criaderos</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="h-6 w-6 text-primary-600 mr-3 mt-0.5" />
                    <span className="text-gray-700">Backend FastAPI con base de datos PostgreSQL</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="h-6 w-6 text-primary-600 mr-3 mt-0.5" />
                    <span className="text-gray-700">Algoritmo de evaluación de riesgo epidemiológico</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="h-6 w-6 text-primary-600 mr-3 mt-0.5" />
                    <span className="text-gray-700">Interfaz web React con visualización geoespacial</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="h-6 w-6 text-primary-600 mr-3 mt-0.5" />
                    <span className="text-gray-700">Extracción automática de metadatos GPS</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="h-6 w-6 text-primary-600 mr-3 mt-0.5" />
                    <span className="text-gray-700">Sistema de testing y validación automatizada</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-20 bg-gray-50">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              Nuestros Valores
            </h2>
            <p className="mx-auto max-w-2xl text-xl text-gray-600">
              Los principios que guían nuestro trabajo y nuestra misión de proteger la salud pública.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4">
            {values.map((value, index) => {
              const Icon = value.icon
              return (
                <div key={index} className="text-center">
                  <div className="mx-auto h-16 w-16 rounded-2xl bg-primary-100 flex items-center justify-center mb-6">
                    <Icon className="h-8 w-8 text-primary-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">{value.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{value.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Impact Section */}
      <section className="py-20">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">
              Nuestro Impacto
            </h2>
            <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
              <div className="p-8 bg-white rounded-2xl shadow-lg border border-gray-100">
                <div className="text-4xl font-bold text-primary-600 mb-2">1,234+</div>
                <div className="text-gray-600">Análisis Realizados</div>
              </div>
              <div className="p-8 bg-white rounded-2xl shadow-lg border border-gray-100">
                <div className="text-4xl font-bold text-primary-600 mb-2">456+</div>
                <div className="text-gray-600">Criaderos Detectados</div>
              </div>
              <div className="p-8 bg-white rounded-2xl shadow-lg border border-gray-100">
                <div className="text-4xl font-bold text-primary-600 mb-2">15</div>
                <div className="text-gray-600">Distritos Cubiertos</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-20 bg-gray-50">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">
              Equipo de Investigación
            </h2>
            <p className="mx-auto max-w-2xl text-xl text-gray-600 mb-16">
              Proyecto desarrollado por estudiantes de la Universidad Nacional de Tucumán
              bajo la supervisión del Ing. Ernesto Rico.
            </p>
            <div className="grid gap-6 md:grid-cols-2">
              <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
                <div className="flex items-center justify-center mb-6">
                  <Users className="h-12 w-12 text-primary-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  Estudiantes Investigadores
                </h3>
                <ul className="text-gray-600 leading-relaxed space-y-2">
                  <li>• <strong>Manuel Antonio García</strong> - Desarrollo backend y arquitectura</li>
                  <li>• <strong>Ricardo Laudani</strong> - Modelos IA y procesamiento</li>
                  <li>• <strong>Mercedes Warnes</strong> - Frontend y análisis de datos</li>
                </ul>
              </div>
              <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
                <div className="flex items-center justify-center mb-6">
                  <Award className="h-12 w-12 text-primary-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  Director de Tesis
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  <strong>Ing. Ernesto Rico</strong><br/>
                  Supervisor académico responsable de la dirección técnica y metodológica
                  del proyecto de investigación.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default AboutPage