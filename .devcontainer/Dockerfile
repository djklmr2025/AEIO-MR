FROM mcr.microsoft.com/devcontainers/javascript-node:0-18

# Instalar dependencias del sistema que pueda necesitar Strapi
RUN apt-get update && apt-get install -y \
    python3 \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*