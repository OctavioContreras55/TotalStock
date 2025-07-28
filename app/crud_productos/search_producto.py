import flet as ft
from conexiones.firebase import db 

def buscar_productos(page, actualizar_tabla=None):
    
    busqueda = ft.AlertDialog(
            title=ft.Text("Buscar Producto por modelo"),
            content=ft.TextField(
                label="Ingrese el nombre del producto",
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: page.dialog.close())
            ]
        )
        