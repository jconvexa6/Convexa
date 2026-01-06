"""
Script para generar códigos QR masivamente para todos los productos del inventario
Ejecuta este script para crear/actualizar todos los QR en la carpeta QR de Google Drive
"""
import os
import sys
from pathlib import Path
import time

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.sheets_service import SheetsService
from app.services.qr_service import QRService
from config import Config


def get_product_id(product: dict) -> str:
    """
    Obtener el ID del producto desde diferentes campos posibles
    
    Args:
        product: Diccionario con los datos del producto
        
    Returns:
        ID del producto o None si no se encuentra
    """
    # Buscar ID en diferentes formatos (prioridad: ID, id, codigo, Código)
    id_keys = ['ID', 'id', 'Id', 'codigo', 'Código', 'CODIGO', 'Codigo']
    
    for key in id_keys:
        if key in product and product[key] is not None:
            product_id = str(product[key]).strip()
            if product_id:
                return product_id
    
    return None


def get_product_code(product: dict) -> str:
    """
    Obtener el código del producto (usado para el nombre del archivo)
    
    Args:
        product: Diccionario con los datos del producto
        
    Returns:
        Código del producto o el ID si no se encuentra código
    """
    import re
    
    # Buscar código en diferentes formatos (prioridad: Codigo, luego ID)
    code_keys = ['Codigo', 'codigo', 'Código', 'código', 'CODIGO']
    
    for key in code_keys:
        if key in product and product[key] is not None:
            code = str(product[key]).strip()
            if code:
                # Sanitizar el código para que sea válido como nombre de archivo
                # Reemplazar caracteres no válidos con guión bajo
                code = re.sub(r'[<>:"/\\|?*]', '_', code)
                # Limitar longitud
                if len(code) > 100:
                    code = code[:100]
                return code
    
    # Si no hay código, usar el ID
    product_id = get_product_id(product)
    if product_id:
        # Sanitizar también el ID
        product_id = re.sub(r'[<>:"/\\|?*]', '_', product_id)
        return product_id
    
    return 'unknown'


def get_product_reference(product: dict) -> str:
    """
    Obtener el campo Referencia del producto (usado como identificador en la URL)
    
    Args:
        product: Diccionario con los datos del producto
        
    Returns:
        Valor de Referencia o None si no se encuentra
    """
    # Buscar Referencia en diferentes formatos
    ref_keys = ['Referencia', 'referencia', 'REFERENCIA', 'Ref', 'ref']
    
    for key in ref_keys:
        if key in product and product[key] is not None:
            referencia = str(product[key]).strip()
            if referencia:
                return referencia
    
    return None


