"""
Rutas para detalle y edición de productos
"""
from flask import Blueprint, render_template, abort
from flask_login import login_required
from app.services.sheets_service import SheetsService

product_bp = Blueprint('product', __name__)


@product_bp.route('/<product_id>')
@product_bp.route('/detail/<product_id>')
@login_required
def detail(product_id):
    """
    Vista de detalle del producto
    """
    try:
        product = SheetsService.get_product_by_id(product_id)
        
        if not product:
            abort(404, description="Producto no encontrado")
        
        return render_template(
            'product/detail.html',
            product=product,
            product_id=product_id
        )
    except Exception as e:
        abort(500, description=f"Error al cargar el producto: {str(e)}")

