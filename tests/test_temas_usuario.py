#!/usr/bin/env python3
"""
Script de prueba para crear usuarios con diferentes temas
para probar el sistema de configuración por usuario.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.crud_usuarios.create_usuarios import crear_usuario_firebase
from app.utils.configuracion import GestorConfiguracionUsuario

def crear_usuarios_con_temas():
    """Crea usuarios de prueba con diferentes configuraciones de tema"""
    print("Creando usuarios de prueba con diferentes temas...")
    
    usuarios_prueba = [
        {
            "nombre": "UsuarioOscuro",
            "contrasena": "123456",
            "es_admin": False,
            "tema": "oscuro"
        },
        {
            "nombre": "UsuarioAzul", 
            "contrasena": "123456",
            "es_admin": False,
            "tema": "azul"
        },
        {
            "nombre": "AdminOscuro",
            "contrasena": "admin123",
            "es_admin": True,
            "tema": "oscuro"
        },
        {
            "nombre": "AdminAzul",
            "contrasena": "admin123", 
            "es_admin": True,
            "tema": "azul"
        }
    ]
    
    for usuario in usuarios_prueba:
        try:
            # Crear usuario en Firebase
            resultado = crear_usuario_firebase(
                nombre=usuario["nombre"],
                contrasena=usuario["contrasena"],
                es_admin=usuario["es_admin"]
            )
            
            if resultado:
                print(f"[OK] Usuario '{usuario['nombre']}' creado exitosamente")
                
                # Configurar tema específico para este usuario
                # Nota: En una implementación real, necesitaríamos el firebase_id del usuario creado
                # Por ahora, usaremos el nombre como ID temporal
                usuario_id = usuario["nombre"].lower()  # Esto es solo para pruebas
                
                GestorConfiguracionUsuario.cambiar_tema_usuario(usuario_id, usuario["tema"])
                print(f"   - Tema configurado: {usuario['tema']}")
                print(f"   - Administrador: {'Sí' if usuario['es_admin'] else 'No'}")
                
            else:
                print(f"[ERROR] Error al crear el usuario '{usuario['nombre']}'")
                
        except Exception as e:
            print(f"[ERROR] Error con usuario '{usuario['nombre']}': {e}")
    
    print("\n" + "="*50)
    print("INSTRUCCIONES DE PRUEBA:")
    print("="*50)
    print("1. Inicia sesión con cualquiera de los usuarios creados:")
    print("   - UsuarioOscuro / 123456 (Usuario normal, tema oscuro)")
    print("   - UsuarioAzul / 123456 (Usuario normal, tema azul)")
    print("   - AdminOscuro / admin123 (Administrador, tema oscuro)")
    print("   - AdminAzul / admin123 (Administrador, tema azul)")
    print("\n2. Verifica que cada usuario tenga su tema correspondiente")
    print("3. Cambia el tema en Configuración y verifica que se guarde por usuario")
    print("4. Cierra sesión y prueba con otro usuario para verificar que")
    print("   cada uno mantiene su tema individual")

if __name__ == "__main__":
    crear_usuarios_con_temas()
