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
                password = str(user.get('password', '')).strip()
                if username and password:
                    users_dict[username] = {'password': password}
            return users_dict
        except Exception as e:
            print(f"⚠️ Advertencia: Error al obtener usuarios desde Excel: {e}")
            print("   El sistema intentará usar usuarios del config como fallback.")
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
            
            if username in users:
                user_data = users[username]
                stored_password = str(user_data.get('password', '')).strip()
                
                # Si la contraseña no está hasheada, comparar directamente
                if not stored_password.startswith('pbkdf2:'):
                    # Comparar contraseña en texto plano
                    if stored_password == password:
                        return User(username, username)
                else:
                    # Verificar contraseña hasheada
                    if check_password_hash(stored_password, password):
                        return User(username, username)
            
            return None
        except Exception as e:
            print(f"Error en autenticación: {e}")
            return None

