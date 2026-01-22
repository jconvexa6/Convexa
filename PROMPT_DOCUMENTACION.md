# Prompt Profesional para Generar Documentación del Sistema de Inventario

## Prompt para IA/Generador de Contenido

```
Crea una página web profesional de documentación técnica para un Sistema de Gestión de Inventario basado en Flask y Google Sheets. La página debe incluir:

## CONTEXTO DEL SISTEMA

**Nombre del Sistema:** Sistema de Gestión de Inventario con Códigos QR
**Tecnología Principal:** Flask (Python), Google Sheets API, Google Drive API
**Plataforma de Despliegue:** Render.com
**URL de Producción:** https://convexa-1.onrender.com

## FUNCIONALIDADES PRINCIPALES

1. **Gestión de Inventario**
   - Lectura y escritura de datos desde Google Sheets
   - Visualización de productos en dashboard interactivo
   - Edición de productos con actualización en tiempo real
   - Registro de movimientos (ingresos y salidas) con histórico

2. **Sistema de Autenticación**
   - Login basado en Google Sheets
   - Gestión de usuarios desde hoja de cálculo externa
   - Sesiones seguras con Flask-Login

3. **Generación Masiva de Códigos QR**
   - Script automatizado para generar QR de todos los productos
   - Los QR codifican URLs que redirigen a la página de detalle del producto
   - Almacenamiento automático en Google Drive
   - Nomenclatura basada en el campo "Referencia" del producto

4. **Características Técnicas**
   - Integración completa con Google Sheets API
   - Integración con Google Drive API
   - Refresh automático de tokens OAuth2
   - Sistema de respaldo local de credenciales
   - Búsqueda flexible de productos por ID o Referencia

## ESTRUCTURA DE LA DOCUMENTACIÓN

La página debe tener las siguientes secciones:

### 1. HERO SECTION
- Título impactante: "Sistema de Gestión de Inventario Inteligente"
- Subtítulo: "Gestiona tu inventario desde Google Sheets con códigos QR integrados"
- Botones de acción: "Ver Demo", "Documentación", "GitHub"
- Imagen o ilustración representativa

### 2. CARACTERÍSTICAS PRINCIPALES
Presentar en cards o grid:
- 📊 **Dashboard Interactivo**: Visualización completa del inventario
- 🔐 **Autenticación Segura**: Login basado en Google Sheets
- 📱 **Códigos QR Automáticos**: Generación masiva con URLs integradas
- 🔄 **Sincronización en Tiempo Real**: Actualización automática con Google Sheets
- 📈 **Histórico de Movimientos**: Registro completo de ingresos y salidas
- ☁️ **Almacenamiento en la Nube**: Integración con Google Drive

### 3. ARQUITECTURA TÉCNICA
- Diagrama o descripción de la arquitectura
- Stack tecnológico (Flask, Python, Google APIs)
- Flujo de datos entre componentes
- Integración con servicios externos

### 4. FUNCIONALIDADES DETALLADAS

#### 4.1 Gestión de Productos
- Visualización de inventario completo
- Búsqueda y filtrado de productos
- Edición de información de productos
- Registro de movimientos de stock

#### 4.2 Sistema de Códigos QR
- Generación masiva automatizada
- Formato de URL: `https://convexa-1.onrender.com/product/detail/{REFERENCIA}`
- Almacenamiento en Google Drive
- Nomenclatura: `{REFERENCIA}.png`

#### 4.3 Autenticación y Seguridad
- Sistema de login basado en Google Sheets
- Gestión de sesiones seguras
- Control de acceso por usuario

### 5. INSTALACIÓN Y CONFIGURACIÓN
- Requisitos del sistema
- Pasos de instalación
- Configuración de credenciales de Google
- Variables de entorno necesarias
- Despliegue en Render.com

### 6. GUÍA DE USO

#### 6.1 Para Administradores
- Cómo configurar Google Sheets
- Cómo generar códigos QR masivamente
- Cómo gestionar usuarios

#### 6.2 Para Usuarios Finales
- Cómo iniciar sesión
- Cómo visualizar productos
- Cómo editar productos
- Cómo registrar movimientos

### 7. SCRIPTS Y HERRAMIENTAS
- `generate_all_qr_codes.py`: Generación masiva de QR
- `refresh_google_token.py`: Gestión de tokens OAuth2
- Documentación de uso de cada script

### 8. API Y SERVICIOS
- Google Sheets API
- Google Drive API
- Endpoints de la aplicación Flask
- Estructura de datos

### 9. SOLUCIÓN DE PROBLEMAS
- Errores comunes y soluciones
- Troubleshooting de credenciales
- Problemas de sincronización
- Errores de generación de QR

### 10. ROADMAP Y MEJORAS FUTURAS
- Funcionalidades planificadas
- Mejoras técnicas pendientes
- Optimizaciones previstas

## REQUISITOS DE DISEÑO

- Diseño moderno y profesional
- Responsive (móvil, tablet, desktop)
- Paleta de colores corporativa (azules, grises, blancos)
- Tipografía clara y legible
- Iconos y gráficos relevantes
- Navegación intuitiva
- Secciones bien organizadas
- Código con syntax highlighting
- Ejemplos visuales cuando sea posible

## TONO Y ESTILO

- Profesional pero accesible
- Técnico pero comprensible
- Claro y conciso
- Orientado a desarrolladores y usuarios técnicos
- Incluir ejemplos prácticos
- Usar casos de uso reales

## ELEMENTOS ADICIONALES

- Tabla de contenidos navegable
- Búsqueda de contenido
- Enlaces a repositorio GitHub
- Sección de contacto o soporte
- Badges de tecnologías utilizadas
- Screenshots o capturas de pantalla (si es posible)
- Diagramas de flujo o arquitectura

## FORMATO DE SALIDA

Genera la documentación en formato HTML/CSS moderno, Markdown, o el formato que prefieras, pero asegúrate de que sea:
- Bien estructurado
- Fácil de navegar
- Visualmente atractivo
- Completo y detallado
- Listo para desplegar o convertir a página web

Por favor, crea una documentación completa, profesional y lista para usar.
```

---

## Versión Corta del Prompt (Para uso rápido)

```
Crea documentación técnica profesional para un Sistema de Gestión de Inventario Flask que:
- Integra Google Sheets y Google Drive
- Genera códigos QR masivamente con URLs que redirigen a productos
- Tiene autenticación basada en Google Sheets
- Incluye dashboard, edición de productos y registro de movimientos
- Se despliega en Render.com

Incluye: hero section, características, arquitectura, guías de instalación/uso, documentación de scripts, solución de problemas, y diseño moderno responsive.
```

---

## Versión para Generar Página de Marketing

```
Crea una landing page profesional para un Sistema de Gestión de Inventario con las siguientes características:

**Producto:** Sistema web que gestiona inventario desde Google Sheets con códigos QR integrados

**Beneficios principales:**
- No necesitas base de datos propia, usa Google Sheets
- Generación automática de códigos QR para cada producto
- Acceso desde cualquier dispositivo con conexión a internet
- Sincronización en tiempo real
- Histórico completo de movimientos

**Target:** Empresas medianas y pequeñas que necesitan gestionar inventario de forma simple y eficiente

**Incluye:**
- Hero section con CTA
- Sección de beneficios
- Demo o screenshots
- Testimonios (opcional)
- Precios/planes (si aplica)
- Formulario de contacto
- Diseño moderno y profesional
```
