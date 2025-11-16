import React from 'react'

const AboutDengue: React.FC = () => {
  return (
    <section className="bg-background py-16 sm:py-20 md:py-24">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-16 text-center">
          <h2 id="dengue" className="scroll-mt-24 text-3xl sm:text-4xl font-bold text-foreground mb-3">
            Información sobre el dengue
          </h2>
          <p className="text-lg text-muted-foreground">
            Conocé cómo se transmite y cómo prevenirlo
          </p>
        </div>

        {/* Contenido */}
        <div className="space-y-12">

          {/* Transmisión */}
          <div className="border-l-4 border-status-danger-bg pl-6 hover:translate-x-1 transition-transform duration-300">
            <h3 className="text-xl sm:text-2xl font-semibold text-foreground mb-3">Transmisión</h3>
            <p className="text-muted-foreground mb-4 leading-relaxed">
              El <em>Aedes aegypti</em> se reproduce en agua limpia y estancada. 
              No se transmite de persona a persona: el mosquito debe picar primero 
              a una persona infectada para luego contagiar a otra.
            </p>
            <p className="text-sm text-muted-foreground italic">
              Una sola hembra puede poner hasta <strong>400 huevos</strong>, 
              que pueden permanecer viables durante varios meses.
            </p>
          </div>

          {/* Síntomas */}
          <div className="border-l-4 border-status-warning-bg pl-6 hover:translate-x-1 transition-transform duration-300">
            <h3 className="text-xl sm:text-2xl font-semibold text-foreground mb-3">Síntomas</h3>
            <p className="text-muted-foreground mb-4 leading-relaxed">
              Los síntomas suelen aparecer entre <strong>5 y 7 días</strong> después de la picadura del mosquito:
            </p>
            <ul className="space-y-2 text-muted-foreground list-disc list-inside">
              <li>Fiebre alta de inicio súbito (hasta 40°C)</li>
              <li>Dolor intenso de cabeza y detrás de los ojos</li>
              <li>Dolores musculares y articulares</li>
              <li>Náuseas, vómitos y erupciones en la piel</li>
            </ul>
          </div>

          {/* Prevención */}
          <div className="border-l-4 border-primary pl-6 hover:translate-x-1 transition-transform duration-300">
            <h3 className="text-xl sm:text-2xl font-semibold text-foreground mb-3">Prevención</h3>
            <p className="text-muted-foreground mb-4 leading-relaxed">
              El <strong>80%</strong> de los criaderos se encuentran en los hogares. 
              Evitá la acumulación de agua en los siguientes lugares:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-2 text-muted-foreground">
              <div className="space-y-2">
                <p>• Macetas y platos debajo de las plantas</p>
                <p>• Baldes y recipientes en desuso</p>
                <p>• Llantas abandonadas</p>
              </div>
              <div className="space-y-2">
                <p>• Canaletas obstruidas</p>
                <p>• Tanques sin tapa</p>
                <p>• Bebederos de mascotas</p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  )
}

export default AboutDengue
