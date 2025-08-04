#!/usr/bin/env python3
"""
Test visual del progress ring en login
"""

import flet as ft
from app.ui.barra_carga import progress_ring_pequeno
from app.utils.temas import GestorTemas
import asyncio

def main(page: ft.Page):
    page.title = "Test Progress Ring"
    page.window.width = 400
    page.window.height = 300
    
    # Configurar tema
    GestorTemas.cambiar_tema("azul")
    tema = GestorTemas.obtener_tema()
    page.bgcolor = tema.BG_COLOR
    
    # Contenedor para el progress ring
    contenedor_test = ft.Container(
        content=None,
        height=60,
        alignment=ft.alignment.center,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.GREY)
    )
    
    async def mostrar_progress_ring(e):
        print("🔄 Mostrando progress ring...")
        contenedor_test.content = progress_ring_pequeno("Verificando credenciales...", 12)
        btn_mostrar.disabled = True
        page.update()
        
        # Simular delay de validación
        await asyncio.sleep(2)
        
        print("✅ Ocultando progress ring...")
        contenedor_test.content = None
        btn_mostrar.disabled = False
        page.update()
    
    btn_mostrar = ft.ElevatedButton(
        "Probar Progress Ring",
        on_click=mostrar_progress_ring
    )
    
    page.add(
        ft.Column([
            ft.Text("Test de Progress Ring", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            contenedor_test,
            btn_mostrar,
            ft.Text("Verifica que aparezca y desaparezca el progress ring", size=12)
        ], 
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20)
    )

if __name__ == "__main__":
    ft.app(target=main)
