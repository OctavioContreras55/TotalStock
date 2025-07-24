import flet as ft


def vista_carga():
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.ProgressRing(),
                ft.Text("Cargando...", size=20)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        expand=True,
        alignment=ft.alignment.center,
    )
    