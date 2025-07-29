import flet as ft
from app.utils.temas import GestorTemas

def vista_inicio(nombre_seccion,contenido, fecha_actual):
    tema = GestorTemas.obtener_tema()
    
    contenido.content = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24, color=tema.TEXT_COLOR),
                    ft.Text(f"Fecha: {fecha_actual}", size=16, color=tema.TEXT_SECONDARY),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=True,
            ),
            ft.Container(height=30),  # Espacio vertical
            ft.Row(
                controls=[
                    ft.Card(
                        content=ft.Column(
                            controls=[
                                ft.Container(height=10),  # Espacio vertical
                                ft.Text("Panel de pendientes", size=20, color=tema.TEXT_COLOR),
                                ft.ListView(
                                    controls=[
                                        ft.ListTile(
                                            leading=ft.Icon(ft.Icons.FIBER_MANUAL_RECORD, size=14, color=tema.PRIMARY_COLOR),
                                            title=ft.Text("Faltan registrar 3 productos nuevos", color=tema.TEXT_COLOR)
                                        ),
                                        ft.ListTile(
                                            leading=ft.Icon(ft.Icons.FIBER_MANUAL_RECORD, size=14, color=tema.PRIMARY_COLOR),
                                            title=ft.Text("Verificar stock de Bodega A", color=tema.TEXT_COLOR)
                                        ),
                                        ft.ListTile(
                                            leading=ft.Icon(ft.Icons.FIBER_MANUAL_RECORD, size=14, color=tema.PRIMARY_COLOR),
                                            title=ft.Text("Actualizar precios de proveedor X", color=tema.TEXT_COLOR)
                                        ),
                                        ft.ListTile(
                                            leading=ft.Icon(ft.Icons.FIBER_MANUAL_RECORD, size=14, color=tema.PRIMARY_COLOR),
                                            title=ft.Text("Revisar productos próximos a caducar", color=tema.TEXT_COLOR)
                                        ),
                                    ],
                                    spacing=2,
                                    padding=0,
                                    expand=False,
                                )
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True
                        ),
                        expand=True,
                        color=tema.CARD_COLOR,
                    ),
                    ft.Container(width=40),  # Más espacio entre tarjetas
                    ft.Card(
                        content=ft.Column(
                            controls=[
                                ft.Container(height=10),
                                ft.Text("Historial", size=20, color=tema.TEXT_COLOR)
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True
                        ),
                        expand=True,
                        color=tema.CARD_COLOR,
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=True
            )
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        expand=True,
        spacing=0
    )