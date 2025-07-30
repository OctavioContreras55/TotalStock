import flet as ft
from app.utils.temas import GestorTemas

#Plan para opcion editar producto:
#1. Crear una vista para editar productos que reciba el ID del producto a editar.
#2. Cargar los datos del producto desde Firestore.

def on_click_editar_producto(page, producto_id, actualizar_tabla):
  tema = GestorTemas.obtener_tema()
  
  # Dimensiones responsivas para el dialog
  ancho_ventana = page.window.width or 1200
  alto_ventana = page.window.height or 800
  ancho_dialog = min(450, ancho_ventana * 0.85)   # Máximo 450px o 85% del ancho
  alto_dialog = min(450, alto_ventana * 0.7)      # Máximo 450px o 70% del alto
  
  vista_editar = ft.AlertDialog(
      title=ft.Text("Editar Producto", color=tema.TEXT_COLOR),
      content=ft.Container(
          content=ft.Column(controls=[
              ft.TextField(label="Modelo", autofocus=True, 
                bgcolor=tema.INPUT_BG, color=tema.TEXT_COLOR,
                border_color=tema.INPUT_BORDER, 
                focused_border_color=tema.PRIMARY_COLOR,
                label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)),
              ft.TextField(label="Tipo", autofocus=True, 
                bgcolor=tema.INPUT_BG, color=tema.TEXT_COLOR,
                border_color=tema.INPUT_BORDER, 
                focused_border_color=tema.PRIMARY_COLOR,
                label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)),
              ft.TextField(label="Nombre", autofocus=True, 
                bgcolor=tema.INPUT_BG, color=tema.TEXT_COLOR,
                border_color=tema.INPUT_BORDER, 
                focused_border_color=tema.PRIMARY_COLOR,
                label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)),
              ft.TextField(label="Precio", autofocus=True, 
                bgcolor=tema.INPUT_BG, color=tema.TEXT_COLOR,
                border_color=tema.INPUT_BORDER, 
                focused_border_color=tema.PRIMARY_COLOR,
                label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)),
              ft.TextField(label="Cantidad", autofocus=True, 
                bgcolor=tema.INPUT_BG, color=tema.TEXT_COLOR,
                border_color=tema.INPUT_BORDER, 
                focused_border_color=tema.PRIMARY_COLOR,
                label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)),
          ]),
          width=ancho_dialog,  # Ancho responsivo
          height=alto_dialog,  # Alto responsivo
      ),
      actions=[
          ft.TextButton("Cancelar", 
              style=ft.ButtonStyle(color=tema.BUTTON_ERROR_BG),
              on_click=lambda e: page.close(vista_editar)),
          ft.ElevatedButton(
              text="Guardar Cambios",
              style=ft.ButtonStyle(
                  bgcolor=tema.BUTTON_PRIMARY_BG,
                  color=tema.BUTTON_TEXT,
                  shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
              ),
              on_click=lambda e: guardar_cambios(producto_id)
          )
      ],
      bgcolor=tema.CARD_COLOR,
  )
  page.open(vista_editar)
  page.update()
  

def guardar_cambios(producto_id):
  pass