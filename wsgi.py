"""
Archivo WSGI para despliegue en producción (Render, Heroku, etc.)
"""
from app import create_app
import os

# Crear la aplicación con configuración de producción
app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == '__main__':
    app.run()

