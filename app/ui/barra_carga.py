import flet as ft
from app.utils.temas import GestorTemas


def vista_carga(mensaje="Cargando...", size=20, show_background=True):
    """
    Vista de carga flexible con opciones personalizables
    
    Args:
        mensaje: Texto a mostrar (default: "Cargando...")
        size: Tamaño del texto (default: 20)
        show_background: Si mostrar fondo completo (default: True)
    """
    tema = GestorTemas.obtener_tema()
    
    contenido = ft.Column(
        controls=[
            ft.ProgressRing(color=tema.PRIMARY_COLOR, width=40, height=40),
            ft.Text(mensaje, size=size, color=tema.TEXT_COLOR, text_align=ft.TextAlign.CENTER)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )
    
    if show_background:
        return ft.Container(
            content=contenido,
            expand=True,
            alignment=ft.alignment.center,
            bgcolor=tema.BG_COLOR,
        )
    else:
        return contenido


def progress_ring_pequeno(mensaje="Verificando...", size=14):
    """Progress ring pequeño para usar en formularios con animación suave"""
    tema = GestorTemas.obtener_tema()
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.ProgressRing(
                    color=tema.PRIMARY_COLOR, 
                    width=20, 
                    height=20,
                    stroke_width=3
                ),
                ft.Text(
                    mensaje, 
                    size=size, 
                    color=tema.TEXT_COLOR,
                    weight=ft.FontWeight.W_500,
                    text_align=ft.TextAlign.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6
        ),
        padding=ft.padding.symmetric(vertical=8, horizontal=12),
        border_radius=8,
        bgcolor=ft.Colors.with_opacity(0.05, tema.PRIMARY_COLOR),  # Fondo sutil
        border=ft.border.all(1, ft.Colors.with_opacity(0.1, tema.PRIMARY_COLOR))
    )
    