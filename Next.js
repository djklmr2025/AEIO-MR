# Elimina vercel.json
rm vercel.json

# Crea next.config.js
cat > next.config.js << EOF
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  }
}

module.exports = nextConfig
EOF