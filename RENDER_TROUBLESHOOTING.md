# Solución de Problemas - Despliegue en Render

## Error: metadata-generation-failed (Python 3.13 incompatible)

**PROBLEMA:** Render está usando Python 3.13, pero pandas 2.1.4 no es compatible.

**SOLUCIÓN INMEDIATA:**

1. **Verifica que `runtime.txt` contenga:** `python-3.11` (no 3.13)
2. **En Render, agrega esta variable de entorno:**
   ```
   PYTHON_VERSION=3.11
   ```
3. **O actualiza pandas a versión 2.2.0 o superior** (ya está actualizado en requirements.txt)

## Error: metadata-generation-failed (General)

Este error generalmente ocurre por problemas con las dependencias. Sigue estos pasos:

### Solución 1: Actualizar el Build Command

En Render, cambia el **Build Command** a:

```bash
pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
```

### Solución 2: Verificar Python Version

Asegúrate de que Render esté usando Python 3.11. El archivo `runtime.txt` especifica la versión.

Si Render no detecta automáticamente la versión, agrega esta variable de entorno:

```
PYTHON_VERSION=3.11.9
```

### Solución 3: Usar versiones más flexibles

Si el error persiste, puedes cambiar `requirements.txt` a usar versiones más flexibles:

```txt
Flask>=3.0.0,<4.0.0
Werkzeug>=3.0.0,<4.0.0
Flask-Login>=0.6.3
pandas>=2.0.0,<3.0.0
gunicorn>=21.0.0
openpyxl>=3.1.0
requests>=2.31.0
```

### Solución 4: Instalar dependencias del sistema

Si el error persiste con pandas (que requiere compiladores C), Render debería manejarlo automáticamente, pero puedes agregar al Build Command:

```bash
pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
```

### Solución 5: Verificar logs completos

En Render, revisa los logs completos del build para ver el error específico. El error "metadata-generation-failed" es genérico y el error real está más abajo en los logs.

## Errores Comunes

### Error: "No module named 'app'"
- Verifica que el **Start Command** sea: `gunicorn wsgi:app`
- Asegúrate de que `wsgi.py` esté en la raíz del proyecto

### Error: "Port already in use"
- Render maneja el puerto automáticamente, no necesitas configurarlo
- Verifica que no estés especificando un puerto en el código

### Error: "Application failed to respond"
- Verifica que `gunicorn` esté en `requirements.txt`
- Revisa que el comando de inicio sea correcto
- Verifica los logs para ver errores de importación

## Configuración Recomendada en Render

### Build Command:
```bash
pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
```

### Start Command:
```bash
gunicorn wsgi:app
```

### Variables de Entorno Mínimas:
```
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-muy-segura
```

## Si Nada Funciona

1. **Verifica los logs completos** en Render (no solo el error final)
2. **Prueba con versiones más antiguas** de las dependencias
3. **Contacta al soporte de Render** con los logs completos

