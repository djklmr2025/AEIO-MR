// next.config.js (si usas Next.js)
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export', // Para exportación estática
  trailingSlash: true,
  images: {
    unoptimized: true
  }
}

module.exports = nextConfig