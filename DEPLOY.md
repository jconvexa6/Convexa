# Guía de Despliegue en Render

## Pasos para Desplegar

### 1. Preparar el Repositorio

Asegúrate de que tu código esté en un repositorio Git (GitHub, GitLab, Bitbucket).

### 2. Crear Servicio en Render

1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Haz clic en **New +** > **Web Service**
3. Conecta tu repositorio

### 3. Configuración del Servicio

**Configuración básica:**
- **Name:** `sistema-inventario` (o el nombre que prefieras)
- **Environment:** `Python 3`
- **Python Version:** `3.11.9` (se especifica en `runtime.txt`)

**Build Command (IMPORTANTE):**
```bash
pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn wsgi:app
```

**Nota:** Si tienes errores de "metadata-generation-failed", usa este Build Command alternativo:
```bash
pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt
```

### 4. Variables de Entorno

Agrega las siguientes variables de entorno en la sección **Environment**:

```
FLASK_ENV=production
SECRET_KEY=genera-una-clave-secreta-muy-segura-aqui-minimo-32-caracteres
INVENTORY_SHEET_URL=https://docs.google.com/spreadsheets/d/11YVSLtIM-pjsVT2fBe4yLEjZnVDGdrtchFQc1GYYPYE/edit
```

**Para generar SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

### 5. Configurar Credenciales de Usuario

Antes de desplegar, genera un hash seguro para la contraseña:

1. Ejecuta localmente:
   ```bash
   python generate_password_hash.py
   ```

2. Edita `config.py` y reemplaza la contraseña en texto plano con el hash generado.

3. Haz commit y push de los cambios.

### 6. Desplegar

Render desplegará automáticamente tu aplicación. Puedes ver el progreso en los logs.

### 7. Verificar Despliegue

Una vez desplegado, visita la URL proporcionada por Render y verifica:
- ✅ El login funciona
- ✅ El dashboard carga los datos
- ✅ La vista de detalle funciona

## Solución de Problemas

### Error: "Module not found"
- Verifica que todas las dependencias estén en `requirements.txt`
- Revisa los logs de build en Render

### Error: "Application failed to respond"
- Verifica que el comando de inicio sea correcto: `gunicorn wsgi:app`
- Asegúrate de que el puerto esté configurado correctamente (Render lo hace automáticamente)

### Error al leer Google Sheets
- Verifica que la URL del sheet sea correcta
- Asegúrate de que el sheet sea público

## Notas Importantes

- ⚠️ **Nunca** subas `config.py` con contraseñas en texto plano a producción
- ⚠️ Usa siempre `SECRET_KEY` fuerte en producción
- ⚠️ Considera usar variables de entorno para todas las configuraciones sensibles

