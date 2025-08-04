import flet as ft
from conexiones.firebase import db
from app.utils.temas import GestorTemas
from app.utils.historial import GestorHistorial
from app.funciones.sesiones import SesionManager
import asyncio

def mostrar_dialogo_editar_usuario(page, usuario_data, actualizar_callback=None):
    """Mostrar diálogo para editar un usuario"""
    tema = GestorTemas.obtener_tema()
    
    # Campos del formulario
    campo_nombre = ft.TextField(
        label="Nombre completo",
        value=usuario_data.get('nombre', ''),
        width=300,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR
    )
    
    campo_username = ft.TextField(
        label="Username",
        value=usuario_data.get('username', ''),
        width=300,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR
    )
    
    campo_email = ft.TextField(
        label="Email",
        value=usuario_data.get('email', ''),
        width=300,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR
    )
    
    # Dropdown para rol
    dropdown_rol = ft.Dropdown(
        label="Rol",
        value=usuario_data.get('rol', 'usuario'),
        width=300,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        options=[
            ft.dropdown.Option("admin", "Administrador"),
            ft.dropdown.Option("usuario", "Usuario"),
            ft.dropdown.Option("supervisor", "Supervisor")
        ]
    )
    
    # Campo para nueva contraseña (opcional)
    campo_password = ft.TextField(
        label="Nueva contraseña (opcional)",
        width=300,
        password=True,
        can_reveal_password=True,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR
    )
    
    # Estado activo/inactivo
    switch_activo = ft.Switch(
        label="Usuario activo",
        value=usuario_data.get('activo', True),
        active_color=tema.PRIMARY_COLOR
    )
    
    async def guardar_cambios(e):
        """Guardar los cambios del usuario"""
        # Validaciones básicas
        if not campo_nombre.value.strip():
            page.open(ft.SnackBar(
                content=ft.Text("El nombre es obligatorio", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return
            
        if not campo_username.value.strip():
            page.open(ft.SnackBar(
                content=ft.Text("El username es obligatorio", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return
            
        if not campo_email.value.strip():
            page.open(ft.SnackBar(
                content=ft.Text("El email es obligatorio", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return
        
        # Mostrar indicador de carga
        mensaje_cargando = ft.AlertDialog(
            title=ft.Text("Actualizando", color=tema.TEXT_COLOR),
            bgcolor=tema.CARD_COLOR,
            content=ft.Container(
                content=ft.Row([
                    ft.Text("Actualizando usuario...", color=tema.TEXT_COLOR),
                    ft.ProgressRing(width=14, height=14, stroke_width=2, color=tema.PRIMARY_COLOR)
                ], alignment=ft.MainAxisAlignment.CENTER),
                padding=ft.Padding(20, 20, 10, 20),
            ),
            modal=True,
        )
        page.open(mensaje_cargando)
        page.close(dialogo_editar)
        page.update()
        
        try:
            # Preparar datos actualizados
            datos_actualizados = {
                'nombre': campo_nombre.value.strip(),
                'username': campo_username.value.strip(),
                'email': campo_email.value.strip(),
                'rol': dropdown_rol.value,
                'activo': switch_activo.value,
                'fecha_modificacion': ft.DateTime.now().isoformat()
            }
            
            # Agregar contraseña si se proporcionó
            if campo_password.value.strip():
                # En un sistema real, aquí deberías hashear la contraseña
                datos_actualizados['password'] = campo_password.value.strip()
            
            # Actualizar en Firebase usando el ID del usuario
            usuario_id = usuario_data.get('id')
            if usuario_id:
                db.collection('usuarios').document(usuario_id).update(datos_actualizados)
            else:
                # Si no hay ID, buscar por username original
                usuarios_ref = db.collection('usuarios')
                query = usuarios_ref.where('username', '==', usuario_data.get('username', ''))
                docs = query.get()
                
                if docs:
                    for doc in docs:
                        doc.reference.update(datos_actualizados)
                        break
                else:
                    raise Exception("Usuario no encontrado en la base de datos")
            
            # Registrar en historial
            gestor_historial = GestorHistorial()
            usuario_actual = SesionManager.obtener_usuario_actual()
            
            await gestor_historial.agregar_actividad(
                tipo="editar_usuario",
                descripcion=f"Editó el usuario: {campo_username.value}",
                usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
            )
            
            # Cerrar indicador de carga
            page.close(mensaje_cargando)
            
            # Mostrar mensaje de éxito
            page.open(ft.SnackBar(
                content=ft.Text("Usuario actualizado correctamente", color=tema.TEXT_COLOR),
                bgcolor=tema.SUCCESS_COLOR
            ))
            
            # Actualizar tabla si se proporcionó callback
            if actualizar_callback:
                await actualizar_callback()
                
        except Exception as error:
            # Cerrar indicador de carga
            page.close(mensaje_cargando)
            
            page.open(ft.SnackBar(
                content=ft.Text(f"Error al actualizar usuario: {str(error)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
    
    # Diálogo principal
    dialogo_editar = ft.AlertDialog(
        title=ft.Text(f"Editar Usuario: {usuario_data.get('username', '')}", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content=ft.Container(
            content=ft.Column([
                campo_nombre,
                campo_username,
                campo_email,
                dropdown_rol,
                campo_password,
                ft.Row([
                    switch_activo,
                ], alignment=ft.MainAxisAlignment.START)
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            width=400,
            height=450,
            padding=ft.Padding(10, 10, 10, 10)
        ),
        actions=[
            ft.ElevatedButton(
                "Guardar cambios",
                style=ft.ButtonStyle(
                    bgcolor=tema.BUTTON_SUCCESS_BG,
                    color=tema.BUTTON_TEXT,
                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                ),
                on_click=guardar_cambios
            ),
            ft.TextButton(
                "Cancelar",
                style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                on_click=lambda e: page.close(dialogo_editar)
            )
        ],
        modal=True,
    )
    
    page.open(dialogo_editar)
    page.update()

def editar_usuario(page, usuario_data, actualizar_callback=None):
    """Función de compatibilidad para editar usuario"""
    try:
        mostrar_dialogo_editar_usuario(page, usuario_data, actualizar_callback)
    except Exception as error:
        page.open(ft.SnackBar(
            content=ft.Text(f"Error al abrir editor: {str(error)}", color=GestorTemas.obtener_tema().TEXT_COLOR),
            bgcolor=GestorTemas.obtener_tema().ERROR_COLOR
        ))
