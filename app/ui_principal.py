import flet as ft
from datetime import datetime
from app.ui_tabla_productos import mostrar_tabla_productos
from app.ui_inventario import vista_inventario as vista_inventario_modular



def principal_view(page: ft.Page):
    page.controls.clear()  # Limpia los controles de la página
    # Configuración de la página principal
    page.window_maximized = True
    page.window_resizable = True
    page.window_minimizable = False
    page.title = "TotalStock: Sistema de Inventario"
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    
    # Contenido de la derecha
    contenido = ft.Container(expand=True, padding=20)
    
    # Diccionario de ejemplo
    productos_ejemplo = [
        {"id": 1, "nombre": "Manzana", "precio": 10.5, "cantidad": 50},
        {"id": 2, "nombre": "Plátano", "precio": 8.0, "cantidad": 30},
        {"id": 3, "nombre": "Naranja", "precio": 12.0, "cantidad": 20},
        {"id": 4, "nombre": "Pera", "precio": 15.0, "cantidad": 40},
    ]
    
    def vista_inicio(nombre_seccion):
        contenido.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24),
                        ft.Text(f"Fecha: {fecha_actual}", size=16)
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
        page.update()
    
    # Función para cambiar la vista al hacer clic en el menú
    def vista_inventario(nombre_seccion):
        vista_inventario_modular(nombre_seccion, contenido, productos_ejemplo)
        page.update()
    
    def vista_categorias(nombre_seccion):
        contenido.content = ft.Column(
            controls=[
                ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24),
                ft.Text("Aquí puedes gestionar las categorías de tus productos.", size=16)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        page.update()
        
    def vista_ubicaciones(nombre_seccion):
        contenido.content = ft.Column(
            controls=[
                ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24),
                ft.Text("Aquí puedes gestionar las ubicaciones de tus productos.", size=16)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        page.update()
    
    def vista_movimientos(nombre_seccion):
        contenido.content = ft.Column(
            controls=[
                ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24),
                ft.Text("Aquí puedes gestionar los movimientos de inventario.", size=16)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        page.update()
    
    def vista_reportes(nombre_seccion):
        contenido.content = ft.Column(
            controls=[
                ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24),
                ft.Text("Aquí puedes generar reportes de inventario.", size=16)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        page.update()
    
    def vista_usuarios(nombre_seccion):
        contenido.content = ft.Column(
            controls=[
                ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24),
                ft.Text("Aquí puedes gestionar los usuarios del sistema.", size=16)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        page.update()
            
    def vista_configuracion(nombre_seccion):
        contenido.content = ft.Column(
            controls=[
                ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24),
                ft.Text("Aquí puedes configurar el sistema.", size=16)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        page.update()
              
    menu_lateral = ft.Container(
        width=250,
        bgcolor=ft.Colors.GREY_900,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=48, color=ft.Colors.BLUE_200),
                            ft.Column(
                                controls=[
                                    ft.Text("Octavio", size=18, weight=ft.FontWeight.BOLD),
                                    ft.Text("Administrador", size=12, color=ft.Colors.GREY_400)
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.START,
                                spacing=2
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=ft.padding.only(bottom=20, left=4, right=4)
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HOME),
                    title=ft.Text("Inicio"),
                    on_click=lambda e: vista_inicio("Inicio"),
                    dense=True
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.INVENTORY_2),
                    title=ft.Text("Inventario"),
                    on_click=lambda e: vista_inventario("Inventario"),
                    dense=True
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LABEL),
                    title=ft.Text("Categorías"),
                    on_click=lambda e: vista_categorias("Categorías"),
                    dense=True
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LOCATION_ON),
                    title=ft.Text("Ubicaciones"),
                    on_click=lambda e: vista_ubicaciones("Ubicaciones"),
                    dense=True
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SWAP_HORIZ),
                    title=ft.Text("Movimientos"),
                    on_click=lambda e: vista_movimientos("Movimientos"),
                    dense=True
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.INSERT_CHART),
                    title=ft.Text("Reportes"),
                    on_click=lambda e: vista_reportes("Reportes"),
                    dense=True
                ),

                ft.Container(expand=True),
                
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SUPERVISED_USER_CIRCLE),
                    title=ft.Text("Usuarios"),
                    on_click=lambda e: vista_usuarios("Usuarios"),
                    dense=True
                ),
                
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SETTINGS),
                    title=ft.Text("Configuración"),
                    on_click=lambda e: vista_configuracion("Configuración"),
                    dense=True
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LOGOUT, color=ft.Colors.RED_400),
                    title=ft.Text("Cerrar sesión", style=ft.TextStyle(color=ft.Colors.RED_400)),
                    on_click=lambda e: print("Cerrar sesión"),
                    dense=True
                ),
                
            ],
            expand=True,
        ),
    )


    page.add(
        ft.Row(
            controls=[
                menu_lateral,
                contenido
            ],
            expand=True,
        )
    )
    
    vista_inicio("Inicio")  # Carga la vista de inicio por defecto
    page.update()  # Actualiza la página para mostrar los cambios iniciales