def generate_all_qr_codes(base_url: str = None, skip_existing: bool = False, limit: int = None):
    """
    Generar códigos QR para todos los productos del inventario
    El QR codificará la URL completa que redirige a la página de detalle del producto
    
    Args:
        base_url: URL base de la aplicación (opcional, se detecta automáticamente)
        skip_existing: Si True, omite productos que ya tienen QR (por defecto False para actualizar todos)
        limit: Número máximo de productos a procesar (None para todos)
    """
    print("="*70)
    print("🔄 GENERADOR MASIVO DE CÓDIGOS QR")
    print("="*70)
    print()
    
    # Obtener URL base
    if base_url is None:
        base_url = os.environ.get('BASE_URL', 'https://convexa-1.onrender.com')
    
    base_url = base_url.rstrip('/')
    print(f"📍 URL base: {base_url}")
    print(f"🔗 Los QR redirigirán a: {base_url}/product/detail/{{REFERENCIA}}")
    print("📝 Usando el campo 'Referencia' como identificador del producto")
    print()
    
    # Obtener todos los productos del inventario
    print("📋 Obteniendo productos del inventario...")
    try:
        products = SheetsService.get_inventory_data()
        total_products = len(products)
        
        if total_products == 0:
            print("❌ No se encontraron productos en el inventario")
            return
        
        print(f"✅ Se encontraron {total_products} productos")
        print()
        
        if limit:
            products = products[:limit]
            print(f"⚠️  Procesando solo los primeros {limit} productos (límite establecido)")
            print()
        
    except Exception as e:
        print(f"❌ Error al obtener productos del inventario: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Estadísticas
    success_count = 0
    error_count = 0
    skipped_count = 0
    errors = []
    
    print("🚀 Iniciando generación de QR...")
    print("="*70)
    print()
    
    # Procesar cada producto
    for idx, product in enumerate(products, 1):
        # Obtener ID, código y referencia del producto
        product_id = get_product_id(product)
        product_code = get_product_code(product)
        product_reference = get_product_reference(product)
        
        if not product_id:
            print(f"⚠️  [{idx}/{total_products}] Producto sin ID válido, omitiendo...")
            skipped_count += 1
            continue
        
        if not product_reference:
            print(f"⚠️  [{idx}/{total_products}] Producto {product_id} sin Referencia válida, omitiendo...")
            skipped_count += 1
            errors.append({
                'id': product_id,
                'code': product_code,
                'error': 'No tiene campo Referencia'
            })
            continue
        
        # Construir URL completa del producto usando la Referencia como identificador
        # Sanitizar la referencia para URL (codificar caracteres especiales)
        import urllib.parse
        reference_encoded = urllib.parse.quote(str(product_reference), safe='')
        product_url = f"{base_url}/product/detail/{reference_encoded}"
        
        # Mostrar progreso
        print(f"[{idx}/{total_products}] Procesando: {product_id} ({product_code})...")
        print(f"   Referencia: {product_reference}")
        print(f"   URL: {product_url}")
        
        try:
            # Generar QR con la URL completa que redirige a la página de detalle
            qr_image = QRService.generate_qr_code(product_url, product_code)
            
            if not qr_image:
                print("   ❌ Falló al generar QR")
                error_count += 1
                errors.append({
                    'id': product_id,
                    'code': product_code,
                    'reference': product_reference,
                    'error': 'Error al generar imagen QR'
                })
                continue
            
            # Nombre del archivo: código del producto + .png
            filename = f"{product_code}.png"
            
            # Subir QR a Drive
            success = QRService.upload_qr_to_drive(qr_image, filename, product_code)
            
            if success:
                print("   ✅ QR generado y subido correctamente")
                success_count += 1
            else:
                print("   ❌ Falló al subir")
                error_count += 1
                errors.append({
                    'id': product_id,
                    'code': product_code,
                    'reference': product_reference,
                    'error': 'Error al subir QR a Drive'
                })
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            error_count += 1
            errors.append({
                'id': product_id,
                'code': product_code,
                'reference': product_reference if 'product_reference' in locals() else None,
                'error': str(e)
            })
        
        # Pequeña pausa para no sobrecargar la API de Google
        if idx < total_products:
            time.sleep(0.5)  # 500ms entre cada QR
    
    # Resumen final
    print()
    print("="*70)
    print("📊 RESUMEN")
    print("="*70)
    print(f"✅ Exitosos:     {success_count}")
    print(f"❌ Errores:      {error_count}")
    print(f"⚠️  Omitidos:     {skipped_count}")
    print(f"📦 Total:        {total_products}")
    print()
    
    if errors:
        print("="*70)
        print("❌ ERRORES DETALLADOS")
        print("="*70)
        for error in errors:
            print(f"  • {error['id']} ({error['code']}): {error['error']}")
        print()
    
    print("="*70)
    print("✨ Proceso completado")
    print("="*70)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generar códigos QR para todos los productos del inventario'
    )
    parser.add_argument(
        '--base-url',
        type=str,
        default=None,
        help='URL base de la aplicación (ej: https://convexa-1.onrender.com)'
    )
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        help='Omitir productos que ya tienen QR (por defecto actualiza todos)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Número máximo de productos a procesar (útil para pruebas)'
    )
    
    args = parser.parse_args()
    
    generate_all_qr_codes(
        base_url=args.base_url,
        skip_existing=args.skip_existing,
        limit=args.limit
    )

