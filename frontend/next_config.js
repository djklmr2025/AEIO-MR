// frontend/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Para despliegue estático en Vercel/Netlify
  output: 'export',
  trailingSlash: true,
  
  // Optimización de imágenes deshabilitada para export estático
  images: {
    unoptimized: true
  },
  
  // Para evitar errores 404 en SPA
  skipTrailingSlashRedirect: true,
  
  // Variables de entorno públicas
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  
  // Configuración para URLs base dinámicas
  assetPrefix: process.env.NODE_ENV === 'production' ? '' : '',
  
  // Configuración para CORS y headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ]
  },
  
  // Configuración experimental para mejor rendimiento
  experimental: {
    optimizeCss: true,
  },
}

module.exports = nextConfig