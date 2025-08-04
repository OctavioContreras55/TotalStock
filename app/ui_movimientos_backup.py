import flet as ft
from app.utils.temas import GestorTemas
from app.utils.historial import GestorHistorial
from app.funciones.sesiones import SesionManager
from app.crud_movimientos.create_movimiento import crear_movimiento_dialog, obtener_movimientos_firebase
from conexiones.firebase import db
import asyncio
from datetime import datetime
from app.ui.barra_carga import vista_carga

async def vista_movimientos(nombre_seccion, contenido, page):
    """Vista para realizar y visualizar movimientos de productos"""
    tema = GestorTemas.obtener_tema()
    
    # Variables de estado
    movimientos_actuales = []
    
    # Dimensiones responsivas
    ancho_ventana = page.window.width or 1200
    alto_ventana = page.window.height or 800
    
    async def cargar_movimientos():
        """Cargar movimientos desde Firebase"""
        return await obtener_movimientos_firebase()
    
    async def actualizar_tabla_movimientos():
        """Actualizar la tabla de movimientos"""
        nonlocal movimientos_actuales
        try:
            print("Actualizando tabla de movimientos")
            contenido.content = vista_carga()
            page.update()
            
            movimientos_actuales = await cargar_movimientos()
            contenido.content = construir_vista_movimientos(movimientos_actuales)
            page.update()
            
        except Exception as e:
            print(f"Error al actualizar tabla de movimientos: {e}")
            page.update()
    
    async def mostrar_dialogo_nuevo_movimiento(e):
        """Mostrar diálogo para crear nuevo movimiento"""
        await crear_movimiento_dialog(page, actualizar_tabla_movimientos)
    
    def construir_tabla_movimientos(movimientos):
        """Construir tabla de movimientos"""
        if not movimientos:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SWAP_HORIZ, size=64, color=tema.TEXT_SECONDARY),
                    ft.Text("No hay movimientos registrados", 
                           size=18, color=tema.TEXT_SECONDARY, text_align=ft.TextAlign.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                height=300
            )
        
        # Crear filas de la tabla
        filas = []
        for mov in movimientos:
            origen = mov.get('ubicacion_origen', {})
            destino = mov.get('ubicacion_destino', {})
            fecha = mov.get('fecha_movimiento', '').split('T')[0] if mov.get('fecha_movimiento') else 'N/A'
            
            fila = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(mov.get('producto_modelo', 'N/A'), color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(str(mov.get('cantidad', 0)), color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(f"{origen.get('almacen', 'N/A')}", color=tema.TEXT_COLOR, size=12)),
                    ft.DataCell(ft.Text(f"{destino.get('almacen', 'N/A')}", color=tema.TEXT_COLOR, size=12)),
                    ft.DataCell(ft.Text(mov.get('tipo_movimiento', 'N/A'), color=tema.TEXT_COLOR, size=12)),
                    ft.DataCell(ft.Text(fecha, color=tema.TEXT_COLOR, size=12)),
                    ft.DataCell(ft.Text(mov.get('usuario', 'N/A'), color=tema.TEXT_COLOR, size=12)),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                mov.get('estado', 'N/A'), 
                                color=ft.Colors.WHITE,
                                size=11,
                                weight=ft.FontWeight.BOLD
                            ),
                            bgcolor=tema.SUCCESS_COLOR if mov.get('estado') == 'Completado' else tema.WARNING_COLOR,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=12
                        )
                    ),
                ]
            )
            filas.append(fila)
        
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Cantidad", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Origen", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Destino", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tipo", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fecha", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Usuario", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD)),
            ],
            rows=filas,
            border=ft.border.all(1, tema.DIVIDER_COLOR),
            border_radius=tema.BORDER_RADIUS,
            column_spacing=10,
            heading_row_color=tema.CARD_COLOR,
            data_row_color={
                ft.MaterialState.SELECTED: tema.SELECTED_COLOR,
                ft.MaterialState.PRESSED: tema.HOVER_COLOR,
            }
        )
    
    def construir_vista_movimientos(movimientos):
        """Construir vista completa de movimientos"""
        return ft.Container(
            content=ft.Column([
                # Header con título
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SWAP_HORIZ, color=tema.PRIMARY_COLOR, size=32),
                        ft.Text(
                            "Gestión de Movimientos",
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
                
                # Botones de acción
                ft.Row([
                    ft.ElevatedButton(
                        "Nuevo Movimiento",
                        icon=ft.Icons.ADD,
                        style=ft.ButtonStyle(
                            bgcolor=tema.BUTTON_SUCCESS_BG,
                            color=tema.BUTTON_TEXT,
                            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                        ),
                        on_click=mostrar_dialogo_nuevo_movimiento,
                        width=200,
                        height=45
                    ),
                    ft.ElevatedButton(
                        "Actualizar",
                        icon=ft.Icons.REFRESH,
                        style=ft.ButtonStyle(
                            bgcolor=tema.BUTTON_BG,
                            color=tema.BUTTON_TEXT,
                            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                        ),
                        on_click=lambda e: asyncio.create_task(actualizar_tabla_movimientos()),
                        width=150,
                        height=45
                    ),
                ], spacing=20, alignment=ft.MainAxisAlignment.START),
                
                # Estadísticas rápidas
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Total Movimientos", color=tema.TEXT_SECONDARY, size=12),
                                ft.Text(str(len(movimientos)), color=tema.TEXT_COLOR, size=24, weight=ft.FontWeight.BOLD)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            bgcolor=tema.CARD_COLOR,
                            padding=15,
                            border_radius=tema.BORDER_RADIUS,
                            width=150
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Hoy", color=tema.TEXT_SECONDARY, size=12),
                                ft.Text(str(len([m for m in movimientos if m.get('fecha_movimiento', '').startswith(datetime.now().strftime('%Y-%m-%d'))])), 
                                       color=tema.PRIMARY_COLOR, size=24, weight=ft.FontWeight.BOLD)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            bgcolor=tema.CARD_COLOR,
                            padding=15,
                            border_radius=tema.BORDER_RADIUS,
                            width=150
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Completados", color=tema.TEXT_SECONDARY, size=12),
                                ft.Text(str(len([m for m in movimientos if m.get('estado') == 'Completado'])), 
                                       color=tema.SUCCESS_COLOR, size=24, weight=ft.FontWeight.BOLD)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            bgcolor=tema.CARD_COLOR,
                            padding=15,
                            border_radius=tema.BORDER_RADIUS,
                            width=150
                        ),
                    ], spacing=20),
                    margin=ft.margin.symmetric(vertical=20)
                ),
                
                # Tabla de movimientos
                ft.Container(
                    content=ft.Column([
                        ft.Text("Historial de Movimientos", 
                               size=20, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                        ft.Container(
                            content=construir_tabla_movimientos(movimientos),
                            bgcolor=tema.BACKGROUND_COLOR,
                            padding=10,
                            border_radius=tema.BORDER_RADIUS,
                            border=ft.border.all(1, tema.DIVIDER_COLOR)
                        )
                    ], spacing=15),
                    expand=True
                )
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=20,
            expand=True
        )
    
    # Cargar datos iniciales
    await actualizar_tabla_movimientos()
                {
                    "id": "prod_3",
                    "modelo": "TEC003", 
                    "nombre": "Teclado Mecánico Corsair",
                    "almacen_actual": "Almacén de Repuestos",
                    "ubicacion_actual": "Estante C-2, Nivel 1",
                    "cantidad_disponible": 8
                }
            ]
        except Exception as e:
            print(f"Error al buscar productos: {e}")
            return []

    async def obtener_historial_movimientos():
        """Obtener historial de movimientos recientes"""
        try:
            # En implementación real desde Firebase
            return [
                {
                    "id": "mov_1",
                    "producto": "Laptop Dell Inspiron",
                    "modelo": "LAP001",
                    "origen": "Almacén Principal → Estante A-3",
                    "destino": "Almacén Secundario → Estante B-2",
                    "cantidad": 5,
                    "usuario": "Admin",
                    "fecha": "2024-01-15 14:30",
                    "motivo": "Redistribución de inventario"
                },
                {
                    "id": "mov_2",
                    "producto": "Mouse Logitech MX",
                    "modelo": "MOU002", 
                    "origen": "Almacén Secundario → Cajón B-1",
                    "destino": "Almacén Principal → Cajón A-5",
                    "cantidad": 25,
                    "usuario": "Operador1",
                    "fecha": "2024-01-15 10:15",
                    "motivo": "Reposición de stock"
                }
            ]
        except Exception as e:
            print(f"Error al obtener historial: {e}")
            return []

    # Campo de búsqueda de productos
    campo_busqueda_producto = ft.TextField(
        label="Buscar producto (modelo o nombre)",
        width=350,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY),
        prefix_icon=ft.Icons.SEARCH
    )

    # Lista de productos encontrados
    lista_productos = ft.Column([], spacing=5)

    async def buscar_productos(e):
        """Buscar productos disponibles para mover"""
        termino = campo_busqueda_producto.value.strip().lower()
        productos = await buscar_productos_por_ubicacion()
        
        lista_productos.controls.clear()
        
        if not termino:
            lista_productos.controls.append(
                ft.Text("Escribe para buscar productos...", color=tema.SECONDARY_TEXT_COLOR, italic=True)
            )
        else:
            productos_filtrados = [
                p for p in productos 
                if termino in p["modelo"].lower() or termino in p["nombre"].lower()
            ]
            
            if productos_filtrados:
                for producto in productos_filtrados:
                    lista_productos.controls.append(crear_tarjeta_producto(producto))
            else:
                lista_productos.controls.append(
                    ft.Text("No se encontraron productos", color=tema.ERROR_COLOR)
                )
        
        page.update()

    def crear_tarjeta_producto(producto):
        """Crear tarjeta visual de producto"""
        def seleccionar_producto(e):
            nonlocal producto_seleccionado, ubicacion_origen
            producto_seleccionado = producto
            ubicacion_origen = {
                "almacen": producto["almacen_actual"],
                "ubicacion": producto["ubicacion_actual"]
            }
            actualizar_panel_movimiento()

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.INVENTORY, color=tema.PRIMARY_COLOR, size=20),
                        ft.Text(producto["modelo"], weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                        ft.Container(
                            content=ft.Text(str(producto["cantidad_disponible"]), 
                                           color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                            bgcolor=tema.SUCCESS_COLOR,
                            border_radius=12,
                            padding=ft.padding.symmetric(horizontal=8, vertical=2)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(producto["nombre"], color=tema.TEXT_COLOR, size=12),
                    ft.Row([
                        ft.Icon(ft.Icons.LOCATION_ON, size=14, color=tema.SECONDARY_TEXT_COLOR),
                        ft.Text(f"{producto['almacen_actual']} → {producto['ubicacion_actual']}", 
                               color=tema.SECONDARY_TEXT_COLOR, size=11)
                    ])
                ], spacing=5),
                padding=10,
                width=340,
                on_click=seleccionar_producto  # Mover on_click al Container
            ),
            color=tema.CARD_COLOR
        )

    # Panel de movimiento (origen y destino)
    panel_movimiento = ft.Container(
        content=ft.Text("Selecciona un producto para iniciar el movimiento", 
                       color=tema.SECONDARY_TEXT_COLOR, italic=True),
        alignment=ft.alignment.center,
        height=300,
        bgcolor=tema.CARD_COLOR,
        border_radius=tema.BORDER_RADIUS,
        padding=20
    )

    def actualizar_panel_movimiento():
        """Actualizar el panel visual de movimiento"""
        if not producto_seleccionado:
            panel_movimiento.content = ft.Text("Selecciona un producto para iniciar el movimiento", 
                                              color=tema.SECONDARY_TEXT_COLOR, italic=True)
            page.update()
            return

        # Campo cantidad a mover
        campo_cantidad = ft.TextField(
            label="Cantidad a mover",
            value="1",
            width=120,
            bgcolor=tema.INPUT_BG,
            color=tema.TEXT_COLOR,
            border_color=tema.INPUT_BORDER,
            focused_border_color=tema.PRIMARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        # Campo motivo
        campo_motivo = ft.TextField(
            label="Motivo del movimiento (opcional)",
            width=300,
            bgcolor=tema.INPUT_BG,
            color=tema.TEXT_COLOR,
            border_color=tema.INPUT_BORDER,
            focused_border_color=tema.PRIMARY_COLOR
        )

        # Crear selectores de destino
        def crear_selector_almacen(almacen):
            def seleccionar_almacen(e):
                nonlocal ubicacion_destino
                ubicacion_destino = {"almacen": almacen["nombre"], "ubicacion": "Por definir"}
                mostrar_selector_ubicacion_especifica(almacen["nombre"])

            esta_seleccionado = (ubicacion_destino and 
                               ubicacion_destino.get("almacen") == almacen["nombre"])

            return ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(almacen["icono"], color=almacen["color"], size=24),
                        ft.Text(almacen["nombre"], color=tema.TEXT_COLOR, size=12, text_align=ft.TextAlign.CENTER)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=15,
                    width=120,
                    on_click=seleccionar_almacen  # Mover on_click al Container
                ),
                color=tema.PRIMARY_COLOR if esta_seleccionado else tema.CARD_COLOR
            )

        def mostrar_selector_ubicacion_especifica(almacen_destino):
            """Mostrar campo para ubicación específica"""
            campo_ubicacion_destino = ft.TextField(
                label=f"Ubicación específica en {almacen_destino}",
                width=250,
                bgcolor=tema.INPUT_BG,
                color=tema.TEXT_COLOR,
                border_color=tema.INPUT_BORDER,
                focused_border_color=tema.PRIMARY_COLOR
            )

            def actualizar_ubicacion_destino(e):
                nonlocal ubicacion_destino
                ubicacion_destino["ubicacion"] = campo_ubicacion_destino.value

            campo_ubicacion_destino.on_change = actualizar_ubicacion_destino
            
            # Agregar campo al panel
            panel_movimiento.content.controls.append(
                ft.Container(
                    content=campo_ubicacion_destino,
                    margin=ft.margin.only(top=10)
                )
            )
            page.update()

        async def ejecutar_movimiento(e):
            """Ejecutar el movimiento del producto"""
            if not ubicacion_destino or not campo_cantidad.value:
                page.open(ft.SnackBar(
                    content=ft.Text("Completa todos los campos requeridos", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))
                return

            try:
                cantidad = int(campo_cantidad.value)
                if cantidad <= 0 or cantidad > producto_seleccionado["cantidad_disponible"]:
                    page.open(ft.SnackBar(
                        content=ft.Text("Cantidad inválida", color=tema.TEXT_COLOR),
                        bgcolor=tema.ERROR_COLOR
                    ))
                    return

                # Aquí iría la lógica de actualización en Firebase
                # Por ahora solo mostramos confirmación
                
                # Registrar en historial
                gestor_historial = GestorHistorial()
                usuario_actual = SesionManager.obtener_usuario_actual()
                
                descripcion = (f"Movió {cantidad} unidades de '{producto_seleccionado['nombre']}' "
                             f"desde {ubicacion_origen['almacen']} → {ubicacion_origen['ubicacion']} "
                             f"hacia {ubicacion_destino['almacen']} → {ubicacion_destino['ubicacion']}")
                
                await gestor_historial.agregar_actividad(
                    tipo="movimiento_producto",
                    descripcion=descripcion,
                    usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
                )

                page.open(ft.SnackBar(
                    content=ft.Text(f"✅ Movimiento registrado exitosamente", color=tema.TEXT_COLOR),
                    bgcolor=tema.SUCCESS_COLOR
                ))

                # Limpiar formulario
                limpiar_movimiento()
                await actualizar_historial()

            except ValueError:
                page.open(ft.SnackBar(
                    content=ft.Text("Cantidad debe ser un número válido", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))
            except Exception as ex:
                page.open(ft.SnackBar(
                    content=ft.Text(f"Error: {str(ex)}", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))

        def limpiar_movimiento():
            """Limpiar el formulario de movimiento"""
            nonlocal producto_seleccionado, ubicacion_origen, ubicacion_destino
            producto_seleccionado = None
            ubicacion_origen = None
            ubicacion_destino = None
            campo_busqueda_producto.value = ""
            lista_productos.controls.clear()
            panel_movimiento.content = ft.Text("Selecciona un producto para iniciar el movimiento", 
                                              color=tema.SECONDARY_TEXT_COLOR, italic=True)
            page.update()

        # Construir panel de movimiento
        panel_movimiento.content = ft.Column([
            # Información del producto seleccionado
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INVENTORY, color=tema.PRIMARY_COLOR),
                    ft.Column([
                        ft.Text(f"{producto_seleccionado['modelo']} - {producto_seleccionado['nombre']}", 
                               weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                        ft.Text(f"Disponible: {producto_seleccionado['cantidad_disponible']} unidades", 
                               color=tema.SECONDARY_TEXT_COLOR, size=12)
                    ], spacing=2)
                ], spacing=10),
                bgcolor=tema.BG_COLOR,
                padding=10,
                border_radius=8,
                border=ft.border.all(1, tema.PRIMARY_COLOR)
            ),

            # Origen (actual)
            ft.Container(
                content=ft.Column([
                    ft.Text("📍 DESDE (Ubicación actual):", weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                    ft.Text(f"{ubicacion_origen['almacen']} → {ubicacion_origen['ubicacion']}", 
                           color=tema.SECONDARY_TEXT_COLOR)
                ]),
                padding=10,
                bgcolor=tema.CARD_COLOR,
                border_radius=8
            ),

            # Flecha indicativa
            ft.Container(
                content=ft.Icon(ft.Icons.ARROW_DOWNWARD, color=tema.PRIMARY_COLOR, size=32),
                alignment=ft.alignment.center
            ),

            # Destino (selección)
            ft.Container(
                content=ft.Column([
                    ft.Text("📍 HACIA (Seleccionar destino):", weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                    ft.Text("Selecciona el almacén de destino:", color=tema.TEXT_COLOR, size=12),
                    ft.Row([
                        crear_selector_almacen(almacen) for almacen in almacenes_disponibles
                    ], spacing=10)
                ]),
                padding=10,
                bgcolor=tema.CARD_COLOR,
                border_radius=8
            ),

            # Campos de cantidad y motivo
            ft.Row([campo_cantidad, campo_motivo], spacing=10),

            # Botones de acción
            ft.Row([
                ft.ElevatedButton(
                    "✅ Ejecutar Movimiento",
                    style=ft.ButtonStyle(
                        bgcolor=tema.BUTTON_SUCCESS_BG,
                        color=tema.BUTTON_TEXT,
                        shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                    ),
                    on_click=lambda e: page.run_task(ejecutar_movimiento, e)
                ),
                ft.ElevatedButton(
                    "🔄 Limpiar",
                    style=ft.ButtonStyle(
                        bgcolor=tema.BUTTON_BG,
                        color=tema.BUTTON_TEXT,
                        shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                    ),
                    on_click=lambda e: limpiar_movimiento()
                )
            ], spacing=10)
        ], spacing=15)

        page.update()

    # Panel de historial
    historial_movimientos = ft.Column([], spacing=10)

    async def actualizar_historial():
        """Actualizar el historial de movimientos"""
        movimientos = await obtener_historial_movimientos()
        historial_movimientos.controls.clear()
        
        for movimiento in movimientos:
            historial_movimientos.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.SWAP_HORIZ, color=tema.PRIMARY_COLOR, size=20),
                                ft.Text(f"{movimiento['modelo']} - {movimiento['producto']}", 
                                       weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                                ft.Text(movimiento['fecha'], color=tema.SECONDARY_TEXT_COLOR, size=11)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(f"📦 Cantidad: {movimiento['cantidad']}", color=tema.TEXT_COLOR, size=12),
                            ft.Text(f"📍 {movimiento['origen']}", color=tema.SECONDARY_TEXT_COLOR, size=11),
                            ft.Text(f"📍 {movimiento['destino']}", color=tema.SECONDARY_TEXT_COLOR, size=11),
                            ft.Text(f"👤 {movimiento['usuario']} | {movimiento['motivo']}", 
                                   color=tema.SECONDARY_TEXT_COLOR, size=10, italic=True)
                        ], spacing=3),
                        padding=12
                    ),
                    color=tema.CARD_COLOR
                )
            )
        
        page.update()

    # Conectar evento de búsqueda
    campo_busqueda_producto.on_change = lambda e: page.run_task(buscar_productos, e)

    # Construir vista principal
    def construir_vista_movimientos():
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SWAP_HORIZ, color=tema.PRIMARY_COLOR, size=32),
                        ft.Text("Movimientos de Productos", size=28, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                    ]),
                    width=ancho_ventana * 0.9,
                    bgcolor=tema.CARD_COLOR,
                    padding=20,
                    alignment=ft.alignment.center,
                    border_radius=tema.BORDER_RADIUS,
                ),

                # Separador
                ft.Container(height=3, bgcolor=tema.DIVIDER_COLOR, margin=ft.margin.only(bottom=20, top=5)),

                # Contenido principal en dos columnas
                ft.Row([
                    # Columna izquierda: Búsqueda y movimiento
                    ft.Container(
                        content=ft.Column([
                            # Búsqueda de productos
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("🔍 Buscar Producto", weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                                    campo_busqueda_producto,
                                    ft.Column(
                                        controls=[lista_productos],
                                        height=200,
                                        scroll=ft.ScrollMode.AUTO
                                    )
                                ]),
                                bgcolor=tema.CARD_COLOR,
                                padding=15,
                                border_radius=tema.BORDER_RADIUS,
                                margin=ft.margin.only(bottom=10)
                            ),

                            # Panel de movimiento
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("🚚 Configurar Movimiento", weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                                    panel_movimiento
                                ]),
                                bgcolor=tema.CARD_COLOR,
                                padding=15,
                                border_radius=tema.BORDER_RADIUS
                            )
                        ]),
                        width=ancho_ventana * 0.55,
                        expand=True
                    ),

                    # Columna derecha: Historial
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📋 Historial de Movimientos", weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                            ft.Column(
                                controls=[historial_movimientos],
                                height=600,
                                scroll=ft.ScrollMode.AUTO
                            )
                        ]),
                        bgcolor=tema.CARD_COLOR,
                        padding=15,
                        border_radius=tema.BORDER_RADIUS,
                        width=ancho_ventana * 0.35,
                        expand=True
                    )
                ], spacing=20)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
            ),
            padding=ft.padding.only(bottom=40),
            bgcolor=tema.BG_COLOR
        )

    # Cargar datos iniciales
    await actualizar_historial()
    
    # Mostrar vista
    contenido.content = construir_vista_movimientos()
    page.update()
