import flet as ft

def mostrar_tabla_productos(page, productos, actualizar_tabla_productos=None):
    # Crear una tabla para mostrar los productos
    
    altura_tabla = max(300, (page.window.height or 800) - 350)
    ancho_tabla = max(800, (page.window.width or 1200) - 400)
    tabla = ft.DataTable(
        border=ft.border.all(1, "black"),
        sort_column_index=0, # Columna por defecto para ordenar
        border_radius=10, # Bordes redondeados
        sort_ascending=True, # Orden ascendente por defecto
        heading_row_color=ft.Colors.BLACK12,  # Color de la fila de encabezado
        heading_row_height=50, # Altura de la fila de encabezado
        data_row_color={ft.ControlState.HOVERED: "0x30FF0000"}, # Color de la fila al pasar el mouse
        show_checkbox_column=True, # Mostrar columna de checkbox
        divider_thickness=0, # Grosor del divisor
        column_spacing=50, # Espaciado entre columnas
        columns=[
            ft.DataColumn(ft.Text("Modelo"), on_sort=lambda e: print(f"{e.column_index}, {e.ascending}"), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Tipo"), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Nombre"), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Precio"), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Cantidad"), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
            ft.DataColumn(ft.Text("Opciones"), heading_row_alignment=ft.CrossAxisAlignment.CENTER),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(producto.get('modelo')))),
                    ft.DataCell(ft.Text(producto.get('tipo'))),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(producto.get('nombre')),
                            width=300  # Ajusta este valor según lo que necesites
                        )
                    ),
                    ft.DataCell(ft.Text(str(producto.get('precio')))),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(str(producto.get('cantidad'))),
                            alignment=ft.alignment.center,  # Centrar el texto
                        )
                    ),
                    ft.DataCell(
                        ft.Row(
                            controls=[
                                ft.IconButton(ft.Icons.EDIT, on_click=lambda e, id=producto.get('id'): print(f"Editar {id}")),
                                ft.IconButton(ft.Icons.DELETE, on_click=lambda e, id=producto.get('id'): print(f"Eliminar {id}")),
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
    )