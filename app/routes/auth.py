"""
Rutas de autenticación
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.services.auth_service import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Vista de login
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')  # No hacer strip de password (puede tener espacios intencionales)
        
        if not username or not password:
            flash('Por favor, ingresa usuario y contraseña.', 'error')
            return render_template('auth/login.html')
        
        # Debug: mostrar qué se está intentando (solo en desarrollo)
        import os
        if os.environ.get('FLASK_ENV') != 'production':
            print(f"Intento de login - Usuario: '{username}', Password recibida: '{password}'")
        
        user = User.authenticate(username, password)
        
        if user:
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Cerrar sesión
    """
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))

