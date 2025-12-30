"""
Servicio para escribir datos en Google Sheets usando la API
"""
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import Config


# Scopes necesarios
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


def get_credentials():
    """
    Obtener credenciales de Google API exclusivamente desde variable de entorno.
    
    La variable de entorno GOOGLE_TOKEN_JSON debe contener el token completo en formato JSON.
    Si la variable no está configurada o es inválida, la función falla explícitamente.
    
    Returns:
        Credentials: Objeto de credenciales de Google API
        
    Raises:
        ValueError: Si la variable de entorno no está configurada o el token es inválido
    """
    # Leer token exclusivamente desde variable de entorno
    token_json_env = os.environ.get('GOOGLE_TOKEN_JSON')
    
    if not token_json_env:
        raise ValueError(
            "GOOGLE_TOKEN_JSON no está configurada. "
            "Configura esta variable de entorno con el contenido completo del token JSON."
        )
    
    try:
        import json
        token_data = json.loads(token_json_env)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"GOOGLE_TOKEN_JSON contiene JSON inválido: {str(e)}. "
            "Verifica que el valor sea un JSON válido."
        )
    except Exception as e:
        raise ValueError(
            f"Error al procesar GOOGLE_TOKEN_JSON: {str(e)}. "
            "Verifica que la variable de entorno esté correctamente configurada."
        )
    
    # Validar que el token tenga los campos necesarios
    required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret']
    missing_fields = [field for field in required_fields if field not in token_data]
    
    if missing_fields:
        raise ValueError(
            f"GOOGLE_TOKEN_JSON está incompleto. Faltan los campos: {', '.join(missing_fields)}"
        )
    
    # Crear credenciales desde el token
    try:
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    except Exception as e:
        raise ValueError(
            f"Error al crear credenciales desde GOOGLE_TOKEN_JSON: {str(e)}. "
            "Verifica que el token sea válido y tenga el formato correcto."
        )
    
    # Verificar si el token tiene los scopes necesarios
    if creds.scopes:
        token_scopes = set(creds.scopes)
        required_scopes = set(SCOPES)
        missing_scopes = required_scopes - token_scopes
        
        if missing_scopes:
            raise ValueError(
                f"El token no tiene los scopes necesarios. Faltan: {', '.join(missing_scopes)}"
            )
    
    # Si el token está expirado, intentar refrescarlo
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                raise ValueError(
                    f"Error al refrescar el token: {str(e)}. "
                    "El refresh_token puede ser inválido o haber expirado."
                )
        else:
            raise ValueError(
                "El token ha expirado y no se puede refrescar. "
                "Genera un nuevo token y actualiza GOOGLE_TOKEN_JSON."
            )
    
    return creds


def get_sheet_id_from_url(url: str) -> str:
    """Extraer ID del sheet desde la URL"""
    if '/d/' in url:
        return url.split('/d/')[1].split('/')[0]
    return url


