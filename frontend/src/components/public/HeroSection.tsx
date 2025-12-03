import React from 'react'
import { Button } from '@/components/ui/Button'
import { CheckCircle, ArrowRight, MapPin } from 'lucide-react'

const HeroSection: React.FC = () => {
  // Smooth scroll handler for section navigation
  const handleScrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)

    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  return (
    <section
      id="hero"
      className="relative bg-background overflow-hidden min-h-screen flex items-center pt-16"
    >
      <div className="relative mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 w-full pb-20 sm:pb-28 lg:pb-32">
        <div className="text-center space-y-6 sm:space-y-8">

          {/* Badge superior */}
          <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 dark:bg-primary/20 px-3 py-1.5 shadow-sm border border-primary/30">
            <CheckCircle className="h-4 w-4 text-primary flex-shrink-0" />
            <span className="text-primary font-medium text-xs sm:text-sm">
              Proyecto Tesis 2025
            </span>
          </div>


          {/* Título principal */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-foreground leading-tight sm:leading-snug md:leading-snug lg:leading-snug">
            Vigilancia inteligente<br />
            <span className="text-primary">del dengue en Tucumán</span>
          </h1>

          {/* Subtítulo */}
          <p className="mx-auto max-w-2xl text-lg sm:text-xl md:text-2xl leading-relaxed text-muted-foreground px-4">
            Sistema de detección temprana con IA para la prevención de criaderos de <em>Aedes aegypti</em>
          </p>

          {/* CTAs principales */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-6 sm:pt-8 px-4">
            <Button
              size="lg"
              onClick={() => handleScrollToSection('demo')}
              className="group bg-primary hover:bg-primary/90 dark:hover:bg-primary/80 text-white px-8 py-6 text-lg font-semibold rounded-lg w-full sm:w-auto transition-colors duration-300"
            >
              Probar detector IA
              <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Button>

            <Button
              size="lg"
              variant="outline"
              onClick={() => handleScrollToSection('mapa')}
              className="border-2 border-secondary text-secondary hover:text-secondary hover:bg-secondary/10 hover:border-secondary/80 dark:text-secondary dark:hover:text-secondary dark:hover:bg-secondary/20 dark:hover:border-secondary px-8 py-6 text-lg font-semibold transition-all duration-300 rounded-lg w-full sm:w-auto flex items-center justify-center"
            >
              <MapPin className="mr-2 h-5 w-5" />
              Ver zonas afectadas
            </Button>
          </div>

          {/* Nota pequeña */}
          <p className="text-sm sm:text-base text-muted-foreground/70 max-w-lg mx-auto px-4 pt-4">
            Probá la detección con IA en tiempo real y contribuí a la vigilancia epidemiológica de tu comunidad
          </p>
        </div>
      </div>
    </section>
  )
}

export default HeroSection
