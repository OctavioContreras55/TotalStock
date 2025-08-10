import flet as ft
from app.utils.temas import GestorTemas
import asyncio

# Variables globales para la selección múltiple
ubicaciones_seleccionadas = set()
checkbox_principal = None
page_ref = None
actualizar_tabla_callback = None

def set_page_reference(page):
    """Establecer referencia a la página para actualizar UI"""
    global page_ref
    page_ref = page

def set_actualizar_tabla_callback(callback):
    """Establecer referencia a la función de actualización de tabla"""
    global actualizar_tabla_callback
    actualizar_tabla_callback = callback

def toggle_seleccion_ubicacion(ubicacion_id, seleccionado):
    """Toggle selección de una ubicación específica"""
    if seleccionado:
        ubicaciones_seleccionadas.add(ubicacion_id)
    else:
        ubicaciones_seleccionadas.discard(ubicacion_id)
    
    # Actualizar visibilidad del botón eliminar
    _actualizar_boton_eliminar()
    
    # Solo actualizar la página, no la tabla completa para evitar conflictos
    if page_ref:
        page_ref.update()

def toggle_seleccion_todas(seleccionar_todas, ubicaciones):
    """Seleccionar o deseleccionar todas las ubicaciones"""
    global ubicaciones_seleccionadas
    if seleccionar_todas:
        ubicaciones_seleccionadas = {ubicacion.get('firebase_id') or ubicacion.get('id', '') for ubicacion in ubicaciones if ubicacion.get('firebase_id') or ubicacion.get('id')}
    else:
        ubicaciones_seleccionadas.clear()
    
    # Actualizar visibilidad del botón eliminar
    _actualizar_boton_eliminar()

def _actualizar_boton_eliminar():
    """Actualizar visibilidad del botón eliminar seleccionados"""
    global page_ref, ubicaciones_seleccionadas
    if page_ref:
        try:
            # Buscar el botón eliminar seleccionados
            btn = _buscar_boton_eliminar(page_ref)
            if btn:
                # Mostrar/ocultar según las selecciones
                btn.visible = len(ubicaciones_seleccionadas) > 0
                # Actualizar el texto con la cantidad
                if len(ubicaciones_seleccionadas) > 0:
                    btn.content.controls[1].value = f"Eliminar ({len(ubicaciones_seleccionadas)})"
                else:
                    btn.content.controls[1].value = "Eliminar Selec."
                page_ref.update()
        except Exception as e:
            print(f"Error al actualizar botón eliminar: {e}")

def _buscar_boton_eliminar(control):
    """Buscar recursivamente el botón eliminar seleccionados"""
    if hasattr(control, 'data') and control.data == "btn_eliminar_seleccionados":
        return control
    
    if hasattr(control, 'content'):
        resultado = _buscar_boton_eliminar(control.content)
        if resultado:
            return resultado
    
    if hasattr(control, 'controls'):
        for subcontrol in control.controls:
            resultado = _buscar_boton_eliminar(subcontrol)
            if resultado:
                return resultado
    
    return None

