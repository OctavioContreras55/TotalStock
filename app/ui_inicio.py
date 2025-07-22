import flet as ft

def vista_inicio(nombre_seccion,contenido, fecha_actual):
    contenido.content = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24),
                    ft.Text(f"Fecha: {fecha_actual}", size=16),
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
                                ft.Text("Panel de pendientes", size=20),
                                ft.ListView(
                                    controls=[
                                        ft.ListTile(
                                            leading=ft.Icon(ft.Icons.FIBER_MANUAL_RECORD, size=14, color=ft.Colors.BLUE_400),
                                            title=ft.Text("Faltan registrar 3 productos nuevos")
                                        ),
                                        ft.ListTile(
                                            leading=ft.Icon(ft.Icons.FIBER_MANUAL_RECORD, size=14, color=ft.Colors.BLUE_400),
                                            title=ft.Text("Verificar stock de Bodega A")
                                        ),
                                        ft.ListTile(
                                            leading=ft.Icon(ft.Icons.FIBER_MANUAL_RECORD, size=14, color=ft.Colors.BLUE_400),
                                            title=ft.Text("Actualizar precios de proveedor X")
                                        ),
                                        ft.ListTile(
                                            leading=ft.Icon(ft.Icons.FIBER_MANUAL_RECORD, size=14, color=ft.Colors.BLUE_400),
                                            title=ft.Text("Revisar productos próximos a caducar")
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
                    ),
                    ft.Container(width=40),  # Más espacio entre tarjetas
                    ft.Card(
                        content=ft.Column(
                            controls=[
                                ft.Container(height=10),
                                ft.Text("Historial", size=20)
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True
                        ),
                        expand=True,
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