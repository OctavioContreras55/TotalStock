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
                        on_click=lambda e: page.run_task(actualizar_tabla_movimientos),
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
                            bgcolor=tema.BG_COLOR,
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
