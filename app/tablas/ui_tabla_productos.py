import flet as ft

def mostrar_tabla_productos(productos):
    # Crear una tabla para mostrar los productos
    tabla = ft.DataTable(
        border=ft.border.all(1, "black"),
        sort_column_index=0, # Columna por defecto para ordenar
        border_radius=10, # Bordes redondeados
        sort_ascending=True, # Orden ascendente por defecto
        heading_row_color=ft.Colors.BLACK12,  # Color de la fila de encabezado
        heading_row_height=100, # Altura de la fila de encabezado
        data_row_color={ft.ControlState.HOVERED: "0x30FF0000"}, # Color de la fila al pasar el mouse
        show_checkbox_column=True, # Mostrar columna de checkbox
        divider_thickness=0, # Grosor del divisor
        column_spacing=200, # Espaciado entre columnas
        columns=[
            ft.DataColumn(ft.Text("ID"), on_sort=lambda e: print(f"{e.column_index}, {e.ascending}")),
            ft.DataColumn(ft.Text("Nombre"), ),
            ft.DataColumn(ft.Text("Precio"), ),
            ft.DataColumn(ft.Text("Cantidad"),),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(producto['id']))),
                    ft.DataCell(ft.Text(producto['nombre'])),
                    ft.DataCell(ft.Text(str(producto['precio']))),
                    ft.DataCell(ft.Text(str(producto['cantidad']))),
                    
                ],
                selected=False,
                on_select_changed=lambda e: print(f"row select changed: {e.data}"),
            ) for producto in productos
        ],
        width=800,
        height=400,
    )
    
    return tabla