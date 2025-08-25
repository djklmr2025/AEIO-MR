# ================== CONFIGURACIÓN CLAUDE ==================
# Obtén tu API key desde: https://console.anthropic.com/
ANTHROPIC_API_KEY=tu_api_key_de_anthropic_aqui

# Modelo Claude a usar (opcional, por defecto claude-3-sonnet-20240229)
CLAUDE_MODEL=claude-3-sonnet-20240229
# Otras opciones disponibles:
# CLAUDE_MODEL=claude-3-haiku-20240307  # Más rápido y económico
# CLAUDE_MODEL=claude-3-opus-20240229   # Más potente pero más costoso

# ================== MEMORIA Y ALMACENAMIENTO ==================
# Directorio donde guardar la memoria de conversaciones
MEMORY_DIR=data/memory

# Número máximo de turnos de conversación a mantener en contexto
MEMORY_MAX_TURNS=8

# Cada cuántos turnos actualizar el resumen de largo plazo
MEMORY_SUMMARY_EVERY=6

# ================== CONFIGURACIÓN DEL SERVIDOR ==================
# Puerto del servidor (opcional, por defecto usa 8000)
# PORT=8000

# Entorno (development/production)
# ENVIRONMENT=development