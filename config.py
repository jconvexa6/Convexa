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
    
    # ID de la pestaña/hoja para usuarios (gid)
    USERS_SHEET_GID = os.environ.get('USERS_SHEET_GID', '0')
    
    # Columnas del Excel de usuarios
    USERS_COLUMN_USERNAME = os.environ.get('USERS_COLUMN_USERNAME', 'User')
    USERS_COLUMN_PASSWORD = os.environ.get('USERS_COLUMN_PASSWORD', 'pass')
    
    # URL del Google Sheet de histórico de movimientos
    HISTORY_SHEET_URL = os.environ.get(
        'HISTORY_SHEET_URL',
        'https://docs.google.com/spreadsheets/d/1RfaOyNpLT4IYR9vsRatE1G0Ru0BVjdHSNuBRF5tfN2M/edit'
    )
    
    # URL del Google Sheet de unidades de medida
    UNITS_OF_MEASURE_SHEET_URL = os.environ.get(
        'UNITS_OF_MEASURE_SHEET_URL',
        'https://docs.google.com/spreadsheets/d/1zV1rrMLT4dDxxgKszlbkUyGfEKqE0GFC_jncUsekIJ4/edit'
    )


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

