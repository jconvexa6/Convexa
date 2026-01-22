"""
Rutas del dashboard
"""
from flask import Blueprint, render_template
from flask_login import login_required
from app.services.sheets_service import SheetsService
import pandas as pd

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


@dashboard_bp.route('/units-of-measure')
@login_required
def units_of_measure():
    """
    Vista de lista de unidades de medida
    Lee los datos desde Google Sheets
    """
    try:
        from config import Config
        
        # Leer datos desde Google Sheets
        df = SheetsService.read_google_sheet(Config.UNITS_OF_MEASURE_SHEET_URL)
        
        # Convertir DataFrame a lista de diccionarios
        units_data = []
        
        for _, row in df.iterrows():
            # Mapear columnas del Google Sheet a nuestro formato
            # El sheet tiene: Id, Codigo, Nombre (columna C puede estar vacía)
            
            # Obtener valores de las columnas (case insensitive)
            id_value = None
            codigo_value = None
            nombre_value = None
            
            # Buscar columnas por diferentes nombres posibles
            for col in df.columns:
                col_lower = str(col).strip().lower()
                if col_lower in ['id', 'id_', 'identificador']:
                    id_value = row[col] if pd.notna(row[col]) else None
                elif col_lower in ['codigo', 'código', 'code']:
                    codigo_value = row[col] if pd.notna(row[col]) else None
                elif col_lower in ['nombre', 'name', 'descripcion', 'descripción']:
                    nombre_value = row[col] if pd.notna(row[col]) else None
            
            # Solo agregar si tiene al menos Id o Codigo
            if id_value or codigo_value:
                # Limpiar valores
                id_str = str(id_value).strip() if id_value else ''
                codigo_str = str(codigo_value).strip() if codigo_value else ''
                nombre_str = str(nombre_value).strip() if nombre_value else ''
                
                # Si el Id está vacío pero hay Codigo, usar Codigo como Id
                if not id_str and codigo_str:
                    id_str = codigo_str
                
                # Si el nombre está vacío, usar el código como nombre
                if not nombre_str and codigo_str:
                    nombre_str = codigo_str
                elif not nombre_str and id_str:
                    nombre_str = id_str
                
                # Omitir filas vacías
                if not id_str and not codigo_str:
                    continue
                
                # Crear objeto de unidad de medida
                unit = {
                    'codigo': id_str if id_str else codigo_str,
                    'nombre': nombre_str if nombre_str else codigo_str if codigo_str else id_str,
                    'descripcion': nombre_str if nombre_str else codigo_str if codigo_str else '',
                    'simbolo': id_str.replace('-', '') if id_str else codigo_str[:3].upper() if codigo_str else '',
                    'activo': True  # Por defecto activo
                }
                
                units_data.append(unit)
        
        return render_template(
            'dashboard/units_of_measure.html',
            units_data=units_data,
            error_message=None
        )
        
    except Exception as e:
        # En caso de error, mostrar mensaje y datos vacíos
        import traceback
        traceback.print_exc()
        return render_template(
            'dashboard/units_of_measure.html',
            units_data=[],
            error_message=f"Error al cargar unidades de medida: {str(e)}"
        )