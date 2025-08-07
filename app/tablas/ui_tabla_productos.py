import flet as ft
from app.utils.temas import GestorTemas
from app.crud_productos.delete_producto import on_eliminar_producto_click
from app.crud_productos.edit_producto import on_click_editar_producto
import asyncio

# Variables globales para referencias
actualizar_tabla_callback = None
productos_seleccionados = []  # Variable global para mantener estado

def toggle_seleccion_todas_productos(seleccionar_todas, productos):
    """Seleccionar o deseleccionar todos los productos"""
    global productos_seleccionados
    if seleccionar_todas:
        productos_seleccionados = [producto.get('firebase_id', '') for producto in productos if producto.get('firebase_id')]
        print(f"✅ DEBUG: Seleccionados TODOS los productos. IDs: {productos_seleccionados}")
    else:
        productos_seleccionados.clear()
        print(f"❌ DEBUG: Deseleccionados TODOS los productos. Lista vacía.")
    
    print(f"🔄 Toggle selección todas - Estado: {seleccionar_todas}, Total seleccionados: {len(productos_seleccionados)}")

def set_actualizar_tabla_callback(callback):
    """Establecer referencia a la función de actualización de tabla"""
    global actualizar_tabla_callback
    actualizar_tabla_callback = callback

def crear_boton_eliminar(producto_id, page, actualizar_tabla_productos):
    tema = GestorTemas.obtener_tema()
    return ft.IconButton(
        ft.Icons.DELETE,
        icon_color=tema.ERROR_COLOR,
        on_click=lambda e: on_eliminar_producto_click(page, producto_id, actualizar_tabla_productos),
        tooltip="Eliminar Producto",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
        )
    )
    
def crear_boton_editar(producto_id, page, actualizar_tabla_productos):
    from app.crud_productos.edit_producto import on_click_editar_producto
    tema = GestorTemas.obtener_tema()
    
    async def editar_handler(e):
        await on_click_editar_producto(page, producto_id, actualizar_tabla_productos)
    
    return ft.IconButton(
        ft.Icons.EDIT,
        icon_color=tema.PRIMARY_COLOR,
        on_click=editar_handler,
        tooltip="Editar Producto",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
        )
    )

