import flet as ft
from app.utils.temas import GestorTemas
from app.crud_productos.delete_producto import on_eliminar_producto_click
from app.crud_productos.edit_producto import on_click_editar_producto
import asyncio

def crear_boton_eliminar(producto_id, page, actualizar_tabla_productos):
    tema = GestorTemas.obtener_tema()
    return ft.IconButton(
        ft.Icons.DELETE,
        icon_color=tema.ERROR_COLOR,
        on_click=lambda e: on_eliminar_producto_click(page, producto_id, actualizar_tabla_productos),
        tooltip="Eliminar Producto",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
        )
    )
    
def crear_boton_editar(producto_id, page, actualizar_tabla_productos):
    from app.crud_productos.edit_producto import on_click_editar_producto
    tema = GestorTemas.obtener_tema()
    
    async def editar_handler(e):
        await on_click_editar_producto(page, producto_id, actualizar_tabla_productos)
    
    return ft.IconButton(
        ft.Icons.EDIT,
        icon_color=tema.PRIMARY_COLOR,
        on_click=editar_handler,
        tooltip="Editar Producto",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
        )
    )

def mostrar_tabla_productos(page, productos, actualizar_tabla_productos=None):
    tema = GestorTemas.obtener_tema()
    # Crear una tabla para mostrar los productos
    
    altura_tabla = max(300, (page.window.height or 800) - 350)
    ancho_tabla = max(800, (page.window.width or 1200) - 400)
    tabla = ft.DataTable(
        border=ft.border.all(1, tema.TABLE_BORDER),
        sort_column_index=0, # Columna por defecto para ordenar
        border_radius=tema.BORDER_RADIUS, # Bordes redondeados
        sort_ascending=True, # Orden ascendente por defecto
        heading_row_color=tema.TABLE_HEADER_BG,  # Color de la fila de encabezado
        heading_row_height=50, # Altura de la fila de encabezado
        data_row_color={ft.ControlState.HOVERED: tema.TABLE_HOVER}, # Color de la fila al pasar el mouse
        show_checkbox_column=True, # Mostrar columna de checkbox
        divider_thickness=0, # Grosor del divisor
        column_spacing=50, # Espaciado entre columnas
        columns=[
            ft.DataColumn(ft.Text("Modelo", color=tema.TEXT_COLOR), on_sort=lambda e: print(f"{e.column_index}, {e.ascending}"), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Tipo", color=tema.TEXT_COLOR), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Nombre", color=tema.TEXT_COLOR), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Precio", color=tema.TEXT_COLOR), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Cantidad", color=tema.TEXT_COLOR), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Opciones", color=tema.TEXT_COLOR), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(producto.get('modelo')), color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(producto.get('tipo'), color=tema.TEXT_COLOR)),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(producto.get('nombre'), color=tema.TEXT_COLOR),
                            width=300  # Ajusta este valor según lo que necesites
                        )
                    ),
                    ft.DataCell(ft.Text(str(producto.get('precio')), color=tema.TEXT_COLOR)),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(str(producto.get('cantidad')), color=tema.TEXT_COLOR),
                            alignment=ft.alignment.center,  # Centrar el texto
                        )
                    ),
                    ft.DataCell(
                        ft.Row(
                            controls=[
                                crear_boton_editar(producto.get('firebase_id', ''), page, actualizar_tabla_productos),
                                crear_boton_eliminar(producto.get('firebase_id', ''), page, actualizar_tabla_productos),
                            ],
                            spacing=10
                        )
                    )
                ],
                selected=False,
                on_select_changed=lambda e: print(f"Fila seleccionada: {e.data}"),
            ) for producto in productos
        ],
        width=ancho_tabla,  # Ancho responsivo
    )
    
    scroll_vertical = ft.Column([tabla], scroll=True, height=altura_tabla)  # Altura responsiva
    return ft.Container(
        content=scroll_vertical,
        alignment=ft.alignment.center,
        bgcolor=tema.CARD_COLOR,
        border_radius=tema.BORDER_RADIUS,
        padding=10,
    )