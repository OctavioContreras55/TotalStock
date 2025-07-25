import flet as ft
from app.tablas.ui_tabla_productos import mostrar_tabla_productos
from app.ui.barra_carga import vista_carga
import asyncio
from app.funciones.carga_archivos import on_click_importar_archivo
from app.funciones.carga_archivos import obtener_productos_de_firebase

async def vista_inventario(nombre_seccion, contenido, productos_ejemplo, page):
    productos = await obtener_productos_de_firebase()
    contenido.content = vista_carga()  # Mostrar barra de carga mientras se carga la vista
    page.update()  # Actualizar la página para mostrar la barra de carga
    await asyncio.sleep(2)  # Simular tiempo de carga
    
    def actualizar_tabla_productos(productos):
        #Actualizar la tabla de productos con los nuevos datos
        contenido.content.controls[-1].content = mostrar_tabla_productos(productos)
        contenido.content.update()
    
    contenido.content = ft.Column(
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.START
                ),
                width=600,
                bgcolor=ft.Colors.GREY_900,
                padding=20,
                alignment=ft.alignment.center,
                border_radius=10,
            ),
            ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.ElevatedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.SEARCH),
                                        ft.Text("Buscar producto")
                                    ])
                                ),
                                width=200,
                                padding=ft.padding.symmetric(horizontal=5, vertical=20)
                            ),
                            ft.Container(
                                content=ft.ElevatedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.ADD),
                                        ft.Text("Agregar producto")
                                    ])
                                ),
                                width=200,
                                padding=ft.padding.symmetric(horizontal=5, vertical=20)
                            ),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.ElevatedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.FILE_UPLOAD),
                                        ft.Text("Importar productos")
                                    ]),
                                    on_click=lambda e: on_click_importar_archivo(page , actualizar_tabla_productos),
                                ),
                                width=200,
                                padding=ft.padding.symmetric(horizontal=5, vertical=20)
                            ),
                            ft.Container(
                                content=ft.ElevatedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.FILE_DOWNLOAD),
                                        ft.Text("Exportar productos")
                                    ])
                                ),
                                width=200,
                                padding=ft.padding.symmetric(horizontal=5, vertical=20)
                            ),
                        ]
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            ft.Row(
                controls=[
                    ft.Container(
                        content=mostrar_tabla_productos(productos_ejemplo),
                        expand=True,
                        padding=ft.padding.all(10)
                        )
                    ],
                )     
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
