"""
Servicio de autenticación
"""
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from config import Config


class User(UserMixin):
    """
    Clase de usuario para Flask-Login
    """
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
    
    @staticmethod
    def get(user_id):
        """
        Obtener usuario por ID
        """
        if user_id in Config.USERS:
            return User(user_id, user_id)
        return None
    
    @staticmethod
    def authenticate(username, password):
        """
        Autenticar usuario
        """
        if username in Config.USERS:
            user_data = Config.USERS[username]
            stored_password = user_data.get('password', '')
            
            # Si la contraseña no está hasheada (desarrollo), hashearla
            if not stored_password.startswith('pbkdf2:'):
                # Para desarrollo: comparar directamente
                # En producción, siempre debe estar hasheada
                if stored_password == password:
                    # Hashear la contraseña para guardarla
                    Config.USERS[username]['password'] = generate_password_hash(password)
                    return User(username, username)
            else:
                # Verificar contraseña hasheada
                if check_password_hash(stored_password, password):
                    return User(username, username)
        
        return None

