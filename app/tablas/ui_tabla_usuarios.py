import flet as ft
from app.crud_usuarios.delete_usuarios import mensaje_confirmacion
from app.utils.temas import GestorTemas

def crear_boton_eliminar(page, uid, actualizar_tabla=None):
    tema = GestorTemas.obtener_tema()
    return ft.IconButton(
        ft.Icons.DELETE,
        icon_color=tema.ERROR_COLOR,
        on_click=lambda e: mensaje_confirmacion(page, uid, actualizar_tabla)
    )
    
def mostrar_tabla_usuarios(page, usuarios, actualizar_tabla=None):
    tema = GestorTemas.obtener_tema()
    # Calcular altura responsiva basada en el tamaño de pantalla
    # Reservamos espacio para header, botones y padding (aproximadamente 300px)
    altura_tabla = max(300, (page.window.height or 800) - 350)
    
    # Crear una tabla para mostrar los usuarios
    tabla = ft.DataTable(
        border=ft.border.all(1, tema.TABLE_BORDER),
        sort_column_index=0,  # Columna por defecto para ordenar
        border_radius=tema.BORDER_RADIUS,  # Bordes redondeados
        sort_ascending=True,  # Orden ascendente por defecto
        heading_row_color=tema.TABLE_HEADER_BG,  # Color de la fila de encabezado
        heading_row_height=100,  # Altura de la fila de encabezado
        data_row_color={ft.ControlState.HOVERED: tema.TABLE_HOVER},  # Color de la fila al pasar el mouse
        show_checkbox_column=True,  # Mostrar columna de checkbox
        divider_thickness=0,  # Grosor del divisor
        column_spacing=200,  # Espaciado entre columnas
        columns=[
            ft.DataColumn(ft.Text("ID", color=tema.TEXT_COLOR), on_sort=lambda e: print(f"{e.column_index}, {e.ascending}")),
            ft.DataColumn(ft.Text("Nombre", color=tema.TEXT_COLOR)),
            ft.DataColumn(ft.Text("Tipo de Usuario", color=tema.TEXT_COLOR)),
            ft.DataColumn(ft.Text("Opciones", color=tema.TEXT_COLOR)),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(usuario.get('id', 'N/A')), color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(usuario.get('nombre', 'Sin nombre'), color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text("Administrador" if usuario.get('es_admin', False) else "Usuario", color=tema.TEXT_COLOR)),
                    ft.DataCell(
                        ft.Row(
                            controls=[
                                ft.IconButton(ft.Icons.EDIT, icon_color=tema.PRIMARY_COLOR, on_click=lambda e, uid=usuario.get('firebase_id', ''): print(f"Editar {uid}")),
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
        width=1200,
    )
    
    scroll_vertical = ft.Column([tabla], scroll=True, height=altura_tabla)  # Altura responsiva
    scroll_horizontal = ft.Row([scroll_vertical], scroll=True, vertical_alignment=ft.MainAxisAlignment.START)
    return ft.Container(
        content=scroll_horizontal,
        bgcolor=tema.CARD_COLOR,
        border_radius=tema.BORDER_RADIUS,
        padding=10,
    )