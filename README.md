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

### Paso 2: Variables de Entorno (solo 2 necesarias)

En Render, ve a **Environment** y agrega:

```
FLASK_ENV=production
SECRET_KEY=cualquier-texto-largo-y-secreto-aqui
```

**Eso es todo.** Las demás configuraciones ya están en el código.

## 📝 Notas

- El Excel de usuarios debe ser público
- El Excel de inventario se configura en `config.py`
- Python 3.11 recomendado

