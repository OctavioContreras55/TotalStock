import flet as ft
from app.tablas.ui_tabla_usuarios import mostrar_tabla_usuarios

def vista_usuarios(nombre_seccion, contenido):
    contenido.content = ft.Column(
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24),
                                ft.Text("Gestión de los usuarios del sistema", size=16,)
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
    
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.START
                ),
                width=600,
                bgcolor=ft.Colors.GREY_900,
                padding=20,
                alignment=ft.alignment.center,
                border_radius=10,
            ),
            ft.Container(
                height=3,
                bgcolor=ft.Colors.WHITE70,
                margin=ft.margin.only(bottom=20, top=5),
            ),
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.ADD),
                                ft.Text("Agregar Usuario")
                            ])
                        ),
                        width=200,
                        padding=ft.padding.symmetric(horizontal=5, vertical=20)
                    ),
                    ft.Container(
                        content=ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.SEARCH),
                                ft.Text("Buscar Usuario")
                            ])
                        ),
                        width=200,
                        padding=ft.padding.symmetric(horizontal=5, vertical=20)
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=20
            ),
            ft.Row(
                controls=[
                    ft.Container(
                        content=mostrar_tabla_usuarios([
                            {"id": 1, "nombre": "Usuario 1", "rol": "Administrador"},
                            {"id": 2, "nombre": "Usuario 2", "rol": "Editor"},
                            {"id": 3, "nombre": "Usuario 3", "rol": "Viewer"},
                        ]),
                        padding=ft.padding.symmetric(horizontal=5, vertical=20)
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.START
            )            
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
    )