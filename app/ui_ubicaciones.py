import flet as ft
from app.utils.temas import GestorTemas
from app.tablas.ui_tabla_ubicaciones import mostrar_tabla_ubicaciones
from app.tablas import ui_tabla_ubicaciones
from app.crud_productos.search_producto import buscar_en_firebase
from app.funciones.carga_archivos import on_click_importar_archivo_ubicaciones
from app.funciones.exportar_productos import exportar_ubicaciones
from app.crud_ubicaciones.create_ubicacion import crear_ubicacion_dialog, obtener_ubicaciones_firebase
from app.crud_ubicaciones.ubicaciones_productos import crear_ubicacion_producto_dialog, obtener_ubicaciones_productos_firebase
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
        """Cargar ubicaciones de productos desde Firebase"""
        try:
            print("[DEBUG] Cargando ubicaciones desde Firebase...")
            ubicaciones = await obtener_ubicaciones_productos_firebase()
            print(f"[DEBUG] Ubicaciones obtenidas: {len(ubicaciones) if ubicaciones else 0}")
            return ubicaciones
        except Exception as e:
            print(f"[DEBUG] Error al cargar desde Firebase: {e}")
            return []

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
            
            # Actualizar ubicaciones actuales
            ubicaciones_actuales = ubicaciones_filtradas
            
            # Crear nueva tabla con ubicaciones filtradas
            nueva_tabla = ui_tabla_ubicaciones.mostrar_tabla_ubicaciones(
                page, ubicaciones_filtradas, actualizar_tabla_ubicaciones
            )
            
            # Actualizar solo el container de la tabla (último elemento de la columna)
            if hasattr(contenido.content, 'controls') and len(contenido.content.controls) >= 4:
                # El container de la tabla es el último elemento
                contenido.content.controls[-1].content = nueva_tabla
                page.update()
            else:
                # Fallback: reconstruir toda la vista si no se puede actualizar solo la tabla
                contenido.content = construir_vista_ubicaciones(ubicaciones_filtradas)
                page.update()
                
        except Exception as e:
            print(f"Error al mostrar ubicaciones filtradas: {e}")
            # En caso de error, reconstruir la vista completa
            try:
                contenido.content = construir_vista_ubicaciones(ubicaciones_filtradas)
                page.update()
            except Exception as e2:
                print(f"Error al reconstruir vista: {e2}")
                page.update()

    async def buscar_ubicaciones(e):
        """Buscar ubicaciones por modelo, almacén o estantería"""
        termino_busqueda = campo_busqueda.value.strip().lower() if campo_busqueda and campo_busqueda.value else ""
        
        if not termino_busqueda:
            await actualizar_tabla_ubicaciones()
            return
        
        try:
            # Filtrar ubicaciones localmente (en una implementación real sería desde Firebase)
            ubicaciones_filtradas = [
                ubicacion for ubicacion in ubicaciones_actuales
                if (termino_busqueda in str(ubicacion.get('modelo', '')).lower() or
                    termino_busqueda in str(ubicacion.get('almacen', '')).lower() or
                    termino_busqueda in str(ubicacion.get('estanteria', '')).lower() or
                    termino_busqueda in str(ubicacion.get('observaciones', '')).lower())
            ]
            
            await mostrar_ubicaciones_filtradas(ubicaciones_filtradas)
            
        except Exception as e:
            print(f"Error en búsqueda de ubicaciones: {e}")

    def mostrar_sugerencias(texto):
        """Mostrar sugerencias de búsqueda basadas en lo que escribe el usuario"""
        if not texto or len(texto) < 2:
            sugerencias_container.visible = False
            page.update()
            return
        
        texto_lower = texto.lower()
        sugerencias = []
        
        # Buscar coincidencias en ubicaciones actuales
        for ubicacion in ubicaciones_actuales[:5]:  # Limitar a 5 sugerencias
            modelo = ubicacion.get('modelo', '').lower()
            almacen = str(ubicacion.get('almacen', '')).lower()
            estanteria = ubicacion.get('estanteria', '').lower()
            
            if (texto_lower in modelo or 
                texto_lower in almacen or 
                texto_lower in estanteria):
                sugerencia_texto = f"{ubicacion.get('modelo', 'N/A')} - Almacén {ubicacion.get('almacen', 'N/A')} / {ubicacion.get('estanteria', 'N/A')}"
                if sugerencia_texto not in [s.content.value for s in sugerencias]:
                    sugerencias.append(
                        ft.Container(
                            content=ft.Text(sugerencia_texto, color=tema.TEXT_COLOR, size=12),
                            bgcolor=tema.CARD_COLOR,
                            padding=8,
                            border_radius=tema.BORDER_RADIUS,
                            on_click=lambda e, texto=sugerencia_texto.split(' - ')[0]: seleccionar_sugerencia(texto),
                            ink=True
                        )
                    )
        
        if sugerencias:
            sugerencias_container.content = ft.Column(
                controls=sugerencias,
                spacing=2,
                scroll=ft.ScrollMode.AUTO,
                height=min(150, len(sugerencias) * 35)
            )
            sugerencias_container.visible = True
        else:
            sugerencias_container.visible = False
        
        page.update()

    def seleccionar_sugerencia(texto):
        """Seleccionar una sugerencia y ejecutar búsqueda"""
        campo_busqueda.value = texto
        sugerencias_container.visible = False
        page.run_task(buscar_ubicaciones, None)
        page.update()

    # Campo de búsqueda con sugerencias
    sugerencias_container = ft.Container(visible=False)
    
    campo_busqueda = ft.TextField(
        label="Buscar por modelo, almacén o estantería",
        width=350,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY),
        on_change=lambda e: mostrar_sugerencias(e.control.value),
        # Removemos on_submit temporalmente para evitar el error
        helper_text="Escriba para ver sugerencias"
    )
    
    # Ahora que campo_busqueda está definido, añadimos el on_submit
    campo_busqueda.on_submit = buscar_ubicaciones

    async def vista_crear_ubicacion_llamada(e):
        """Mostrar diálogo para asignar ubicación a producto"""
        await crear_ubicacion_producto_dialog(page, actualizar_tabla_ubicaciones)

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
                
                # Barra de búsqueda y botones de acción - Responsiva
                ft.Container(
                    content=ft.Column([
                        # Fila de búsqueda con sugerencias
                        ft.Column([
                            ft.Row([
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
                                    expand=True
                                ),
                            ]),
                            # Container para sugerencias
                            sugerencias_container
                        ], spacing=5),
                        
                        # Fila de botones de acción - Centrados y con ancho fijo
                        ft.Container(
                            content=ft.Row([
                                # Botón Agregar Ubicación
                                ft.ElevatedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.ADD_LOCATION, color=tema.ICON_BTN_COLOR, size=16),
                                        ft.Text("Asignar Ubicación", color=tema.BUTTON_TEXT, size=12)
                                    ], spacing=5),
                                    style=ft.ButtonStyle(
                                        bgcolor=tema.BUTTON_BG,
                                        color=tema.BUTTON_TEXT,
                                        shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                    ),
                                    on_click=vista_crear_ubicacion_llamada,
                                    width=180
                                ),
                                
                                # Botón Importar Excel
                                ft.ElevatedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.FILE_UPLOAD, color=tema.ICON_BTN_COLOR, size=16),
                                        ft.Text("Importar Excel", color=tema.BUTTON_TEXT, size=12)
                                    ], spacing=5),
                                    style=ft.ButtonStyle(
                                        bgcolor=tema.BUTTON_BG,
                                        color=tema.BUTTON_TEXT,
                                        shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                    ),
                                    on_click=lambda e: on_click_importar_archivo_ubicaciones(page),
                                    width=160
                                ),
                                
                                # Botón Exportar
                                ft.ElevatedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.FILE_DOWNLOAD, color=tema.ICON_BTN_COLOR, size=16),
                                        ft.Text("Exportar", color=tema.BUTTON_TEXT, size=12)
                                    ], spacing=5),
                                    style=ft.ButtonStyle(
                                        bgcolor=tema.BUTTON_BG,
                                        color=tema.BUTTON_TEXT,
                                        shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                    ),
                                    on_click=exportar_ubicaciones_llamada,
                                    width=130
                                ),
                            ], spacing=15, alignment=ft.MainAxisAlignment.CENTER),
                            alignment=ft.alignment.center
                        ),
                    ], spacing=15),
                    width=ancho_ventana * 0.95,
                    padding=ft.padding.symmetric(horizontal=10, vertical=15)
                ),
                
                # Tabla de ubicaciones - Contenedor responsivo
                ft.Container(
                    content=mostrar_tabla_ubicaciones(page, ubicaciones, actualizar_tabla_ubicaciones),
                    width=ancho_ventana * 0.95,  # Más responsivo
                    padding=ft.padding.symmetric(horizontal=10, vertical=20),
                    bgcolor=tema.CARD_COLOR,
                    border_radius=tema.BORDER_RADIUS,
                    alignment=ft.alignment.center,
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
