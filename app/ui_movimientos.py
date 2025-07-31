import flet as ft
from app.utils.temas import GestorTemas
from app.utils.historial import GestorHistorial
from app.funciones.sesiones import SesionManager
from conexiones.firebase import db
import asyncio
from datetime import datetime

async def vista_movimientos(nombre_seccion, contenido, page):
    """Vista para realizar movimientos de productos entre ubicaciones y almacenes"""
    tema = GestorTemas.obtener_tema()
    
    # Estado del movimiento
    producto_seleccionado = None
    ubicacion_origen = None
    ubicacion_destino = None
    cantidad_a_mover = 0
    
    # Dimensiones responsivas
    ancho_ventana = page.window.width or 1200
    alto_ventana = page.window.height or 800

    # Lista de almacenes disponibles
    almacenes_disponibles = [
        {"id": "almacen_1", "nombre": "Almacén Principal", "icono": ft.Icons.WAREHOUSE, "color": tema.PRIMARY_COLOR},
        {"id": "almacen_2", "nombre": "Almacén Secundario", "icono": ft.Icons.STORE, "color": tema.SUCCESS_COLOR},
        {"id": "almacen_3", "nombre": "Almacén de Repuestos", "icono": ft.Icons.BUILD, "color": tema.WARNING_COLOR}
    ]

    async def buscar_productos_por_ubicacion():
        """Buscar productos con sus ubicaciones actuales"""
        try:
            # En una implementación real, esto vendría de Firebase
            return [
                {
                    "id": "prod_1",
                    "modelo": "LAP001",
                    "nombre": "Laptop Dell Inspiron",
                    "almacen_actual": "Almacén Principal",
                    "ubicacion_actual": "Estante A-3, Nivel 2",
                    "cantidad_disponible": 15
                },
                {
                    "id": "prod_2", 
                    "modelo": "MOU002",
                    "nombre": "Mouse Logitech MX",
                    "almacen_actual": "Almacén Secundario",
                    "ubicacion_actual": "Cajón B-1",
                    "cantidad_disponible": 50
                },
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
