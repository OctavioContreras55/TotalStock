import flet as ft
from app.utils.temas import GestorTemas
import asyncio

def crear_boton_editar(ubicacion_id, page, actualizar_tabla_ubicaciones):
    """Crear botón de editar ubicación"""
    tema = GestorTemas.obtener_tema()
    
    async def editar_ubicacion(e):
        # TODO: Implementar edición de ubicación
        page.open(ft.SnackBar(
            content=ft.Text(f"Editar ubicación {ubicacion_id} - Pendiente", color=tema.TEXT_COLOR),
            bgcolor=tema.WARNING_COLOR
        ))
    
    return ft.IconButton(
        ft.Icons.EDIT_LOCATION,
        icon_color=tema.PRIMARY_COLOR,
        on_click=lambda e: print(f"Editar ubicación: {ubicacion_id}"),
        tooltip="Editar ubicación"
    )

def crear_boton_eliminar(ubicacion_id, page, actualizar_tabla_ubicaciones):
    """Crear botón de eliminar ubicación"""
    tema = GestorTemas.obtener_tema()
    
    def eliminar_ubicacion(e):
        # TODO: Implementar eliminación de ubicación
        page.open(ft.SnackBar(
            content=ft.Text(f"Eliminar ubicación {ubicacion_id} - Pendiente", color=tema.TEXT_COLOR),
            bgcolor=tema.WARNING_COLOR
        ))
    
    return ft.IconButton(
        ft.Icons.DELETE,
        icon_color=tema.ERROR_COLOR,
        on_click=eliminar_ubicacion,
        tooltip="Eliminar ubicación"
    )

def crear_boton_mover(ubicacion_id, page, actualizar_tabla_ubicaciones):
    """Crear botón para mover producto a otra ubicación"""
    tema = GestorTemas.obtener_tema()
    
    def mover_producto(e):
        # TODO: Implementar movimiento de producto
        page.open(ft.SnackBar(
            content=ft.Text(f"Mover producto {ubicacion_id} - Pendiente", color=tema.TEXT_COLOR),
            bgcolor=tema.WARNING_COLOR
        ))
    
    return ft.IconButton(
        ft.Icons.MOVE_UP,
        icon_color=tema.SUCCESS_COLOR,
        on_click=mover_producto,
        tooltip="Mover a otra ubicación"
    )

def mostrar_tabla_ubicaciones(page, ubicaciones, actualizar_tabla_ubicaciones=None):
    """Mostrar tabla de ubicaciones con almacén y ubicación específica"""
    tema = GestorTemas.obtener_tema()
    
    # Dimensiones responsivas
    ancho_ventana = page.window.width or 1200
    alto_ventana = page.window.height or 800
    
    # Cálculos responsivos para la tabla
    if ancho_ventana < 1200:
        ancho_tabla = ancho_ventana * 0.85
        altura_tabla = alto_ventana * 0.5
    elif ancho_ventana < 1600:
        ancho_tabla = ancho_ventana * 0.88
        altura_tabla = alto_ventana * 0.55
    else:
        ancho_tabla = ancho_ventana * 0.9
        altura_tabla = alto_ventana * 0.6

    if not ubicaciones:
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.LOCATION_OFF, size=64, color=tema.SECONDARY_TEXT_COLOR),
                ft.Text("No hay ubicaciones para mostrar", size=18, color=tema.SECONDARY_TEXT_COLOR),
                ft.Text("Agrega ubicaciones o importa desde Excel", size=14, color=tema.SECONDARY_TEXT_COLOR)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10),
            alignment=ft.alignment.center,
            bgcolor=tema.CARD_COLOR,
            border_radius=tema.BORDER_RADIUS,
            padding=40,
            width=ancho_tabla,
            height=altura_tabla
        )

    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Modelo", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Producto", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Almacén", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Ubicación Específica", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Cantidad", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Acciones", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    # Modelo
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(str(ubicacion.get('modelo', 'N/A')), color=tema.TEXT_COLOR, weight=ft.FontWeight.W_500),
                            padding=ft.padding.symmetric(horizontal=8, vertical=4)
                        )
                    ),
                    
                    # Nombre del producto
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(ubicacion.get('nombre', 'Sin nombre'), color=tema.TEXT_COLOR),
                            width=250,  # Ancho fijo para nombres largos
                            padding=ft.padding.symmetric(horizontal=8, vertical=4)
                        )
                    ),
                    
                    # Almacén
                    ft.DataCell(
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(
                                    ft.Icons.WAREHOUSE,
                                    color=tema.PRIMARY_COLOR if ubicacion.get('almacen') == 'Almacén Principal' 
                                          else tema.SUCCESS_COLOR if ubicacion.get('almacen') == 'Almacén Secundario'
                                          else tema.WARNING_COLOR,
                                    size=16
                                ),
                                ft.Text(ubicacion.get('almacen', 'Sin asignar'), color=tema.TEXT_COLOR, size=12)
                            ], spacing=5),
                            padding=ft.padding.symmetric(horizontal=8, vertical=4)
                        )
                    ),
                    
                    # Ubicación específica
                    ft.DataCell(
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.LOCATION_ON, color=tema.SECONDARY_TEXT_COLOR, size=14),
                                ft.Text(
                                    ubicacion.get('ubicacion', 'Sin ubicación'), 
                                    color=tema.TEXT_COLOR, 
                                    size=12,
                                    width=200
                                )
                            ], spacing=5),
                            padding=ft.padding.symmetric(horizontal=8, vertical=4)
                        )
                    ),
                    
                    # Cantidad
                    ft.DataCell(
                        ft.Container(
                            content=ft.Container(
                                content=ft.Text(
                                    str(ubicacion.get('cantidad', 0)), 
                                    color=ft.Colors.WHITE,
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER
                                ),
                                bgcolor=tema.ERROR_COLOR if ubicacion.get('cantidad', 0) < 5 
                                        else tema.WARNING_COLOR if ubicacion.get('cantidad', 0) < 20 
                                        else tema.SUCCESS_COLOR,
                                border_radius=12,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                alignment=ft.alignment.center
                            ),
                            alignment=ft.alignment.center,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4)
                        )
                    ),
                    
                    # Acciones
                    ft.DataCell(
                        ft.Row([
                            crear_boton_mover(ubicacion.get('firebase_id', ''), page, actualizar_tabla_ubicaciones),
                            crear_boton_editar(ubicacion.get('firebase_id', ''), page, actualizar_tabla_ubicaciones),
                            crear_boton_eliminar(ubicacion.get('firebase_id', ''), page, actualizar_tabla_ubicaciones),
                        ],
                        spacing=5
                        )
                    )
                ],
                selected=False,
                on_select_changed=lambda e: print(f"Ubicación seleccionada: {e.data}"),
            ) for ubicacion in ubicaciones
        ],
        width=ancho_tabla,
    )
    
    scroll_vertical = ft.Column([tabla], scroll=True, height=altura_tabla)
    
    return ft.Container(
        content=scroll_vertical,
        alignment=ft.alignment.center,
        bgcolor=tema.CARD_COLOR,
        border_radius=tema.BORDER_RADIUS,
        padding=15,
        border=ft.border.all(1, tema.DIVIDER_COLOR)
    )
