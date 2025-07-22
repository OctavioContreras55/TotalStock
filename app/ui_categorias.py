import flet as ft

def categorias_mostrar(nombre_seccion, contenido):

    contenido.content = ft.Column(
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            content=ft.Text("Categoría de cadenas", size=16),
                            on_click=lambda e: print("Categoría de cadenas seleccionada"),
                            width=200,
                            height=50,
                            icon=ft.Icon(ft.Icons.LINK),
                            
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
    )