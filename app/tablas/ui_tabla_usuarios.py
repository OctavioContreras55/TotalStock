import flet as ft
from app.crud_usuarios.delete_usuarios import mensaje_confirmacion
from app.utils.temas import GestorTemas
import asyncio

# Variables globales para la selección múltiple
usuarios_seleccionados = set()
checkbox_principal = None
page_ref = None
actualizar_tabla_callback = None
boton_eliminar_ref = None  # Nueva referencia directa al botón

def set_page_reference(page):
    """Establecer referencia a la página para actualizar UI"""
    global page_ref
    page_ref = page

def set_boton_eliminar_reference(boton):
    """Establecer referencia directa al botón eliminar"""
    global boton_eliminar_ref
    boton_eliminar_ref = boton

def set_actualizar_tabla_callback(callback):
    """Establecer referencia a la función de actualización de tabla"""
    global actualizar_tabla_callback
    actualizar_tabla_callback = callback
    print(f"📋 Callback de actualización establecido: {callback is not None}")

def toggle_seleccion_usuario(usuario_id, seleccionado):
    """Toggle selección de un usuario específico"""
    if seleccionado:
        usuarios_seleccionados.add(usuario_id)
    else:
        usuarios_seleccionados.discard(usuario_id)
    
    # Actualizar visibilidad del botón eliminar
    _actualizar_boton_eliminar()
    
    # Solo actualizar la página, no la tabla completa para evitar conflictos
    if page_ref:
        page_ref.update()

def toggle_seleccion_todas(seleccionar_todas, usuarios):
    """Seleccionar o deseleccionar todos los usuarios"""
    global usuarios_seleccionados
    if seleccionar_todas:
        usuarios_seleccionados = {usuario.get('firebase_id') or usuario.get('id', '') for usuario in usuarios if usuario.get('firebase_id') or usuario.get('id')}
    else:
        usuarios_seleccionados.clear()
    
    # Actualizar visibilidad del botón eliminar
    _actualizar_boton_eliminar()

def _actualizar_boton_eliminar():
    """Actualizar visibilidad del botón eliminar seleccionados"""
    global page_ref, usuarios_seleccionados, boton_eliminar_ref
    if page_ref and boton_eliminar_ref:
        try:
            nueva_visibilidad = len(usuarios_seleccionados) > 0
            if boton_eliminar_ref.visible != nueva_visibilidad:  # Solo actualizar si cambia
                boton_eliminar_ref.visible = nueva_visibilidad
                print(f"🔴 Botón eliminar actualizado: visible={nueva_visibilidad}, seleccionados={len(usuarios_seleccionados)}")
                page_ref.update()
        except Exception as e:
            print(f"❌ Error al actualizar botón eliminar: {e}")
    else:
        print("⚠️ Referencia al botón eliminar no encontrada")

async def eliminar_usuarios_seleccionados(page, callback_actualizar=None):
    """Eliminar usuarios seleccionados"""
    global usuarios_seleccionados, actualizar_tabla_callback
    if not usuarios_seleccionados:
        return
    
    # Usar el callback proporcionado o el global
    callback_a_usar = callback_actualizar or actualizar_tabla_callback
    
    try:
        # Crear diálogo de confirmación
        texto_confirmacion = f"¿Estás seguro de que deseas eliminar {len(usuarios_seleccionados)} usuario(s) seleccionado(s)?"
        
        async def confirmar_eliminacion(e):
            try:
                from conexiones.firebase import db
                from app.utils.cache_firebase import cache_firebase
                
                # Eliminar usuarios de Firebase
                usuarios_eliminados = len(usuarios_seleccionados)
                ids_eliminados = list(usuarios_seleccionados.copy())  # Copia para uso posterior
                
                for usuario_id in usuarios_seleccionados:
                    doc_ref = db.collection('usuarios').document(usuario_id)
                    doc_ref.delete()
                    print(f"Usuario {usuario_id} eliminado de Firebase")
                
                # Invalidar cache para futuras consultas
                cache_firebase._cache_usuarios = []
                cache_firebase._ultimo_update_usuarios = None
                print("🗑️ Cache invalidado para futuras consultas")
                
                # Limpiar selección
                usuarios_seleccionados.clear()
                
                # Cerrar diálogo
                page.close(dialogo)
                
                # Mostrar snackbar de éxito
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"{usuarios_eliminados} usuario(s) eliminado(s) exitosamente"),
                        bgcolor=ft.Colors.GREEN_400
                    )
                )
                
                # ACTUALIZACIÓN AUTOMÁTICA: Recargar tabla después de eliminar
                if callback_a_usar:
                    print(f"⚡ Ejecutando actualización automática después de eliminar {usuarios_eliminados} usuarios")
                    try:
                        # Llamar al callback para actualizar la tabla
                        await callback_a_usar(True)  # Forzar refresh desde Firebase
                    except Exception as e:
                        print(f"Error en actualización automática: {e}")
                        page.update()
                else:
                    print("⚠️ No hay callback de actualización disponible")
                    page.update()
                
            except Exception as e:
                print(f"Error al eliminar usuarios: {e}")
                page.close(dialogo)
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Error al eliminar usuarios: {str(e)}"),
                        bgcolor=ft.Colors.RED_400
                    )
                )
        
        def cancelar_eliminacion(e):
            page.close(dialogo)
        
        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(texto_confirmacion),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar_eliminacion),
                ft.TextButton("Eliminar", on_click=lambda e: page.run_task(confirmar_eliminacion, e)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.open(dialogo)
        
    except Exception as e:
        print(f"Error en eliminar_usuarios_seleccionados: {e}")
        page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(f"Error: {str(e)}"),
                bgcolor=ft.Colors.RED_400
            )
        )

