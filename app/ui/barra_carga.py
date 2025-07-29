import flet as ft
from app.utils.temas import GestorTemas


def vista_carga():
    tema = GestorTemas.obtener_tema()
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.ProgressRing(color=tema.PRIMARY_COLOR),
                ft.Text("Cargando...", size=20, color=tema.TEXT_COLOR)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        expand=True,
        alignment=ft.alignment.center,
        bgcolor=tema.BG_COLOR,
    )
    