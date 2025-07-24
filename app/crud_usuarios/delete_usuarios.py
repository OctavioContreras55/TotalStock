import flet as ft
from conexiones.firebase import db
import asyncio




def eliminar_usuario_firebase(id_usuario):
    try:
        referencia_usuarios = db.collection('usuarios')
        referencia_usuarios.document(id_usuario).delete()
        print(f"Usuario con ID {id_usuario} eliminado exitosamente.")
        return True
    except Exception as e:
        print(f"Error al eliminar usuario: {str(e)}")
        return False
    
    
async def on_eliminar_click(e, page, id_usuario, actualizar_tabla):
    if eliminar_usuario_firebase(id_usuario):
        print("Usuario eliminado exitosamente.")
        if actualizar_tabla:
            await actualizar_tabla()
        page.open(ft.SnackBar(ft.Text("Usuario eliminado exitosamente."), duration=2000))  # milisegundos, opcional
        page.update()
    else:
        print("Error al eliminar usuario.")


def mensaje_confirmacion(page, id_usuario, actualizar_tabla):
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
        title=ft.Text("Confirmación de eliminación"),
        content=ft.Text("¿Estás seguro de eliminar el usuario?"),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialogo(page)),
            ft.TextButton("Eliminar", on_click=confirmar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )


    page.open(dialog)
    page.update()

