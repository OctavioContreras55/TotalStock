import flet as ft

def main(page: ft.Page):
    def cerrar_dialogo(e):
        page.close(dlg)  # <-- cerrar correctamente

    dlg = ft.AlertDialog(
        title=ft.Text("¿Seguro que quieres eliminar este usuario?"),
        content=ft.Text("Esta acción no se puede deshacer."),
        actions=[
            ft.TextButton("Sí", on_click=cerrar_dialogo),
            ft.TextButton("No", on_click=cerrar_dialogo),
        ]
    )

    def mostrar_dialogo(e):
        page.open(dlg)  # <-- forma correcta según documentación

    page.add(ft.ElevatedButton("Eliminar usuario", on_click=mostrar_dialogo))

ft.app(target=main)
