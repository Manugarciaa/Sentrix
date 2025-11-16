import React from 'react'
import { Cpu, Map, Brain, Users } from 'lucide-react'

const AboutSentrix: React.FC = () => {
  return (
    <section className="bg-background py-16 sm:py-20 md:py-24 lg:py-28">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 grid md:grid-cols-[2fr_1fr] gap-8 sm:gap-12 md:gap-16 lg:gap-20 items-start">
        {/* Lado izquierdo — descripción y tecnología */}
        <div className="flex flex-col justify-start">
          {/* Header */}
          <h2 id="about-sentrix" className="scroll-mt-24 text-2xl sm:text-3xl md:text-4xl font-bold text-foreground mb-4">
            Acerca de <span className="text-primary">Sentrix</span>
          </h2>
          <p className="text-base sm:text-lg text-muted-foreground mb-6 italic">
            Nace de <em>sentinel</em> y el sufijo tecnológico “-x”. Significa “vigilancia extendida y automatizada, con componente de análisis”. Su tono es innovador, corto y con fuerza de marca.
          </p>
          <p className="text-muted-foreground leading-relaxed mb-10">
            Un sistema centinela que vigila y una red que conecta. Sentrix combina vigilancia epidemiológica
            con inteligencia artificial para prevenir brotes de dengue en Tucumán.
          </p>

          {/* Tecnología */}
          <h3 className="text-lg sm:text-xl font-semibold text-foreground mb-4">Tecnología</h3>
          <p className="text-muted-foreground mb-6">
            Implementación de <span className="font-semibold text-foreground">YOLO v11</span> para detección automática
            de criaderos potenciales en imágenes, combinada con análisis geoespacial en tiempo real.
          </p>

          <div className="flex flex-wrap gap-3">
            {['Deep Learning', 'Mapas de calor', 'Geolocalización', 'Reportes ciudadanos'].map((t, i) => (
              <span
                key={i}
                className="px-4 py-2 bg-card border border-border rounded-lg text-muted-foreground text-sm"
              >
                {t}
              </span>
            ))}
          </div>
        </div>

        {/* Lado derecho — esquema de impacto / íconos */}
        <div className="grid grid-cols-2 gap-4 sm:gap-6 md:gap-8 auto-rows-min">
          {[
            { icon: Cpu, label: 'IA en imágenes', color: 'text-primary' },
            { icon: Map, label: 'Mapa geoespacial', color: 'text-secondary' },
            { icon: Brain, label: 'Aprendizaje continuo', color: 'text-accent-600' },
            { icon: Users, label: 'Participación ciudadana', color: 'text-primary' },
          ].map((item, i) => {
            const Icon = item.icon
            return (
              <div
                key={i}
                className="bg-card/40 p-4 sm:p-6 md:p-8 rounded-xl text-center border border-border shadow-sm flex flex-col justify-center items-center"
              >
                <Icon className={`w-8 h-8 sm:w-9 sm:h-9 md:w-10 md:h-10 mb-4 ${item.color}`} />
                <p className="font-semibold text-foreground">{item.label}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

export default AboutSentrix
