"""
Rutas del dashboard
"""
from flask import Blueprint, render_template
from flask_login import login_required
from app.services.sheets_service import SheetsService

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """
    Dashboard principal con tabla de inventario
    """
    try:
        # Obtener datos del inventario
        inventory_data = SheetsService.get_inventory_data()
        
        return render_template(
            'dashboard/index.html',
            inventory_data=inventory_data
        )
    except Exception as e:
        # En caso de error, mostrar dashboard vacío con mensaje
        return render_template(
            'dashboard/index.html',
            inventory_data=[],
            error_message=f"Error al cargar datos: {str(e)}"
        )

