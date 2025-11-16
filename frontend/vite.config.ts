import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
// import { VitePWA } from 'vite-plugin-pwa' // Disabled - causing issues
import path from 'path'
import { visualizer } from 'rollup-plugin-visualizer'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [
    react(),
    // PWA plugin disabled for now - causing deployment issues
    // VitePWA({...})
    mode === 'production' && visualizer({
      filename: './dist/stats.html',
      open: false,
      gzipSize: true,
      brotliSize: true,
    }),
  ].filter(Boolean),
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/components': path.resolve(__dirname, './src/components'),
      '@/pages': path.resolve(__dirname, './src/pages'),
      '@/hooks': path.resolve(__dirname, './src/hooks'),
      '@/store': path.resolve(__dirname, './src/store'),
      '@/lib': path.resolve(__dirname, './src/lib'),
      '@/types': path.resolve(__dirname, './src/types'),
      '@/api': path.resolve(__dirname, './src/api'),
      '@/utils': path.resolve(__dirname, './src/utils')
    }
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    cssCodeSplit: true,
    cssMinify: true,
    minify: 'terser',
    target: 'es2015',
    reportCompressedSize: true,
    chunkSizeWarningLimit: 1000,
    terserOptions: {
      compress: {
        drop_console: mode === 'production',
        drop_debugger: mode === 'production',
        pure_funcs: mode === 'production' ? ['console.log', 'console.info', 'console.debug'] : [],
        passes: 2,
      },
      mangle: {
        safari10: true,
      },
      format: {
        comments: false,
      },
    },
    rollupOptions: {
      external: mode === 'production' ? ['msw'] : [],
      output: {
        manualChunks: (id) => {
          // Core React
          if (id.includes('node_modules/react/') || id.includes('node_modules/react-dom/')) {
            return 'react-vendor'
          }
          // Router
          if (id.includes('node_modules/react-router')) {
            return 'router'
          }
          // Radix UI components - split by package
          if (id.includes('@radix-ui')) {
            return 'radix-ui'
          }
          // Maps - heavy library
          if (id.includes('leaflet') || id.includes('react-leaflet')) {
            return 'maps'
          }
          // Charts
          if (id.includes('recharts')) {
            return 'charts'
          }
          // React Query
          if (id.includes('@tanstack/react-query')) {
            return 'react-query'
          }
          // Framer Motion
          if (id.includes('framer-motion')) {
            return 'framer-motion'
          }
          // Image processing
          if (id.includes('heic2any') || id.includes('exifr')) {
            return 'image-processing'
          }
          // Other large dependencies
          if (id.includes('node_modules')) {
            return 'vendor'
          }
        },
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name?.split('.')
          const extType = info?.[info.length - 1]
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType || '')) {
            return `assets/images/[name]-[hash][extname]`
          } else if (/woff|woff2|eot|ttf|otf/i.test(extType || '')) {
            return `assets/fonts/[name]-[hash][extname]`
          }
          return `assets/[name]-[hash][extname]`
        },
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
      }
    }
  },
  define: {
    'process.env': {},
    'global': 'globalThis'
  },
  optimizeDeps: {
    exclude: mode === 'production' ? ['msw'] : []
  }
}))