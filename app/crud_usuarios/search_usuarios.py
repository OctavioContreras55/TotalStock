import flet as ft

def buscar_usuarios(page, actualizar_tabla=None):
    try:
        # Crear un campo de texto para la búsqueda
        campo_busqueda = ft.TextField(
            label="Buscar usuario",
            on_change=lambda e: buscar_usuario(e, page, actualizar_tabla)
        )
        
        # Agregar el campo de búsqueda a la página
        page.add(campo_busqueda)
    except Exception as error:
        print(f"Error al buscar usuarios: {error}")