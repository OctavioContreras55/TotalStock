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
    
    # Estado para el menú seleccionado
    seccion_actual = ft.Ref[str]()
    seccion_actual.current = "Inicio"  # Sección por defecto
    
    # Configuración responsiva de la página principal
    ancho_ventana = page.window.width or 1200
    alto_ventana = page.window.height or 800
    
    # Ancho del menú lateral adaptativo
    if ancho_ventana < 1200:      # Laptops
        ancho_menu = 220
    elif ancho_ventana < 1600:    # Monitores medianos
        ancho_menu = 250  
    else:                         # Monitores grandes
        ancho_menu = 280
    
    page.window_maximized = True
    page.window_resizable = True
    page.window_minimizable = False
    min_width = max(900, int(ancho_ventana * 0.7))   # Más flexible para laptops
    min_height = max(650, int(alto_ventana * 0.75))  # Más flexible para laptops
    page.window.min_width = min_width
    page.window.min_height = min_height
    page.title = "TotalStock: Sistema de Inventario"
    fecha_actual = datetime.now().strftime("%d/%m/%Y") #Obtiene la fecha actual en formato dd/mm/yyyy
    
    # Contenido de la derecha
    contenido = ft.Container(expand=True, padding=20, bgcolor=tema.BG_COLOR)
    
    # Función para crear ListTile con estado de selección
    def crear_menu_item(icono, texto, seccion, on_click_func, es_async=False, es_especial=False, color_especial=None):
        es_seleccionado = seccion_actual.current == seccion
        
        # Función de clic que maneja tanto sync como async
        def manejar_clic(e):
            if es_async:
                asyncio.run(cambiar_seccion_async(seccion, on_click_func))
            else:
                cambiar_seccion_sync(seccion, on_click_func)
        
        return ft.ListTile(
            leading=ft.Icon(icono, color=color_especial if es_especial else tema.SIDEBAR_ICON_COLOR),
            title=ft.Text(texto, color=color_especial if es_especial else tema.SIDEBAR_TEXT_COLOR),
            dense=True,
            selected=es_seleccionado,  # Propiedad nativa de selección
            on_click=manejar_clic,
            style=ft.ListTileStyle.LIST if es_seleccionado else None,
            bgcolor=ft.Colors.with_opacity(0.2, tema.PRIMARY_COLOR) if es_seleccionado else None,
            hover_color=ft.Colors.with_opacity(0.1, tema.PRIMARY_COLOR),
            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS) if es_seleccionado else None
        )
    
    # Función para cambiar sección y actualizar estado visual
    async def cambiar_seccion_async(nueva_seccion, funcion_vista):
        seccion_actual.current = nueva_seccion
        await funcion_vista()
        actualizar_menu()
    
    def cambiar_seccion_sync(nueva_seccion, funcion_vista):
        seccion_actual.current = nueva_seccion
        funcion_vista()
        actualizar_menu()
    
    # Función para actualizar la apariencia del menú
    def actualizar_menu():
        # Recrear el menú con el estado actualizado
        menu_lateral.content = crear_contenido_menu()
        page.update()
    
    
    async def vista_inicio(nombre_seccion):
        try:
            dashboard_content = await vista_inicio_modular(page, nombre_seccion, contenido, fecha_actual)
            contenido.content = dashboard_content
            page.update()
        except Exception as e:
            print(f"Error al cargar vista inicio: {e}")
            contenido.content = ft.Column([
                ft.Text(f"Error al cargar {nombre_seccion}", size=24, color=tema.ERROR_COLOR),
                ft.Text(f"Error: {str(e)}", size=16, color=tema.TEXT_SECONDARY)
            ])
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
        
    async def on_cerrar_sesion(e):
        await cerrar_sesion(page)

    # Función para crear el contenido del menú con estado
    def crear_contenido_menu():
        return ft.Column(
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
                crear_menu_item(ft.Icons.HOME, "Inicio", "Inicio", lambda: asyncio.create_task(vista_inicio("Inicio")), es_async=True),
                crear_menu_item(ft.Icons.INVENTORY_2, "Inventario", "Inventario", lambda: vista_inventario("Inventario"), es_async=True),
                crear_menu_item(ft.Icons.LABEL, "Categorías", "Categorías", lambda: vista_categorias("Categorías")),
                crear_menu_item(ft.Icons.LOCATION_ON, "Ubicaciones", "Ubicaciones", lambda: vista_ubicaciones("Ubicaciones")),
                crear_menu_item(ft.Icons.SWAP_HORIZ, "Movimientos", "Movimientos", lambda: vista_movimientos("Movimientos")),
                crear_menu_item(ft.Icons.INSERT_CHART, "Reportes", "Reportes", lambda: vista_reportes("Reportes")),

                ft.Container(expand=True),
                
                crear_menu_item(ft.Icons.SUPERVISED_USER_CIRCLE, "Usuarios", "Usuarios", lambda: vista_usuarios("Usuarios"), es_async=True),
                crear_menu_item(ft.Icons.SETTINGS, "Configuración", "Configuración", lambda: vista_configuracion("Configuración")),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LOGOUT, color=tema.ERROR_COLOR),
                    title=ft.Text("Cerrar sesión", style=ft.TextStyle(color=tema.ERROR_COLOR)),
                    dense=True,
                    on_click=on_cerrar_sesion,
                    hover_color=ft.Colors.with_opacity(0.1, tema.ERROR_COLOR)
                ),
                
            ],
            expand=True,
        )
        
    # Contenedor del menú lateral - Responsivo         
    menu_lateral = ft.Container(
        width=ancho_menu,  # Ancho adaptativo
        bgcolor=tema.SIDEBAR_COLOR,
        padding=20,
        content=crear_contenido_menu()
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
    
    await vista_inicio("Inicio")  # Carga la vista de inicio por defecto
    page.update()  # Actualiza la página para mostrar los cambios iniciales
