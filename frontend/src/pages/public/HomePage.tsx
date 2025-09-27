import React from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { routes } from '@/lib/config'
import { Search, Upload, MapPin, Users, Shield, Zap, ArrowRight, Play, CheckCircle, TrendingUp, AlertTriangle } from 'lucide-react'

const HomePage: React.FC = () => {
  const features = [
    {
      icon: Search,
      title: 'Detección con IA',
      description: 'Utiliza inteligencia artificial avanzada para detectar criaderos de Aedes aegypti en imágenes.',
    },
    {
      icon: MapPin,
      title: 'Geolocalización',
      description: 'Mapea automáticamente los sitios de riesgo con coordenadas GPS precisas.',
    },
    {
      icon: Users,
      title: 'Participación Ciudadana',
      description: 'Permite a la comunidad reportar focos potenciales de manera colaborativa.',
    },
    {
      icon: Shield,
      title: 'Validación Experta',
      description: 'Sistema de revisión por especialistas para garantizar la precisión de las detecciones.',
    },
    {
      icon: Upload,
      title: 'Fácil de Usar',
      description: 'Interfaz intuitiva para subir imágenes y obtener resultados instantáneos.',
    },
    {
      icon: Zap,
      title: 'Tiempo Real',
      description: 'Análisis rápido y notificaciones inmediatas para respuesta oportuna.',
    },
  ]

  const stats = [
    { label: 'Imágenes Procesadas', value: '1,234+' },
    { label: 'Criaderos Detectados', value: '456+' },
    { label: 'Precisión del Modelo', value: '87.3%' },
    { label: 'Dataset Training', value: '858MB' },
  ]

  return (
    <div className="flex flex-col">
      {/* Hero Section - Modern Minimalist */}
      <section className="relative bg-white">
        <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6 lg:px-8 lg:py-28">
          <div className="text-center">
            <div className="inline-flex items-center rounded-full bg-primary-50 px-4 py-1.5 text-sm font-medium text-primary-700 mb-8">
              <CheckCircle className="h-4 w-4 mr-2" />
              Proyecto de Tesis - UNT 2025
            </div>
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl lg:text-7xl">
              Sistema Sentrix
              <span className="block text-primary-600">Detección IA</span>
            </h1>
            <p className="mx-auto mt-8 max-w-2xl text-xl text-gray-600 leading-relaxed">
              Sistema experimental de detección automatizada de criaderos de <em>Aedes aegypti</em>
              mediante modelos YOLOv11, desarrollado como proyecto de investigación académica.
            </p>
            <div className="mt-12 flex flex-col sm:flex-row gap-4 justify-center">
              <Link to={routes.public.about}>
                <Button size="lg" className="bg-primary-600 text-white hover:bg-primary-700 px-8 py-4 text-lg">
                  Ver Investigación
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link to={routes.public.report}>
                <Button size="lg" variant="outline" className="border-gray-300 text-gray-700 hover:bg-gray-50 px-8 py-4 text-lg">
                  <Play className="mr-2 h-5 w-5" />
                  Probar Sistema
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section - Minimalist */}
      <section className="bg-gray-50 py-16">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl font-bold text-gray-900 mb-2">{stat.value}</div>
                <div className="text-sm font-medium text-gray-600 uppercase tracking-wide">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section - Modern Grid */}
      <section className="py-24 bg-white">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl mb-6">
              Tecnología Avanzada para la Prevención
            </h2>
            <p className="mx-auto max-w-2xl text-xl text-gray-600 leading-relaxed">
              Sistema integral que combina inteligencia artificial, participación ciudadana y
              validación experta.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-12 md:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <div key={index} className="group">
                  <div className="flex flex-col items-center text-center space-y-4">
                    <div className="h-16 w-16 rounded-2xl bg-primary-100 flex items-center justify-center group-hover:bg-primary-200 transition-colors duration-200">
                      <Icon className="h-8 w-8 text-primary-600" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900">{feature.title}</h3>
                    <p className="text-gray-600 leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* CTA Section - Modern */}
      <section className="bg-gray-900">
        <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl mb-6">
              ¿Listo para hacer la diferencia?
            </h2>
            <p className="mx-auto max-w-2xl text-xl text-gray-300 leading-relaxed">
              Únete a nuestra comunidad y ayuda a prevenir el dengue en tu localidad.
              Cada reporte cuenta en la lucha contra esta enfermedad.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
              <Link to={routes.public.register}>
                <Button size="lg" className="bg-primary-600 text-white hover:bg-primary-700 px-8 py-4 text-lg">
                  Crear Cuenta Gratuita
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link to={routes.public.map}>
                <Button size="lg" variant="outline" className="border-gray-600 text-gray-300 hover:bg-gray-800 px-8 py-4 text-lg">
                  Ver Mapa de Riesgos
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* About Section - Modern Two Column */}
      <section className="py-24 bg-gray-50">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-2 lg:gap-16 lg:items-center">
            <div>
              <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl mb-8">
                ¿Qué es el Dengue?
              </h2>
              <div className="space-y-6">
                <p className="text-xl text-gray-600 leading-relaxed">
                  El dengue es una enfermedad viral transmitida por mosquitos del género Aedes aegypti.
                  Es uno de los principales problemas de salud pública en regiones tropicales y subtropicales.
                </p>
                <p className="text-xl text-gray-600 leading-relaxed">
                  La prevención es la clave: eliminando los criaderos de mosquitos podemos
                  reducir significativamente la transmisión de la enfermedad.
                </p>
              </div>
              <div className="mt-10">
                <Link to={routes.public.prevention}>
                  <Button className="bg-primary-600 text-white hover:bg-primary-700 px-6 py-3">
                    Aprender Sobre Prevención
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
            <div className="mt-12 lg:mt-0">
              <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
                <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
                  <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
                  Síntomas del Dengue
                </h3>
                <ul className="space-y-4">
                  <li className="flex items-center">
                    <div className="h-2 w-2 bg-red-500 rounded-full mr-4" />
                    <span className="text-gray-700">Fiebre alta (40°C)</span>
                  </li>
                  <li className="flex items-center">
                    <div className="h-2 w-2 bg-red-500 rounded-full mr-4" />
                    <span className="text-gray-700">Dolor de cabeza intenso</span>
                  </li>
                  <li className="flex items-center">
                    <div className="h-2 w-2 bg-red-500 rounded-full mr-4" />
                    <span className="text-gray-700">Dolor detrás de los ojos</span>
                  </li>
                  <li className="flex items-center">
                    <div className="h-2 w-2 bg-red-500 rounded-full mr-4" />
                    <span className="text-gray-700">Dolores musculares y articulares</span>
                  </li>
                  <li className="flex items-center">
                    <div className="h-2 w-2 bg-red-500 rounded-full mr-4" />
                    <span className="text-gray-700">Erupción cutánea</span>
                  </li>
                </ul>
                <div className="mt-6 p-4 bg-red-50 rounded-lg">
                  <p className="text-sm text-red-800 font-medium">
                    Si presentas estos síntomas, consulta inmediatamente a un profesional de la salud.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage