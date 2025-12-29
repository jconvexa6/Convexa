# Desplegar en Render - Guía Simple

## 📋 Pasos

### 1. En Render Dashboard
- Crea un **Web Service**
- Conecta tu repositorio de GitHub

### 2. Configuración
- **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command:** `gunicorn wsgi:app`

### 3. Variables de Entorno (solo 2)

Ve a la sección **Environment** y agrega estas 2 variables:

| Variable | Valor |
|----------|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | `cualquier-texto-largo-y-secreto` |

**Ejemplo de SECRET_KEY:**
```
mi-clave-super-secreta-123456789
```

### 4. Listo
Render desplegará automáticamente tu aplicación.

## ❓ ¿Qué son las variables de entorno?

Son configuraciones que Render usa al ejecutar tu aplicación. Solo necesitas estas 2:
- `FLASK_ENV=production` → Le dice a Flask que está en producción
- `SECRET_KEY` → Clave secreta para las sesiones (pon cualquier texto largo)

## 🐛 Si hay errores

1. Verifica que `runtime.txt` tenga `python-3.11`
2. Revisa los logs en Render
3. Asegúrate de que los Excel sean públicos

