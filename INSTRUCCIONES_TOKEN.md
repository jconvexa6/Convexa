# 🔐 Configurar Token de Google para Producción

Para que funcione la edición y creación de productos en Render, necesitas configurar el token de Google.

## 🔄 Sistema de Refresh Automático

El sistema ahora maneja automáticamente la renovación de tokens:
- ✅ **Refresh automático**: Si el token expira, se renueva automáticamente usando el `refresh_token`
- ✅ **Respaldo local**: El token actualizado se guarda en `app/static/Credenciales/token.json` como respaldo
- ✅ **Fallback inteligente**: Si la variable de entorno no está disponible, usa el archivo local

## Opción 1: Variable de Entorno (RECOMENDADO)

1. Abre el archivo `app/static/Credenciales/token.json` en tu máquina local
2. Copia TODO su contenido
3. En Render Dashboard:
   - Ve a tu servicio → **Environment**
   - Agrega nueva variable:
     - **Nombre:** `GOOGLE_TOKEN_JSON`
     - **Valor:** Pega todo el contenido del JSON (todo en una sola línea)

**Ejemplo del valor:**
```
{"token":"ya29.a0Aa7pCA...","refresh_token":"1//01UCdRe...","token_uri":"https://oauth2.googleapis.com/token","client_id":"1012866464546-...","client_secret":"GOCSPX-...","scopes":["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]}
```

## Opción 2: Archivo Local (Fallback)

Si no configuras la variable de entorno, el sistema intentará cargar el token desde:
- `app/static/Credenciales/token.json`

**Nota:** Este archivo está en `.gitignore` y no se sube a Git.

## ⚠️ Si el Token Expira Completamente

Si el `refresh_token` también expira (raro, pero puede pasar), necesitas generar un nuevo token:

### Generar Nuevo Token (Local)

1. Ejecuta este script en tu máquina local (asegúrate de tener `token.json` actualizado):
```python
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json

# Cargar token existente
with open('app/static/Credenciales/token.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)

# Si está expirado, refrescar
if creds.expired:
    creds.refresh(Request())
    
    # Guardar nuevo token
    new_token = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': list(creds.scopes)
    }
    
    with open('app/static/Credenciales/token.json', 'w') as f:
        json.dump(new_token, f, indent=2)
    
    print("✅ Token actualizado. Copia el contenido a GOOGLE_TOKEN_JSON en Render")
```

2. Copia el contenido actualizado de `token.json` a la variable de entorno `GOOGLE_TOKEN_JSON` en Render

## ✅ Después de configurar

- Render redesplegará automáticamente
- El token se refrescará automáticamente cuando expire (mientras el `refresh_token` sea válido)
- El token actualizado se guardará localmente como respaldo

