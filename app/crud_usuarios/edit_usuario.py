import flet as ft
from conexiones.firebase import db
from app.utils.temas import GestorTemas
from app.utils.historial import GestorHistorial
from app.funciones.sesiones import SesionManager
from datetime import datetime
import asyncio

def mostrar_dialogo_editar_usuario(page, usuario_data, actualizar_callback=None):
    """Mostrar diálogo para editar un usuario - Solo nombre, contraseña y admin"""
    tema = GestorTemas.obtener_tema()
    
    # Campo nombre
    campo_nombre = ft.TextField(
        label="Nombre completo",
        value=usuario_data.get('nombre', ''),
        width=300,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR
    )
    
    # Campo contraseña (opcional)
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
    
    # Switch para admin
    switch_admin = ft.Switch(
        label="Es Administrador",
        value=usuario_data.get('es_admin', False),
        active_color=tema.PRIMARY_COLOR
    )
    
    async def guardar_cambios(e):
        """Guardar los cambios del usuario - Solo nombre, contraseña y admin"""
        # Validación básica
        if not campo_nombre.value.strip():
            page.open(ft.SnackBar(
                content=ft.Text("El nombre es obligatorio", color=tema.TEXT_COLOR),
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
                'es_admin': switch_admin.value,
                'fecha_modificacion': datetime.now().isoformat()
            }
            
            # Agregar contraseña si se proporcionó - CORREGIDO: usar 'contrasena'
            if campo_password.value.strip():
                datos_actualizados['contrasena'] = campo_password.value.strip()
                print(f"[DEBUG] Nueva contraseña establecida: {campo_password.value.strip()}")
            
            # Actualizar en Firebase usando el firebase_id del usuario
            firebase_id = usuario_data.get('firebase_id')
            if firebase_id:
                db.collection('usuarios').document(firebase_id).update(datos_actualizados)
                print(f"[OK] Usuario {firebase_id} actualizado en Firebase")
            else:
                raise Exception("ID de usuario no encontrado")

            # ACTUALIZACIÓN OPTIMISTA: Actualizar datos localmente para UI inmediata
            usuario_data_actualizada = usuario_data.copy()
            usuario_data_actualizada.update(datos_actualizados)
            
            # Invalidar cache para futuras consultas
            from app.utils.cache_firebase import cache_firebase
            cache_firebase._cache_usuarios = []
            cache_firebase._ultimo_update_usuarios = None
            print("[ELIMINAR] Cache de usuarios invalidado después de editar")
            
            print("[PROCESO] Preparando actualización silenciosa")
            
            # Registrar en historial
            gestor_historial = GestorHistorial()
            usuario_actual = SesionManager.obtener_usuario_actual()
            
            await gestor_historial.agregar_actividad(
                tipo="editar_usuario",
                descripcion=f"Editó el usuario: {campo_nombre.value}",
                usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
            )
            
            # Cerrar indicador de carga
            page.close(mensaje_cargando)
            
            # Mostrar mensaje de éxito
            page.open(ft.SnackBar(
                content=ft.Text("Usuario actualizado correctamente", color=tema.TEXT_COLOR),
                bgcolor=tema.SUCCESS_COLOR
            ))
            
            # Actualizar tabla automáticamente después de editar
            if actualizar_callback:
                print("[RAPIDO] Ejecutando actualización automática después de editar usuario")
                try:
                    await actualizar_callback(forzar_refresh=True)  # Forzar refresh desde Firebase
                except Exception as e:
                    print(f"Error en actualización automática: {e}")
                    page.update()
            else:
                print("[WARN] No hay callback de actualización disponible")
                page.update()
                
        except Exception as error:
            # Cerrar indicador de carga
            page.close(mensaje_cargando)
            
            page.open(ft.SnackBar(
                content=ft.Text(f"Error al actualizar usuario: {str(error)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))    # Diálogo principal
    dialogo_editar = ft.AlertDialog(
        title=ft.Text(f"Editar Usuario: {usuario_data.get('nombre', '')}", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content=ft.Container(
            content=ft.Column([
                campo_nombre,
                campo_password,
                ft.Row([
                    switch_admin,
                ], alignment=ft.MainAxisAlignment.START)
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            width=400,
            height=300,  # Altura reducida
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
