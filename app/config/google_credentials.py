"""
Configuración de credenciales de Google API
Este archivo NO se sube a Git (.gitignore)
"""
import os

def get_token_data():
    """
    Obtener datos del token de Google
    Prioridad: 1. Variable de entorno, 2. Archivo local
    """
    # 1. Intentar desde variable de entorno (RECOMENDADO para producción)
    token_json_env = os.environ.get('GOOGLE_TOKEN_JSON')
    if token_json_env:
        try:
            import json
            return json.loads(token_json_env)
        except:
            pass
    
    # 2. Intentar desde archivo local
    token_paths = [
        os.path.join('app', 'static', 'Credenciales', 'token.json'),
        os.path.join('app', 'templates', 'llavesAcceso', 'token.json'),
        'token.json',
    ]
    
    for path in token_paths:
        if os.path.exists(path):
            try:
                import json
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                continue
    
    # 3. Si estás en desarrollo local y necesitas hardcodear temporalmente,
    # descomenta y pega tu token aquí (NO RECOMENDADO para producción):
    """
    return {
        "token": "TU_TOKEN_AQUI",
        "refresh_token": "TU_REFRESH_TOKEN_AQUI",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "TU_CLIENT_ID_AQUI",
        "client_secret": "TU_CLIENT_SECRET_AQUI",
        "scopes": [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    }
    """
    
    return None
