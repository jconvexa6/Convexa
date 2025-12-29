"""
Servicio de autenticación
"""
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from app.services.sheets_service import SheetsService


class User(UserMixin):
    """
    Clase de usuario para Flask-Login
    """
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
    
    @staticmethod
    def _get_users_from_sheet():
        """
        Obtener usuarios desde Google Sheets
        Retorna diccionario vacío si hay error (fallback silencioso)
        """
        try:
            users_data = SheetsService.get_users_data()
            # Convertir a diccionario para búsqueda rápida
            users_dict = {}
            for user in users_data:
                username = str(user.get('username', '')).strip()
                password = str(user.get('password', ''))  # NO hacer strip aquí
                if username and password:
                    # Guardar con el username original (sin normalizar)
                    users_dict[username] = {'password': password}
                    print(f"DEBUG - Usuario cargado: '{username}', Password (repr): {repr(password)}")
            print(f"✓ Usuarios cargados desde Excel: {list(users_dict.keys())}")
            return users_dict
        except Exception as e:
            print(f"⚠️ Advertencia: Error al obtener usuarios desde Excel: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    @staticmethod
    def get(user_id):
        """
        Obtener usuario por ID desde Google Sheets
        """
        users = User._get_users_from_sheet()
        if user_id in users:
            return User(user_id, user_id)
        return None
    
    @staticmethod
    def authenticate(username, password):
        """
        Autenticar usuario desde Google Sheets
        """
        try:
            users = User._get_users_from_sheet()
            
            # Normalizar username (case insensitive)
            username = str(username).strip()
            # NO hacer strip de password - puede tener espacios intencionales
            
            # Buscar usuario (case insensitive)
            user_found = None
            for user_key in users.keys():
                if str(user_key).strip().lower() == username.lower():
                    user_found = user_key
                    break
            
            if user_found:
                user_data = users[user_found]
                stored_password = str(user_data.get('password', ''))
                
                # Debug: mostrar comparación
                print(f"DEBUG Auth - Usuario encontrado: '{user_found}'")
                print(f"DEBUG Auth - Password almacenada (repr): {repr(stored_password)}")
                print(f"DEBUG Auth - Password ingresada (repr): {repr(password)}")
                print(f"DEBUG Auth - Longitud almacenada: {len(stored_password)}")
                print(f"DEBUG Auth - Longitud ingresada: {len(password)}")
                
                # Si la contraseña no está hasheada, comparar directamente
                if not stored_password.startswith('pbkdf2:'):
                    # Comparar contraseña en texto plano
                    # Intentar varias formas de comparación
                    matches = [
                        stored_password == password,  # Exacta
                        stored_password.strip() == password.strip(),  # Con strip
                        stored_password.rstrip() == password.rstrip(),  # Solo espacios finales
                    ]
                    
                    print(f"DEBUG Auth - Comparaciones: exacta={matches[0]}, strip={matches[1]}, rstrip={matches[2]}")
                    
                    if any(matches):
                        print(f"DEBUG Auth - ✓ Contraseña correcta")
                        return User(user_found, user_found)
                    else:
                        print(f"DEBUG Auth - ✗ Contraseña incorrecta")
                else:
                    # Verificar contraseña hasheada
                    if check_password_hash(stored_password, password):
                        return User(user_found, user_found)
            
            return None
        except Exception as e:
            print(f"Error en autenticación: {e}")
            import traceback
            traceback.print_exc()
            return None

