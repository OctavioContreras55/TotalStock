import flet as ft
from conexiones.firebase import db
from app.utils.temas import GestorTemas
import asyncio

def mostrar_dialogo_busqueda(page, mostrar_productos_filtrados):
    tema = GestorTemas.obtener_tema()
    
    # Dimensiones responsivas para el dialog
    ancho_ventana = page.window.width or 1200
    ancho_dialog = min(400, ancho_ventana * 0.8)    # Máximo 400px o 80% del ancho
    
    campo_buscar = ft.TextField(
      label="Buscar Producto por modelo",
      width=min(300, ancho_dialog * 0.7),  # Campo responsivo
      autofocus=True,
      bgcolor=tema.INPUT_BG,
      color=tema.TEXT_COLOR,
      border_color=tema.INPUT_BORDER,
      focused_border_color=tema.PRIMARY_COLOR,
      label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    async def validar_busqueda(e):
        if not campo_buscar.value.strip():
          page.open(ft.SnackBar(
          content=ft.Text("Por favor, ingrese un modelo para buscar.", color=tema.TEXT_COLOR),
          bgcolor=tema.ERROR_COLOR
      ))
        else:
            await buscar_en_firebase(page, campo_buscar.value, mostrar_productos_filtrados, dialogo_busqueda)

    dialogo_busqueda = ft.AlertDialog(
        title=ft.Text("Buscar Producto", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content=ft.Container(
          content=ft.Row(
              controls=[
                  campo_buscar,
                  ft.ElevatedButton(
                      text="Buscar",
                      style=ft.ButtonStyle(
                          bgcolor=tema.BUTTON_PRIMARY_BG,
                          color=tema.BUTTON_TEXT,
                          shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                      ),
                      on_click=validar_busqueda
                  )
              ]
          ),
          width=ancho_dialog,   # Ancho responsivo
          height=100,
        ),
        actions=[
            ft.TextButton("Cerrar", 
                         style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                         on_click=lambda e: page.close(dialogo_busqueda)),
        ]
    )

    page.open(dialogo_busqueda)
    page.update()

async def buscar_en_firebase(page, busqueda, actualizar_tabla=None, dialogo_busqueda=None):
    tema = GestorTemas.obtener_tema()
    try:
        # OPTIMIZACIÓN: Buscar primero en cache local antes que en Firebase
        from app.utils.cache_firebase import cache_firebase
        from app.utils.monitor_firebase import monitor_firebase
        
        print(f"🔍 BÚSQUEDA INICIADA: '{busqueda}' - usando cache local (0 consultas Firebase)")
        todos_productos = await cache_firebase.obtener_productos()
        
        # Filtrar localmente (sin consulta a Firebase)
        productos_encontrados = []
        busqueda_lower = busqueda.lower().strip()
        
        for producto in todos_productos:
            modelo = producto.get('modelo', '').lower()
            if busqueda_lower in modelo:  # Búsqueda más flexible (contiene)
                productos_encontrados.append(producto)

        print(f"🎯 BÚSQUEDA COMPLETADA: {len(productos_encontrados)} productos encontrados (filtrado local)")

        if productos_encontrados:
            page.close(dialogo_busqueda)  # Cerrar el dialog
            page.open(ft.SnackBar(
                content=ft.Text(f"Se encontraron {len(productos_encontrados)} productos", color=tema.TEXT_COLOR),
                bgcolor=tema.SUCCESS_COLOR
            ))
            if actualizar_tabla:
                await actualizar_tabla(productos_encontrados)
        else:
            page.open(ft.SnackBar(
                content=ft.Text("No se encontraron productos con ese modelo.", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))

    except Exception as e:
        print(f"Error al buscar productos: {str(e)}")
        page.open(ft.SnackBar(
            content=ft.Text("Error al buscar productos.", color=tema.TEXT_COLOR),
            bgcolor=tema.ERROR_COLOR
        ))
        page.update()
        
