#!/usr/bin/env python3
"""
Punto de entrada principal para TotalStock
"""

import sys
import os

# Agregar el directorio raíz al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar y ejecutar la aplicación
if __name__ == "__main__":
    import flet as ft
    from app.ui.login import login_view
    from app.ui.principal import principal_view
    from app.utils.temas import GestorTemas

    def obtener_ruta_recurso(ruta_relativa):
        """Obtiene la ruta correcta para recursos, tanto en desarrollo como en ejecutable"""
        try:
            # PyInstaller crea una carpeta temporal _MEIPASS cuando ejecuta
            ruta_base = sys._MEIPASS
        except AttributeError:
            # En desarrollo, usar la ruta actual
            ruta_base = os.path.dirname(os.path.abspath(__file__))
        
        return os.path.join(ruta_base, ruta_relativa)

    async def main(page: ft.Page):
        tema = GestorTemas.obtener_tema()
        
        # Configuración de la ventana
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = tema.BG_COLOR
        page.window.maximized = True
        page.window.resizable = True
        page.window.min_width = 1200  # Ancho mínimo más amplio
        page.window.min_height = 800  # Alto mínimo más amplio
        page.title = "TotalStock: Sistema de Inventario"
        
        # Configurar icono de la ventana
        try:
            ruta_icono = obtener_ruta_recurso("assets/logo.ico")
            if os.path.exists(ruta_icono):
                page.window.icon = ruta_icono
                print(f"✅ Icono de ventana configurado: {ruta_icono}")
            else:
                print(f"⚠️  No se encontró el icono en: {ruta_icono}")
        except Exception as e:
            print(f"⚠️  Error al configurar icono de ventana: {e}")

        # Función a ejecutar al iniciar sesión correctamente
        async def cargar_pantalla_principal():
            page.controls.clear()
            await principal_view(page)
            page.update()

        # Limpiar controles y mostrar pantalla de login
        page.controls.clear()
        login_view(page, cargar_pantalla_principal)  # Quitar await porque login_view no es async
        page.update()

    # Ejecutar la aplicación
    print("🚀 Iniciando TotalStock...")
    print("📊 Sistema de Gestión de Inventario")
    print("=" * 50)
    
    ft.app(target=main, port=0)
