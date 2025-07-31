#!/usr/bin/env python3
"""
Script de prueba para crear un usuario normal (no administrador) 
para probar el control de acceso por roles.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crud_usuarios.create_usuarios import crear_usuario_firebase

def crear_usuario_prueba():
    """Crea un usuario normal para probar el control de acceso"""
    print("Creando usuario normal para pruebas...")
    
    try:
        # Crear usuario normal (no administrador)
        resultado = crear_usuario_firebase(
            nombre="UsuarioNormal",
            contrasena="123456",
            es_admin=False
        )
        
        if resultado:
            print("✅ Usuario normal 'UsuarioNormal' creado exitosamente")
            print("   - Nombre: UsuarioNormal")
            print("   - Contraseña: 123456")
            print("   - Administrador: No")
            print("\nAhora puedes probar el control de acceso:")
            print("1. Cierra la aplicación actual")
            print("2. Inicia sesión con 'UsuarioNormal' y contraseña '123456'")
            print("3. Intenta acceder al módulo de Usuarios")
            print("4. Deberías ver el módulo deshabilitado con un candado")
            print("5. Si haces clic, aparecerá el mensaje de acceso denegado")
        else:
            print("❌ Error al crear el usuario")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    crear_usuario_prueba()
