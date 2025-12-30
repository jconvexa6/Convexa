"""
Servicio para escribir datos en Google Sheets usando la API
"""
import os
import pickle
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
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
    Obtener credenciales de Google API
    """
    creds = None
    
    # Primero intentar desde variable de entorno (para producción en Render)
    token_json_env = os.environ.get('GOOGLE_TOKEN_JSON')
    if token_json_env:
        try:
            import json
            token_data = json.loads(token_json_env)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
            if creds and creds.valid:
                return creds
            elif creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                return creds
        except Exception as e:
            print(f"Error al cargar token desde variable de entorno: {e}")
    
    # Intentar desde archivo de configuración local (no en git)
    try:
        from app.config.google_credentials import get_token_data
        token_data = get_token_data()
        if token_data:
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
            if creds and creds.valid:
                return creds
            elif creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                return creds
    except ImportError:
        # El archivo no existe, continuar con búsqueda normal
        pass
    except Exception as e:
        print(f"Error al cargar token desde configuración: {e}")
    
    # Buscar token en múltiples ubicaciones
    token_paths = [
        os.path.join('app', 'static', 'Credenciales', 'token.json'),
        os.path.join('app', 'static', 'Credenciales', 'token.pickle'),
        os.path.join('app', 'templates', 'llavesAcceso', 'token.pickle'),
        'token.pickle',
        os.path.join('app', 'templates', 'llavesAcceso', 'token.json'),
    ]
    
    credentials_paths = [
        os.path.join('app', 'static', 'Credenciales', 'credentials.json'),
        os.path.join('app', 'templates', 'llavesAcceso', 'credentials.json'),
        'credentials.json',
    ]
    
    # Buscar token
    token_path = None
    for path in token_paths:
        if os.path.exists(path):
            token_path = path
            break
    
    # Buscar credentials
    credentials_path = None
    for path in credentials_paths:
        if os.path.exists(path):
            credentials_path = path
            break
    
    # Cargar token si existe
    if token_path:
        try:
            if token_path.endswith('.json'):
                import json
                with open(token_path, 'r', encoding='utf-8') as token:
                    token_data = json.load(token)
                    # Cargar credenciales desde el JSON
                    creds = Credentials.from_authorized_user_info(token_data, SCOPES)
            else:
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
        except FileNotFoundError:
            creds = None
        except Exception as e:
            print(f"Error al cargar token: {e}")
            creds = None
    
    # Verificar si el token tiene los scopes necesarios
    if creds and creds.valid:
        token_scopes = set(creds.scopes if creds.scopes else [])
        required_scopes = set(SCOPES)
        missing_scopes = required_scopes - token_scopes
        
        if missing_scopes:
            creds = None
    
    # Si no hay credenciales válidas, intentar refrescar
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                
                # Guardar token refrescado SIEMPRE
                if not token_path:
                    token_path = os.path.join('app', 'static', 'Credenciales', 'token.json')
                
                save_dir = os.path.dirname(token_path) if os.path.dirname(token_path) else '.'
                if not os.path.exists(save_dir) and save_dir != '.':
                    os.makedirs(save_dir)
                
                try:
                    if token_path.endswith('.json'):
                        import json
                        token_dict = {
                            'token': creds.token,
                            'refresh_token': creds.refresh_token,
                            'token_uri': creds.token_uri,
                            'client_id': creds.client_id,
                            'client_secret': creds.client_secret,
                            'scopes': creds.scopes,
                        }
                        with open(token_path, 'w', encoding='utf-8') as token:
                            json.dump(token_dict, token, indent=2)
                    else:
                        with open(token_path, 'wb') as token:
                            pickle.dump(creds, token)
                except Exception as e:
                    print(f"⚠️ Error al guardar token refrescado: {e}")
            except Exception as e:
                print(f"Error al refrescar token: {e}")
                import traceback
                traceback.print_exc()
                creds = None
    
    # Si no hay credenciales, necesitamos autenticación
    if not creds:
        if not credentials_path:
            raise FileNotFoundError(
                "No se encontró credentials.json. "
                "Colócalo en app/static/Credenciales/, app/templates/llavesAcceso/ o en la raíz del proyecto."
            )
        
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Guardar token SIEMPRE después de autenticación
        # Determinar dónde guardar el token
        if not token_path:
            # Si no hay token_path, usar el primero de la lista
            token_path = os.path.join('app', 'static', 'Credenciales', 'token.json')
        
            save_dir = os.path.dirname(token_path) if os.path.dirname(token_path) else '.'
            if not os.path.exists(save_dir) and save_dir != '.':
                os.makedirs(save_dir)
        
        try:
            if token_path.endswith('.json'):
                import json
                token_dict = {
                    'token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'token_uri': creds.token_uri,
                    'client_id': creds.client_id,
                    'client_secret': creds.client_secret,
                    'scopes': creds.scopes,
                }
                with open(token_path, 'w', encoding='utf-8') as token:
                    json.dump(token_dict, token, indent=2)
            else:
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
        except Exception as e:
            print(f"⚠️ Error al guardar token: {e}")
            import traceback
            traceback.print_exc()
    
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

