import flet as ft
from datetime import datetime
from app.ui_inventario import vista_inventario as vista_inventario_modular
from app.ui_inicio import vista_inicio as vista_inicio_modular
from app.funciones.sesiones import cerrar_sesion
from app.ui_usuarios import vista_usuarios as vista_usuarios_modular
from app.ui_categorias import categorias_mostrar
from app.utils.temas import GestorTemas
from conexiones.firebase import db
import asyncio


async def principal_view(page: ft.Page):
    tema = GestorTemas.obtener_tema()
    page.controls.clear()  # Limpia los controles de la página
    page.bgcolor = tema.BG_COLOR  # Establecer el color de fondo
    
    # Configuración de la página principal
    page.window_maximized = True
    page.window_resizable = True
    page.window_minimizable = False
    min_width = max(1020, int(page.window.width * 0.8))
    min_height = max(800, int(page.window.height * 0.8))
    page.window.min_width = min_width
    page.window.min_height = min_height
    page.title = "TotalStock: Sistema de Inventario"
    fecha_actual = datetime.now().strftime("%d/%m/%Y") #Obtiene la fecha actual en formato dd/mm/yyyy
    
    # Contenido de la derecha
    contenido = ft.Container(expand=True, padding=20, bgcolor=tema.BG_COLOR)
    
    
    def vista_inicio(nombre_seccion):
        vista_inicio_modular(nombre_seccion, contenido, fecha_actual)
        page.update()
    
    # Función para cambiar la vista al hacer clic en el menú
    async def vista_inventario(nombre_seccion):
        await vista_inventario_modular(nombre_seccion, contenido, page)
        page.update()
    
    def vista_categorias(nombre_seccion):
        categorias_mostrar(nombre_seccion, contenido)
        page.update()
        
    def vista_ubicaciones(nombre_seccion):
        contenido.content = ft.Column(
            controls=[
                ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24, color=tema.TEXT_COLOR),
                ft.Text("Aquí puedes gestionar las ubicaciones de tus productos.", size=16, color=tema.TEXT_SECONDARY)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        page.update()
    
    def vista_movimientos(nombre_seccion):
        contenido.content = ft.Column(
            controls=[
                ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24, color=tema.TEXT_COLOR),
                ft.Text("Aquí puedes gestionar los movimientos de inventario.", size=16, color=tema.TEXT_SECONDARY)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        page.update()
    
    def vista_reportes(nombre_seccion):
        contenido.content = ft.Column(
            controls=[
                ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24, color=tema.TEXT_COLOR),
                ft.Text("Aquí puedes generar reportes de inventario.", size=16, color=tema.TEXT_SECONDARY)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        page.update()
    
    async def vista_usuarios(nombre_seccion):
        await vista_usuarios_modular(nombre_seccion, contenido, page)
        page.update()
            
    def vista_configuracion(nombre_seccion):
        from app.ui_configuracion import vista_configuracion as vista_configuracion_modular
        vista_configuracion_modular(nombre_seccion, contenido, page)
        page.update()
        
    def on_cerrar_sesion(e):
        cerrar_sesion(page)
        
    # Contenedor del menú lateral          
    menu_lateral = ft.Container(
        width=250,
        bgcolor=tema.SIDEBAR_COLOR,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=48, color=tema.PRIMARY_COLOR),
                            ft.Column(
                                controls=[
                                    ft.Text("Octavio", size=18, weight=ft.FontWeight.BOLD, color=tema.SIDEBAR_TEXT_COLOR),
                                    ft.Text("Administrador", size=12, color=tema.SIDEBAR_TEXT_SECONDARY),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.START,
                                spacing=2,
                                
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=ft.padding.only(bottom=10, left=4, right=4)
                ),
                ft.Container(
                    height=2,
                    bgcolor=tema.DIVIDER_COLOR,
                    margin=ft.margin.only(bottom=20, top=5)
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HOME, color=tema.SIDEBAR_ICON_COLOR),
                    title=ft.Text("Inicio", color=tema.SIDEBAR_TEXT_COLOR),
                    on_click=lambda e: vista_inicio("Inicio"),
                    dense=True
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.INVENTORY_2, color=tema.SIDEBAR_ICON_COLOR),
                    title=ft.Text("Inventario", color=tema.SIDEBAR_TEXT_COLOR),
                    on_click=lambda e: asyncio.run(vista_inventario("Inventario")),
                    dense=True
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LABEL, color=tema.SIDEBAR_ICON_COLOR),
                    title=ft.Text("Categorías", color=tema.SIDEBAR_TEXT_COLOR),
                    on_click=lambda e: vista_categorias("Categorías"),
                    dense=True
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LOCATION_ON, color=tema.SIDEBAR_ICON_COLOR),
                    title=ft.Text("Ubicaciones", color=tema.SIDEBAR_TEXT_COLOR),
                    on_click=lambda e: vista_ubicaciones("Ubicaciones"),
                    dense=True
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SWAP_HORIZ, color=tema.SIDEBAR_ICON_COLOR),
                    title=ft.Text("Movimientos", color=tema.SIDEBAR_TEXT_COLOR),
                    on_click=lambda e: vista_movimientos("Movimientos"),
                    dense=True
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.INSERT_CHART, color=tema.SIDEBAR_ICON_COLOR),
                    title=ft.Text("Reportes", color=tema.SIDEBAR_TEXT_COLOR),
                    on_click=lambda e: vista_reportes("Reportes"),
                    dense=True
                ),

                ft.Container(expand=True),
                
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SUPERVISED_USER_CIRCLE, color=tema.SIDEBAR_ICON_COLOR),
                    title=ft.Text("Usuarios", color=tema.SIDEBAR_TEXT_COLOR),
                    on_click=lambda e: asyncio.run(vista_usuarios("Usuarios")),
                    dense=True
                ),
                
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SETTINGS, color=tema.SIDEBAR_ICON_COLOR),
                    title=ft.Text("Configuración", color=tema.SIDEBAR_TEXT_COLOR),
                    on_click=lambda e: vista_configuracion("Configuración"),
                    dense=True
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LOGOUT, color=tema.ERROR_COLOR),
                    title=ft.Text("Cerrar sesión", style=ft.TextStyle(color=tema.ERROR_COLOR)),
                    on_click=on_cerrar_sesion,
                    dense=True
                ),
                
            ],
            expand=True,
        ),
    )

    # Contenido inicial de la página
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
