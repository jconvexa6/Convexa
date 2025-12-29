# Estructura del Proyecto

## 📁 Organización de Archivos

```
WEBSITE-INV/
├── app/                          # Paquete principal de la aplicación
│   ├── __init__.py              # Inicialización de Flask y Blueprints
│   ├── routes/                   # Blueprints de rutas
│   │   ├── __init__.py
│   │   ├── auth.py              # Rutas de autenticación (login/logout)
│   │   ├── dashboard.py          # Rutas del dashboard principal
│   │   └── product.py           # Rutas de detalle de productos
│   ├── services/                 # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── auth_service.py       # Servicio de autenticación
│   │   └── sheets_service.py    # Servicio para leer Google Sheets
│   ├── templates/                # Plantillas HTML (Jinja2)
│   │   ├── base.html            # Template base
│   │   ├── auth/
│   │   │   └── login.html       # Vista de login
│   │   ├── dashboard/
│   │   │   └── index.html       # Dashboard con DataTable
│   │   └── product/
│   │       └── detail.html      # Vista de detalle de producto
│   └── static/                   # Archivos estáticos
│       ├── css/
│       │   └── style.css        # Estilos personalizados
│       └── js/                   # JavaScript (si se necesita)
│
├── app.py                        # Archivo principal para desarrollo
├── wsgi.py                       # Archivo WSGI para producción (Render)
├── config.py                     # Configuración de la aplicación
├── runtime.txt                   # Versión de Python para Render
├── requirements.txt              # Dependencias del proyecto
│
├── generate_password_hash.py    # Utilidad para generar hash de contraseñas
│
├── README.md                     # Documentación principal
├── DEPLOY.md                     # Guía de despliegue en Render
├── RENDER_TROUBLESHOOTING.md    # Solución de problemas en Render
├── USUARIOS_EXCEL.md            # Guía de configuración de usuarios
└── PROJECT_STRUCTURE.md         # Este archivo
```

## 📦 Archivos Principales

### Archivos de Configuración
- **`config.py`**: Configuración de Flask, URLs de Google Sheets, credenciales
- **`runtime.txt`**: Especifica Python 3.11 para Render
- **`requirements.txt`**: Dependencias de Python
- **`.gitignore`**: Archivos ignorados por Git

### Archivos de Ejecución
- **`app.py`**: Ejecuta la aplicación en desarrollo (`python app.py`)
- **`wsgi.py`**: Archivo WSGI para producción (usado por Gunicorn en Render)

### Documentación
- **`README.md`**: Documentación principal del proyecto
- **`DEPLOY.md`**: Guía paso a paso para desplegar en Render
- **`RENDER_TROUBLESHOOTING.md`**: Solución de problemas comunes
- **`USUARIOS_EXCEL.md`**: Configuración de usuarios desde Excel
- **`PROJECT_STRUCTURE.md`**: Este archivo - estructura del proyecto

## 🔧 Archivos de Utilidad
- **`generate_password_hash.py`**: Script para generar hash de contraseñas

## 📝 Notas

- Los archivos `env/` y `venv/` están en `.gitignore` (entornos virtuales)
- Los archivos `__pycache__/` están ignorados (caché de Python)
- Los archivos `.env` están ignorados (variables de entorno sensibles)

