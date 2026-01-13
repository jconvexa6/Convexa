# Scripts de Utilidad

Este directorio contiene scripts útiles para gestionar el inventario y los códigos QR.

## 📋 Scripts Disponibles

### 1. `generate_all_qr_codes.py`
Genera códigos QR masivamente para todos los productos del inventario y los sube a la carpeta QR en Google Drive.

### 2. `refresh_google_token.py`
Refresca el token de Google cuando expire.

---

## 🚀 Uso de `generate_all_qr_codes.py`

### Uso Básico
```bash
python scripts/generate_all_qr_codes.py
```

Este comando:
- Lee todos los productos del inventario desde Google Sheets
- Genera un código QR para cada producto que codifica la URL completa con la Referencia al final
- Sube cada QR a la carpeta QR en Google Drive
- Muestra un resumen con estadísticas al finalizar

**Nota importante**: El QR codifica la URL completa: `https://convexa-1.onrender.com/product/detail/{REFERENCIA}` (ejemplo: `https://convexa-1.onrender.com/product/detail/604-2RS1-C3GJN`) El campo "Referencia" se usa como identificador del producto en la URL.

### Opciones Avanzadas

#### Especificar URL base personalizada
```bash
python scripts/generate_all_qr_codes.py --base-url https://tu-dominio.com
```

#### Procesar solo los primeros N productos (útil para pruebas)
```bash
python scripts/generate_all_qr_codes.py --limit 10
```

#### Ver todas las opciones
```bash
python scripts/generate_all_qr_codes.py --help
```

### Ejemplos de Uso

**Generar QR para todos los productos:**
```bash
python scripts/generate_all_qr_codes.py
```

**Probar con solo 5 productos:**
```bash
python scripts/generate_all_qr_codes.py --limit 5
```

**Generar QR con URL personalizada:**
```bash
python scripts/generate_all_qr_codes.py --base-url https://convexa-1.onrender.com
```

**Combinar opciones:**
```bash
python scripts/generate_all_qr_codes.py --base-url https://convexa-1.onrender.com --limit 20
```

---

## 📝 Requisitos Previos

Antes de ejecutar los scripts, asegúrate de:

1. ✅ Tener configurado el token de Google (`GOOGLE_TOKEN_JSON` o archivo `token.json`)
2. ✅ Tener acceso a internet para conectarse a Google Sheets y Google Drive
3. ✅ Tener instaladas todas las dependencias del proyecto (`pip install -r requirements.txt`)

---

## 🔍 Cómo Funciona

1. **Lectura del Inventario**: El script lee todos los productos desde Google Sheets usando `SheetsService.get_inventory_data()`

2. **Extracción de Datos**: Para cada producto, extrae:
   - **ID del producto**: Busca en campos como 'ID', 'id', 'codigo', 'Código', etc. (usado para validación)
   - **Código del producto**: Usado para logging y referencia
   - **Referencia del producto**: Usado para el nombre del archivo QR y al final de la URL
     - Nombre del archivo: `{REFERENCIA}.png` (ej: `604-2RS1-C3GJN.png`)
     - URL: `https://convexa-1.onrender.com/product/detail/{REFERENCIA}` (ej: `https://convexa-1.onrender.com/product/detail/604-2RS1-C3GJN`)

3. **Generación de QR**: Crea un código QR que codifica la URL completa con la Referencia al final:
   ```
   https://convexa-1.onrender.com/product/detail/604-2RS1-C3GJN
   ```
   Al escanear el QR, el usuario será redirigido a la página de detalle del producto usando la Referencia como identificador.

4. **Subida a Drive**: Sube cada QR a la carpeta QR en Google Drive. Si el archivo ya existe, lo actualiza.

---

## ⚠️ Notas Importantes

- El script procesa los productos **secuencialmente** con una pausa de 500ms entre cada uno para no sobrecargar la API de Google
- Si un producto ya tiene un QR, **se actualiza** (no se omite por defecto)
- Los errores se muestran al final en un resumen detallado
- El script muestra el progreso en tiempo real: `[X/Total] Procesando: ID (CODIGO)...`

---

## 🐛 Solución de Problemas

### Error: "GOOGLE_TOKEN_JSON no está configurada"
**Solución**: Configura la variable de entorno o coloca un archivo `token.json` en `app/static/Credenciales/`

### Error: "No se encontraron productos"
**Solución**: Verifica que el Google Sheet de inventario sea accesible y tenga productos con IDs válidos

### Error: "Producto sin Referencia válida"
**Solución**: Asegúrate de que todos los productos tengan el campo "Referencia" completado en el inventario, ya que este campo se usa como identificador en la URL


### Error: "Error al subir QR a Drive"
**Solución**: Verifica que tengas permisos de escritura en Google Drive y que la carpeta QR exista

---

## 📊 Salida del Script

El script muestra:
- ✅ Progreso en tiempo real
- 📊 Resumen final con estadísticas:
  - Productos procesados exitosamente
  - Errores encontrados
  - Productos omitidos (sin ID válido)
- ❌ Lista detallada de errores (si los hay)

---

## 💡 Consejos

- **Primera ejecución**: Usa `--limit 5` para probar con pocos productos
- **Producción**: Ejecuta sin límites para procesar todos los productos
- **Actualización masiva**: Ejecuta periódicamente para asegurar que todos los QR estén actualizados

