"""
Configuración de la aplicación Flask
"""
import os
from datetime import timedelta


class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-2024'
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # URL del Google Sheet de inventario
    INVENTORY_SHEET_URL = os.environ.get(
        'INVENTORY_SHEET_URL',
        'https://docs.google.com/spreadsheets/d/11YVSLtIM-pjsVT2fBe4yLEjZnVDGdrtchFQc1GYYPYE/edit'
    )
    
    # URL del Google Sheet de usuarios
    USERS_SHEET_URL = os.environ.get(
        'USERS_SHEET_URL',
        'https://docs.google.com/spreadsheets/d/1DagcKZIkcvN0ODF0G-4Ddrml9e9HqNfFj-c6Z7zBrFs/edit'
    )
    
    # Columnas del Excel de usuarios
    USERS_COLUMN_USERNAME = os.environ.get('USERS_COLUMN_USERNAME', 'User')
    USERS_COLUMN_PASSWORD = os.environ.get('USERS_COLUMN_PASSWORD', 'pass')


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

