"""
Configuración de la aplicación Flask
"""
import os
from datetime import timedelta


class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-2024'
    SESSION_COOKIE_SECURE = False  # True en producción con HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # URL del Google Sheet de inventario
    INVENTORY_SHEET_URL = os.environ.get(
        'INVENTORY_SHEET_URL',
        'https://docs.google.com/spreadsheets/d/11YVSLtIM-pjsVT2fBe4yLEjZnVDGdrtchFQc1GYYPYE/edit'
    )
    
    # Credenciales de usuario (en producción usar base de datos)
    # Por ahora, usuario y contraseña (en desarrollo se acepta texto plano)
    # En producción, usar hash: generate_password_hash('tu_contraseña')
    USERS = {
        'admin': {
            'password': 'admin123',  # Contraseña por defecto (cambiar en producción)
        }
    }


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # Requiere HTTPS


# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

