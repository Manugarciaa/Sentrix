import React from 'react'

const PublicMapPage: React.FC = () => {
  return (
    <div className="py-12">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Mapa de Riesgos</h1>
        <div className="prose max-w-none">
          <p className="text-lg text-gray-600">
            Mapa público con datos agregados de focos de dengue reportados.
          </p>
        </div>
      </div>
    </div>
  )
}

export default PublicMapPage