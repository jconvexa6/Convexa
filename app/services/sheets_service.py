"""
Servicio para leer datos de Google Sheets
"""
import pandas as pd
import requests
from typing import List, Dict, Optional
from config import Config


class SheetsService:
    """
    Servicio para obtener datos de Google Sheets
    """
    
    @staticmethod
    def get_sheet_id_from_url(url: str) -> Optional[str]:
        """
        Extraer el ID de la hoja de cálculo desde la URL
        """
        try:
            if '/d/' in url:
                sheet_id = url.split('/d/')[1].split('/')[0]
                return sheet_id
            return None
        except Exception:
            return None
    
    @staticmethod
    def get_sheet_as_csv_url(sheet_id: str, gid: str = '0') -> str:
        """
        Generar URL para descargar la hoja como CSV
        """
        return f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
    
    @staticmethod
    def read_google_sheet(sheet_url: str = None, gid: str = '0') -> pd.DataFrame:
        """
        Leer Google Sheet y retornar como DataFrame de Pandas
        
        Args:
            sheet_url: URL del Google Sheet (opcional, usa la del config por defecto)
            gid: ID de la hoja específica (default: '0' para la primera hoja)
        
        Returns:
            DataFrame de Pandas con los datos
        """
        if sheet_url is None:
            sheet_url = Config.INVENTORY_SHEET_URL
        
        sheet_id = SheetsService.get_sheet_id_from_url(sheet_url)
        
        if not sheet_id:
            raise ValueError(f"No se pudo extraer el ID de la hoja desde: {sheet_url}")
        
        csv_url = SheetsService.get_sheet_as_csv_url(sheet_id, gid)
        
        try:
            # Descargar el CSV
            response = requests.get(csv_url, timeout=10)
            response.raise_for_status()
            
            # Leer CSV en DataFrame
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            
            # Limpiar nombres de columnas (eliminar espacios)
            df.columns = df.columns.str.strip()
            
            return df
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error al descargar el Google Sheet: {e}")
        except Exception as e:
            raise Exception(f"Error al procesar el Google Sheet: {e}")
    
    @staticmethod
    def get_inventory_data(sheet_url: str = None) -> List[Dict]:
        """
        Obtener datos de inventario como lista de diccionarios
        
        Args:
            sheet_url: URL del Google Sheet (opcional)
        
        Returns:
            Lista de diccionarios con los datos del inventario
        """
        try:
            df = SheetsService.read_google_sheet(sheet_url)
            
            # Convertir DataFrame a lista de diccionarios
            # Reemplazar NaN con None para JSON
            df = df.where(pd.notna(df), None)
            
            # Agregar un ID único basado en el índice si no existe una columna ID
            if 'id' not in df.columns and 'ID' not in df.columns:
                df.insert(0, 'id', range(1, len(df) + 1))
            
            # Convertir a lista de diccionarios
            data = df.to_dict('records')
            
            return data
        
        except Exception as e:
            print(f"Error en get_inventory_data: {e}")
            return []
    
    @staticmethod
    def get_product_by_id(product_id: str, sheet_url: str = None) -> Optional[Dict]:
        """
        Obtener un producto específico por ID
        
        Args:
            product_id: ID del producto
            sheet_url: URL del Google Sheet (opcional)
        
        Returns:
            Diccionario con los datos del producto o None si no se encuentra
        """
        try:
            data = SheetsService.get_inventory_data(sheet_url)
            
            # Buscar producto por ID
            for product in data:
                # El ID puede estar como string o int
                product_id_str = str(product.get('id', ''))
                if product_id_str == str(product_id):
                    return product
            
            return None
        
        except Exception as e:
            print(f"Error en get_product_by_id: {e}")
            return None

