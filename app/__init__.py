"""
Inicialización de la aplicación Flask
"""
from flask import Flask
from flask_login import LoginManager
from config import config
# Importar modelos (para Flask-Login)
from app.services.auth_service import User

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'


def create_app(config_name='default'):
    """
    Factory function para crear la aplicación Flask
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    login_manager.init_app(app)
    
    
    
    @login_manager.user_loader
    def load_user(user_id):
        """Cargar usuario para Fl|ask-Login"""
        return User.get(user_id)
    
    # Registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.product import product_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(product_bp, url_prefix='/product')
    
    return app

