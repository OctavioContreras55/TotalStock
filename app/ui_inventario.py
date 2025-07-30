import flet as ft
from app.tablas.ui_tabla_productos import mostrar_tabla_productos
from app.ui.barra_carga import vista_carga
import asyncio
from app.funciones.carga_archivos import on_click_importar_archivo
from app.crud_productos.create_producto import obtener_productos_firebase, vista_crear_producto
from app.crud_productos.search_producto import mostrar_dialogo_busqueda
from app.utils.temas import GestorTemas

async def vista_inventario(nombre_seccion, contenido, page):
    #productos = await obtener_productos_firebase()
    contenido.content = vista_carga()  # Mostrar barra de carga mientras se carga la vista
    await obtener_productos_firebase()  # Cargar productos desde Firebase
    page.update()  # Actualizar la página para mostrar la barra de carga
    if page is None:
        page = contenido.page
    
    productos_actuales = []

    # Obtener productos iniciales
    try:
        productos_iniciales = await obtener_productos_firebase()
        productos_actuales = productos_iniciales  # Inicializar productos actuales
    except Exception as e:
        print(f"Error al obtener productos iniciales: {e}")
        productos_iniciales = []
        productos_actuales = []

    async def actualizar_tabla_productos():
        nonlocal productos_actuales
        try:
            print("Actualizando tabla productos")
            contenido.content = vista_carga()
            page.update()
            productos_actuales = await obtener_productos_firebase()  # Aquí deberías llamar a la función que obtiene los productos de Firebase
            contenido.content = construir_vista_inventario(productos_actuales)
            page.update()
        except Exception as e:
            print(f"Error al actualizar tabla: {e}")
            productos_actuales = []
            contenido.content = construir_vista_inventario([])
            page.update()

    async def mostrar_productos_filtrados(productos_filtrados):
        nonlocal productos_actuales
        try:
            print("Mostrando productos filtrados")
            contenido.content = vista_carga()
            page.update()
            productos_actuales = productos_filtrados
            contenido.content = construir_vista_inventario(productos_actuales)
            page.update()
        except Exception as e:
            print(f"Error al mostrar productos filtrados: {e}")
            page.update()

    async def vista_crear_producto_llamada(e):
        try:
            print("Ventana de crear producto llamada exitosamente")
            await vista_crear_producto(page, actualizar_tabla_productos)
        except Exception as error:
            print(f"Error al abrir ventana: {error}")
    
            
    def construir_vista_inventario(productos):
        tema = GestorTemas.obtener_tema()
        
        # Dimensiones responsivas
        ancho_ventana = page.window.width or 1200
        ancho_header = min(700, ancho_ventana * 0.7)    # Header responsivo
        ancho_boton = min(200, ancho_ventana * 0.15)    # Botones responsivos
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24, color=tema.TEXT_COLOR),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        width=ancho_header,  # Ancho responsivo
                        bgcolor=tema.CARD_COLOR,
                        margin=ft.margin.only(top=20, bottom=20),
                        padding=ft.padding.only(top=20, bottom=20, left=10, right=10),
                        alignment=ft.alignment.center,
                        border_radius=tema.BORDER_RADIUS,
                    ),
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.ElevatedButton(
                                            content=ft.Row([
                                                ft.Icon(ft.Icons.SEARCH, color=tema.ICON_BTN_COLOR),
                                                ft.Text("Buscar producto", color=tema.BUTTON_TEXT)
                                            ]),
                                            style=ft.ButtonStyle(
                                                bgcolor=tema.BUTTON_BG,
                                                color=tema.BUTTON_TEXT,
                                                shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                            ),
                                            on_click=lambda e: mostrar_dialogo_busqueda(page, mostrar_productos_filtrados)
                                        ),
                                        width=ancho_boton,  # Ancho responsivo
                                        padding=ft.padding.symmetric(horizontal=5, vertical=20)
                                    ),
                                    ft.Container(
                                        content=ft.ElevatedButton(
                                            content=ft.Row([
                                                ft.Icon(ft.Icons.ADD, color=tema.ICON_BTN_COLOR),
                                                ft.Text("Agregar producto", color=tema.BUTTON_TEXT)
                                            ]),
                                            style=ft.ButtonStyle(
                                                bgcolor=tema.BUTTON_BG,
                                                color=tema.BUTTON_TEXT,
                                                shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                            ),
                                            on_click=vista_crear_producto_llamada
                                        ),
                                        width=ancho_boton,  # Ancho responsivo
                                        padding=ft.padding.symmetric(horizontal=5, vertical=20)
                                    ),
                                ],
                            ),
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.ElevatedButton(
                                            content=ft.Row([
                                                ft.Icon(ft.Icons.FILE_UPLOAD, color=tema.ICON_BTN_COLOR),
                                                ft.Text("Importar productos", color=tema.BUTTON_TEXT)
                                            ]),
                                            style=ft.ButtonStyle(
                                                bgcolor=tema.BUTTON_BG,
                                                color=tema.BUTTON_TEXT,
                                                shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                            ),
                                            on_click=lambda e: on_click_importar_archivo(page),
                                        ),
                                        width=ancho_boton,  # Ancho responsivo
                                        padding=ft.padding.symmetric(horizontal=5, vertical=20)
                                    ),
                                    ft.Container(
                                        content=ft.ElevatedButton(
                                            content=ft.Row([
                                                ft.Icon(ft.Icons.FILE_DOWNLOAD, color=tema.ICON_BTN_COLOR),
                                                ft.Text("Exportar productos", color=tema.BUTTON_TEXT)
                                            ]),
                                            style=ft.ButtonStyle(
                                                bgcolor=tema.BUTTON_BG,
                                                color=tema.BUTTON_TEXT,
                                                shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                            ),
                                        ),
                                        width=ancho_boton,  # Ancho responsivo
                                        padding=ft.padding.symmetric(horizontal=5, vertical=20)
                                    ),
                                ],
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Container(
                                        content=mostrar_tabla_productos(page, productos, actualizar_tabla_productos),
                                        padding=ft.padding.symmetric(horizontal=5, vertical=20),
                                        bgcolor=tema.CARD_COLOR,
                                        border_radius=tema.BORDER_RADIUS,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.START
                    )     
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(bottom=40),
            bgcolor=tema.BG_COLOR,
        )
    contenido.content = construir_vista_inventario(productos_actuales)
    page.update()  # Actualizar la página para mostrar el contenido inicial
