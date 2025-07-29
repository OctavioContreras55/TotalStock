import flet as ft
from app.utils.temas import GestorTemas

def categorias_mostrar(nombre_seccion, contenido):
    tema = GestorTemas.obtener_tema()

    contenido.content = ft.Column(
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            content=ft.Text("Categoría de cadenas", size=16, color=tema.BUTTON_TEXT),
                            on_click=lambda e: print("Categoría de cadenas seleccionada"),
                            width=200,
                            height=50,
                            icon=ft.Icon(ft.Icons.LINK, color=tema.PRIMARY_COLOR),
                            style=ft.ButtonStyle(
                                bgcolor=tema.BUTTON_BG,
                                color=tema.BUTTON_TEXT,
                                shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                            )
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
    )