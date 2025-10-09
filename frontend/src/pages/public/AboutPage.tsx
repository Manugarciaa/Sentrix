import React from 'react'
import { Info, Clock } from 'lucide-react'

const AboutPage: React.FC = () => {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-b from-white to-blue-50/30 min-h-screen flex items-center pt-28 pb-12 sm:pt-32 sm:pb-16">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="mx-auto h-24 w-24 rounded-full bg-primary-50 flex items-center justify-center mb-8">
              <Info className="h-12 w-12 text-primary-600" />
            </div>
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight text-gray-900 mb-6">
              Acerca de Sentrix
            </h1>
            <div className="inline-flex items-center rounded-full bg-warning-100 px-6 py-2 text-sm font-medium text-warning-800 mb-8">
              <Clock className="h-4 w-4 mr-2" />
              Sección en desarrollo
            </div>
            <p className="mx-auto max-w-2xl text-base sm:text-lg text-gray-700 leading-relaxed">
              Esta sección contendrá información detallada sobre el proyecto Sentrix,
              el equipo de desarrollo y los objetivos de la investigación.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}

export default AboutPage