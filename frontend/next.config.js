// frontend/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  // Para evitar errores 404 en SPA
  skipTrailingSlashRedirect: true
}

module.exports = nextConfig