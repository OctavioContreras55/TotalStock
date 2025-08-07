#!/usr/bin/env python3
"""
Test rápido para verificar que las funciones están correctamente estructuradas
"""

import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test básico de imports para verificar sintaxis"""
    print("🧪 TESTING IMPORTS Y SINTAXIS")
    print("=" * 40)
    
    try:
        from app.ui_usuarios import vista_usuarios
        print("✅ app.ui_usuarios - Import exitoso")
    except Exception as e:
        print(f"❌ app.ui_usuarios - Error: {e}")
    
    try:
        from app.tablas.ui_tabla_usuarios import mostrar_tabla_usuarios
        print("✅ app.tablas.ui_tabla_usuarios - Import exitoso")
    except Exception as e:
        print(f"❌ app.tablas.ui_tabla_usuarios - Error: {e}")
    
    try:
        from app.crud_usuarios.edit_usuario import mostrar_ventana_editar_usuario
        print("✅ app.crud_usuarios.edit_usuario - Import exitoso")
    except Exception as e:
        print(f"❌ app.crud_usuarios.edit_usuario - Error: {e}")
    
    try:
        from app.crud_usuarios.create_usuarios import crear_usuario_firebase
        print("✅ app.crud_usuarios.create_usuarios - Import exitoso")
    except Exception as e:
        print(f"❌ app.crud_usuarios.create_usuarios - Error: {e}")
    
    print("\n🎉 TESTS DE SINTAXIS COMPLETADOS")

if __name__ == "__main__":
    test_imports()
