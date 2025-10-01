import React from 'react'
import { Mail, Clock } from 'lucide-react'

const ContactPage: React.FC = () => {
  return (
    <div className="bg-white min-h-screen">
      <section className="py-20">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="mx-auto h-24 w-24 rounded-full bg-gray-100 flex items-center justify-center mb-8">
              <Mail className="h-12 w-12 text-gray-400" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-6">
              Contacto
            </h1>
            <div className="inline-flex items-center rounded-full bg-orange-100 px-6 py-2 text-sm font-medium text-orange-800 mb-8">
              <Clock className="h-4 w-4 mr-2" />
              Sección en desarrollo
            </div>
            <p className="mx-auto max-w-2xl text-xl text-gray-600 leading-relaxed">
              Esta sección incluirá información de contacto completa,
              formularios y datos del equipo de investigación.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}

export default ContactPage