"""
Rutas para detalle y edición de productos
"""
from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.sheets_service import SheetsService
from app.services.sheets_writer import SheetsWriter
from app.services.qr_service import QRService

product_bp = Blueprint('product', __name__)


# Opciones fijas para el formulario de creación de producto
CODIGO_OPCIONES = ['RMEC', 'EFFI', 'RNEU', 'RHID', 'EEPO', 'EAUT', 'LCON', 'SIND', 'EAPO']
UNIDAD_MEDIDA_OPCIONES = [
    'Unidad', 'Metros', 'Gramos', 'Kilogramos', 'Mililitros', 'Litro',
    'Galón', 'Caneca', 'Juegos', 'Kit'
]


@product_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Vista para crear un nuevo producto
    """
    if request.method == 'POST':
        return _create_product(current_user.username)
    
    # GET: Mostrar formulario de creación
    try:
        inventory_data = SheetsService.get_inventory_data()
        next_id = SheetsService.get_next_product_id()
        # Siguiente consecutivo por abreviatura de código (ej. RMEC -> 3 para RMEC-3)
        codigo_siguiente = {
            abrev: SheetsService.get_next_codigo_consecutivo(abrev)
            for abrev in CODIGO_OPCIONES
        }
        # Campos a mostrar (sin ID como editable; ID es auto)
        if inventory_data:
            sample_product = inventory_data[0]
            fields = [k for k in sample_product.keys() if str(k).strip().lower() not in ('id', 'id ')]
            if 'Codigo' not in fields and 'codigo' not in [f.lower() for f in fields]:
                fields.insert(0, 'Codigo')
            if 'Unidad-medida' not in fields and not any('unidad' in str(f).lower() for f in fields):
                fields.append('Unidad-medida')
        else:
            fields = ['Codigo', 'Referencia', 'Descripcion', 'Unidad-medida', 'cantidad', 'Ubicación', 'Stock-min', 'Estado']
        return render_template(
            'product/create.html',
            fields=fields,
            next_id=next_id,
            codigo_opciones=CODIGO_OPCIONES,
            codigo_siguiente=codigo_siguiente,
            unidad_medida_opciones=UNIDAD_MEDIDA_OPCIONES
        )
    except Exception as e:
        flash(f'Error al cargar formulario: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))


def _create_product(username: str):
    """
    Crear un nuevo producto. El ID se asigna automáticamente (siguiente consecutivo).
    """
    try:
        form_data = request.form.to_dict()
        
        # Asignar ID automático (siguiente consecutivo)
        product_id = str(SheetsService.get_next_product_id())
        form_data['ID'] = product_id
        
        # Crear producto en el inventario
        success = SheetsWriter.create_product_in_inventory(form_data)
        
        if not success:
            flash('Error al crear el producto en el inventario.', 'error')
            return redirect(url_for('product.create'))
        
        flash('Producto creado correctamente.', 'success')
        
        # Generar QR para el nuevo producto
        try:
            # Obtener código del producto (segunda columna)
            product_code = form_data.get('Codigo') or form_data.get('Código') or form_data.get('codigo')
            
            if product_code:
                base_url = request.url_root.rstrip('/')
                qr_success = QRService.generate_and_upload_qr(
                    product_id=str(product_id),
                    product_code=str(product_code),
                    base_url=base_url
                )
                if qr_success:
                    print(f"✓ QR generado para nuevo producto {product_id}")
        except Exception as e:
            print(f"⚠️ Error al generar QR (no crítico): {e}")
        
        return redirect(url_for('product.detail', product_id=product_id))
        
    except Exception as e:
        flash(f'Error al crear el producto: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('product.create'))


@product_bp.route('/<product_id>', methods=['GET', 'POST'])
@product_bp.route('/detail/<product_id>', methods=['GET', 'POST'])
@login_required
def detail(product_id):
    """
    Vista de detalle y edición del producto
    """
    try:
        if not product_id or str(product_id).strip() == '':
            flash('ID de producto no válido.', 'error')
            return redirect(url_for('dashboard.index'))
        
        product = SheetsService.get_product_by_id(product_id)
        
        if not product:
            flash(f'Producto con ID "{product_id}" no encontrado.', 'error')
            return redirect(url_for('dashboard.index'))
        
        # Si es POST, procesar el guardado
        if request.method == 'POST':
            return _save_product(product_id, product, current_user.username)
        
        # Si es GET, mostrar formulario de edición
        return render_template(
            'product/detail.html',
            product=product,
            product_id=product_id,
            unidad_medida_opciones=UNIDAD_MEDIDA_OPCIONES
        )
    except Exception as e:
        abort(500, description=f"Error al cargar el producto: {str(e)}")


def _save_product(product_id: str, original_product: dict, username: str):
    """
    Guardar cambios del producto y registrar movimiento
    """
    try:
        # Obtener datos del formulario
        form_data = request.form.to_dict()
        
        # Obtener tipo de movimiento y unidades
        tipo_movimiento = form_data.get('tipo_movimiento', '').strip()
        unidades_str = form_data.get('unidades', '0').strip()
        
        if not tipo_movimiento:
            flash('Por favor, seleccione un tipo de movimiento (Ingreso o Salida).', 'error')
            return redirect(url_for('product.detail', product_id=product_id))
        
        try:
            unidades = float(unidades_str) if unidades_str else 0
            if unidades <= 0:
                flash('Las unidades deben ser mayor a 0.', 'error')
                return redirect(url_for('product.detail', product_id=product_id))
        except ValueError:
            flash('Las unidades deben ser un número válido.', 'error')
            return redirect(url_for('product.detail', product_id=product_id))
        
        # Calcular ajuste según el tipo de movimiento
        if tipo_movimiento == 'ingreso':
            ajuste = unidades  # Positivo para aumentar
        elif tipo_movimiento == 'salida':
            ajuste = -unidades  # Negativo para disminuir
        else:
            flash('Tipo de movimiento inválido.', 'error')
            return redirect(url_for('product.detail', product_id=product_id))
        
        # Obtener stock actual
        # Buscar el campo de cantidad/stock (puede tener diferentes nombres)
        stock_actual = 0
        stock_field = None
        
        # Buscar en original_product primero
        for field in ['cantidad', 'Cantidad', 'stock', 'Stock', 'CANTIDAD', 'STOCK', 'cantidad ']:
            # Buscar exacto
            if field in original_product:
                try:
                    val = original_product[field]
                    stock_actual = float(val) if val and str(val).strip() else 0
                    stock_field = field
                    break
                except (ValueError, TypeError):
                    continue
            
            # Buscar case-insensitive
            for key in original_product.keys():
                if str(key).strip().lower() == field.lower():
                    try:
                        val = original_product[key]
                        stock_actual = float(val) if val and str(val).strip() else 0
                        stock_field = key
                        break
                    except (ValueError, TypeError):
                        continue
            if stock_field:
                break
        
        if stock_field is None:
            flash('No se pudo determinar el stock actual del producto. Verifique que exista un campo "cantidad" o "stock".', 'error')
            return redirect(url_for('product.detail', product_id=product_id))
        
        # Calcular nuevo stock
        nuevo_stock = stock_actual + ajuste
        
        # Validar que el stock no sea negativo
        if nuevo_stock < 0:
            flash(f'No se puede realizar la operación. El stock resultante sería negativo ({nuevo_stock}). Stock actual: {stock_actual}', 'error')
            return redirect(url_for('product.detail', product_id=product_id))
        
        # Preparar datos actualizados (excluir ID y Código)
        updated_data = {}
        campos_bloqueados = ['id', 'ID', 'Codigo', 'Código', 'codigo', 'CODIGO']
        
        for key, value in form_data.items():
            if key not in campos_bloqueados and key not in ['tipo_movimiento', 'unidades']:
                updated_data[key] = value
        
        # Actualizar el stock
        updated_data[stock_field] = nuevo_stock
        
        # Actualizar producto en el inventario
        try:
            success = SheetsWriter.update_product_in_inventory(product_id, updated_data)
            
            if not success:
                flash('Error al actualizar el producto en el inventario. Verifique las credenciales de Google Sheets.', 'error')
                return redirect(url_for('product.detail', product_id=product_id))
        except FileNotFoundError as e:
            flash('No se encontró el archivo credentials.json. Colóquelo en app/static/Credenciales/ o en la raíz del proyecto.', 'error')
            return redirect(url_for('product.detail', product_id=product_id))
        except Exception as e:
            error_msg = str(e)
            if 'Google Sheets API no está habilitada' in error_msg:
                flash(
                    '❌ Google Sheets API no está habilitada. '
                    'Habilítala en: https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=1012866464546',
                    'error'
                )
            else:
                flash(f'Error al actualizar el producto: {error_msg}', 'error')
            import traceback
            traceback.print_exc()
            return redirect(url_for('product.detail', product_id=product_id))
        
        # Registrar movimiento en histórico (solo si hay ajuste)
        if ajuste != 0:
            # Función helper para buscar campo case-insensitive
            def get_field(data, possible_names):
                for name in possible_names:
                    # Buscar exacto
                    if name in data:
                        return data[name]
                    # Buscar case-insensitive
                    for key in data.keys():
                        if str(key).strip().lower() == name.lower():
                            return data[key]
                return ''
            
            # Preparar datos para el histórico
            history_data = {
                'Codigo': get_field(original_product, ['Codigo', 'Código', 'codigo', 'CODIGO']) or get_field(form_data, ['Codigo', 'Código', 'codigo']),
                'Referencia': get_field(original_product, ['Referencia', 'referencia']) or get_field(form_data, ['Referencia']),
                'Descripcion': get_field(original_product, ['Descripcion', 'Descripción', 'descripcion']) or get_field(form_data, ['Descripcion', 'Descripción']),
                'Unidad-medida': get_field(original_product, ['Unidad-medida', 'Unidad medida', 'unidad-medida']) or get_field(form_data, ['Unidad-medida']),
                'cantidad': nuevo_stock,  # Stock final después del ajuste
                'Ubicación': get_field(original_product, ['Ubicación', 'Ubicacion', 'ubicación']) or get_field(form_data, ['Ubicación', 'Ubicacion']),
                'Stock-min': get_field(original_product, ['Stock-min', 'Stock min', 'stock-min']) or get_field(form_data, ['Stock-min']),
                'Estado': get_field(original_product, ['Estado', 'estado']) or get_field(form_data, ['Estado']),
                'Metodo': 'Ingreso' if tipo_movimiento == 'ingreso' else 'Salida',
                'UnidadesUtilizadas': unidades,  # Unidades utilizadas (siempre positivo)
            }
            
            # Registrar en histórico
            history_success = SheetsWriter.append_row_to_history(history_data, username)
            
            if not history_success:
                flash('Producto actualizado, pero hubo un error al registrar el movimiento en el histórico.', 'warning')
            else:
                flash('Producto actualizado y movimiento registrado correctamente.', 'success')
        else:
            flash('Producto actualizado correctamente (sin ajuste de unidades).', 'success')
        
        # Generar QR para el producto (si no existe)
        try:
            # Obtener código del producto (segunda columna)
            def get_code_field(data, possible_names):
                for name in possible_names:
                    if name in data:
                        return data[name]
                    for key in data.keys():
                        if str(key).strip().lower() == name.lower():
                            return data[key]
                return None
            
            # Buscar código en diferentes formatos (segunda columna típicamente es "Código" o "Codigo")
            product_code = get_code_field(original_product, ['Codigo', 'Código', 'codigo', 'CODIGO', 'Codigo'])
            
            if product_code:
                # Obtener URL base de la aplicación
                base_url = request.url_root.rstrip('/')
                
                # Generar y subir QR
                qr_success = QRService.generate_and_upload_qr(
                    product_id=product_id,
                    product_code=str(product_code),
                    base_url=base_url
                )
                
                if not qr_success:
                    print(f"Error al generar QR para producto {product_id}")
        except Exception as e:
            print(f"Error al generar QR: {e}")
        
        return redirect(url_for('product.detail', product_id=product_id))
        
    except Exception as e:
        flash(f'Error al guardar el producto: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('product.detail', product_id=product_id))

