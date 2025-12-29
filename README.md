# Sistema de Inventario - Flask Web Application

Aplicación web desarrollada en Flask para gestión de inventario, con lectura de datos desde Google Sheets.

## 🚀 Características

- ✅ Autenticación segura con Flask-Login
- ✅ Dashboard con tabla DataTable (búsqueda, ordenamiento, paginación)
- ✅ Lectura de datos desde Google Sheets
- ✅ Vista de detalle de productos
- ✅ Arquitectura modular con Blueprints
- ✅ Listo para despliegue en Render

## 📋 Requisitos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)

## 🛠️ Instalación Local

### 1. Clonar o descargar el proyecto

```bash
cd WEBSITE-INV
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar credenciales de usuario

Por defecto, el sistema usa:
- **Usuario:** `admin`
- **Contraseña:** `admin123`

⚠️ **IMPORTANTE:** Cambia estas credenciales en producción editando `config.py` y generando un hash seguro de la contraseña.

Para generar un hash de contraseña:

```python
from werkzeug.security import generate_password_hash
print(generate_password_hash('tu_contraseña_segura'))
```

Luego actualiza `config.py` con el hash generado.

### 5. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## 🌐 Despliegue en Render

### 1. Preparación

1. Crea una cuenta en [Render](https://render.com)
2. Conecta tu repositorio Git o sube el código

### 2. Configurar el servicio

1. En Render, crea un nuevo **Web Service**
2. Configura:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app`
   - **Environment:** `Python 3`

### 3. Variables de entorno

Configura las siguientes variables de entorno en Render:

```
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
INVENTORY_SHEET_URL=https://docs.google.com/spreadsheets/d/11YVSLtIM-pjsVT2fBe4yLEjZnVDGdrtchFQc1GYYPYE/edit
```

### 4. Desplegar

Render desplegará automáticamente tu aplicación.

## 📁 Estructura del Proyecto

```
WEBSITE-INV/
├── app/
│   ├── __init__.py          # Inicialización de Flask
│   ├── routes/               # Blueprints de rutas
│   │   ├── __init__.py
│   │   ├── auth.py          # Autenticación
│   │   ├── dashboard.py      # Dashboard principal
│   │   └── product.py        # Detalle de productos
│   ├── services/             # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── auth_service.py   # Servicio de autenticación
│   │   └── sheets_service.py # Servicio de Google Sheets
│   ├── templates/            # Plantillas HTML
│   │   ├── base.html
│   │   ├── auth/
│   │   │   └── login.html
│   │   ├── dashboard/
│   │   │   └── index.html
│   │   └── product/
│   │       └── detail.html
│   └── static/               # Archivos estáticos
│       ├── css/
│       │   └── style.css
│       └── js/
├── config.py                 # Configuración
├── app.py                    # Ejecución en desarrollo
├── wsgi.py                   # WSGI para producción
├── run.py                    # Script alternativo
├── requirements.txt          # Dependencias
└── README.md                 # Este archivo
```

## 🔐 Autenticación

El sistema usa Flask-Login para manejo de sesiones. **Las credenciales se leen desde un Google Sheet (Excel)**.

### Configuración de Usuarios

Los usuarios y contraseñas se leen desde un Google Sheet. Por defecto, se usa la misma hoja del inventario, pero puedes configurar una hoja diferente.

**Estructura del Excel:**
- Columna 1: `usuario` (o `username`, `user`)
- Columna 2: `contraseña` (o `password`, `pass`)

Ver `USUARIOS_EXCEL.md` para más detalles sobre cómo configurar el Excel de usuarios.

⚠️ **En producción, considera usar contraseñas hasheadas para mayor seguridad.**

## 📊 Google Sheets

La aplicación lee datos desde un Google Sheet público. La URL se configura en `config.py` o mediante la variable de entorno `INVENTORY_SHEET_URL`.

**URL por defecto:**
```
https://docs.google.com/spreadsheets/d/11YVSLtIM-pjsVT2fBe4yLEjZnVDGdrtchFQc1GYYPYE/edit
```

El servicio convierte automáticamente el Google Sheet a CSV y lo procesa con Pandas.

## 🎨 Tecnologías Utilizadas

- **Flask 3.0.0** - Framework web
- **Flask-Login 0.6.3** - Autenticación
- **Pandas 2.1.4** - Procesamiento de datos
- **Bootstrap 5.3.0** - Framework CSS
- **DataTables** - Tablas interactivas
- **Gunicorn** - Servidor WSGI para producción

## 📝 Notas

- El Google Sheet debe ser público o accesible sin autenticación
- La primera columna se usa como ID único del producto
- Si no hay columna "id", se genera automáticamente basado en el índice

## 🐛 Solución de Problemas

### Error al leer Google Sheets
- Verifica que la URL del sheet sea correcta
- Asegúrate de que el sheet sea público o accesible
- Revisa la conexión a internet

### Error de autenticación
- Verifica las credenciales en `config.py`
- Asegúrate de que Flask-Login esté correctamente configurado

### Error en producción
- Verifica que todas las variables de entorno estén configuradas
- Revisa los logs en Render
- Asegúrate de que `gunicorn` esté en `requirements.txt`

## 📄 Licencia

Este proyecto es de uso interno.

