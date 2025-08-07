#!/usr/bin/env python3
"""
Test para verificar la funcionalidad de movimientos entre ubicaciones
"""

import flet as ft
import asyncio
from app.ui_movimientos import vista_movimientos

def main(page: ft.Page):
    page.title = "Test - Movimientos entre Ubicaciones"
    page.window.width = 1200
    page.window.height = 800
    page.scroll = ft.ScrollMode.AUTO
    
    # Configurar página
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Crear contenedor principal
    contenido = ft.Container()
    page.add(contenido)
    
    async def mostrar_movimientos():
        await vista_movimientos("Movimientos", contenido, page)
    
    # Ejecutar la vista de movimientos
    page.run_task(mostrar_movimientos)

if __name__ == "__main__":
    print("🧪 Iniciando test de movimientos entre ubicaciones...")
    print("📌 Funcionalidad agregada:")
    print("   ✅ Botón 'Movimiento de Ubicaciones' en vista de movimientos")
    print("   ✅ Diálogo específico para trasladar productos entre ubicaciones")
    print("   ✅ Actualización automática de ubicaciones origen y destino")
    print("   ✅ Registro de movimientos en historial")
    print("   ✅ Invalidación de cache para refrescar tablas")
    print("")
    print("🎯 Para probar:")
    print("   1. Ve a la vista de 'Movimientos'")
    print("   2. Haz clic en 'Movimiento de Ubicaciones'")
    print("   3. Selecciona una ubicación origen con cantidad > 0")
    print("   4. Especifica nueva ubicación de destino")
    print("   5. Define cantidad y motivo")
    print("   6. Verifica que se actualicen las tablas automáticamente")
    print("")
    
    ft.app(target=main)
