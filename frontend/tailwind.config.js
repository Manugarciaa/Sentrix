/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class', 'class'], // Use class-based dark mode for manual toggle
  content: ['./index.html', './src/**/*.{ts,tsx,js,jsx}'],
  theme: {
  	extend: {
  		colors: {
  			sentrix: {
  				chocolate: '#7D5A3B',      // Marrón chocolate
  				steel: '#5B8FB9',          // Azul institucional
  				mustard: '#E8B923',        // Amarillo mostaza
  				darkChocolate: '#654A30',  // Marrón oscuro
  				burnedOrange: '#D97941',   // Naranja quemado
  			},
  			primary: {
  				'50': '#FAF8F5',
  				'100': '#F5F0EA',
  				'200': '#E8DCCC',
  				'300': '#D4BFA0',
  				'400': '#BF9B6B',
  				'500': '#A9825F',      // ⭐ Dark mode
  				'600': '#7D5A3B',      // ⭐ Light mode PRINCIPAL
  				'700': '#654A30',
  				'800': '#523B26',
  				'900': '#453220',
  				'950': '#261C12',
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			secondary: {
  				'50': '#F0F7FC',
  				'100': '#E0EFF9',
  				'200': '#BAD9F1',
  				'300': '#7EBDE6',
  				'400': '#4A9DD6',
  				'500': '#7BA8CC',      // ⭐ Dark mode
  				'600': '#5B8FB9',      // ⭐ Light mode PRINCIPAL
  				'700': '#4A7A9E',
  				'800': '#3C6384',
  				'900': '#2F465E',
  				'950': '#1F2D3E',
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},

  			accent: {
  				'50': '#FFFBEB',
  				'100': '#FEF3C7',
  				'200': '#FDE68A',
  				'300': '#FCD34D',
  				'400': '#E8B923',      // ⭐ Light mode PRINCIPAL
  				'500': '#F5D049',      // ⭐ Dark mode warning
  				'600': '#C99D1E',
  				'700': '#A67C17',
  				'800': '#6E4B18',
  				'900': '#5E3E19',
  				'950': '#37200A',
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},

  			danger: {
  				'50': '#FEF5F2',
  				'100': '#FEE8E2',
  				'200': '#FDD0C4',
  				'300': '#FBA89B',
  				'400': '#F48442',      // ⭐ Dark mode - Naranja luminoso
  				'500': '#E85D42',      // ⭐ Crítico
  				'600': '#C73E1D',      // ⭐ Light mode
  				'700': '#9E3018',
  				'800': '#7A2515',
  				'900': '#5F1E12',
  				'950': '#330F09'
  			},
  			warning: {
  				'50': '#FFFBEB',
  				'100': '#FEF3C7',
  				'200': '#FDE68A',
  				'300': '#FCD34D',
  				'400': '#F5D049',      // ⭐ Dark mode
  				'500': '#E8B923',      // ⭐ Light mode
  				'600': '#C99D1E',
  				'700': '#A67C17',
  				'800': '#78350F',
  				'900': '#5E3E19',
  				'950': '#37200A'
  			},
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			background: 'hsl(var(--background))',
  			foreground: 'hsl(var(--foreground))',
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			},
  			status: {
  				success: {
  					DEFAULT: 'hsl(var(--status-success-bg))',
  					light: 'hsl(var(--status-success-bg-light))',
  					border: 'hsl(var(--status-success-border))',
  					text: 'hsl(var(--status-success-text))',
  					muted: 'hsl(var(--status-success-text-muted))'
  				},
  				warning: {
  					DEFAULT: 'hsl(var(--status-warning-bg))',
  					light: 'hsl(var(--status-warning-bg-light))',
  					border: 'hsl(var(--status-warning-border))',
  					text: 'hsl(var(--status-warning-text))',
  					muted: 'hsl(var(--status-warning-text-muted))'
  				},
  				danger: {
  					DEFAULT: 'hsl(var(--status-danger-bg))',
  					light: 'hsl(var(--status-danger-bg-light))',
  					border: 'hsl(var(--status-danger-border))',
  					text: 'hsl(var(--status-danger-text))',
  					muted: 'hsl(var(--status-danger-text-muted))'
  				},
  				critical: {
  					DEFAULT: 'hsl(var(--status-critical-bg))',
  					light: 'hsl(var(--status-critical-bg-light))',
  					border: 'hsl(var(--status-critical-border))',
  					text: 'hsl(var(--status-critical-text))',
  					muted: 'hsl(var(--status-critical-text-muted))'
  				},
  				info: {
  					DEFAULT: 'hsl(var(--status-info-bg))',
  					light: 'hsl(var(--status-info-bg-light))',
  					border: 'hsl(var(--status-info-border))',
  					text: 'hsl(var(--status-info-text))',
  					muted: 'hsl(var(--status-info-text-muted))'
  				}
  			},
  			sidebar: {
  				DEFAULT: 'hsl(var(--sidebar-background))',
  				foreground: 'hsl(var(--sidebar-foreground))',
  				primary: 'hsl(var(--sidebar-primary))',
  				'primary-foreground': 'hsl(var(--sidebar-primary-foreground))',
  				accent: 'hsl(var(--sidebar-accent))',
  				'accent-foreground': 'hsl(var(--sidebar-accent-foreground))',
  				border: 'hsl(var(--sidebar-border))',
  				ring: 'hsl(var(--sidebar-ring))'
  			}
  		},
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		},
  		fontFamily: {
  			sans: [
  				'Poppins',
  				'system-ui',
  				'sans-serif'
  			],
  			mono: [
  				'JetBrains Mono',
  				'monospace'
  			],
  			akira: [
  				'Akira',
  				'sans-serif'
  			]
  		},
  		keyframes: {
  			'accordion-down': {
  				from: {
  					height: 0
  				},
  				to: {
  					height: 'var(--radix-accordion-content-height)'
  				}
  			},
  			'accordion-up': {
  				from: {
  					height: 'var(--radix-accordion-content-height)'
  				},
  				to: {
  					height: 0
  				}
  			},
  			'fade-in': {
  				'0%': {
  					opacity: '0'
  				},
  				'100%': {
  					opacity: '1'
  				}
  			},
  			'slide-in-from-top': {
  				'0%': {
  					transform: 'translateY(-100%)'
  				},
  				'100%': {
  					transform: 'translateY(0)'
  				}
  			},
  			'slide-in-from-bottom': {
  				'0%': {
  					transform: 'translateY(100%)'
  				},
  				'100%': {
  					transform: 'translateY(0)'
  				}
  			},
  			'pulse-subtle': {
  				'0%, 100%': {
  					opacity: '1'
  				},
  				'50%': {
  					opacity: '0.8'
  				}
  			},
  			'slide-in-right': {
  				'0%': {
  					transform: 'translateX(100%)',
  					opacity: '0'
  				},
  				'100%': {
  					transform: 'translateX(0)',
  					opacity: '1'
  				}
  			},
  			shimmer: {
  				'0%': {
  					backgroundPosition: '-200% 0'
  				},
  				'100%': {
  					backgroundPosition: '200% 0'
  				}
  			}
  		},
  		animation: {
  			'accordion-down': 'accordion-down 0.2s ease-out',
  			'accordion-up': 'accordion-up 0.2s ease-out',
  			'fade-in': 'fade-in 0.3s ease-out',
  			'slide-in-from-top': 'slide-in-from-top 0.3s ease-out',
  			'slide-in-from-bottom': 'slide-in-from-bottom 0.3s ease-out',
  			'pulse-subtle': 'pulse-subtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
  			'slide-in-right': 'slide-in-right 0.3s ease-out',
  			shimmer: 'shimmer 2s linear infinite'
  		},
  		spacing: {
  			'18': '4.5rem',
  			'88': '22rem',
  			'128': '32rem'
  		},
  		maxWidth: {
  			'8xl': '88rem',
  			'9xl': '96rem'
  		}
  	}
  },
  plugins: [require('@tailwindcss/forms'), require('@tailwindcss/typography'), require("tailwindcss-animate")]
}