class SheetsWriter:
    """
    Servicio para escribir en Google Sheets
    """
    
    @staticmethod
    def append_row_to_history(data: dict, username: str = 'Sistema') -> bool:
        """
        Agregar una fila al histórico de movimientos
        
        Args:
            data: Diccionario con los datos del movimiento
            username: Usuario que realiza el movimiento
        
        Returns:
            True si se agregó correctamente, False en caso contrario
        """
        try:
            creds = get_credentials()
            service = build('sheets', 'v4', credentials=creds)
            
            sheet_id = get_sheet_id_from_url(Config.HISTORY_SHEET_URL)
            
            # Preparar los valores de la fila según las columnas del histórico
            # Columnas: Codigo, Referencia, Descripcion, Unidad-medida, cantidad, 
            # Ubicación, Stock-min, Estado, Metodo, FechaMovimiento, Usuario, UnidadesUtilizadas
            values = [
                data.get('Codigo', ''),
                data.get('Referencia', ''),
                data.get('Descripcion', ''),
                data.get('Unidad-medida', ''),
                data.get('cantidad', ''),  # Stock final después del ajuste
                data.get('Ubicación', ''),
                data.get('Stock-min', ''),
                data.get('Estado', ''),
                data.get('Metodo', ''),  # 'Ingreso' o 'Salida'
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # FechaMovimiento
                username,  # Usuario
                data.get('UnidadesUtilizadas', ''),  # Unidades utilizadas (ajuste)
            ]
            
            body = {
                'values': [values]
            }
            
            result = service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range='A:Z',  # Rango amplio
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return True
            
        except HttpError as e:
            error_message = str(e)
            
            if 'SERVICE_DISABLED' in error_message or 'has not been used' in error_message:
                raise Exception(
                    "Google Sheets API no está habilitada. "
                    "Habilítala en la consola de Google Cloud."
                )
            
            print(f"Error HTTP al escribir en histórico: {e}")
            import traceback
            traceback.print_exc()
            return False
        except Exception as e:
            print(f"Error al escribir en histórico: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def create_product_in_inventory(product_data: dict) -> str:
        """
        Crear un nuevo producto en el inventario
        
        Args:
            product_data: Diccionario con los datos del nuevo producto
        
        Returns:
            ID del producto creado o None si falló
        """
        try:
            creds = get_credentials()
            service = build('sheets', 'v4', credentials=creds)
            
            sheet_id = get_sheet_id_from_url(Config.INVENTORY_SHEET_URL)
            
            # Leer el sheet para obtener los headers
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range='A1:Z1'  # Solo la primera fila (headers)
            ).execute()
            
            rows = result.get('values', [])
            if not rows:
                print("❌ No se encontraron headers en el sheet")
                return None
            
            headers = [str(h).strip() for h in rows[0]]
            
            # Preparar valores en el orden de las columnas
            values = []
            for header in headers:
                # Buscar el valor en product_data (case insensitive)
                value = ''
                for key, val in product_data.items():
                    if str(key).strip().lower() == header.lower():
                        value = str(val) if val is not None else ''
                        break
                values.append(value)
            
            # Agregar la nueva fila
            body = {
                'values': [values]
            }
            
            result = service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range='A:Z',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            if values and len(values) > 0:
                product_id = values[0] if values[0] else None
                return product_id
            
            return None
            
        except Exception as e:
            print(f"Error al crear producto: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def update_product_in_inventory(product_id: str, updated_data: dict) -> bool:
        """
        Actualizar un producto en el inventario
        
        Args:
            product_id: ID del producto
            updated_data: Diccionario con los datos actualizados
        
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            creds = get_credentials()
            service = build('sheets', 'v4', credentials=creds)
            
            sheet_id = get_sheet_id_from_url(Config.INVENTORY_SHEET_URL)
            
            # Leer el sheet para encontrar la fila del producto
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range='A:Z'
            ).execute()
            
            rows = result.get('values', [])
            if not rows:
                return False
            
            # La primera fila son los headers
            headers = [str(h).strip() for h in rows[0]]
            
            # Buscar la fila del producto
            # Buscar en la columna 'id' o primera columna
            row_index = None
            id_col_index = None
            
            # Buscar columna de ID (prioridad: primera columna si es 'ID', luego 'id', luego 'codigo'/'código')
            id_col_index = None
            
            if len(headers) > 0 and str(headers[0]).strip() == 'ID':
                id_col_index = 0
            else:
                for idx, header in enumerate(headers):
                    header_lower = str(header).strip().lower()
                    if header_lower == 'id':
                        id_col_index = idx
                        break
                
                if id_col_index is None:
                    for idx, header in enumerate(headers):
                        if str(header).strip() == 'ID':
                            id_col_index = idx
                            break
                
                if id_col_index is None:
                    for idx, header in enumerate(headers):
                        header_lower = str(header).strip().lower()
                        if header_lower in ['codigo', 'código']:
                            id_col_index = idx
                            break
            
            if id_col_index is None:
                print(f"Error: No se encontró columna de ID en el Google Sheet")
                return False
            else:
                product_id_str = str(product_id).strip()
                
                for i, row in enumerate(rows[1:], start=2):
                    if len(row) > id_col_index:
                        row_id = str(row[id_col_index]).strip()
                        if row_id == product_id_str or row_id == str(product_id):
                            row_index = i
                            break
                
                if not row_index:
                    print(f"Error: No se encontró el producto con ID: '{product_id}'")
                    return False
            
            # Preparar valores actualizados manteniendo el orden de las columnas
            updated_values = []
            original_row = rows[row_index - 1]  # -1 porque row_index es 1-based pero rows es 0-based
            
            for idx, header in enumerate(headers):
                # Normalizar nombre del header para comparación
                header_normalized = header.lower().strip()
                
                # Buscar en updated_data (case insensitive)
                found = False
                for key, value in updated_data.items():
                    if str(key).lower().strip() == header_normalized:
                        updated_values.append(str(value))
                        found = True
                        break
                
                if not found:
                    # Mantener valor original
                    if idx < len(original_row):
                        updated_values.append(original_row[idx])
                    else:
                        updated_values.append('')
            
            # Actualizar la fila
            range_name = f'{row_index}:{row_index}'
            body = {
                'values': [updated_values]
            }
            
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return True
            
        except HttpError as e:
            error_details = e.error_details if hasattr(e, 'error_details') else []
            error_message = str(e)
            
            # Verificar si es un error de API deshabilitada
            if 'SERVICE_DISABLED' in error_message or 'has not been used' in error_message:
                print("❌ ERROR: Google Sheets API no está habilitada en tu proyecto.")
                print("📋 Para solucionarlo:")
                print("   1. Ve a: https://console.developers.google.com/apis/library/sheets.googleapis.com")
                print("   2. Selecciona tu proyecto (ID: 1012866464546)")
                print("   3. Haz clic en 'HABILITAR'")
                print("   4. Espera unos minutos y vuelve a intentar")
                raise Exception(
                    "Google Sheets API no está habilitada. "
                    "Habilítala en: https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=1012866464546"
                )
            
            print(f"Error HTTP al actualizar producto: {e}")
            import traceback
            traceback.print_exc()
            return False
        except Exception as e:
            print(f"Error al actualizar producto: {e}")
            import traceback
            traceback.print_exc()
            return False

