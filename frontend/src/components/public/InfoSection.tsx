import React from 'react'
import { Droplets, Smartphone, Users } from 'lucide-react'

const InfoSection: React.FC = () => {
  const steps = [
    {
      icon: Droplets,
      title: 'Detectá agua estancada',
      description: 'Revisá baldes, botellas o canaletas con agua limpia y quieta.',
    },
    {
      icon: Smartphone,
      title: 'Reportá desde tu celular',
      description: 'Subí una foto con ubicación para ayudar a detectar criaderos.',
    },
    {
      icon: Users,
      title: 'Ayudá a prevenir',
      description: 'Tus reportes colaboran con las acciones municipales.',
    },
  ]

  return (
    <section className="bg-background py-12 sm:py-16 md:py-20 lg:py-24">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4">Cómo funciona la prevención</h2>
        <p className="text-base sm:text-lg text-muted-foreground mb-16">
          Tres pasos simples para ayudar a tu comunidad
        </p>

        <div className="flex flex-col md:flex-row items-center justify-center gap-12">
          {steps.map((s, i) => {
            const Icon = s.icon
            return (
              <div key={i} className="flex flex-col items-center max-w-xs relative">
                <div className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8 text-primary" />
                </div>
                <h3 className="text-lg sm:text-xl font-semibold mb-2">{s.title}</h3>
                <p className="text-muted-foreground text-sm">{s.description}</p>
                {i < steps.length - 1 && (
                  <div className="hidden md:block absolute top-8 right-[-80px] w-16 h-[2px] bg-border"></div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

export default InfoSection
