# Desplegar en Render - Guía Simple

## 📋 Pasos

### 1. En Render Dashboard
- Crea un **Web Service**
- Conecta tu repositorio de GitHub

### 2. Configuración
- **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command:** `gunicorn wsgi:app`

### 3. Variables de Entorno

Ve a la sección **Environment** en Render y agrega estas variables:

#### 🔴 Obligatorias

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `FLASK_ENV` | `production` | Entorno de producción |
| `SECRET_KEY` | `tu-clave-secreta-muy-larga` | Clave secreta para sesiones (genera una única) |

**Ejemplo de SECRET_KEY:**
```
mi-clave-super-secreta-2024-abc123xyz789
```

#### 🟠 Para escritura en Google Sheets (editar/crear productos)

**IMPORTANTE:** Para que funcione la edición y creación de productos, necesitas configurar el token de Google:

| Variable | Descripción |
|----------|-------------|
| `GOOGLE_TOKEN_JSON` | Token de Google API en formato JSON (ver instrucciones abajo) |

**Cómo obtener el token:**
1. En tu máquina local, después de autenticarte, el token se guarda en `app/static/Credenciales/token.json`
2. Abre ese archivo y copia TODO su contenido
3. En Render, crea la variable `GOOGLE_TOKEN_JSON` y pega el contenido completo (todo en una sola línea, sin saltos de línea)

**Ejemplo del valor:**
```
{"token":"ya29.a0Aa7pCA...","refresh_token":"1//01UCdRe...","token_uri":"https://oauth2.googleapis.com/token","client_id":"1012866464546-...","client_secret":"GOCSPX-...","scopes":["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]}
```

#### 🟡 Opcionales (tienen valores por defecto)

Si quieres usar URLs diferentes a las configuradas por defecto:

| Variable | Valor por Defecto | Descripción |
|----------|-------------------|-------------|
| `INVENTORY_SHEET_URL` | `https://docs.google.com/spreadsheets/d/11YVSLtIM-pjsVT2fBe4yLEjZnVDGdrtchFQc1GYYPYE/edit` | URL del Google Sheet de inventario |
| `USERS_SHEET_URL` | `https://docs.google.com/spreadsheets/d/1DagcKZIkcvN0ODF0G-4Ddrml9e9HqNfFj-c6Z7zBrFs/edit` | URL del Google Sheet de usuarios |
| `USERS_SHEET_GID` | `0` | ID de la pestaña/hoja para usuarios |
| `USERS_COLUMN_USERNAME` | `User` | Nombre de la columna de usuario |
| `USERS_COLUMN_PASSWORD` | `pass` | Nombre de la columna de contraseña |
| `HISTORY_SHEET_URL` | `https://docs.google.com/spreadsheets/d/1RfaOyNpLT4IYR9vsRatE1G0Ru0BVjdHSNuBRF5tfN2M/edit` | URL del Google Sheet de histórico |

### 4. Listo
Render desplegará automáticamente tu aplicación.

## 📝 Notas Importantes

### Variables de Entorno para Google API

Para que funcione la escritura en Google Sheets y la generación de QR, necesitas configurar el token de Google:

**Opción 1: Token JSON (Recomendado)**
Agrega esta variable de entorno en Render:
```
GOOGLE_TOKEN_JSON={"token":"...","refresh_token":"...","token_uri":"...","client_id":"...","client_secret":"...","scopes":["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]}
```

**Cómo obtener el token:**
1. En tu máquina local, después de autenticarte, el token se guarda en `app/static/Credenciales/token.json`
2. Copia todo el contenido de ese archivo
3. Pégalo como valor de `GOOGLE_TOKEN_JSON` en Render (todo en una sola línea)

**Opción 2: Credentials JSON (Alternativa)**
Si prefieres usar Service Account:
```
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
```

### Otras Notas

- **SECRET_KEY**: Genera una clave única y segura para producción. Puedes usar:
  ```python
  import secrets
  print(secrets.token_hex(32))
  ```
- Las URLs de Google Sheets deben ser públicas o tener permisos de lectura
- El token se refrescará automáticamente si expira

## 🐛 Si hay errores

1. Verifica que `runtime.txt` tenga `python-3.11`
2. Revisa los logs en Render
3. Asegúrate de que los Google Sheets sean públicos o accesibles
4. Verifica que las APIs de Google (Sheets y Drive) estén habilitadas

