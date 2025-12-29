# Configuración de Usuarios desde Excel

El sistema ahora lee los usuarios y contraseñas desde un Google Sheet (Excel en línea).

## 📋 Estructura del Excel de Usuarios

El Excel debe tener al menos dos columnas:

| usuario | contraseña |
|---------|------------|
| admin   | admin123   |
| juan    | miPass123  |
| maria   | password456|

### Nombres de Columnas

El sistema busca automáticamente las columnas con estos nombres (case insensitive):
- **Usuario:** `usuario`, `username`, `user`
- **Contraseña:** `contraseña`, `password`, `pass`

Puedes usar cualquiera de estos nombres en tu Excel.

## 🔧 Configuración

### Opción 1: Misma hoja, diferente pestaña

Si los usuarios están en la misma hoja del inventario pero en una pestaña diferente:

1. En `config.py`, asegúrate de que `USERS_SHEET_URL` apunte a la misma URL del inventario
2. Configura el `USERS_SHEET_GID` con el ID de la pestaña

Para obtener el GID de una pestaña:
- Abre el Google Sheet
- Haz clic en la pestaña
- Mira la URL, el GID está al final: `...&gid=123456789`

### Opción 2: Hoja separada

Si los usuarios están en un Google Sheet completamente diferente:

1. Comparte el Google Sheet como público (o accesible sin autenticación)
2. En `config.py` o variable de entorno, configura:
   ```python
   USERS_SHEET_URL = 'https://docs.google.com/spreadsheets/d/TU_SHEET_ID/edit'
   ```

## 🔐 Seguridad de Contraseñas

### Contraseñas en texto plano (desarrollo)

Por defecto, el sistema acepta contraseñas en texto plano para facilitar el desarrollo.

### Contraseñas hasheadas (producción)

Para mayor seguridad, puedes hashear las contraseñas:

1. Ejecuta el script:
   ```bash
   python generate_password_hash.py
   ```

2. Ingresa la contraseña y copia el hash generado

3. En el Excel, reemplaza la contraseña en texto plano con el hash

El sistema detectará automáticamente si la contraseña está hasheada (empieza con `pbkdf2:`) y la verificará correctamente.

## 📝 Ejemplo de Excel

```
| usuario | contraseña                                    |
|---------|-----------------------------------------------|
| admin   | admin123                                      |
| juan    | pbkdf2:sha256:600000$salt$hash_generado      |
| maria   | miPasswordSegura                             |
```

## ⚙️ Variables de Entorno

Puedes configurar estas variables de entorno:

```bash
USERS_SHEET_URL=https://docs.google.com/spreadsheets/d/TU_SHEET_ID/edit
USERS_SHEET_GID=0
USERS_COLUMN_USERNAME=usuario
USERS_COLUMN_PASSWORD=contraseña
```

## 🐛 Solución de Problemas

### Error: "No se encontraron las columnas necesarias"

- Verifica que el Excel tenga columnas con nombres similares a: `usuario`, `username`, `user` y `contraseña`, `password`, `pass`
- Asegúrate de que no haya espacios extra en los nombres de las columnas

### Error: "Error al obtener usuarios desde Excel"

- Verifica que el Google Sheet sea público o accesible
- Revisa que la URL sea correcta
- Asegúrate de que el GID de la pestaña sea correcto

### Los usuarios no se autentican

- Verifica que las contraseñas en el Excel coincidan exactamente (sin espacios extra)
- Si usas contraseñas hasheadas, asegúrate de que el hash sea completo y correcto

