# 🔐 Configurar Token de Google para Producción

Para que funcione la edición y creación de productos en Render, necesitas configurar el token de Google.

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

## Opción 2: Archivo de Configuración

1. Crea el archivo `app/config/google_credentials.py` en el servidor de Render
2. Copia el contenido de `app/config/google_credentials.py.example`
3. Pega tu token en el diccionario `return`

**Nota:** Este archivo está en `.gitignore` y no se sube a Git.

## ✅ Después de configurar

Render redesplegará automáticamente. El token se refrescará automáticamente si expira.

