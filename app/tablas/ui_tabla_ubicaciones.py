import flet as ft
from app.utils.temas import GestorTemas
import asyncio

def crear_tabla_ubicaciones(ubicaciones, page, actualizar_tabla_ubicaciones):
    """Crear tabla de ubicaciones para usar en búsquedas y filtros"""
    return mostrar_tabla_ubicaciones(page, ubicaciones, actualizar_tabla_ubicaciones)

def crear_boton_editar(ubicacion_id, page, actualizar_tabla_ubicaciones):
    """Crear botón de editar ubicación"""
    tema = GestorTemas.obtener_tema()
    
    async def editar_ubicacion(e):
        """Editar ubicación - mostrar diálogo de edición"""
        try:
            from conexiones.firebase import db
            from datetime import datetime
            
            # Obtener datos actuales de la ubicación
            doc_ref = db.collection('ubicaciones').document(ubicacion_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                page.open(ft.SnackBar(
                    content=ft.Text("❌ Ubicación no encontrada", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))
                return
            
            ubicacion_data = doc.to_dict()
            
            # Solo campo de observaciones (editable)
            campo_observaciones = ft.TextField(
                label="Observaciones",
                value=ubicacion_data.get('observaciones', ''),
                width=350,
                multiline=True,
                max_lines=4,
                bgcolor=tema.INPUT_BG,
                color=tema.TEXT_COLOR,
                border_color=tema.INPUT_BORDER,
                helper_text="Edite las observaciones de esta ubicación"
            )
            
            # Campos de solo lectura para mostrar información
            info_producto = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.INVENTORY_2, color=tema.PRIMARY_COLOR, size=16),
                        ft.Text(f"Producto: {ubicacion_data.get('modelo', 'N/A')}", 
                               color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD)
                    ], spacing=8),
                    ft.Row([
                        ft.Icon(ft.Icons.WAREHOUSE, color=tema.WARNING_COLOR, size=16),
                        ft.Text(f"Almacén: {ubicacion_data.get('almacen', 'N/A')}", 
                               color=tema.TEXT_COLOR)
                    ], spacing=8),
                    ft.Row([
                        ft.Icon(ft.Icons.SHELVES, color=tema.SUCCESS_COLOR, size=16),
                        ft.Text(f"Estantería: {ubicacion_data.get('estanteria', 'N/A')}", 
                               color=tema.TEXT_COLOR)
                    ], spacing=8),
                    ft.Row([
                        ft.Icon(ft.Icons.NUMBERS, color=tema.PRIMARY_COLOR, size=16),
                        ft.Text(f"Cantidad: {ubicacion_data.get('cantidad', 1)}", 
                               color=tema.TEXT_COLOR)
                    ], spacing=8),
                ], spacing=8),
                bgcolor=tema.CARD_COLOR,
                padding=15,
                border_radius=tema.BORDER_RADIUS,
                border=ft.border.all(1, tema.DIVIDER_COLOR)
            )
            
            async def guardar_cambios(e):
                try:
                    # Solo actualizar observaciones
                    doc_ref.update({
                        'observaciones': campo_observaciones.value.strip(),
                        'fecha_modificacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    page.close(dialogo_editar)
                    page.open(ft.SnackBar(
                        content=ft.Text("✅ Observaciones actualizadas exitosamente", color=tema.TEXT_COLOR),
                        bgcolor=tema.SUCCESS_COLOR
                    ))
                    
                    # Actualizar tabla
                    if actualizar_tabla_ubicaciones:
                        await actualizar_tabla_ubicaciones()
                        
                except Exception as error:
                    page.open(ft.SnackBar(
                        content=ft.Text(f"❌ Error al guardar: {str(error)}", color=tema.TEXT_COLOR),
                        bgcolor=tema.ERROR_COLOR
                    ))
            
            # Diálogo de edición
            dialogo_editar = ft.AlertDialog(
                title=ft.Text(f"Editar Observaciones: {ubicacion_data.get('modelo', '')}", color=tema.TEXT_COLOR),
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Información de la ubicación:", 
                               color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD, size=14),
                        info_producto,
                        ft.Container(height=15),
                        ft.Text("Editar observaciones:", 
                               color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD, size=14),
                        campo_observaciones,
                        ft.Container(height=5),
                        ft.Text("💡 Para cambiar ubicación o cantidad, use la función 'Mover'", 
                               color=tema.TEXT_SECONDARY, size=11, italic=True),
                    ], spacing=10),
                    width=400,
                    height=450,
                    padding=ft.Padding(15, 15, 15, 15)
                ),
                bgcolor=tema.CARD_COLOR,
                actions=[
                    ft.ElevatedButton(
                        "Guardar Observaciones",
                        style=ft.ButtonStyle(
                            bgcolor=tema.SUCCESS_COLOR,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                        ),
                        on_click=guardar_cambios
                    ),
                    ft.TextButton(
                        "Cancelar",
                        style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                        on_click=lambda e: page.close(dialogo_editar)
                    ),
                ],
                modal=True,
            )
            
            page.open(dialogo_editar)
            
        except Exception as error:
            print(f"Error al editar ubicación: {error}")
            page.open(ft.SnackBar(
                content=ft.Text(f"❌ Error: {str(error)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
    
    return ft.IconButton(
        ft.Icons.EDIT_LOCATION,
        icon_color=tema.PRIMARY_COLOR,
        icon_size=20,
        on_click=lambda e: page.run_task(editar_ubicacion, e),
        tooltip="Editar ubicación"
    )

def crear_boton_eliminar(ubicacion_id, page, actualizar_tabla_ubicaciones):
    """Crear botón de eliminar ubicación"""
    tema = GestorTemas.obtener_tema()
    
    async def confirmar_eliminacion(e):
        """Mostrar diálogo de confirmación antes de eliminar"""
        def eliminar_definitivo(e):
            page.close(dialogo_confirmacion)
            page.run_task(eliminar_ubicacion_firebase, ubicacion_id)
        
        def cancelar_eliminacion(e):
            page.close(dialogo_confirmacion)
        
        dialogo_confirmacion = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación", color=tema.TEXT_COLOR),
            content=ft.Text("¿Está seguro de que desea eliminar esta ubicación? Esta acción no se puede deshacer.", 
                           color=tema.TEXT_COLOR),
            bgcolor=tema.CARD_COLOR,
            actions=[
                ft.ElevatedButton(
                    "Eliminar",
                    style=ft.ButtonStyle(
                        bgcolor=tema.ERROR_COLOR,
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                    ),
                    on_click=eliminar_definitivo
                ),
                ft.TextButton(
                    "Cancelar",
                    style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                    on_click=cancelar_eliminacion
                ),
            ],
            modal=True,
        )
        page.open(dialogo_confirmacion)
    
    async def eliminar_ubicacion_firebase(ubicacion_id):
        """Eliminar ubicación de Firebase"""
        try:
            from conexiones.firebase import db
            from app.utils.historial import GestorHistorial
            from app.funciones.sesiones import SesionManager
            
            # Obtener datos de la ubicación antes de eliminar para el historial
            doc_ref = db.collection('ubicaciones').document(ubicacion_id)
            doc = doc_ref.get()
            if doc.exists:
                ubicacion_data = doc.to_dict()
                modelo = ubicacion_data.get('modelo', 'Sin modelo')
                almacen = ubicacion_data.get('almacen', 'Sin almacén')
                estanteria = ubicacion_data.get('estanteria', 'Sin estantería')
                
                # Eliminar de Firebase
                doc_ref.delete()
                
                # Registrar en historial
                gestor_historial = GestorHistorial()
                usuario_actual = SesionManager.obtener_usuario_actual()
                
                await gestor_historial.agregar_actividad(
                    tipo="eliminar_ubicacion",
                    descripcion=f"Eliminó ubicación: {modelo} de {almacen}/{estanteria}",
                    usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
                )
                
                page.open(ft.SnackBar(
                    content=ft.Text("✅ Ubicación eliminada exitosamente", color=tema.TEXT_COLOR),
                    bgcolor=tema.SUCCESS_COLOR
                ))
                
                # Actualizar tabla
                if actualizar_tabla_ubicaciones:
                    await actualizar_tabla_ubicaciones()
            else:
                page.open(ft.SnackBar(
                    content=ft.Text("❌ Ubicación no encontrada", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))
                
        except Exception as error:
            print(f"Error al eliminar ubicación: {error}")
            page.open(ft.SnackBar(
                content=ft.Text(f"❌ Error al eliminar: {str(error)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
    
    return ft.IconButton(
        ft.Icons.DELETE,
        icon_color=tema.ERROR_COLOR,
        icon_size=20,
        on_click=lambda e: page.run_task(confirmar_eliminacion, e),
        tooltip="Eliminar ubicación"
    )

def crear_boton_mover(ubicacion_id, page, actualizar_tabla_ubicaciones):
    """Crear botón para mover producto a otra ubicación"""
    tema = GestorTemas.obtener_tema()
    
    async def mover_producto(e):
        """Mover producto a otra ubicación"""
        try:
            from conexiones.firebase import db
            from datetime import datetime
            
            # Obtener datos actuales de la ubicación
            doc_ref = db.collection('ubicaciones').document(ubicacion_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                page.open(ft.SnackBar(
                    content=ft.Text("❌ Ubicación no encontrada", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))
                return
            
            ubicacion_data = doc.to_dict()
            
            # Campos para nueva ubicación
            campo_nuevo_almacen = ft.TextField(
                label="Nuevo Almacén",
                width=300,
                bgcolor=tema.INPUT_BG,
                color=tema.TEXT_COLOR,
                border_color=tema.INPUT_BORDER,
                helper_text="Almacén de destino"
            )
            
            campo_nueva_estanteria = ft.TextField(
                label="Nueva Estantería",
                width=300,
                bgcolor=tema.INPUT_BG,
                color=tema.TEXT_COLOR,
                border_color=tema.INPUT_BORDER,
                helper_text="Estantería de destino"
            )
            
            campo_cantidad_mover = ft.TextField(
                label="Cantidad a mover",
                value=str(ubicacion_data.get('cantidad', 1)),
                width=150,
                keyboard_type=ft.KeyboardType.NUMBER,
                bgcolor=tema.INPUT_BG,
                color=tema.TEXT_COLOR,
                border_color=tema.INPUT_BORDER,
                helper_text=f"Máximo: {ubicacion_data.get('cantidad', 1)}"
            )
            
            async def ejecutar_movimiento(e):
                try:
                    cantidad_a_mover = int(campo_cantidad_mover.value) if campo_cantidad_mover.value else 0
                    cantidad_actual = ubicacion_data.get('cantidad', 1)
                    
                    if cantidad_a_mover <= 0 or cantidad_a_mover > cantidad_actual:
                        page.open(ft.SnackBar(
                            content=ft.Text(f"❌ Cantidad inválida. Máximo disponible: {cantidad_actual}", color=tema.TEXT_COLOR),
                            bgcolor=tema.ERROR_COLOR
                        ))
                        return
                    
                    # Crear nueva ubicación
                    nueva_ubicacion = {
                        "modelo": ubicacion_data.get('modelo', ''),
                        "nombre_producto": ubicacion_data.get('nombre_producto', ''),
                        "tipo_producto": ubicacion_data.get('tipo_producto', ''),
                        "almacen": campo_nuevo_almacen.value.strip(),
                        "estanteria": campo_nueva_estanteria.value.strip(),
                        "cantidad": cantidad_a_mover,
                        "observaciones": f"Movido desde {ubicacion_data.get('almacen', '')}/{ubicacion_data.get('estanteria', '')}",
                        "fecha_asignacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "usuario_asignacion": ubicacion_data.get('usuario_asignacion', 'Sistema')
                    }
                    
                    # Guardar nueva ubicación
                    db.collection("ubicaciones").add(nueva_ubicacion)
                    
                    # Actualizar ubicación original
                    nueva_cantidad = cantidad_actual - cantidad_a_mover
                    if nueva_cantidad > 0:
                        doc_ref.update({
                            'cantidad': nueva_cantidad,
                            'fecha_modificacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                    else:
                        # Si se movió todo, eliminar ubicación original
                        doc_ref.delete()
                    
                    # Registrar en historial
                    from app.utils.historial import GestorHistorial
                    from app.funciones.sesiones import SesionManager
                    
                    gestor_historial = GestorHistorial()
                    usuario_actual = SesionManager.obtener_usuario_actual()
                    
                    await gestor_historial.agregar_actividad(
                        tipo="mover_ubicacion",
                        descripcion=f"Movió {cantidad_a_mover}x {ubicacion_data.get('modelo', '')} de {ubicacion_data.get('almacen', '')}/{ubicacion_data.get('estanteria', '')} → {campo_nuevo_almacen.value}/{campo_nueva_estanteria.value}",
                        usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
                    )
                    
                    page.close(dialogo_mover)
                    page.open(ft.SnackBar(
                        content=ft.Text("✅ Producto movido exitosamente", color=tema.TEXT_COLOR),
                        bgcolor=tema.SUCCESS_COLOR
                    ))
                    
                    # Actualizar tabla
                    if actualizar_tabla_ubicaciones:
                        await actualizar_tabla_ubicaciones()
                        
                except Exception as error:
                    page.open(ft.SnackBar(
                        content=ft.Text(f"❌ Error al mover: {str(error)}", color=tema.TEXT_COLOR),
                        bgcolor=tema.ERROR_COLOR
                    ))
            
            # Diálogo de movimiento
            dialogo_mover = ft.AlertDialog(
                title=ft.Text(f"Mover Producto: {ubicacion_data.get('modelo', '')}", color=tema.TEXT_COLOR),
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(f"Ubicación actual: {ubicacion_data.get('almacen', '')} / {ubicacion_data.get('estanteria', '')}", 
                               color=tema.TEXT_SECONDARY, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Cantidad disponible: {ubicacion_data.get('cantidad', 1)}", 
                               color=tema.TEXT_COLOR),
                        ft.Container(height=15),
                        ft.Text("Nueva ubicación:", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD),
                        campo_nuevo_almacen,
                        campo_nueva_estanteria,
                        campo_cantidad_mover,
                    ], spacing=15),
                    width=350,
                    height=350,
                    padding=ft.Padding(15, 15, 15, 15)
                ),
                bgcolor=tema.CARD_COLOR,
                actions=[
                    ft.ElevatedButton(
                        "Mover Producto",
                        style=ft.ButtonStyle(
                            bgcolor=tema.WARNING_COLOR,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                        ),
                        on_click=ejecutar_movimiento
                    ),
                    ft.TextButton(
                        "Cancelar",
                        style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                        on_click=lambda e: page.close(dialogo_mover)
                    ),
                ],
                modal=True,
            )
            
            page.open(dialogo_mover)
            
        except Exception as error:
            print(f"Error al mover producto: {error}")
            page.open(ft.SnackBar(
                content=ft.Text(f"❌ Error: {str(error)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
    
    return ft.IconButton(
        ft.Icons.MOVE_UP,
        icon_color=tema.SUCCESS_COLOR,
        icon_size=20,
        on_click=lambda e: page.run_task(mover_producto, e),
        tooltip="Mover a otra ubicación"
    )

def mostrar_tabla_ubicaciones(page, ubicaciones, actualizar_tabla_ubicaciones=None):
    """Mostrar tabla de ubicaciones con almacén y ubicación específica"""
    tema = GestorTemas.obtener_tema()
    
    # Dimensiones responsivas mejoradas
    ancho_ventana = page.window.width or 1200
    alto_ventana = page.window.height or 800
    
    # Cálculos responsivos para la tabla - Más conservadores
    if ancho_ventana < 1000:
        ancho_tabla = ancho_ventana * 0.95
        altura_tabla = alto_ventana * 0.5
        ancho_modelo = 100
        ancho_almacen = 70
        ancho_estanteria = 80
        ancho_cantidad = 70
        ancho_fecha = 120
        ancho_observaciones = 120
        ancho_acciones = 100
    elif ancho_ventana < 1400:
        ancho_tabla = ancho_ventana * 0.92
        altura_tabla = alto_ventana * 0.55
        ancho_modelo = 120
        ancho_almacen = 80
        ancho_estanteria = 90
        ancho_cantidad = 80
        ancho_fecha = 130
        ancho_observaciones = 150
        ancho_acciones = 110
    else:
        ancho_tabla = ancho_ventana * 0.88
        altura_tabla = alto_ventana * 0.6
        ancho_modelo = 140
        ancho_almacen = 90
        ancho_estanteria = 100
        ancho_cantidad = 90
        ancho_fecha = 140
        ancho_observaciones = 170
        ancho_acciones = 120

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
            ft.DataColumn(
                ft.Text("Tipo", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD, size=12), 
                heading_row_alignment=ft.CrossAxisAlignment.CENTER
            ),
            ft.DataColumn(
                ft.Text("Almacén", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD, size=12), 
                heading_row_alignment=ft.CrossAxisAlignment.CENTER
            ),
            ft.DataColumn(
                ft.Text("Estantería", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD, size=12), 
                heading_row_alignment=ft.CrossAxisAlignment.CENTER
            ),
            ft.DataColumn(
                ft.Text("Cantidad", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD, size=12), 
                heading_row_alignment=ft.CrossAxisAlignment.CENTER
            ),
            ft.DataColumn(
                ft.Text("Fecha", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD, size=12), 
                heading_row_alignment=ft.CrossAxisAlignment.CENTER
            ),
            ft.DataColumn(
                ft.Text("Observaciones", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD, size=12), 
                heading_row_alignment=ft.CrossAxisAlignment.CENTER
            ),
            ft.DataColumn(
                ft.Text("Acciones", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD, size=12), 
                heading_row_alignment=ft.CrossAxisAlignment.CENTER
            ),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    # Modelo
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                str(ubicacion.get('modelo', 'N/A')), 
                                color=tema.TEXT_COLOR, 
                                weight=ft.FontWeight.W_500,
                                size=11,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            width=ancho_modelo,
                            padding=ft.padding.symmetric(horizontal=5, vertical=4)
                        )
                    ),
                    
                    # Almacén
                    ft.DataCell(
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(
                                    ft.Icons.WAREHOUSE,
                                    color=tema.PRIMARY_COLOR,
                                    size=14
                                ),
                                ft.Text(
                                    ubicacion.get('almacen', 'N/A'), 
                                    color=tema.TEXT_COLOR, 
                                    size=11
                                )
                            ], spacing=3),
                            width=ancho_almacen,
                            padding=ft.padding.symmetric(horizontal=5, vertical=4)
                        )
                    ),
                    
                    # Estantería
                    ft.DataCell(
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.SHELVES, color=tema.SECONDARY_TEXT_COLOR, size=12),
                                ft.Text(
                                    ubicacion.get('estanteria', 'N/A'), 
                                    color=tema.TEXT_COLOR, 
                                    size=11,
                                    overflow=ft.TextOverflow.ELLIPSIS
                                )
                            ], spacing=3),
                            width=ancho_estanteria,
                            padding=ft.padding.symmetric(horizontal=5, vertical=4)
                        )
                    ),
                    
                    # Cantidad
                    ft.DataCell(
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.INVENTORY_2, color=tema.WARNING_COLOR, size=12),
                                ft.Text(
                                    str(ubicacion.get('cantidad', '1')), 
                                    color=tema.TEXT_COLOR, 
                                    size=11,
                                    weight=ft.FontWeight.W_500
                                )
                            ], spacing=3),
                            width=ancho_cantidad,
                            padding=ft.padding.symmetric(horizontal=5, vertical=4)
                        )
                    ),
                    
                    # Fecha de asignación (formato más corto)
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                ubicacion.get('fecha_asignacion', 'N/A')[:10] if ubicacion.get('fecha_asignacion') else 'N/A', 
                                color=tema.TEXT_COLOR, 
                                size=10,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            width=ancho_fecha,
                            padding=ft.padding.symmetric(horizontal=5, vertical=4)
                        )
                    ),
                    
                    # Observaciones
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                ubicacion.get('observaciones', 'N/A'), 
                                color=tema.SECONDARY_TEXT_COLOR, 
                                size=10,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            width=ancho_observaciones,
                            padding=ft.padding.symmetric(horizontal=5, vertical=4)
                        )
                    ),
                    
                    # Acciones
                    ft.DataCell(
                        ft.Container(
                            content=ft.Row([
                                crear_boton_mover(ubicacion.get('firebase_id', ''), page, actualizar_tabla_ubicaciones),
                                crear_boton_editar(ubicacion.get('firebase_id', ''), page, actualizar_tabla_ubicaciones),
                                crear_boton_eliminar(ubicacion.get('firebase_id', ''), page, actualizar_tabla_ubicaciones),
                            ],
                            spacing=4,
                            tight=True,
                            alignment=ft.MainAxisAlignment.CENTER
                            ),
                            width=ancho_acciones,
                            padding=ft.padding.symmetric(horizontal=3, vertical=4),
                            alignment=ft.alignment.center
                        )
                    )
                ],
                selected=False,
                on_select_changed=lambda e: print(f"Ubicación seleccionada: {e.data}"),
            ) for ubicacion in ubicaciones
        ],
        width=ancho_tabla,
        column_spacing=5,  # Reducir espacio entre columnas
        horizontal_lines=ft.BorderSide(width=0.5, color=tema.DIVIDER_COLOR),
        vertical_lines=ft.BorderSide(width=0.5, color=tema.DIVIDER_COLOR),
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
