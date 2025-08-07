import flet as ft
from app.tablas.ui_tabla_productos import mostrar_tabla_productos
from app.ui.barra_carga import vista_carga
import asyncio
from app.funciones.carga_archivos import on_click_importar_archivo
from app.crud_productos.create_producto import obtener_productos_firebase, vista_crear_producto
from app.crud_productos.search_producto import mostrar_dialogo_busqueda
from app.funciones.exportar_productos import mostrar_dialogo_exportar
from app.utils.temas import GestorTemas

async def vista_inventario(nombre_seccion, contenido, page):
    from app.utils.monitor_firebase import monitor_firebase
    from app.utils.cache_firebase import cache_firebase
    
    print("🏪 ENTRANDO A INVENTARIO - Optimizando carga...")
    
    if page is None:
        page = contenido.page
    
    productos_actuales = []

    # CARGA INMEDIATA desde cache si está disponible
    productos_cache = cache_firebase.obtener_productos_inmediato()
    if productos_cache:
        # Mostrar datos inmediatamente sin loading screen
        print("⚡ CARGA INSTANTÁNEA desde cache - Saltando loading screen")
        productos_actuales = productos_cache
        # Continuar directamente sin mostrar barra de carga
    else:
        # Solo mostrar loading si no hay cache
        print("📡 No hay cache - Mostrando loading y consultando Firebase")
        contenido.content = vista_carga("Cargando inventario...", 18)
        page.update()
        
        # Obtener productos iniciales desde Firebase
        try:
            productos_iniciales = await obtener_productos_firebase()
            productos_actuales = productos_iniciales
            print(f"📊 Vista inventario cargada con {len(productos_actuales)} productos")
        except Exception as e:
            print(f"Error al obtener productos iniciales: {e}")
            productos_iniciales = []
            productos_actuales = []

    async def actualizar_tabla_productos(forzar_refresh=False):
        """
        Actualizar tabla con carga optimizada.
        """
        nonlocal productos_actuales
        try:
            if forzar_refresh:
                print("🔄 ACTUALIZANDO TABLA - Refresh forzado (post-operación)")
                contenido.content = vista_carga("Actualizando datos...", 16)
                page.update()
                
                # Forzar consulta a Firebase (ej: después de crear/editar)
                productos_actuales = await cache_firebase.obtener_productos(forzar_refresh=True)
                print(f"   → Refresh forzado completado: {len(productos_actuales)} productos")
            else:
                # Carga optimizada normal
                productos_cache_rapido = cache_firebase.obtener_productos_inmediato()
                if productos_cache_rapido:
                    print("⚡ ACTUALIZACIÓN INMEDIATA desde cache")
                    productos_actuales = productos_cache_rapido
                else:
                    print("📡 Cache expirado - Consultando Firebase")
                    contenido.content = vista_carga("Actualizando inventario...", 16)
                    page.update()
                    productos_actuales = await cache_firebase.obtener_productos()
                print(f"   → Actualización normal completada: {len(productos_actuales)} productos")
                
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
    
    async def sincronizar_inventario_manual():
        """Sincronización manual del inventario con ubicaciones"""
        try:
            from app.utils.sincronizacion_inventario import sincronizar_inventario_completo
            tema = GestorTemas.obtener_tema()
            
            # Mostrar loading
            contenido.content = vista_carga("Sincronizando cantidades con ubicaciones...", 18)
            page.update()
            
            # Ejecutar sincronización
            resultado = await sincronizar_inventario_completo(mostrar_resultados=True)
            
            # Mostrar resultado al usuario
            if resultado['exito']:
                mensaje = f"✅ Sincronización completada: {resultado['productos_actualizados']} productos actualizados"
                if resultado['productos_sin_ubicacion'] > 0:
                    mensaje += f"\n⚠️ {resultado['productos_sin_ubicacion']} productos sin ubicaciones asignadas"
                if resultado['modelos_nuevos']:
                    mensaje += f"\n🆕 Modelos en ubicaciones no encontrados en inventario: {', '.join(resultado['modelos_nuevos'])}"
                
                page.open(ft.SnackBar(
                    content=ft.Text(mensaje, color=tema.TEXT_COLOR),
                    bgcolor=tema.SUCCESS_COLOR,
                    duration=8000
                ))
            else:
                page.open(ft.SnackBar(
                    content=ft.Text(f"❌ Error en sincronización: {'; '.join(resultado['errores'])}", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR,
                    duration=5000
                ))
            
            # Actualizar tabla con datos frescos
            await actualizar_tabla_productos(forzar_refresh=True)
            
        except Exception as e:
            tema = GestorTemas.obtener_tema()
            page.open(ft.SnackBar(
                content=ft.Text(f"❌ Error al sincronizar: {str(e)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            # Mostrar tabla actual aunque haya error
            contenido.content = construir_vista_inventario(productos_actuales)
            page.update()
    
            
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
                                        content=ft.IconButton(
                                            ft.Icons.REFRESH,
                                            icon_color=tema.SECONDARY_TEXT_COLOR,
                                            on_click=lambda e: page.run_task(actualizar_tabla_productos),
                                            tooltip="Actualizar lista"
                                        ),
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
                                            on_click=lambda e: on_click_importar_archivo(page, actualizar_tabla_productos),
                                        ),
                                        width=ancho_boton,  # Ancho responsivo
                                        padding=ft.padding.symmetric(horizontal=5, vertical=20)
                                    ),
                                    ft.Container(
                                        content=ft.ElevatedButton(
                                            content=ft.Row([
                                                ft.Icon(ft.Icons.SYNC, color=tema.ICON_BTN_COLOR),
                                                ft.Text("Sincronizar cantidades", color=tema.BUTTON_TEXT)
                                            ]),
                                            style=ft.ButtonStyle(
                                                bgcolor=ft.Colors.ORANGE_700,
                                                color=tema.BUTTON_TEXT,
                                                shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                            ),
                                            on_click=lambda e: page.run_task(sincronizar_inventario_manual),
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
                                            on_click=lambda e: mostrar_dialogo_exportar(productos_actuales, page)
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
                                        content=mostrar_tabla_productos(page, productos, actualizar_tabla_productos, contenido),
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