async def eliminar_ubicaciones_seleccionadas(page, actualizar_tabla_ubicaciones):
    """Eliminar múltiples ubicaciones seleccionadas"""
    global ubicaciones_seleccionadas
    tema = GestorTemas.obtener_tema()
    
    if not ubicaciones_seleccionadas:
        page.open(ft.SnackBar(
            content=ft.Text("[WARN] No hay ubicaciones seleccionadas", color=tema.TEXT_COLOR),
            bgcolor=tema.WARNING_COLOR
        ))
        return
    
    # Diálogo de confirmación
    def confirmar_eliminacion(e):
        page.close(dialogo_confirmacion)
        page.run_task(procesar_eliminacion)
    
    def cancelar_eliminacion(e):
        page.close(dialogo_confirmacion)
    
    async def procesar_eliminacion():
        # Mostrar progreso INMEDIATAMENTE
        mensaje_progreso = ft.AlertDialog(
            title=ft.Text("Eliminando ubicaciones", color=tema.TEXT_COLOR),
            bgcolor=tema.CARD_COLOR,
            content=ft.Container(
                content=ft.Row([
                    ft.ProgressRing(width=18, height=18, stroke_width=2, color=tema.PRIMARY_COLOR),
                    ft.Text(f"Eliminando {len(ubicaciones_seleccionadas)} ubicaciones...", color=tema.TEXT_COLOR)
                ], spacing=12, alignment=ft.MainAxisAlignment.CENTER),
                padding=ft.Padding(15, 10, 15, 10),
                width=320
            ),
            modal=True,
        )
        page.open(mensaje_progreso)
        page.update()
        
        # Delay mínimo para que el AlertDialog sea visible
        await asyncio.sleep(1.0)  # 1 segundo mínimo
        
        try:
            from conexiones.firebase import db
            from app.utils.historial import GestorHistorial
            from app.funciones.sesiones import SesionManager
            
            eliminadas = 0
            errores = 0
            
            for ubicacion_id in ubicaciones_seleccionadas:
                try:
                    db.collection('ubicaciones').document(ubicacion_id).delete()
                    eliminadas += 1
                    
                    # Pequeño delay para hacer visible el progreso
                    if eliminadas % 5 == 0:  # Cada 5 ubicaciones
                        await asyncio.sleep(0.1)  # 100ms para mostrar progreso
                        
                except Exception as e:
                    print(f"Error al eliminar ubicación {ubicacion_id}: {e}")
                    errores += 1
            
            # Registrar en historial
            gestor_historial = GestorHistorial()
            usuario_actual = SesionManager.obtener_usuario_actual()
            
            await gestor_historial.agregar_actividad(
                tipo="eliminar_ubicacion",
                descripcion=f"Eliminó {eliminadas} ubicaciones masivamente (Errores: {errores})",
                usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
            )
            
            # Limpiar selecciones
            ubicaciones_seleccionadas.clear()
            
            # Delay mínimo antes de cerrar para asegurar visibilidad
            await asyncio.sleep(0.5)  # Medio segundo adicional
            
            # Cerrar progreso y mostrar resultado
            page.close(mensaje_progreso)
            
            if eliminadas > 0:
                # Invalidar cache y actualizar tabla
                from app.utils.cache_firebase import cache_firebase
                cache_firebase.invalidar_cache_ubicaciones()
                
                await actualizar_tabla_ubicaciones(forzar_refresh=True)
                
                mensaje = f"Ubicaciones eliminadas: {eliminadas}"
                if errores > 0:
                    mensaje += f" (Errores: {errores})"
                
                # Mensaje de éxito con AlertDialog
                mensaje_exito = ft.AlertDialog(
                    title=ft.Text(mensaje, color=tema.TEXT_COLOR),
                    bgcolor=tema.CARD_COLOR,
                    actions=[ft.TextButton("Aceptar", 
                                           style=ft.ButtonStyle(color=tema.PRIMARY_COLOR),
                                           on_click=lambda e: page.close(mensaje_exito))],
                    modal=True,
                )
                page.open(mensaje_exito)
            else:
                page.open(ft.SnackBar(
                    content=ft.Text("[ERROR] No se pudieron eliminar las ubicaciones", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))
                
        except Exception as e:
            print(f"Error en eliminación masiva: {e}")
            page.close(mensaje_progreso)
            page.open(ft.SnackBar(
                content=ft.Text(f"Error: {str(e)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
    
    dialogo_confirmacion = ft.AlertDialog(
        title=ft.Text("Confirmar eliminación", color=tema.TEXT_COLOR, size=16),
        bgcolor=tema.CARD_COLOR,
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.WARNING, color=tema.WARNING_COLOR, size=18),
                    ft.Text(f"¿Eliminar {len(ubicaciones_seleccionadas)} ubicaciones?", 
                           color=tema.TEXT_COLOR, size=13)
                ], spacing=6),
                ft.Text("Acción irreversible.", color=tema.TEXT_SECONDARY, size=10)
            ], spacing=8),
            padding=ft.Padding(8, 5, 8, 5),
            width=240,
            height=60
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar_eliminacion, 
                         style=ft.ButtonStyle(color=tema.TEXT_SECONDARY)),
            ft.ElevatedButton("Eliminar", on_click=confirmar_eliminacion,
                            style=ft.ButtonStyle(bgcolor=tema.ERROR_COLOR, color=tema.TEXT_COLOR))
        ],
        modal=True,
    )
    
    page.open(dialogo_confirmacion)

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
                    content=ft.Text("[ERROR] Ubicación no encontrada", color=tema.TEXT_COLOR),
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
                        content=ft.Text("[OK] Observaciones actualizadas exitosamente", color=tema.TEXT_COLOR),
                        bgcolor=tema.SUCCESS_COLOR
                    ))
                    
                    # Actualizar tabla
                    if actualizar_tabla_ubicaciones:
                        await actualizar_tabla_ubicaciones()
                        
                except Exception as error:
                    page.open(ft.SnackBar(
                        content=ft.Text(f"[ERROR] Error al guardar: {str(error)}", color=tema.TEXT_COLOR),
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
                        ft.Text("[IDEA] Para cambiar ubicación o cantidad, use la función 'Mover'", 
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
                content=ft.Text(f"[ERROR] Error: {str(error)}", color=tema.TEXT_COLOR),
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
                
                # Esperar un momento para asegurar que Firebase procese la eliminación
                await asyncio.sleep(0.2)
                
                # Invalidar cache de ubicaciones para forzar refresh
                from app.utils.cache_firebase import cache_firebase
                cache_firebase.invalidar_cache_ubicaciones()
                
                # Registrar en historial
                gestor_historial = GestorHistorial()
                usuario_actual = SesionManager.obtener_usuario_actual()
                
                await gestor_historial.agregar_actividad(
                    tipo="eliminar_ubicacion",
                    descripcion=f"Eliminó ubicación: {modelo} de {almacen}/{estanteria}",
                    usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
                )
                
                page.open(ft.SnackBar(
                    content=ft.Text("[OK] Ubicación eliminada exitosamente", color=tema.TEXT_COLOR),
                    bgcolor=tema.SUCCESS_COLOR
                ))
                
                # Actualizar tabla con refresh forzado
                if actualizar_tabla_ubicaciones:
                    await actualizar_tabla_ubicaciones(forzar_refresh=True)
            else:
                page.open(ft.SnackBar(
                    content=ft.Text("[ERROR] Ubicación no encontrada", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))
                
        except Exception as error:
            print(f"Error al eliminar ubicación: {error}")
            page.open(ft.SnackBar(
                content=ft.Text(f"[ERROR] Error al eliminar: {str(error)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
    
    return ft.IconButton(
        ft.Icons.DELETE,
        icon_color=tema.ERROR_COLOR,
        icon_size=20,
        on_click=lambda e: page.run_task(confirmar_eliminacion, e),
        tooltip="Eliminar ubicación"
    )

# def crear_boton_mover(ubicacion_id, page, actualizar_tabla_ubicaciones):
#     """Crear botón para mover producto a otra ubicación - MOVIDO A VISTA DE MOVIMIENTOS"""
#     # Esta funcionalidad se movió a la vista de Movimientos
#     pass

def mostrar_tabla_ubicaciones(page, ubicaciones, actualizar_tabla_ubicaciones=None):
    """Mostrar tabla de ubicaciones con almacén y ubicación específica + Selección múltiple"""
    global ubicaciones_seleccionadas, checkbox_principal
    tema = GestorTemas.obtener_tema()
    
    # Configurar referencias globales
    set_page_reference(page)
    if actualizar_tabla_ubicaciones:
        set_actualizar_tabla_callback(actualizar_tabla_ubicaciones)
    
    # Estado para el ordenamiento
    orden_actual = {"columna": 1, "ascendente": True}  # Columna 1 = Modelo/Tipo
    
    # Función auxiliar para obtener modelo de forma segura
    def obtener_modelo_ubicacion_seguro(ubicacion):
        try:
            modelo = ubicacion.get('modelo', '')
            return str(modelo).lower() if modelo is not None else ''
        except:
            return ''
    
    # Aplicar ordenamiento inicial
    ubicaciones_mostrar = sorted(ubicaciones, key=obtener_modelo_ubicacion_seguro)
    
    # Función para reordenar y actualizar tabla
    def aplicar_ordenamiento():
        nonlocal ubicaciones_mostrar
        if orden_actual["columna"] == 1:  # Columna modelo/tipo
            ubicaciones_mostrar = sorted(ubicaciones, key=obtener_modelo_ubicacion_seguro, reverse=not orden_actual["ascendente"])
            print(f"[OK] Aplicando ordenamiento ubicaciones: {'ascendente' if orden_actual['ascendente'] else 'descendente'}")
            if actualizar_tabla_ubicaciones:
                actualizar_tabla_ubicaciones()
    
    # Función para manejar ordenamiento
    def ordenar_ubicaciones(e):
        print(f"🔀 DEBUG UBICACIONES: Ordenamiento solicitado - Columna: {e.column_index}, Ascendente: {e.ascending}")
        if e.column_index == 1:  # Solo columna modelo/tipo
            orden_actual["columna"] = e.column_index
            orden_actual["ascendente"] = e.ascending
            aplicar_ordenamiento()
    
    # Dimensiones responsivas mejoradas
    ancho_ventana = page.window.width or 1200
    alto_ventana = page.window.height or 800
    
    # Cálculos responsivos para la tabla - Más conservadores
    if ancho_ventana < 1000:
        ancho_tabla = ancho_ventana * 0.95
        altura_tabla = alto_ventana * 0.3
        ancho_checkbox = 50
        ancho_modelo = 90
        ancho_almacen = 60
        ancho_estanteria = 70
        ancho_cantidad = 60
        ancho_fecha = 110
        ancho_observaciones = 100
        ancho_acciones = 90
    elif ancho_ventana < 1400:
        ancho_tabla = ancho_ventana * 0.92
        altura_tabla = alto_ventana * 0.4
        ancho_checkbox = 55
        ancho_modelo = 110
        ancho_almacen = 70
        ancho_estanteria = 80
        ancho_cantidad = 70
        ancho_fecha = 120
        ancho_observaciones = 130
        ancho_acciones = 100
    else:
        ancho_tabla = ancho_ventana * 0.88
        altura_tabla = alto_ventana * 0.52
        ancho_checkbox = 60
        ancho_modelo = 130
        ancho_almacen = 80
        ancho_estanteria = 90
        ancho_cantidad = 80
        ancho_fecha = 130
        ancho_observaciones = 150
        ancho_acciones = 110

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

    def on_checkbox_principal_changed(e):
        """Manejar cambio del checkbox principal (seleccionar/deseleccionar todas)"""
        toggle_seleccion_todas(e.control.value, ubicaciones)
        # Actualizar todos los checkboxes individuales
        for fila in tabla.rows:
            checkbox_individual = fila.cells[0].content.content
            checkbox_individual.value = e.control.value
        page.update()

    def on_checkbox_individual_changed(e, ubicacion_id):
        """Manejar cambio de checkbox individual"""
        toggle_seleccion_ubicacion(ubicacion_id, e.control.value)
        
        # Actualizar estado del checkbox principal
        total_ubicaciones = len([u for u in ubicaciones if u.get('firebase_id') or u.get('id')])
        seleccionadas = len(ubicaciones_seleccionadas)
        
        if seleccionadas == 0:
            checkbox_principal.value = False
        elif seleccionadas == total_ubicaciones:
            checkbox_principal.value = True
        else:
            checkbox_principal.value = None  # Estado indeterminado
        
        page.update()

    # Checkbox principal para seleccionar todas
    checkbox_principal = ft.Checkbox(
        value=False,
        on_change=on_checkbox_principal_changed,
        fill_color=tema.PRIMARY_COLOR
    )

    tabla = ft.DataTable(
        sort_column_index=1,  # Columna de modelo/tipo por defecto
        sort_ascending=True,  # Orden ascendente por defecto
        columns=[
            ft.DataColumn(
                ft.Container(
                    content=checkbox_principal,
                    width=ancho_checkbox,
                    alignment=ft.alignment.center
                ), 
                heading_row_alignment=ft.CrossAxisAlignment.CENTER
            ),
            ft.DataColumn(
                ft.Text("Modelo", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD, size=12), 
                on_sort=ordenar_ubicaciones,
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
                    # Checkbox de selección
                    ft.DataCell(
                        ft.Container(
                            content=ft.Checkbox(
                                value=(ubicacion.get('firebase_id') or ubicacion.get('id')) in ubicaciones_seleccionadas,
                                on_change=lambda e, uid=ubicacion.get('firebase_id') or ubicacion.get('id'): on_checkbox_individual_changed(e, uid),
                                fill_color=tema.PRIMARY_COLOR
                            ),
                            width=ancho_checkbox,
                            alignment=ft.alignment.center
                        )
                    ),
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
                                crear_boton_editar(ubicacion.get('firebase_id', ''), page, actualizar_tabla_ubicaciones),
                                crear_boton_eliminar(ubicacion.get('firebase_id', ''), page, actualizar_tabla_ubicaciones),
                            ],
                            spacing=8,
                            tight=True,
                            alignment=ft.MainAxisAlignment.CENTER
                            ),
                            width=ancho_acciones,
                            padding=ft.padding.symmetric(horizontal=3, vertical=4),
                            alignment=ft.alignment.center
                        )
                    )
                ],
                selected=False
            ) for ubicacion in ubicaciones_mostrar if ubicacion.get('firebase_id') or ubicacion.get('id')  # Ubicaciones con ID de Firebase o local
        ],
        width=ancho_tabla,
        column_spacing=35,  # Mejor espaciado entre columnas para aprovechar el ancho
        horizontal_lines=ft.BorderSide(width=0.5, color=tema.DIVIDER_COLOR),
        vertical_lines=ft.BorderSide(width=0.5, color=tema.DIVIDER_COLOR),
        horizontal_margin=5,  # Margen horizontal reducido
        expand_loose=True,  # Expandir de forma flexible
        expand=True,  # Expandir al máximo disponible
    )
    
    scroll_vertical = ft.Column([tabla], scroll=True, height=altura_tabla, 
                                expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    return ft.Container(
        content=scroll_vertical,
        alignment=ft.alignment.top_center,  # Alineación superior y centrada
        bgcolor=tema.CARD_COLOR,
        border_radius=tema.BORDER_RADIUS,
        padding=10,  # Padding reducido para más espacio útil
        border=ft.border.all(1, tema.DIVIDER_COLOR),
        expand=True,  # Expandir al máximo del contenedor padre
        width=None,  # Permitir que el contenedor determine el ancho automáticamente
    )
