import flet as ft
from app.utils.temas import GestorTemas
from app.tablas.ui_tabla_ubicaciones import mostrar_tabla_ubicaciones
from app.crud_productos.search_producto import buscar_en_firebase
from app.funciones.carga_archivos import on_click_importar_archivo_ubicaciones
from app.funciones.exportar_productos import exportar_ubicaciones
from app.crud_ubicaciones.create_ubicacion import crear_ubicacion_dialog, obtener_ubicaciones_firebase
from app.ui.barra_carga import vista_carga
import asyncio

async def vista_ubicaciones(nombre_seccion, contenido, page):
    """Vista de ubicaciones de productos - Similar a inventario pero con almacén y ubicación"""
    tema = GestorTemas.obtener_tema()
    
    # Variables para mantener estado
    ubicaciones_actuales = []
    
    # Dimensiones responsivas
    ancho_ventana = page.window.width or 1200
    alto_ventana = page.window.height or 800
    
    # Cálculos responsivos para botones
    if ancho_ventana < 1200:
        ancho_boton = 180
    elif ancho_ventana < 1600:
        ancho_boton = 200
    else:
        ancho_boton = 220

    async def cargar_ubicaciones_firebase():
        """Cargar ubicaciones desde Firebase"""
        return await obtener_ubicaciones_firebase()

    async def actualizar_tabla_ubicaciones():
        """Actualiza la tabla de ubicaciones"""
        nonlocal ubicaciones_actuales
        try:
            print("Actualizando tabla de ubicaciones")
            contenido.content = vista_carga()
            page.update()
            
            ubicaciones_actuales = await cargar_ubicaciones_firebase()
            contenido.content = construir_vista_ubicaciones(ubicaciones_actuales)
            page.update()
            
        except Exception as e:
            print(f"Error al actualizar tabla de ubicaciones: {e}")
            page.update()

    async def mostrar_ubicaciones_filtradas(ubicaciones_filtradas):
        """Muestra ubicaciones filtradas por búsqueda"""
        nonlocal ubicaciones_actuales
        try:
            print("Mostrando ubicaciones filtradas")
            contenido.content = vista_carga()
            page.update()
            ubicaciones_actuales = ubicaciones_filtradas
            contenido.content = construir_vista_ubicaciones(ubicaciones_actuales)
            page.update()
        except Exception as e:
            print(f"Error al mostrar ubicaciones filtradas: {e}")
            page.update()

    # Campo de búsqueda
    campo_busqueda = ft.TextField(
        label="Buscar por modelo o nombre",
        width=300,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )

    async def buscar_ubicaciones(e):
        """Buscar ubicaciones por modelo o nombre"""
        termino_busqueda = campo_busqueda.value.strip().lower()
        
        if not termino_busqueda:
            await actualizar_tabla_ubicaciones()
            return
        
        try:
            # Filtrar ubicaciones localmente (en una implementación real sería desde Firebase)
            ubicaciones_filtradas = [
                ubicacion for ubicacion in ubicaciones_actuales
                if (termino_busqueda in str(ubicacion.get('modelo', '')).lower() or
                    termino_busqueda in str(ubicacion.get('nombre', '')).lower() or
                    termino_busqueda in str(ubicacion.get('almacen', '')).lower() or
                    termino_busqueda in str(ubicacion.get('ubicacion', '')).lower())
            ]
            
            await mostrar_ubicaciones_filtradas(ubicaciones_filtradas)
            
        except Exception as e:
            print(f"Error en búsqueda de ubicaciones: {e}")

    async def vista_crear_ubicacion_llamada(e):
        """Mostrar diálogo para crear nueva ubicación"""
        await crear_ubicacion_dialog(page, actualizar_tabla_ubicaciones)

    async def exportar_ubicaciones_llamada(e):
        """Exportar ubicaciones"""
        await exportar_ubicaciones(ubicaciones_actuales, page)

    def construir_vista_ubicaciones(ubicaciones):
        """Construye la vista completa de ubicaciones"""
        
        return ft.Container(
            content=ft.Column([
                # Header con título
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOCATION_ON, color=tema.PRIMARY_COLOR, size=32),
                        ft.Text(
                            "Gestión de Ubicaciones",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=tema.TEXT_COLOR
                        ),
                    ]),
                    width=ancho_ventana * 0.9,
                    bgcolor=tema.CARD_COLOR,
                    padding=20,
                    alignment=ft.alignment.center,
                    border_radius=tema.BORDER_RADIUS,
                ),
                
                # Separador
                ft.Container(
                    height=3,
                    bgcolor=tema.DIVIDER_COLOR,
                    margin=ft.margin.only(bottom=20, top=5),
                ),
                
                # Barra de búsqueda y botones de acción
                ft.Row([
                    # Búsqueda
                    ft.Container(
                        content=ft.Row([
                            campo_busqueda,
                            ft.IconButton(
                                ft.Icons.SEARCH,
                                icon_color=tema.PRIMARY_COLOR,
                                on_click=buscar_ubicaciones
                            ),
                            ft.IconButton(
                                ft.Icons.REFRESH,
                                icon_color=tema.SECONDARY_TEXT_COLOR,
                                on_click=lambda e: page.run_task(actualizar_tabla_ubicaciones),
                                tooltip="Actualizar lista"
                            )
                        ]),
                        padding=ft.padding.symmetric(horizontal=5, vertical=20)
                    ),
                    
                    # Botones de acción
                    ft.Container(
                        content=ft.Row([
                            # Botón Agregar Ubicación
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.ADD_LOCATION, color=tema.ICON_BTN_COLOR),
                                    ft.Text("Agregar Ubicación", color=tema.BUTTON_TEXT)
                                ]),
                                style=ft.ButtonStyle(
                                    bgcolor=tema.BUTTON_BG,
                                    color=tema.BUTTON_TEXT,
                                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                ),
                                on_click=vista_crear_ubicacion_llamada,
                            ),
                            
                            # Botón Importar Excel
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.FILE_UPLOAD, color=tema.ICON_BTN_COLOR),
                                    ft.Text("Importar Ubicaciones", color=tema.BUTTON_TEXT)
                                ]),
                                style=ft.ButtonStyle(
                                    bgcolor=tema.BUTTON_BG,
                                    color=tema.BUTTON_TEXT,
                                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                ),
                                on_click=lambda e: on_click_importar_archivo_ubicaciones(page),
                            ),
                            
                            # Botón Exportar
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.FILE_DOWNLOAD, color=tema.ICON_BTN_COLOR),
                                    ft.Text("Exportar Ubicaciones", color=tema.BUTTON_TEXT)
                                ]),
                                style=ft.ButtonStyle(
                                    bgcolor=tema.BUTTON_BG,
                                    color=tema.BUTTON_TEXT,
                                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                ),
                                on_click=exportar_ubicaciones_llamada,
                            ),
                        ], spacing=10),
                        width=ancho_boton * 3.2,
                        padding=ft.padding.symmetric(horizontal=5, vertical=20)
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                
                # Tabla de ubicaciones
                ft.Row([
                    ft.Column([
                        ft.Container(
                            content=mostrar_tabla_ubicaciones(page, ubicaciones, actualizar_tabla_ubicaciones),
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

    # Cargar datos iniciales y mostrar vista
    await actualizar_tabla_ubicaciones()
