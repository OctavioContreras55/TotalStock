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

    async def main(page: ft.Page):
        tema = GestorTemas.obtener_tema()
        
        # Configuración del tema
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = tema.BG_COLOR
        page.window.maximized = True
        page.window.resizable = True
        page.title = "TotalStock: Sistema de Inventario"

        # Función a ejecutar al iniciar sesión correctamente
        async def cargar_pantalla_principal():
            page.controls.clear()
            await principal_view(page)
            page.update()

        # Limpiar controles y mostrar pantalla de login
        page.controls.clear()
        await login_view(page, cargar_pantalla_principal)
        page.update()

    # Ejecutar la aplicación
    print("🚀 Iniciando TotalStock...")
    print("📊 Sistema de Gestión de Inventario")
    print("=" * 50)
    
    ft.app(target=main, port=0)
