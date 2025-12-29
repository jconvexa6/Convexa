"""
Script de utilidad para generar hash de contraseñas
Ejecutar: python generate_password_hash.py
"""
from werkzeug.security import generate_password_hash

if __name__ == '__main__':
    print("=" * 50)
    print("Generador de Hash de Contraseñas")
    print("=" * 50)
    print()
    
    password = input("Ingresa la contraseña a hashear: ")
    
    if password:
        hashed = generate_password_hash(password)
        print()
        print("Hash generado:")
        print(hashed)
        print()
        print("Copia este hash y pégalo en config.py en la sección USERS")
        print("Reemplaza el valor de 'password' con este hash.")
    else:
        print("No se ingresó ninguna contraseña.")

