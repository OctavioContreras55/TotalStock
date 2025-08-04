import flet as ft
from conexiones.firebase import db
from app.utils.temas import GestorTemas
from app.utils.historial import GestorHistorial
from app.funciones.sesiones import SesionManager
import asyncio
from app.ui.barra_carga import vista_carga

def on_eliminar_producto_click(page, producto_id, actualizar_tabla):
    tema = GestorTemas.obtener_tema()
    
    # Dimensiones responsivas para el dialog
    ancho_ventana = page.window.width or 1200
    ancho_dialog = min(350, ancho_ventana * 0.8)  # Máximo 350px o 80% del ancho
    
    async def confirmar_eliminacion(e):
        try:
            # Obtener nombre del producto antes de eliminarlo
            doc_ref = db.collection("productos").document(producto_id)
            doc = doc_ref.get()
            producto_nombre = "producto"
            
            if doc.exists:
                producto_data = doc.to_dict()
                producto_nombre = producto_data.get('nombre', 'producto')
            
            # Eliminar el producto
            doc_ref.delete()
            
            # Invalidar cache para forzar actualización inmediata
            from app.utils.cache_firebase import cache_firebase
            cache_firebase.invalidar_cache_productos()
            
            # Registrar actividad en el historial
            gestor_historial = GestorHistorial()
            usuario_actual = SesionManager.obtener_usuario_actual()
            
            await gestor_historial.agregar_actividad(
                tipo="eliminar_producto",
                descripcion=f"Eliminó producto '{producto_nombre}' (ID: {producto_id})",
                usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
            )
            
            # Actualizar dashboard dinámicamente - TEMPORALMENTE DESHABILITADO  
            # from app.utils.actualizador_dashboard import actualizar_dashboard_sincrono
            # actualizar_dashboard_sincrono()
            
            print("✅ Producto eliminado - actualización manual con botón refresh")
            
            page.open(ft.SnackBar(
                content=ft.Text("Producto eliminado correctamente.", color=tema.TEXT_COLOR),
                bgcolor=tema.SUCCESS_COLOR
            ))
            
            if actualizar_tabla:
                await actualizar_tabla()
            page.close(dialogo_confirmacion)
            
        except Exception as e:
            page.open(ft.SnackBar(
                content=ft.Text(f"Error al eliminar producto: {str(e)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))

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