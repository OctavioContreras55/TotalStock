import flet as ft
from app.tablas.ui_tabla_usuarios import mostrar_tabla_usuarios
from app.tablas import ui_tabla_usuarios
from app.crud_usuarios.create_usuarios import mostrar_ventana_crear_usuario, obtener_usuarios_firebase
from app.utils.temas import GestorTemas
import asyncio
from app.ui.barra_carga import vista_carga

async def vista_usuarios(nombre_seccion, contenido, page=None):
    """Vista de usuarios con búsqueda y selección múltiple"""
    from app.utils.cache_firebase import cache_firebase
    
    tema = GestorTemas.obtener_tema()
    
    print("👥 ENTRANDO A USUARIOS - Optimizando carga...")
    
    if page is None:
        page = contenido.page
    
    # Establecer referencia de página para selección múltiple
    ui_tabla_usuarios.set_page_reference(page)
    
    # Establecer callback de actualización
    ui_tabla_usuarios.set_actualizar_tabla_callback(None)  # Se establecerá después
    
    usuarios_actuales = []
    
    # Crear referencia al botón eliminar para control directo
    boton_eliminar_ref = None
    
    # Dimensiones responsivas
    ancho_ventana = page.window.width or 1200
    alto_ventana = page.window.height or 800
    
    # CARGA OPTIMIZADA con cache
    print("📡 Consultando usuarios con cache optimizado...")
    contenido.content = vista_carga("Cargando usuarios...", 18)
    page.update()
    
    try:
        usuarios_actuales = await cache_firebase.obtener_usuarios()
        print(f"👥 Vista usuarios cargada con {len(usuarios_actuales)} usuarios")
    except Exception as e:
        print(f"Error al obtener usuarios iniciales: {e}")
        usuarios_actuales = []

    async def actualizar_tabla_usuarios(forzar_refresh=False):
        """Actualizar tabla con estrategia optimista - sin parpadeo"""
        nonlocal usuarios_actuales
        try:
            if forzar_refresh:
                print("🔄 REFRESH TRADICIONAL: Consultando Firebase")
                # Solo para casos donde realmente necesitamos recargar desde Firebase
                from app.utils.cache_firebase import cache_firebase
                cache_firebase._cache_usuarios = []
                cache_firebase._ultimo_update_usuarios = None
                usuarios_actuales = await cache_firebase.obtener_usuarios(forzar_refresh=True, mostrar_loading=False)
                print(f"   → Refresh completado: {len(usuarios_actuales)} usuarios")
            else:
                # Usar cache optimizado para usuarios
                print("📡 Cache usuarios - Consultando con sistema optimizado")
                from app.utils.cache_firebase import cache_firebase
                usuarios_actuales = await cache_firebase.obtener_usuarios(mostrar_loading=False)
                print(f"   → Actualización normal completada: {len(usuarios_actuales)} usuarios")
                
            # Actualizar solo la tabla, no toda la vista
            if hasattr(contenido.content, 'controls') and len(contenido.content.controls) >= 4:
                nueva_tabla = ui_tabla_usuarios.mostrar_tabla_usuarios(
                    page, usuarios_actuales, actualizar_tabla_usuarios
                )
                contenido.content.controls[-1].content = nueva_tabla
                page.update()
            else:
                contenido.content = construir_vista_usuarios(usuarios_actuales)
                page.update()
                
        except Exception as e:
            print(f"Error al actualizar tabla usuarios: {e}")
            usuarios_actuales = []
            contenido.content = construir_vista_usuarios([])
            page.update()

    async def mostrar_usuarios_filtrados(usuarios_filtrados):
        """Muestra usuarios filtrados por búsqueda"""
        nonlocal usuarios_actuales
        try:
            print("Mostrando usuarios filtrados")
            
            usuarios_actuales = usuarios_filtrados
            
            nueva_tabla = ui_tabla_usuarios.mostrar_tabla_usuarios(
                page, usuarios_filtrados, actualizar_tabla_usuarios
            )
            
            if hasattr(contenido.content, 'controls') and len(contenido.content.controls) >= 4:
                contenido.content.controls[-1].content = nueva_tabla
                page.update()
            else:
                contenido.content = construir_vista_usuarios(usuarios_filtrados)
                page.update()
                
        except Exception as e:
            print(f"Error al mostrar usuarios filtrados: {e}")
            try:
                contenido.content = construir_vista_usuarios(usuarios_filtrados)
                page.update()
            except Exception as e2:
                print(f"Error al reconstruir vista: {e2}")
                page.update()

    async def buscar_usuarios(e):
        """Buscar usuarios por nombre o ID"""
        termino_busqueda = campo_busqueda.value.strip().lower() if campo_busqueda and campo_busqueda.value else ""
        
        if not termino_busqueda:
            await actualizar_tabla_usuarios()
            return
        
        try:
            usuarios_filtrados = [
                usuario for usuario in usuarios_actuales
                if (termino_busqueda in str(usuario.get('nombre', '')).lower() or
                    termino_busqueda in str(usuario.get('id', '')).lower() or
                    termino_busqueda in str(usuario.get('firebase_id', '')).lower())
            ]
            
            await mostrar_usuarios_filtrados(usuarios_filtrados)
            
        except Exception as e:
            print(f"Error en búsqueda de usuarios: {e}")

    def mostrar_sugerencias(texto):
        """Mostrar sugerencias de búsqueda basadas en lo que escribe el usuario"""
        if not texto or len(texto) < 2:
            sugerencias_container.visible = False
            page.update()
            return
        
        texto_lower = texto.lower()
        sugerencias = []
        
        for usuario in usuarios_actuales[:5]:  # Limitar a 5 sugerencias
            nombre = str(usuario.get('nombre', '')).lower()
            user_id = str(usuario.get('id', '')).lower()
            
            if (texto_lower in nombre or texto_lower in user_id):
                sugerencia_texto = f"{usuario.get('nombre', 'Sin nombre')} (ID: {usuario.get('id', 'N/A')})"
                if sugerencia_texto not in [s.content.value for s in sugerencias]:
                    sugerencias.append(
                        ft.Container(
                            content=ft.Text(sugerencia_texto, color=tema.TEXT_COLOR, size=12),
                            bgcolor=tema.CARD_COLOR,
                            padding=8,
                            border_radius=tema.BORDER_RADIUS,
                            on_click=lambda e, texto=usuario.get('nombre', ''): seleccionar_sugerencia(texto),
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
        page.run_task(buscar_usuarios, None)
        page.update()

    # Campo de búsqueda con sugerencias
    sugerencias_container = ft.Container(visible=False)
    
    campo_busqueda = ft.TextField(
        label="Buscar por nombre o ID",
        width=350,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY),
        on_change=lambda e: mostrar_sugerencias(e.control.value),
        helper_text="Escriba para ver sugerencias"
    )
    
    campo_busqueda.on_submit = buscar_usuarios

    def abrir_ventana_crear_usuario(e):
        """Función para abrir la ventana de crear usuario"""
        try:
            mostrar_ventana_crear_usuario(page, actualizar_tabla_usuarios)
            print("Ventana de crear usuario llamada exitosamente")
        except Exception as error:
            print(f"Error al abrir ventana: {error}")

    def construir_vista_usuarios(usuarios):
        """Construye la vista completa de usuarios"""
        nonlocal boton_eliminar_ref
        
        # Crear botón eliminar con referencia
        boton_eliminar_ref = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.DELETE_SWEEP, color="#FFFFFF", size=16),
                ft.Text("Eliminar Selec.", color="#FFFFFF", size=12)
            ], spacing=5),
            style=ft.ButtonStyle(
                bgcolor=tema.ERROR_COLOR,
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
            ),
            on_click=lambda e: page.run_task(ui_tabla_usuarios.eliminar_usuarios_seleccionados, page, actualizar_tabla_usuarios),
            width=170,
            visible=False,  # Se mostrará cuando haya selecciones
            data="btn_eliminar_usuarios_seleccionados"  # ID para encontrarlo después
        )
        
        # Establecer referencia en el módulo de tabla
        ui_tabla_usuarios.set_boton_eliminar_reference(boton_eliminar_ref)
        
        return ft.Container(
            content=ft.Column([
                # Header con título
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PEOPLE, color=tema.PRIMARY_COLOR, size=32),
                        ft.Text(
                            "Gestión de Usuarios",
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
                    margin=ft.margin.only(bottom=15, top=5),
                ),
                
                # Barra de búsqueda y botones de acción
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
                                            on_click=buscar_usuarios
                                        ),
                                        ft.IconButton(
                                            ft.Icons.REFRESH,
                                            icon_color=tema.SECONDARY_TEXT_COLOR,
                                            on_click=lambda e: page.run_task(actualizar_tabla_usuarios),
                                            tooltip="Actualizar lista"
                                        )
                                    ]),
                                    expand=True
                                ),
                            ]),
                            # Container para sugerencias
                            sugerencias_container
                        ], spacing=5),
                        
                        # Fila de botones de acción - Agregar Usuario a la derecha
                        ft.Container(
                            content=ft.Row([
                                # Botón Eliminar Seleccionados - A la izquierda (usar la referencia)
                                boton_eliminar_ref,
                                
                                # Espaciador para empujar el botón agregar a la derecha
                                ft.Container(expand=True),
                                
                                # Botón Agregar Usuario - A la derecha
                                ft.ElevatedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.ADD, color=tema.ICON_BTN_COLOR, size=16),
                                        ft.Text("Agregar Usuario", color=tema.BUTTON_TEXT, size=12)
                                    ], spacing=5),
                                    style=ft.ButtonStyle(
                                        bgcolor=tema.BUTTON_BG,
                                        color=tema.BUTTON_TEXT,
                                        shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                    ),
                                    on_click=abrir_ventana_crear_usuario,
                                    width=180
                                ),
                            ], spacing=15, alignment=ft.MainAxisAlignment.START),
                            alignment=ft.alignment.center_left  # Alineación general a la izquierda
                        ),
                    ], spacing=15),
                    width=ancho_ventana * 0.95,
                    padding=ft.padding.symmetric(horizontal=10, vertical=10)
                ),
                
                # Separador adicional entre botones y tabla
                ft.Container(height=5),
                
                # Tabla de usuarios - Contenedor responsivo centrado y optimizado
                ft.Container(
                    content=ft.Container(
                        content=mostrar_tabla_usuarios(page, usuarios, actualizar_tabla_usuarios),
                        width=ancho_ventana * 0.96,  # Más ancho para aprovechar mejor el espacio
                        padding=ft.padding.symmetric(horizontal=15, vertical=20),  # Padding reducido para más espacio
                        margin=ft.margin.only(top=10, bottom=100),  # Pegado más arriba
                        bgcolor=tema.CARD_COLOR,
                        border_radius=tema.BORDER_RADIUS,
                        alignment=ft.alignment.top_center,  # Alineación superior y centrada
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=8,
                            color=ft.Colors.BLACK12,
                            offset=ft.Offset(0, 3)
                        )
                    ),
                    alignment=ft.alignment.top_center,  # Centrado horizontal y pegado arriba
                    width=ancho_ventana * 0.99,  # Container padre ocupa casi todo el ancho
                    height=alto_ventana * 0.7,  # Altura responsiva para dejar espacio para botones
                )     
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(bottom=150),  # Mucho más padding para separación visible
            bgcolor=tema.BG_COLOR,
        )

    # Cargar datos iniciales y mostrar vista
    contenido.content = construir_vista_usuarios(usuarios_actuales) 
    
    # Establecer callback de actualización después de construir la vista
    ui_tabla_usuarios.set_actualizar_tabla_callback(actualizar_tabla_usuarios)
    
    page.update()
