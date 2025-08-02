#!/usr/bin/env python3
"""
Test de animación del progress ring en login
"""

import flet as ft
from app.ui.barra_carga import progress_ring_pequeno
from app.utils.temas import GestorTemas
import asyncio

def main(page: ft.Page):
    page.title = "Test Animación Progress Ring"
    page.window.width = 400
    page.window.height = 400
    
    # Configurar tema
    GestorTemas.cambiar_tema("azul")
    tema = GestorTemas.obtener_tema()
    page.bgcolor = tema.BG_COLOR
    
    # Contenedor animado como en el login
    contenedor_animado = ft.AnimatedSwitcher(
        content=ft.Container(height=0),  # Inicialmente invisible
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=300,
        reverse_duration=300,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN
    )
    
    async def probar_animacion(e):
        print("🎬 Iniciando animación de expansión...")
        
        # Expandir y mostrar contenido
        contenedor_animado.content = ft.Container(
            content=progress_ring_pequeno("Probando animación...", 12),
            height=60,
            width=300,
            alignment=ft.alignment.center
        )
        btn_probar.disabled = True
        page.update()
        
        # Esperar 3 segundos
        await asyncio.sleep(3)
        
        print("🎬 Iniciando animación de contracción...")
        
        # Contraer y ocultar contenido
        contenedor_animado.content = ft.Container(height=0)
        btn_probar.disabled = False
        page.update()
        
        print("✅ Animación completada")
    
    btn_probar = ft.ElevatedButton(
        "Probar Animación",
        on_click=probar_animacion,
        style=ft.ButtonStyle(
            bgcolor=tema.PRIMARY_COLOR,
            color=ft.Colors.WHITE
        )
    )
    
    page.add(
        ft.Column([
            ft.Text("Test de Animación del Progress Ring", 
                   style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                   color=tema.TEXT_COLOR),
            ft.Text("Campo de usuario", size=12, color=tema.TEXT_SECONDARY),
            ft.TextField(label="Usuario", disabled=True),
            ft.Text("Campo de contraseña", size=12, color=tema.TEXT_SECONDARY),
            ft.TextField(label="Contraseña", disabled=True),
            contenedor_animado,  # Aquí se expande/contrae
            btn_probar,
            ft.Text("Observa cómo se expande/contrae el espacio", 
                   size=10, color=tema.TEXT_SECONDARY)
        ], 
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15)
    )

if __name__ == "__main__":
    ft.app(target=main)
