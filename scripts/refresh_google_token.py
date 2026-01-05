"""
Script para refrescar el token de Google cuando expire
Ejecuta este script cuando necesites actualizar el token manualmente
"""
import os
import sys
import json
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Scopes necesarios
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def refresh_token():
    """Refrescar el token de Google"""
    
    # Rutas posibles del token
    token_paths = [
        Path('app/static/Credenciales/token.json'),
        Path('app/templates/llavesAcceso/token.json'),
        Path('token.json'),
    ]
    
    token_path = None
    for path in token_paths:
        if path.exists():
            token_path = path
            break
    
    if not token_path:
        print("❌ No se encontró el archivo token.json")
        print("📁 Buscado en:")
        for path in token_paths:
            print(f"   - {path}")
        return False
    
    print(f"✅ Token encontrado en: {token_path}")
    
    try:
        # Cargar token existente
        with open(token_path, 'r', encoding='utf-8') as f:
            token_data = json.load(f)
        
        print("📋 Campos encontrados:", list(token_data.keys()))
        
        # Validar campos necesarios
        required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret']
        missing_fields = [field for field in required_fields if field not in token_data]
        
        if missing_fields:
            print(f"❌ Faltan campos necesarios: {', '.join(missing_fields)}")
            return False
        
        # Crear credenciales
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        
        # Verificar si está expirado
        if creds.valid:
            print("✅ El token es válido y no necesita refrescarse")
            print(f"   Token expira en: {creds.expiry if hasattr(creds, 'expiry') else 'N/A'}")
        else:
            print("🔄 Token expirado, refrescando...")
            
            if not creds.refresh_token:
                print("❌ No hay refresh_token disponible. Necesitas generar un nuevo token.")
                return False
            
            # Refrescar token
            creds.refresh(Request())
            print("✅ Token refrescado exitosamente")
        
        # Guardar token actualizado (incluso si no se refrescó, para asegurar formato correcto)
        updated_token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': list(creds.scopes) if creds.scopes else SCOPES
        }
        
        # Guardar en el mismo archivo
        with open(token_path, 'w', encoding='utf-8') as f:
            json.dump(updated_token_data, f, indent=2)
        
        print(f"💾 Token guardado en: {token_path}")
        print("\n" + "="*60)
        print("📋 Para usar en Render, copia este JSON (todo en una línea):")
        print("="*60)
        print(json.dumps(updated_token_data, separators=(',', ':')))
        print("="*60)
        print("\n💡 Pega este valor en la variable de entorno GOOGLE_TOKEN_JSON en Render")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al refrescar el token: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🔄 Refrescador de Token de Google")
    print("="*60)
    refresh_token()

