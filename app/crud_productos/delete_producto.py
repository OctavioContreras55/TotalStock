import flet as ft
from conexiones.firebase import db
from app.utils.temas import GestorTemas
import asyncio
from app.ui.barra_carga import vista_carga

def on_eliminar_producto_click(page, producto_id, actualizar_tabla):
    tema = GestorTemas.obtener_tema()
    
    # Dimensiones responsivas para el dialog
    ancho_ventana = page.window.width or 1200
    ancho_dialog = min(350, ancho_ventana * 0.8)  # Máximo 350px o 80% del ancho
    
    async def confirmar_eliminacion(e):
        db.collection("productos").document(producto_id).delete()
        page.open(ft.SnackBar(
            content=ft.Text("Producto eliminado correctamente.", color=tema.TEXT_COLOR),
            bgcolor=tema.SUCCESS_COLOR
        ))
        if actualizar_tabla:
            await actualizar_tabla()
        page.close(dialogo_confirmacion)

    dialogo_confirmacion = ft.AlertDialog(
        title=ft.Text("Confirmar Eliminación", color=tema.TEXT_COLOR),
        content=ft.Container(
            content=ft.Text("¿Estás seguro de que deseas eliminar este producto?", color=tema.TEXT_SECONDARY),
            width=ancho_dialog,  # Ancho responsivo
        ),
        actions=[
            ft.TextButton("Cancelar", 
                style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                on_click=lambda e: page.close(dialogo_confirmacion)),
            ft.ElevatedButton(
                text="Eliminar",
                style=ft.ButtonStyle(
                    bgcolor=tema.BUTTON_ERROR_BG,
                    color=tema.BUTTON_TEXT,
                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                ),
                on_click=confirmar_eliminacion
            )
        ],
        bgcolor=tema.CARD_COLOR
    )

    page.open(dialogo_confirmacion)
    page.update()