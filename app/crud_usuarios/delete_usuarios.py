import flet as ft
from conexiones.firebase import db
from app.utils.temas import GestorTemas
from app.utils.historial import GestorHistorial
from app.funciones.sesiones import SesionManager
import asyncio




async def eliminar_usuario_firebase(id_usuario): #Se manda a llamar en on_eliminar_click
    try:
        # Obtener datos del usuario antes de eliminarlo
        doc_ref = db.collection('usuarios').document(id_usuario)
        doc = doc_ref.get()
        usuario_nombre = "usuario"
        
        if doc.exists:
            usuario_data = doc.to_dict()
            usuario_nombre = usuario_data.get('nombre', 'usuario')
        
        # Eliminar el usuario
        doc_ref.delete()
        
        # Registrar actividad en el historial
        gestor_historial = GestorHistorial()
        usuario_actual = SesionManager.obtener_usuario_actual()
        
        await gestor_historial.agregar_actividad(
            tipo="eliminar_usuario",
            descripcion=f"Eliminó usuario '{usuario_nombre}' (ID: {id_usuario})",
            usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
        )
        
        print(f"Usuario con ID {id_usuario} eliminado exitosamente.")
        return True
    except Exception as e:
        print(f"Error al eliminar usuario: {str(e)}")
        return False
    
    
async def on_eliminar_click(e, page, id_usuario, actualizar_tabla): #Se manda a llamar desde el botón de eliminar en la tabla de usuarios
    if await eliminar_usuario_firebase(id_usuario):
        print("Usuario eliminado exitosamente.")
        if actualizar_tabla:
            await actualizar_tabla()
        page.open(ft.SnackBar(ft.Text("Usuario eliminado exitosamente."), duration=2000))  # milisegundos, opcional
        page.update()
    else:
        print("Error al eliminar usuario.")


def mensaje_confirmacion(page, id_usuario, actualizar_tabla): # Se manda a llamar desde el botón de eliminar en la tabla de usuarios
    tema = GestorTemas.obtener_tema()
    print(f"Se llamó a mensaje_confirmacion para ID: {id_usuario}")

    def confirmar(e):
        page.close(dialog)
        page.update()
        asyncio.run(on_eliminar_click(e, page, id_usuario, actualizar_tabla))

    def cerrar_dialogo(page):
        page.close(dialog)
        page.update()
        
    dialog = ft.AlertDialog(
        modal=True, 
        title=ft.Text("Confirmación de eliminación", color=tema.TEXT_COLOR),
        content=ft.Text("¿Estás seguro de eliminar el usuario?", color=tema.TEXT_SECONDARY),
        bgcolor=tema.CARD_COLOR,
        actions=[
            ft.TextButton("Cancelar", 
                         style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                         on_click=lambda e: cerrar_dialogo(page)),
            ft.TextButton("Eliminar", 
                         style=ft.ButtonStyle(color=tema.ERROR_COLOR),
                         on_click=confirmar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )


    page.open(dialog)
    page.update()

