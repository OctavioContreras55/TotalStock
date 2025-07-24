import flet as ft
from app.crud_usuarios.delete_usuarios import mensaje_confirmacion

def crear_boton_eliminar(page, uid, actualizar_tabla=None):
    return ft.IconButton(
        ft.Icons.DELETE,
        on_click=lambda e: mensaje_confirmacion(page, uid, actualizar_tabla)
    )
def mostrar_tabla_usuarios(page, usuarios, actualizar_tabla=None):
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
                                crear_boton_eliminar(page, usuario.get('firebase_id', ''), actualizar_tabla),
                            ],
                            spacing=10
                        )
                    ),
                ],
                selected=False,
                on_select_changed=lambda e: print(f"Fila seleccionada: {e.data}"),
            )   for usuario in usuarios
        ],
        height=800,
        width=1200,
    )
    
    scroll_vertical = ft.Column([tabla], scroll=True, expand=True)
    scroll_horizontal = ft.Row([scroll_vertical], scroll=True, expand=1, vertical_alignment=ft.MainAxisAlignment.START)
    return scroll_horizontal