def mostrar_tabla_usuarios(page, usuarios, actualizar_tabla=None):
    """Mostrar tabla de usuarios con selección múltiple"""
    global usuarios_seleccionados, checkbox_principal
    tema = GestorTemas.obtener_tema()
    
    # Configurar referencias globales
    set_page_reference(page)
    if actualizar_tabla:
        set_actualizar_tabla_callback(actualizar_tabla)
    
    # Calcular altura responsiva basada en el tamaño de pantalla
    altura_tabla = max(300, (page.window.height or 800) - 350)
    ancho_tabla = max(800, (page.window.width or 1200) - 400)
    
    # Calcular anchos de columnas responsivos
    ancho_checkbox = 50
    ancho_id = 100
    ancho_nombre = 200
    ancho_tipo = 150
    ancho_acciones = 120
    
    # Función para manejar el checkbox principal
    def on_checkbox_principal_changed(e):
        seleccionar_todas = e.control.value
        toggle_seleccion_todas(seleccionar_todas, usuarios)
        
        # Forzar actualización del valor del checkbox principal
        if 'checkbox_principal' in locals():
            checkbox_principal.value = seleccionar_todas
        
        print(f"🔲 Checkbox principal cambiado a: {seleccionar_todas}, seleccionados: {len(usuarios_seleccionados)}")
        
        # Actualizar la tabla completa para reflejar los cambios
        if actualizar_tabla:
            page.run_task(actualizar_tabla)
        else:
            page.update()
    
    # Función para manejar checkboxes individuales
    def on_checkbox_individual_changed(e, usuario_id):
        toggle_seleccion_usuario(usuario_id, e.control.value)
        
        # Actualizar checkbox principal basado en la selección actual
        total_usuarios = len([u for u in usuarios if u.get('firebase_id') or u.get('id')])
        if len(usuarios_seleccionados) == 0:
            checkbox_principal.value = False
        elif len(usuarios_seleccionados) == total_usuarios:
            checkbox_principal.value = True
        else:
            checkbox_principal.value = False
        
        # Actualizar botón eliminar
        _actualizar_boton_eliminar()
        
        if page_ref:
            page_ref.update()
    
    # Checkbox principal - Definir DESPUÉS de la función
    checkbox_principal = ft.Checkbox(
        value=len(usuarios_seleccionados) == len([u for u in usuarios if u.get('firebase_id') or u.get('id')]) and len(usuarios) > 0,
        on_change=on_checkbox_principal_changed,
        fill_color=tema.PRIMARY_COLOR
    )
    
    print(f"🔲 Checkbox principal creado con valor inicial: {checkbox_principal.value}")
    
    # Crear una tabla para mostrar los usuarios
    tabla = ft.DataTable(
        border=ft.border.all(1, tema.TABLE_BORDER),
        sort_column_index=1,  # Columna nombre (ahora es índice 1, ya que quitamos ID)
        border_radius=tema.BORDER_RADIUS,
        sort_ascending=True,
        heading_row_color=tema.TABLE_HEADER_BG,
        heading_row_height=50,
        data_row_color={ft.ControlState.HOVERED: tema.TABLE_HOVER},
        divider_thickness=0,
        column_spacing=35,  # Espaciado optimizado entre columnas
        horizontal_margin=5,  # Margen horizontal reducido
        expand_loose=True,  # Expandir de forma flexible
        expand=True,  # Expandir al máximo disponible
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
                ft.Text("Nombre", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD, size=12), 
                heading_row_alignment=ft.CrossAxisAlignment.CENTER
            ),
            ft.DataColumn(
                ft.Text("Tipo de Usuario", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD, size=12), 
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
                                value=(usuario.get('firebase_id') or usuario.get('id')) in usuarios_seleccionados,
                                on_change=lambda e, uid=usuario.get('firebase_id') or usuario.get('id'): on_checkbox_individual_changed(e, uid),
                                fill_color=tema.PRIMARY_COLOR
                            ),
                            width=ancho_checkbox,
                            alignment=ft.alignment.center
                        )
                    ),
                    # Nombre
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                usuario.get('nombre', 'Sin nombre'), 
                                color=tema.TEXT_COLOR,
                                size=12
                            ),
                            width=ancho_nombre,
                            alignment=ft.alignment.center_left
                        )
                    ),
                    # Tipo de Usuario
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                "Administrador" if usuario.get('es_admin', False) else "Usuario", 
                                color=tema.TEXT_COLOR,
                                size=12
                            ),
                            width=ancho_tipo,
                            alignment=ft.alignment.center_left
                        )
                    ),
                    # Acciones
                    ft.DataCell(
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.IconButton(
                                        ft.Icons.EDIT, 
                                        icon_color=tema.PRIMARY_COLOR, 
                                        on_click=lambda e, uid=usuario.get('firebase_id', ''): editar_usuario(uid, page, lambda: page.run_task(actualizar_tabla) if actualizar_tabla else None),
                                        tooltip="Editar usuario"
                                    ),
                                    crear_boton_eliminar(page, usuario.get('firebase_id', ''), actualizar_tabla),
                                ],
                                spacing=5,
                                alignment=ft.MainAxisAlignment.CENTER
                            ),
                            width=ancho_acciones,
                            alignment=ft.alignment.center
                        )
                    ),
                ],
                selected=False
            ) for usuario in usuarios if usuario.get('firebase_id') or usuario.get('id')  # Solo usuarios con ID
        ],
        width=ancho_tabla,
    )
    
    scroll_vertical = ft.Column([tabla], scroll=True, height=altura_tabla, 
                                expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    return ft.Container(
        content=scroll_vertical,
        alignment=ft.alignment.top_center,  # Alineación superior y centrada
        bgcolor=tema.CARD_COLOR,
        border_radius=tema.BORDER_RADIUS,
        padding=10,  # Padding interno optimizado
        border=ft.border.all(1, tema.DIVIDER_COLOR),
        expand=True,  # Expandir al máximo del contenedor padre
        width=None,  # Permitir que el contenedor determine el ancho automáticamente
    )

def crear_boton_eliminar(page, uid, actualizar_tabla=None):
    tema = GestorTemas.obtener_tema()
    return ft.IconButton(
        ft.Icons.DELETE,
        icon_color=tema.ERROR_COLOR,
        on_click=lambda e: mensaje_confirmacion(page, uid, actualizar_tabla),
        tooltip="Eliminar usuario"
    )

def editar_usuario(usuario_id, page, actualizar_tabla_callback):
    """Función para editar usuario"""
    try:
        # Primero obtener los datos del usuario desde Firebase
        from app.utils.cache_firebase import cache_firebase
        usuarios = cache_firebase._cache_usuarios if cache_firebase._cache_usuarios else []
        
        # Buscar el usuario por firebase_id
        usuario_data = None
        for usuario in usuarios:
            if usuario.get('firebase_id') == usuario_id or usuario.get('id') == usuario_id:
                usuario_data = usuario
                break
        
        if not usuario_data:
            print(f"No se encontró usuario con ID: {usuario_id}")
            if hasattr(page, 'show_snack_bar'):
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("Usuario no encontrado"),
                        bgcolor=ft.Colors.RED_400
                    )
                )
            return
        
        # Importar y ejecutar la función de editar usuario
        from app.crud_usuarios.edit_usuario import mostrar_dialogo_editar_usuario
        mostrar_dialogo_editar_usuario(page, usuario_data, actualizar_tabla_callback)
    except Exception as e:
        print(f"Error al abrir diálogo de editar usuario: {e}")
        if hasattr(page, 'show_snack_bar'):
            page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"Error al editar usuario: {str(e)}"),
                    bgcolor=ft.Colors.RED_400
                )
            )