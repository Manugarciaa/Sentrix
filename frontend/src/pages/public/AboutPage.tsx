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
              Acerca de Sentrix
            </h1>
            <p className="mx-auto max-w-3xl text-xl text-gray-600 leading-relaxed">
              Somos una plataforma integral que combina inteligencia artificial, participación ciudadana
              y expertise científico para crear la red de prevención del dengue más avanzada de la región.
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
                Nuestra Misión
              </h2>
              <div className="space-y-6">
                <p className="text-lg text-gray-600 leading-relaxed">
                  Reducir significativamente la incidencia del dengue mediante tecnología innovadora
                  que permite la detección temprana y control efectivo de criaderos de Aedes aegypti.
                </p>
                <p className="text-lg text-gray-600 leading-relaxed">
                  Creemos que la prevención es la clave para combatir esta enfermedad, y por eso
                  desarrollamos herramientas que empoderan tanto a las autoridades sanitarias como
                  a los ciudadanos.
                </p>
              </div>
            </div>
            <div className="mt-12 lg:mt-0">
              <div className="bg-primary-50 rounded-2xl p-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">
                  ¿Qué nos hace diferentes?
                </h3>
                <ul className="space-y-4">
                  {features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <CheckCircle className="h-6 w-6 text-primary-600 mr-3 mt-0.5" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
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
              Nuestro Equipo
            </h2>
            <p className="mx-auto max-w-2xl text-xl text-gray-600 mb-16">
              Un equipo multidisciplinario de expertos en salud pública, inteligencia artificial
              y desarrollo tecnológico comprometidos con la prevención del dengue.
            </p>
            <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
              <div className="flex items-center justify-center mb-6">
                <Award className="h-12 w-12 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Experiencia Multidisciplinaria
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Nuestro equipo combina expertise en epidemiología, machine learning, desarrollo de software
                y salud pública para crear soluciones innovadoras y efectivas en la lucha contra el dengue.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default AboutPage