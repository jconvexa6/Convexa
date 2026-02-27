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
            
            # NO generar IDs automáticamente - usar solo los IDs que existen en la hoja
            # Convertir a lista de diccionarios
            data = df.to_dict('records')
            
            # Filtrar solo productos que tengan un ID válido (en cualquier formato: id, ID, codigo, etc.)
            filtered_data = []
            for item in data:
                # Buscar ID en diferentes formatos
                has_id = False
                for key in ['id', 'ID', 'Id', 'codigo', 'Código', 'CODIGO', 'Codigo']:
                    if key in item and item[key] is not None and str(item[key]).strip() != '':
                        has_id = True
                        break
                
                if has_id:
                    filtered_data.append(item)
            
            return filtered_data
        
        except Exception as e:
            print(f"Error en get_inventory_data: {e}")
            return []
    
    @staticmethod
    def get_next_product_id(sheet_url: str = None):
        """
        Obtener el siguiente ID consecutivo para un nuevo producto.
        Lee el inventario, toma el máximo valor numérico de la columna ID y retorna max + 1.
        Si no hay productos o no hay IDs numéricos, retorna 1.
        
        Returns:
            int: Siguiente ID a asignar
        """
        try:
            data = SheetsService.get_inventory_data(sheet_url)
            if not data:
                return 1
            ids = []
            id_keys = ['id', 'ID', 'Id', 'Id ', 'ID ']
            for item in data:
                for key in id_keys:
                    if key in item and item[key] is not None:
                        raw = str(item[key]).strip()
                        if not raw:
                            continue
                        try:
                            ids.append(int(float(raw)))
                        except (ValueError, TypeError):
                            pass
                        break
            return max(ids, default=0) + 1
        except Exception as e:
            print(f"Error en get_next_product_id: {e}")
            return 1
    
    @staticmethod
    def get_next_codigo_consecutivo(prefix: str, sheet_url: str = None) -> int:
        """
        Obtener el siguiente número consecutivo para un código con la abreviatura dada.
        Busca en el inventario todos los valores de Codigo que empiecen con "PREFIX-"
        (ej. RMEC-1, RMEC-2), extrae el número y retorna max + 1. Si no hay ninguno, retorna 1.
        
        Args:
            prefix: Abreviatura del código (ej. RMEC, EFFI)
            sheet_url: URL del Google Sheet (opcional)
        
        Returns:
            int: Siguiente consecutivo a usar (ej. para RMEC-3 devuelve 3)
        """
        import re
        try:
            data = SheetsService.get_inventory_data(sheet_url)
            prefix_clean = str(prefix).strip().upper()
            if not prefix_clean:
                return 1
            numbers = []
            code_keys = ['Codigo', 'codigo', 'Código', 'CODIGO', 'Codigo ']
            for item in data:
                for key in code_keys:
                    if key not in item or item[key] is None:
                        continue
                    raw = str(item[key]).strip()
                    if not raw:
                        continue
                    # Aceptar "RMEC-1" o "RMEC1"
                    if raw.upper().startswith(prefix_clean):
                        rest = raw[len(prefix_clean):].lstrip('-')
                        match = re.match(r'^(\d+)', rest)
                        if match:
                            numbers.append(int(match.group(1)))
                    break
            return max(numbers, default=0) + 1
        except Exception as e:
            print(f"Error en get_next_codigo_consecutivo: {e}")
            return 1
    
    @staticmethod
    def get_product_by_id(product_id: str, sheet_url: str = None) -> Optional[Dict]:
        """
        Obtener un producto específico por ID o Referencia
        
        Busca primero por ID (en campos como 'ID', 'id', 'codigo', etc.) y luego por Referencia.
        Esto permite usar tanto el ID como la Referencia como identificador en las URLs.
        
        Args:
            product_id: ID o Referencia del producto
            sheet_url: URL del Google Sheet (opcional)
        
        Returns:
            Diccionario con los datos del producto o None si no se encuentra
        """
        try:
            data = SheetsService.get_inventory_data(sheet_url)
            
            # Decodificar el product_id si viene codificado en la URL
            import urllib.parse
            product_id_str = urllib.parse.unquote(str(product_id).strip())
            
            for product in data:
                # Primero buscar por ID en diferentes formatos de columna
                for id_key in ['id', 'ID', 'Id', 'codigo', 'Código', 'CODIGO', 'Codigo']:
                    if id_key in product:
                        product_id_value = str(product[id_key]).strip() if product[id_key] is not None else ''
                        if product_id_value == product_id_str:
                            return product
                
                # Si no se encontró por ID, buscar por Referencia
                for ref_key in ['Referencia', 'referencia', 'REFERENCIA', 'Ref', 'ref']:
                    if ref_key in product:
                        product_ref_value = str(product[ref_key]).strip() if product[ref_key] is not None else ''
                        if product_ref_value == product_id_str:
                            return product
            
            return None
        
        except Exception as e:
            print(f"Error en get_product_by_id: {e}")
            return None
    
    @staticmethod
    def get_users_data(sheet_url: str = None, gid: str = None) -> List[Dict]:
        """
        Obtener datos de usuarios desde Google Sheets
        
        Args:
            sheet_url: URL del Google Sheet (opcional, usa USERS_SHEET_URL del config)
            gid: ID de la pestaña específica (opcional, usa USERS_SHEET_GID del config)
        
        Returns:
            Lista de diccionarios con los datos de usuarios
        """
        try:
            if sheet_url is None:
                sheet_url = Config.USERS_SHEET_URL
            
            if gid is None:
                gid = Config.USERS_SHEET_GID
            
            df = SheetsService.read_google_sheet(sheet_url, gid)
            
            # Limpiar nombres de columnas (eliminar espacios y convertir a minúsculas para comparación)
            df.columns = df.columns.str.strip()
            
            # Normalizar nombres de columnas (buscar variaciones)
            username_col = None
            password_col = None
            
            # Buscar columna de usuario (case insensitive)
            for col in df.columns:
                col_lower = col.lower()
                if Config.USERS_COLUMN_USERNAME.lower() in col_lower or 'usuario' in col_lower or 'username' in col_lower or 'user' in col_lower:
                    username_col = col
                if Config.USERS_COLUMN_PASSWORD.lower() in col_lower or 'contraseña' in col_lower or 'password' in col_lower or 'pass' in col_lower:
                    password_col = col
            
            if username_col is None or password_col is None:
                raise ValueError(
                    f"No se encontraron las columnas necesarias. "
                    f"Esperadas: '{Config.USERS_COLUMN_USERNAME}' y '{Config.USERS_COLUMN_PASSWORD}'. "
                    f"Encontradas: {list(df.columns)}"
                )
            
            # Seleccionar solo las columnas necesarias y renombrarlas
            df_users = df[[username_col, password_col]].copy()
            df_users.columns = ['username', 'password']
            
            # Eliminar filas vacías
            df_users = df_users.dropna(subset=['username', 'password'])
            
            # Convertir a lista de diccionarios
            users_data = df_users.to_dict('records')
            
            return users_data
        
        except Exception as e:
            print(f"Error en get_users_data: {e}")
            return []

