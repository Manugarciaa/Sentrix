/**
 * Sentrix Design Tokens - Sistema de tokens visuales reutilizables
 * Estilo TweakCN - Científico Ambiental
 */

export const SentrixUI = {
  // Radios de borde
  radius: {
    sm: '0.375rem',    // 6px - Pequeño
    md: '0.5rem',      // 8px - Medio (default)
    lg: '0.75rem',     // 12px - Grande
    xl: '1rem',        // 16px - Extra grande
    full: '9999px',    // Redondeado completo
  },

  // Sombras
  shadow: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    DEFAULT: '0 2px 12px rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  },

  // Transiciones
  transition: {
    fast: 'all 0.15s ease-out',
    DEFAULT: 'all 0.2s ease-out',
    slow: 'all 0.3s ease-out',
    colors: 'background-color 0.2s ease-out, color 0.2s ease-out',
  },

  // Espaciado de secciones
  spacing: {
    section: 'py-12 md:py-16 lg:py-24',
    container: 'px-6 sm:px-10 lg:px-20',
    card: 'p-6 sm:p-8',
    cardCompact: 'p-4 sm:p-6',
  },

  // Tipografía
  typography: {
    heading: {
      h1: 'text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight',
      h2: 'text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight',
      h3: 'text-2xl sm:text-3xl font-bold',
      h4: 'text-xl sm:text-2xl font-semibold',
      h5: 'text-lg sm:text-xl font-semibold',
      h6: 'text-base sm:text-lg font-semibold',
    },
    body: {
      lg: 'text-lg leading-relaxed',
      DEFAULT: 'text-base leading-relaxed',
      sm: 'text-sm',
      xs: 'text-xs',
    },
    weight: {
      normal: 'font-normal',   // 400
      medium: 'font-medium',   // 500
      semibold: 'font-semibold', // 600
      bold: 'font-bold',       // 700
    },
  },

  // Colores (referencia a CSS variables)
  colors: {
    primary: 'hsl(var(--primary))',
    primaryForeground: 'hsl(var(--primary-foreground))',
    accent: 'hsl(var(--accent))',
    accentForeground: 'hsl(var(--accent-foreground))',
    background: 'hsl(var(--background))',
    foreground: 'hsl(var(--foreground))',
    card: 'hsl(var(--card))',
    cardForeground: 'hsl(var(--card-foreground))',
    muted: 'hsl(var(--muted))',
    mutedForeground: 'hsl(var(--muted-foreground))',
    border: 'hsl(var(--border))',
  },

  // Grids
  grid: {
    cols1: 'grid-cols-1',
    cols2: 'grid-cols-1 sm:grid-cols-2',
    cols3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    cols4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
    gap: {
      sm: 'gap-4',
      DEFAULT: 'gap-6',
      lg: 'gap-8',
    },
  },

  // Animaciones
  animation: {
    fadeIn: 'animate-fade-in',
    slideInTop: 'animate-slide-in-from-top',
    slideInBottom: 'animate-slide-in-from-bottom',
    pulse: 'animate-pulse-subtle',
    lift: 'hover-lift',
    liftLg: 'hover-lift-lg',
  },

  // Focus states
  focus: {
    ring: 'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
  },
} as const

/**
 * Helper para combinar clases de tokens
 */
export const tokens = {
  card: `bg-card text-card-foreground border border-border rounded-xl ${SentrixUI.shadow.DEFAULT} transition-all duration-300`,
  cardHover: 'hover:shadow-md hover:-translate-y-0.5',
  button: `inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 ${SentrixUI.focus.ring}`,
  input: `flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm transition-colors duration-200 ${SentrixUI.focus.ring}`,
} as const

export type SentrixUIType = typeof SentrixUI
