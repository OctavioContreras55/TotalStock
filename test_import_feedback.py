#!/usr/bin/env python3
"""
Test rápido del feedback de importación de ubicaciones
"""
import flet as ft
from app.utils.temas import GestorTemas
import asyncio

def main(page: ft.Page):
    page.title = "Test Importación Ubicaciones"
    page.window.width = 400
    page.window.height = 300
    
    tema = GestorTemas.obtener_tema()
    
    async def test_feedback():
        # Simular el diálogo de progreso que aparece durante importación
        mensaje_cargando = ft.AlertDialog(
            title=ft.Text("Importando Ubicaciones", color=tema.TEXT_COLOR),
            bgcolor=tema.CARD_COLOR,
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.ProgressRing(width=20, height=20, stroke_width=3, color=tema.PRIMARY_COLOR),
                        ft.Text("Procesando ubicaciones...", color=tema.TEXT_COLOR, size=14)
                    ], spacing=15, alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=10),
                    ft.Text("Total a procesar: 262 ubicaciones", 
                           color=tema.TEXT_SECONDARY, size=12, text_align=ft.TextAlign.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(20, 15, 20, 15),
                width=300
            ),
            modal=True,
        )
        
        page.open(mensaje_cargando)
        page.update()
        
        # Simular tiempo de procesamiento
        await asyncio.sleep(3)
        
        # Cerrar y mostrar resultado
        page.close(mensaje_cargando)
        page.open(ft.SnackBar(
            content=ft.Text("✅ 262 ubicaciones importadas | 30 cantidades sincronizadas", color=tema.TEXT_COLOR),
            bgcolor=tema.SUCCESS_COLOR,
            duration=5000
        ))
        page.update()
    
    btn_test = ft.ElevatedButton(
        "Probar Feedback de Importación",
        style=ft.ButtonStyle(
            bgcolor=tema.BUTTON_BG,
            color=tema.BUTTON_TEXT,
            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
        ),
        on_click=lambda e: page.run_task(test_feedback)
    )
    
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("Test de Feedback de Importación", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                btn_test,
                ft.Container(height=20),
                ft.Text("Este test simula el feedback que el usuario ve durante la importación", 
                       size=12, text_align=ft.TextAlign.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
