import flet as ft
from app.utils.temas import GestorTemas
from app.utils.historial import GestorHistorial
from app.funciones.sesiones import SesionManager
from app.crud_movimientos.movimiento_inventario import crear_movimiento_inventario_dialog
from app.crud_movimientos.create_movimiento import crear_movimiento_ubicacion_dialog, obtener_movimientos_firebase
from conexiones.firebase import db
import asyncio
from datetime import datetime
from app.ui.barra_carga import vista_carga

async def vista_movimientos(nombre_seccion, contenido, page):
    """Vista para realizar y visualizar movimientos de productos"""
    from app.utils.cache_firebase import cache_firebase
    tema = GestorTemas.obtener_tema()
    
    # Variables de estado
    movimientos_actuales = []
    
    # Dimensiones responsivas
    ancho_ventana = page.window.width or 1200
    alto_ventana = page.window.height or 800
    
    async def cargar_movimientos():
        """Cargar movimientos desde Firebase con cache"""
        return await cache_firebase.obtener_movimientos()
    
    async def actualizar_tabla_movimientos(forzar_refresh=False):
        """Actualizar la tabla de movimientos"""
        nonlocal movimientos_actuales
        try:
            if not forzar_refresh:
                # Carga optimizada con cache
                contenido.content = vista_carga("Cargando movimientos...", 16)
                page.update()
            
            movimientos_actuales = await cache_firebase.obtener_movimientos(forzar_refresh=forzar_refresh)
            contenido.content = construir_vista_movimientos(movimientos_actuales)
            page.update()
            
        except Exception as e:
            print(f"Error al actualizar tabla de movimientos: {e}")
            movimientos_actuales = []
            contenido.content = construir_vista_movimientos([])
            page.update()
    
    async def mostrar_dialogo_nuevo_movimiento(e):
        """Mostrar diálogo para crear nuevo movimiento de inventario"""
        await crear_movimiento_inventario_dialog(page, lambda: actualizar_tabla_movimientos(forzar_refresh=True))
    
    async def mostrar_dialogo_movimiento_ubicacion(e):
        """Mostrar diálogo para crear movimiento entre ubicaciones"""
        await crear_movimiento_ubicacion_dialog(page, lambda: actualizar_tabla_movimientos(forzar_refresh=True))
    
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
            # Verificar si es string y convertir si es necesario
            if isinstance(mov, str):
                continue
                
            if not isinstance(mov, dict):
                continue
                
            # Procesar ubicaciones - pueden ser strings o dicts
            ubicacion_origen = mov.get('ubicacion_origen', 'N/A')
            ubicacion_destino = mov.get('ubicacion_destino', 'N/A')
            
            # Si es dict, extraer almacén, si es string, usar directamente
            if isinstance(ubicacion_origen, dict):
                origen_texto = f"{ubicacion_origen.get('almacen', 'N/A')}/{ubicacion_origen.get('estanteria', 'N/A')}"
            else:
                origen_texto = str(ubicacion_origen)
                
            if isinstance(ubicacion_destino, dict):
                destino_texto = f"{ubicacion_destino.get('almacen', 'N/A')}/{ubicacion_destino.get('estanteria', 'N/A')}"
            else:
                destino_texto = str(ubicacion_destino)
                
            fecha = mov.get('fecha_movimiento', '').split('T')[0] if mov.get('fecha_movimiento') else 'N/A'
            
            # Extraer nombre del usuario (puede ser string o dict)
            usuario_raw = mov.get('usuario', 'N/A')
            if isinstance(usuario_raw, dict):
                # Si es diccionario, extraer el nombre
                usuario_nombre = usuario_raw.get('nombre', usuario_raw.get('username', 'Usuario'))
            else:
                # Si es string, usar directamente
                usuario_nombre = str(usuario_raw)
            
            fila = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(mov.get('modelo', mov.get('producto_modelo', 'N/A')), color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(str(mov.get('cantidad', 0)), color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(origen_texto, color=tema.TEXT_COLOR, size=12)),
                    ft.DataCell(ft.Text(destino_texto, color=tema.TEXT_COLOR, size=12)),
                    ft.DataCell(ft.Text(mov.get('tipo', mov.get('tipo_movimiento', 'N/A')), color=tema.TEXT_COLOR, size=12)),
                    ft.DataCell(ft.Text(fecha, color=tema.TEXT_COLOR, size=12)),
                    ft.DataCell(ft.Text(usuario_nombre, color=tema.TEXT_COLOR, size=12)),
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
            column_spacing=100,  # Espaciado máximo para distribución completa del ancho
            horizontal_margin=1,  # Margen prácticamente nulo para máximo espacio
            heading_row_color=tema.CARD_COLOR,
            data_row_color={
                ft.ControlState.SELECTED: tema.SELECTED_COLOR,
                ft.ControlState.PRESSED: tema.CARD_COLOR,
            },
            width=None,  # Permitir que la tabla use todo el ancho disponible
            expand_loose=True,  # Expandir para llenar el contenedor
        )
    
    def construir_vista_movimientos(movimientos):
        """Construir vista completa de movimientos"""
        
        # Debug: Contar tipos de movimientos
        tipos_debug = {}
        for mov in movimientos:
            tipo = mov.get('tipo', 'sin_tipo')
            tipos_debug[tipo] = tipos_debug.get(tipo, 0) + 1
        print(f"[BUSCAR] DEBUG TIPOS EN UI: {tipos_debug}")
        
        # Contadores específicos
        entradas = len([m for m in movimientos if m.get('tipo') == 'entrada_inventario'])
        salidas = len([m for m in movimientos if m.get('tipo') == 'salida_inventario'])
        ajustes = len([m for m in movimientos if m.get('tipo') == 'ajuste_inventario'])
        traslados = len([m for m in movimientos if m.get('tipo') == 'movimiento_ubicacion'])
        
        print(f"🔢 CONTADORES: Entradas={entradas}, Salidas={salidas}, Ajustes={ajustes}, Traslados={traslados}")
        
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
                    width=ancho_ventana * 0.95,  # Más ancho para el header
                    bgcolor=tema.CARD_COLOR,
                    padding=15,  # Padding reducido del header
                    alignment=ft.alignment.center,
                    border_radius=tema.BORDER_RADIUS,
                ),
                
                # Separador
                ft.Container(
                    height=3,
                    bgcolor=tema.DIVIDER_COLOR,
                    margin=ft.margin.only(bottom=15, top=5),  # Margin reducido
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
                        width=180,
                        height=45,
                        tooltip="Movimientos de inventario: Entradas, Salidas, Ajustes"
                    ),
                    ft.ElevatedButton(
                        "Movimiento de Ubicaciones",
                        icon=ft.Icons.COMPARE_ARROWS,
                        style=ft.ButtonStyle(
                            bgcolor=tema.BUTTON_BG,
                            color=tema.BUTTON_TEXT,
                            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                        ),
                        on_click=mostrar_dialogo_movimiento_ubicacion,
                        width=220,
                        height=45,
                        tooltip="Traslados físicos entre almacenes y estanterías"
                    ),
                    ft.ElevatedButton(
                        "Actualizar",
                        icon=ft.Icons.REFRESH,
                        style=ft.ButtonStyle(
                            bgcolor=tema.BUTTON_BG,
                            color=tema.BUTTON_TEXT,
                            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                        ),
                        on_click=lambda e: page.run_task(actualizar_tabla_movimientos, True),  # Forzar refresh
                        width=150,
                        height=45
                    ),
                ], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
                
                # Estadísticas por tipo de movimiento - Más separados y centrados
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Entradas", color=tema.TEXT_SECONDARY, size=14, weight=ft.FontWeight.W_500),
                                ft.Text(str(len([m for m in movimientos if m.get('tipo') == 'entrada_inventario'])), 
                                       color=tema.SUCCESS_COLOR, size=28, weight=ft.FontWeight.BOLD)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            bgcolor=tema.CARD_COLOR,
                            padding=20,
                            border_radius=tema.BORDER_RADIUS,
                            width=180,
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=5,
                                color=ft.Colors.BLACK12,
                                offset=ft.Offset(0, 2)
                            )
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Salidas", color=tema.TEXT_SECONDARY, size=14, weight=ft.FontWeight.W_500),
                                ft.Text(str(len([m for m in movimientos if m.get('tipo') == 'salida_inventario'])), 
                                       color=tema.WARNING_COLOR, size=28, weight=ft.FontWeight.BOLD)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            bgcolor=tema.CARD_COLOR,
                            padding=20,
                            border_radius=tema.BORDER_RADIUS,
                            width=180,
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=5,
                                color=ft.Colors.BLACK12,
                                offset=ft.Offset(0, 2)
                            )
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Ajustes", color=tema.TEXT_SECONDARY, size=14, weight=ft.FontWeight.W_500),
                                ft.Text(str(len([m for m in movimientos if m.get('tipo') == 'ajuste_inventario'])), 
                                       color=tema.PRIMARY_COLOR, size=28, weight=ft.FontWeight.BOLD)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            bgcolor=tema.CARD_COLOR,
                            padding=20,
                            border_radius=tema.BORDER_RADIUS,
                            width=180,
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=5,
                                color=ft.Colors.BLACK12,
                                offset=ft.Offset(0, 2)
                            )
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Traslados", color=tema.TEXT_SECONDARY, size=14, weight=ft.FontWeight.W_500),
                                ft.Text(str(len([m for m in movimientos if m.get('tipo') == 'movimiento_ubicacion'])), 
                                       color=tema.DIVIDER_COLOR, size=28, weight=ft.FontWeight.BOLD)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            bgcolor=tema.CARD_COLOR,
                            padding=20,
                            border_radius=tema.BORDER_RADIUS,
                            width=180,
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=5,
                                color=ft.Colors.BLACK12,
                                offset=ft.Offset(0, 2)
                            )
                        ),
                    ], spacing=40, alignment=ft.MainAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    margin=ft.margin.symmetric(vertical=25)
                ),
                
                # Tabla de movimientos - Contenedor optimizado centrado y pegado arriba
                ft.Container(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Historial de Movimientos", 
                                       size=20, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                                ft.Text(f"({len(movimientos)} registros)", 
                                       size=14, color=tema.TEXT_SECONDARY)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Container(height=10),  # Separación reducida
                            ft.Container(
                                content=ft.Column([
                                    construir_tabla_movimientos(movimientos)
                                ], scroll=ft.ScrollMode.AUTO, expand=True),
                                bgcolor=tema.CARD_COLOR,
                                padding=15,  # Padding interno aumentado para mejor espaciado del contenido
                                border_radius=tema.BORDER_RADIUS,
                                border=ft.border.all(1, tema.DIVIDER_COLOR),
                                expand=True,  # Expandir para usar todo el espacio disponible
                                shadow=ft.BoxShadow(
                                    spread_radius=1,
                                    blur_radius=8,
                                    color=ft.Colors.BLACK12,
                                    offset=ft.Offset(0, 3)
                                ),
                                width=ancho_ventana * 0.95,  # Container hijo usa casi todo el ancho disponible
                                alignment=ft.alignment.top_center  # Alineación superior y centrada
                            )
                        ], spacing=5),
                        width=ancho_ventana * 0.995,  # Ancho máximo para usar todo el espacio disponible
                        padding=ft.padding.symmetric(horizontal=12, vertical=15),  # Padding aumentado para mejor espaciado
                        margin=ft.margin.only(top=5, bottom=40),  # Márgenes más pequeños para contenedor compacto
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
                    width=ancho_ventana * 0.995,  # Container padre usa casi todo el ancho disponible
                    height=alto_ventana * 0.57  # Altura más pequeña para mejor visualización
                )
            ], spacing=10),  # Espaciado reducido para vista más compacta
            padding=10,  # Padding reducido para contenedor más compacto
            expand=True,
            height=alto_ventana - 100  # Altura más pequeña para mejor visualización
        )
    
    # Cargar datos iniciales con cache
    movimientos_iniciales = await cache_firebase.obtener_movimientos()
    movimientos_actuales = movimientos_iniciales
    contenido.content = construir_vista_movimientos(movimientos_actuales)
    page.update()
