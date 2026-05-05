"""
Inicialización de la aplicación Flask
"""
from flask import Flask
from flask_login import LoginManager
from config import config
# Importar modelos (para Flask-Login)
from app.services.auth_service import User

from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.product import product_bp
from app.routes.maintenance import maintenance_bp

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

    # Salud sin auth: Render y otros proxies suelen comprobar GET/HEAD en "/".
    # "/" aquí exige login (302), así que usamos "/health" en el panel de Render.
    @app.route('/health')
    def health_check():
        return 'ok', 200

    # Inicializar extensiones
    login_manager.init_app(app)
    
    
    
    @login_manager.user_loader
    def load_user(user_id):
        """Cargar usuario para Flask-Login"""
        return User.get(user_id)
    
    # Registrar blueprints
   
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(product_bp, url_prefix='/product')
    app.register_blueprint(maintenance_bp)
    
    return app