def mostrar_tabla_productos(page, productos, actualizar_tabla_productos=None, contenido=None):
    tema = GestorTemas.obtener_tema()
    global productos_seleccionados  # Usar variable global
    
    # Configurar callback global
    if actualizar_tabla_productos:
        set_actualizar_tabla_callback(actualizar_tabla_productos)
    
    # Estado para el ordenamiento
    orden_actual = {"columna": 0, "ascendente": True}  # Estado del ordenamiento
    
    # Función auxiliar para obtener modelo de forma segura
    def obtener_modelo_seguro(producto):
        try:
            modelo = producto.get('modelo', '')
            return str(modelo).lower() if modelo is not None else ''
        except:
            return ''
    
    # Aplicar ordenamiento inicial
    productos_mostrar = sorted(productos, key=obtener_modelo_seguro)
    
    # Función para reordenar y actualizar tabla
    def aplicar_ordenamiento():
        nonlocal productos_mostrar
        if orden_actual["columna"] == 0:  # Columna modelo
            productos_mostrar = sorted(productos, key=obtener_modelo_seguro, reverse=not orden_actual["ascendente"])
            print(f"✅ Aplicando ordenamiento: {'ascendente' if orden_actual['ascendente'] else 'descendente'}")
            
            # Para ordenamiento SÍ necesitamos reconstruir la tabla para mostrar el nuevo orden
            if actualizar_tabla_callback:
                page.run_task(actualizar_tabla_callback)
            else:
                page.update()
    
    # Función para manejar ordenamiento
    def ordenar_productos(e):
        print(f"🔀 DEBUG: Ordenamiento solicitado - Columna: {e.column_index}, Ascendente: {e.ascending}")
        if e.column_index == 1:  # Columna modelo (ajustado porque checkbox está en índice 0)
            orden_actual["columna"] = e.column_index
            orden_actual["ascendente"] = e.ascending
            aplicar_ordenamiento()
    
    # Función para eliminar productos seleccionados
    async def eliminar_productos_seleccionados():
        print(f"🗑️ DEBUG: Función eliminar_productos_seleccionados llamada")
        print(f"🗑️ DEBUG: productos_seleccionados actual: {productos_seleccionados}")
        print(f"🗑️ DEBUG: Cantidad a eliminar: {len(productos_seleccionados)}")
        
        if not productos_seleccionados:
            print("⚠️ DEBUG: No hay productos seleccionados, mostrando SnackBar")
            page.open(ft.SnackBar(
                content=ft.Text("No hay productos seleccionados", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return
        
        # Mostrar diálogo de confirmación
        def confirmar_eliminacion(e):
            page.close(dialogo_confirmacion)
            page.run_task(procesar_eliminacion_multiple)
        
        def cancelar_eliminacion(e):
            page.close(dialogo_confirmacion)
        
        dialogo_confirmacion = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación", color=tema.TEXT_COLOR),
            content=ft.Text(f"¿Está seguro que desea eliminar {len(productos_seleccionados)} producto(s)?", color=tema.TEXT_COLOR),
            bgcolor=tema.CARD_COLOR,
            actions=[
                ft.TextButton("Cancelar", style=ft.ButtonStyle(color=tema.TEXT_SECONDARY), on_click=cancelar_eliminacion),
                ft.TextButton("Eliminar", style=ft.ButtonStyle(color=tema.ERROR_COLOR), on_click=confirmar_eliminacion),
            ],
            modal=True,
        )
        page.open(dialogo_confirmacion)
    
    async def procesar_eliminacion_multiple():
        # Mostrar AlertDialog de progreso
        mensaje_cargando = ft.AlertDialog(
            title=ft.Text("Eliminando productos", color=tema.TEXT_COLOR),
            bgcolor=tema.CARD_COLOR,
            content=ft.Container(
                content=ft.Row(
                    controls=[
                        ft.ProgressRing(width=16, height=16, stroke_width=2, color=tema.PRIMARY_COLOR),
                        ft.Text(f"Eliminando {len(productos_seleccionados)} productos...", color=tema.TEXT_COLOR)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                padding=ft.Padding(15, 10, 15, 10),
            ),
            modal=True,
        )
        
        page.open(mensaje_cargando)
        page.update()
        await asyncio.sleep(1.0)  # Tiempo mínimo para visibilidad
        
        try:
            from conexiones.firebase import db
            from app.utils.historial import GestorHistorial
            from app.funciones.sesiones import SesionManager
            
            eliminados = 0
            errores = 0
            
            print(f"🗑️ DEBUG: Iniciando eliminación de {len(productos_seleccionados)} productos")
            print(f"🗑️ DEBUG: IDs a eliminar: {productos_seleccionados}")
            
            for producto_id in productos_seleccionados:
                try:
                    print(f"🗑️ DEBUG: Eliminando producto con ID: {producto_id}")
                    db.collection('productos').document(producto_id).delete()
                    eliminados += 1
                    print(f"✅ DEBUG: Producto {producto_id} eliminado exitosamente")
                    
                    # Delay para mostrar progreso
                    if eliminados % 5 == 0:
                        await asyncio.sleep(0.1)
                        
                except Exception as e:
                    print(f"❌ DEBUG: Error eliminando producto {producto_id}: {e}")
                    errores += 1
            
            # Registrar en historial
            gestor_historial = GestorHistorial()
            usuario_actual = SesionManager.obtener_usuario_actual()
            
            await gestor_historial.agregar_actividad(
                tipo="eliminar_productos_multiple",
                descripcion=f"Eliminó {eliminados} productos (Errores: {errores})",
                usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
            )
            
            # Limpiar selección
            productos_seleccionados.clear()
            
            # Mensaje de éxito
            mensaje_exito = ft.AlertDialog(
                title=ft.Text(f"Productos eliminados: {eliminados}", color=tema.TEXT_COLOR),
                bgcolor=tema.CARD_COLOR,
                actions=[ft.TextButton("Aceptar", 
                                       style=ft.ButtonStyle(color=tema.PRIMARY_COLOR),
                                       on_click=lambda e: page.close(mensaje_exito))],
                modal=True,
            )
            
            await asyncio.sleep(0.5)  # Tiempo antes de cerrar
            page.close(mensaje_cargando)
            page.open(mensaje_exito)
            
            # Actualizar tabla con datos frescos desde Firebase
            if actualizar_tabla_productos:
                await actualizar_tabla_productos(forzar_refresh=True)  # Forzar refresh desde Firebase
                
        except Exception as e:
            page.close(mensaje_cargando)
            page.open(ft.SnackBar(
                content=ft.Text(f"Error al eliminar productos: {e}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
    
    # Función para manejar selección de productos (igual que en ubicaciones)
    def manejar_seleccion_producto(e, producto_id):
        global productos_seleccionados  # Usar variable global
        print(f"🔍 DEBUG: Selección cambiada - Producto: {producto_id}, Estado: {e.control.value}")
        if e.control.value:  # Checkbox marcado
            if producto_id not in productos_seleccionados:
                productos_seleccionados.append(producto_id)
                print(f"✅ Producto agregado a selección. ID: {producto_id}, Total: {len(productos_seleccionados)}")
        else:  # Checkbox desmarcado
            if producto_id in productos_seleccionados:
                productos_seleccionados.remove(producto_id)
                print(f"❌ Producto removido de selección. ID: {producto_id}, Total: {len(productos_seleccionados)}")
        
        print(f"🔍 DEBUG: Estado actual productos_seleccionados: {productos_seleccionados}")
        
        # Actualizar visibilidad del botón
        actualizar_boton_eliminar()
        
        # Solo actualizar la página, igual que en ubicaciones
        page.update()
    
    # Función para actualizar el botón de eliminación
    def actualizar_boton_eliminar():
        print(f"🔄 Actualizando botón eliminar. Productos seleccionados: {len(productos_seleccionados)}")
        if len(productos_seleccionados) > 0:
            boton_eliminar_multiple.text = f"Eliminar {len(productos_seleccionados)} Seleccionados"
            boton_eliminar_multiple.visible = True
        else:
            boton_eliminar_multiple.text = "Eliminar Seleccionados"
            boton_eliminar_multiple.visible = False
        boton_eliminar_multiple.update()
    
    def on_checkbox_principal_changed(e):
        """Manejar cambio del checkbox principal (seleccionar/deseleccionar todas)"""
        toggle_seleccion_todas_productos(e.control.value, productos)
        # Actualizar todos los checkboxes individuales
        for fila in tabla.rows:
            checkbox_individual = fila.cells[0].content.content
            checkbox_individual.value = e.control.value
        
        # Actualizar visibilidad del botón
        actualizar_boton_eliminar()
        page.update()

    def on_checkbox_individual_changed(e, producto_id):
        """Manejar cambio de checkbox individual"""
        manejar_seleccion_producto(e, producto_id)
        
        # Actualizar estado del checkbox principal
        total_productos = len([p for p in productos if p.get('firebase_id')])
        seleccionados = len(productos_seleccionados)
        
        if seleccionados == 0:
            checkbox_principal.value = False
        elif seleccionados == total_productos:
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
    
    # Crear una tabla para mostrar los productos
    altura_tabla = max(300, (page.window.height or 800) - 350)
    ancho_tabla = max(800, (page.window.width or 1200) - 400)
    tabla = ft.DataTable(
        border=ft.border.all(1, tema.TABLE_BORDER),
        sort_column_index=1, # Columna por defecto para ordenar (ahora será la 1 porque agregamos checkbox)
        border_radius=tema.BORDER_RADIUS, # Bordes redondeados
        sort_ascending=True, # Orden ascendente por defecto
        heading_row_color=tema.TABLE_HEADER_BG,  # Color de la fila de encabezado
        heading_row_height=50, # Altura de la fila de encabezado
        data_row_color={ft.ControlState.HOVERED: tema.TABLE_HOVER}, # Color de la fila al pasar el mouse
        show_checkbox_column=False, # Usar checkbox manual como en ubicaciones
        divider_thickness=0, # Grosor del divisor
        column_spacing=50, # Espaciado entre columnas
        columns=[
            ft.DataColumn(
                ft.Container(
                    content=checkbox_principal,
                    width=50,
                    alignment=ft.alignment.center
                ), 
                heading_row_alignment=ft.CrossAxisAlignment.CENTER
            ),  # Columna checkbox con checkbox principal
            ft.DataColumn(
                ft.Text("Modelo", color=tema.TEXT_COLOR), 
                on_sort=lambda e: ordenar_productos(e), 
                heading_row_alignment=ft.CrossAxisAlignment.CENTER
            ),
            ft.DataColumn(ft.Text("Tipo", color=tema.TEXT_COLOR), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Nombre", color=tema.TEXT_COLOR), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Precio", color=tema.TEXT_COLOR), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Cantidad", color=tema.TEXT_COLOR), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Opciones", color=tema.TEXT_COLOR), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    # Checkbox manual (como en ubicaciones)
                    ft.DataCell(
                        ft.Container(
                            content=ft.Checkbox(
                                value=producto.get('firebase_id', '') in productos_seleccionados,
                                on_change=lambda e, producto_id=producto.get('firebase_id', ''): on_checkbox_individual_changed(e, producto_id),
                                fill_color=tema.PRIMARY_COLOR
                            ),
                            width=50,
                            alignment=ft.alignment.center
                        )
                    ),
                    ft.DataCell(ft.Text(str(producto.get('modelo')), color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(producto.get('tipo'), color=tema.TEXT_COLOR)),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(producto.get('nombre'), color=tema.TEXT_COLOR),
                            width=300  # Ajusta este valor según lo que necesites
                        )
                    ),
                    ft.DataCell(ft.Text(str(producto.get('precio')), color=tema.TEXT_COLOR)),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(str(producto.get('cantidad')), color=tema.TEXT_COLOR),
                            alignment=ft.alignment.center,  # Centrar el texto
                        )
                    ),
                    ft.DataCell(
                        ft.Row(
                            controls=[
                                crear_boton_editar(producto.get('firebase_id', ''), page, actualizar_tabla_productos),
                                crear_boton_eliminar(producto.get('firebase_id', ''), page, actualizar_tabla_productos),
                            ],
                            spacing=10
                        )
                    )
                ],
                selected=False,  # Como en ubicaciones
            ) for producto in productos_mostrar  # Usar productos_mostrar en lugar de productos
        ],
        width=ancho_tabla,  # Ancho responsivo
    )
    
    # Botón para eliminar productos seleccionados
    boton_eliminar_multiple = ft.ElevatedButton(
        text="Eliminar Seleccionados",
        icon=ft.Icon(ft.Icons.DELETE_SWEEP),
        style=ft.ButtonStyle(
            bgcolor=tema.ERROR_COLOR,
            color=tema.BUTTON_TEXT,
            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
        ),
        on_click=lambda e: page.run_task(eliminar_productos_seleccionados),
        visible=False  # Inicialmente oculto
    )
    
    scroll_vertical = ft.Column([
        ft.Container(
            content=ft.Row([boton_eliminar_multiple], alignment=ft.MainAxisAlignment.END),
            padding=ft.Padding(0, 0, 0, 10)
        ),
        tabla
    ], scroll=True, height=altura_tabla)  # Altura responsiva
    return ft.Container(
        content=scroll_vertical,
        alignment=ft.alignment.center,
        bgcolor=tema.CARD_COLOR,
        border_radius=tema.BORDER_RADIUS,
        padding=10,
    )