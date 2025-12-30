# Sistema de Inventario

Aplicación web Flask para gestionar inventario desde Google Sheets.

## 🚀 Inicio Rápido

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar
```bash
python app.py
```

Abre: `http://localhost:5000`

## 🔐 Login

Los usuarios se leen desde este Excel:
- URL: `https://docs.google.com/spreadsheets/d/1DagcKZIkcvN0ODF0G-4Ddrml9e9HqNfFj-c6Z7zBrFs/edit`
- Columnas: `User` y `pass`

## 🌐 Desplegar en Render

### Paso 1: Configuración en Render
- **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command:** `gunicorn wsgi:app`

### Paso 2: Variables de Entorno

En Render, ve a **Environment** y agrega:

#### Obligatorias:
```
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-muy-larga-aqui
```

#### Opcionales (tienen valores por defecto):
Si necesitas cambiar las URLs de los Google Sheets, agrega:
```
INVENTORY_SHEET_URL=https://docs.google.com/spreadsheets/d/...
USERS_SHEET_URL=https://docs.google.com/spreadsheets/d/...
HISTORY_SHEET_URL=https://docs.google.com/spreadsheets/d/...
USERS_SHEET_GID=0
USERS_COLUMN_USERNAME=User
USERS_COLUMN_PASSWORD=pass
```

**Nota:** Si no agregas las opcionales, se usarán los valores por defecto configurados en `config.py`.

## 📝 Notas

- El Excel de usuarios debe ser público
- El Excel de inventario se configura en `config.py`
- Python 3.11 recomendado

