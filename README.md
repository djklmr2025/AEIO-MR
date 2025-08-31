# AEIO-MR (ARKAIOS)

**Descarga Nuestra App para Android desde Aqui:** [bit.ly/4mFPEDN](http://bit.ly/4mFPEDN)

**Donaciones y Aportaciones en agradecimiento al proyecto:** [bit.ly/4lUL9nj](http://bit.ly/4lUL9nj)

**Soporte, ayuda comentarios o dudas:** djklmr@hotmail.com

![Project Status](https://img.shields.io/badge/status-active-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-Android%20%7C%20Web-blue.svg)
![AI](https://img.shields.io/badge/AI-GPT--4o%20%7C%20Claude-purple.svg)
![OS](https://img.shields.io/badge/OS-Puter%20Linux-orange.svg)

## 📋 Descripción

**ARKAIOS** es una interfaz de inteligencia artificial avanzada que combina **GPT-4o** y **Claude** con el sistema operativo en la nube **Puter.js**, ofreciendo un laboratorio completo de IA con capacidades de computación distribuida y gestión de archivos en tiempo real.

### ¿Qué es ARKAIOS?

ARKAIOS es un núcleo de IA que actúa como:
- **Científico-Constructor**: Análisis técnico y desarrollo de soluciones
- **Operador del Sistema**: Gestión completa del entorno Puter
- **Creativo-Diseñador**: Generación de contenido e imágenes

## ✨ Características Principales

### 🤖 Inteligencia Artificial Híbrida
- **GPT-4o**: Modelo principal para conversaciones y análisis
- **Claude Sonnet 4 / Opus 4**: Modelos alternativos especializados
- **Memoria persistente**: Sistema de registro y recuperación de contexto
- **Múltiples roles**: Personalidades especializadas según la tarea

### 🖥️ Integración Puter OS
- **Sistema de archivos completo**: Lectura, escritura y gestión de `/home`
- **Subida de archivos**: Drag & drop, clipboard, selección manual
- **Descompresión**: Soporte para ZIP/RAR automático
- **Galería visual**: Visualización de imágenes almacenadas

### 🎨 Generación de Contenido
- **Texto a imagen**: Generación automática con guardado en `/home`
- **Análisis visual**: Procesamiento de imágenes adjuntas
- **Exportación**: Descarga de respuestas en formato TXT
- **Procesamiento multimedia**: Soporte para PDF, imágenes, texto

### 🔧 Capacidades del Sistema
- **Comandos integrados**:
  - `img: [prompt]` - Generación de imágenes
  - `analizar imagen [n|url]` - Análisis visual
  - `listar [ruta]` - Exploración de directorios
  - `descomprimir [archivo.zip]` - Extracción automática
  - `crear archivo [ruta]: [contenido]` - Creación de archivos
  - `leer archivo [ruta]` - Lectura de contenido

## 🚀 Acceso Rápido

### 📱 Aplicación Android
Descarga la APK optimizada:
[**Descargar Android**](http://bit.ly/4g2n8JN)

### 🌐 Versión Web
Accede directamente desde tu navegador:
[**Acceder a ARKAIOS Web**](http://bit.ly/4lUCpOm)

## 🏗️ Arquitectura del Sistema

### Componentes Principales
```
ARKAIOS/
├── arkaios.html          # Interfaz principal con GPT-4o
├── Puter.js             # Interfaz alternativa con Claude
├── server_arkaios.py    # Servidor backend con persistencia
└── data/
    ├── memory/          # Sistema de memoria persistente
    ├── tasks.json       # Gestor de tareas
    └── logs/           # Registros del sistema
```

### Stack Tecnológico
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Backend**: Python Flask con threading
- **IA**: OpenAI GPT-4o + Anthropic Claude
- **OS**: Puter.js (Linux en la nube)
- **Storage**: Sistema de archivos virtualizado
- **Persistencia**: JSON + JSONL logging

## 🛠️ Instalación y Uso

### Instalación Local (Desarrollo)

1. **Clonar el repositorio**:
```bash
git clone https://github.com/djklmr2025/AEIO-MR.git
cd AEIO-MR
```

2. **Instalar dependencias Python**:
```bash
pip install flask python-dotenv
```

3. **Ejecutar servidor local**:
```bash
python server_arkaios.py
```

4. **Acceder a la interfaz**:
```
http://127.0.0.1:5000/
```

### Uso en Producción

#### Android
- Descarga e instala la APK
- La aplicación incluye servidor embebido
- Funciona offline con memoria local

#### Web
- Acceso directo sin instalación
- Requiere conexión a internet
- Sincronización automática con Puter

## 🎯 Casos de Uso

### Para Desarrolladores
- Análisis de código y debugging
- Generación de documentación técnica
- Automatización de tareas del sistema
- Gestión de proyectos con IA

### Para Creativos
- Generación de imágenes conceptuales
- Escritura asistida por IA
- Análisis de contenido visual
- Ideación y brainstorming

### Para Investigadores
- Procesamiento de documentos PDF
- Análisis de datasets
- Generación de reportes
- Gestión de literatura científica

## 🔒 Privacidad y Seguridad

- **Datos locales**: Memoria persistente en el dispositivo
- **Sin tracking**: No se almacenan conversaciones en servidores externos
- **Puter secure**: Entorno sandboxed con permisos limitados
- **Logs opcionales**: Sistema de logging desactivable

## 📊 Estado del Proyecto

- ✅ **Core IA**: GPT-4o integrado y funcional
- ✅ **Puter OS**: Sistema de archivos completo
- ✅ **Multimedia**: Soporte para imágenes y documentos
- ✅ **Memoria**: Persistencia local y exportación
- ✅ **Mobile**: APK Android optimizada
- 🔄 **Claude**: Integración en desarrollo
- 🔄 **APIs**: Expansión de endpoints

## 🤝 Contribuir

Las contribuciones son bienvenidas. Para contribuir:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Áreas de Contribución
- Nuevos modelos de IA
- Comandos del sistema
- Optimizaciones de UI/UX
- Documentación técnica
- Testing y QA

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👤 Autor

**djklmr2025**
- GitHub: [@djklmr2025](https://github.com/djklmr2025)
- Email: djklmr@hotmail.com

## 🙏 Agradecimientos

- **OpenAI** por GPT-4o
- **Anthropic** por Claude
- **Puter Team** por el sistema operativo en la nube
- **Chat-5** por el diseño y desarrollo inicial
- Comunidad open source por las librerías utilizadas

## 📞 Soporte Técnico

### Reportar Issues
- Abre un issue en este repositorio
- Incluye logs del sistema (`/api/log`)
- Especifica versión (Android/Web)
- Contacto directo: djklmr@hotmail.com

### Documentación
- **Comandos**: Escribe `ayuda` en el chat
- **API**: Revisa `server_arkaios.py`
- **Puter**: [Documentación oficial](https://puter.com/docs)

## 🔬 Roadmap

### v2.0 (En desarrollo)
- [ ] Integración completa Claude Opus 4
- [ ] Modo colaborativo multi-usuario
- [ ] Plugin system para extensiones
- [ ] API REST completa

### v3.0 (Futuro)
- [ ] Soporte para más modelos de IA
- [ ] Interfaz de realidad mixta
- [ ] Integración con servicios en la nube
- [ ] Marketplace de comandos

---

⭐ **Si ARKAIOS te resulta útil, dale una estrella al repositorio**

🚀 **ARKAIOS está listo para usar Puter + GPT-4o + Claude**

---

*"El futuro de la computación es la simbiosis entre humanos e IA"* - **ARKAIOS**
