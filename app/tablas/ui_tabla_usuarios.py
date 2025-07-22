import flet as ft

def mostrar_tabla_usuarios(usuarios):
    # Crear una tabla para mostrar los usuarios
    tabla = ft.DataTable(
        border=ft.border.all(1, "black"),
        sort_column_index=0,  # Columna por defecto para ordenar
        border_radius=10,  # Bordes redondeados
        sort_ascending=True,  # Orden ascendente por defecto
        heading_row_color=ft.Colors.BLACK12,  # Color de la fila de encabezado
        heading_row_height=100,  # Altura de la fila de encabezado
        data_row_color={ft.ControlState.HOVERED: "0x30FF0000"},  # Color de la fila al pasar el mouse
        show_checkbox_column=True,  # Mostrar columna de checkbox
        divider_thickness=0,  # Grosor del divisor
        column_spacing=200,  # Espaciado entre columnas
        columns=[
            ft.DataColumn(ft.Text("ID"), on_sort=lambda e: print(f"{e.column_index}, {e.ascending}")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Tipo de Usuario")),
            ft.DataColumn(ft.Text("Opciones")),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(usuario.get('id', 'N/A')))),
                    ft.DataCell(ft.Text(usuario.get('nombre', 'Sin nombre'))),
                    ft.DataCell(ft.Text("Administrador" if usuario.get('es_admin', False) else "Usuario")),
                    ft.DataCell(
                        ft.Row(
                            controls=[
                                ft.IconButton(ft.Icons.EDIT, on_click=lambda e, uid=usuario.get('firebase_id', ''): print(f"Editar {uid}")),
                                ft.IconButton(ft.Icons.DELETE, on_click=lambda e, uid=usuario.get('firebase_id', ''): print(f"Eliminar {uid}"))
                            ],
                            spacing=10
                        )
                    ),
                ],
                selected=False,
                on_select_changed=lambda e: print(f"Fila seleccionada: {e.data}"),
            )   for usuario in usuarios
        ],
        width=1000,
        
        expand=True,
    )
    
    return tabla