import flet as ft
from app.tablas.ui_tabla_productos import mostrar_tabla_productos

def vista_inventario(nombre_seccion, contenido, productos_ejemplo):
    contenido.content = ft.Column(
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24),
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
            ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.ElevatedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.SEARCH),
                                        ft.Text("Buscar producto")
                                    ])
                                ),
                                width=200,
                                padding=ft.padding.symmetric(horizontal=5, vertical=20)
                            ),
                            ft.Container(
                                content=ft.ElevatedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.ADD),
                                        ft.Text("Agregar producto")
                                    ])
                                ),
                                width=200,
                                padding=ft.padding.symmetric(horizontal=5, vertical=20)
                            ),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.ElevatedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.FILE_UPLOAD),
                                        ft.Text("Importar productos")
                                    ])
                                ),
                                width=200,
                                padding=ft.padding.symmetric(horizontal=5, vertical=20)
                            ),
                            ft.Container(
                                content=ft.ElevatedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.FILE_DOWNLOAD),
                                        ft.Text("Exportar productos")
                                    ])
                                ),
                                width=200,
                                padding=ft.padding.symmetric(horizontal=5, vertical=20)
                            ),
                        ]
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            ft.Row(
                controls=[
                    ft.Container(
                        content=mostrar_tabla_productos(productos_ejemplo),
                        expand=True,
                        padding=ft.padding.all(10)
                        )
                    ],
                )     
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
