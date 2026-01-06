# 🔐 CÓMO CONFIGURAR EL TOKEN DE GOOGLE - GUÍA SIMPLE

## 📋 Paso a Paso (MUY FÁCIL)

### Paso 1: Abrir el archivo del token

1. En tu computadora, abre la carpeta del proyecto
2. Ve a la carpeta: `app` → `static` → `Credenciales`
3. Abre el archivo llamado `token.json` con el Bloc de notas (Notepad)

### Paso 2: Copiar TODO el contenido

1. Presiona `Ctrl + A` (esto selecciona todo el texto)
2. Presiona `Ctrl + C` (esto copia todo)

**IMPORTANTE:** Debes copiar TODO el contenido, desde la primera `{` hasta la última `}`

### Paso 3: Ir a Render

1. Abre tu navegador
2. Ve a: https://dashboard.render.com
3. Inicia sesión con tu cuenta

### Paso 4: Encontrar tu aplicación

1. En la lista de servicios, busca tu aplicación (probablemente se llama "convexa" o similar)
2. Haz clic en el nombre de tu aplicación

### Paso 5: Ir a la sección de Variables de Entorno

1. En el menú de la izquierda, busca y haz clic en **"Environment"** (o "Variables de Entorno")
2. Verás una lista de variables que ya tienes configuradas

### Paso 6: Agregar la nueva variable

1. Haz clic en el botón **"Add Environment Variable"** (o "Agregar Variable de Entorno")
2. En el campo **"Key"** (o "Clave"), escribe exactamente esto:
   ```
   GOOGLE_TOKEN_JSON
   ```
3. En el campo **"Value"** (o "Valor"), pega lo que copiaste antes:
   - Presiona `Ctrl + V` para pegar
   - **MUY IMPORTANTE:** Asegúrate de que todo esté en UNA SOLA LÍNEA (sin saltos de línea)
   - Si ves que hay saltos de línea, elimínalos y ponlo todo junto

### Paso 7: Guardar

1. Haz clic en el botón **"Save Changes"** (o "Guardar Cambios")
2. Render comenzará a redesplegar tu aplicación automáticamente

### Paso 8: Esperar

1. Espera unos minutos (2-5 minutos normalmente)
2. Verás que Render está "Building" (construyendo) y luego "Deploying" (desplegando)
3. Cuando termine, verás un mensaje verde que dice "Live" (en vivo)

## ✅ ¡Listo!

Después de esto, tu aplicación debería funcionar correctamente. Puedes probar editando un producto.

---

## 🆘 Si algo sale mal

### Error: "GOOGLE_TOKEN_JSON no está configurada"

**Solución:** Significa que no agregaste la variable o no la guardaste correctamente.
- Vuelve al Paso 5 y verifica que la variable existe
- Verifica que el nombre sea exactamente: `GOOGLE_TOKEN_JSON` (con mayúsculas y guión bajo)

### Error: "JSON inválido"

**Solución:** Significa que el contenido que pegaste no está bien formateado.
- Vuelve al Paso 2 y copia TODO el contenido del archivo `token.json`
- Asegúrate de que esté todo en una sola línea
- Verifica que empiece con `{` y termine con `}`

### La aplicación no funciona después de configurar

**Solución:**
1. Ve a Render y verifica que el despliegue terminó correctamente
2. Si hay errores, haz clic en "Logs" (Registros) para ver qué pasó
3. Si el error dice algo sobre el token, verifica que copiaste TODO el contenido correctamente

---

## 📸 Ejemplo visual de cómo debería verse

Cuando agregues la variable, debería verse así:

```
Key: GOOGLE_TOKEN_JSON
Value: {"token":"ya29.a0Aa7pCA...","refresh_token":"1//01UCdRe...","token_uri":"https://oauth2.googleapis.com/token","client_id":"1012866464546-...","client_secret":"GOCSPX-...","scopes":["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]}
```

**Nota:** El valor será mucho más largo, pero debe estar TODO en una sola línea.

---

## 💡 Consejo

Si tienes problemas, puedes:
1. Copiar el contenido del `token.json` a un editor de texto simple (como Notepad)
2. Eliminar todos los saltos de línea manualmente
3. Copiar esa versión de una sola línea y pegarla en Render




