import flet as ft
from conexiones.firebase import db
import asyncio

def mostrar_dialogo_busqueda(page, mostrar_productos_filtrados):
    campo_buscar = ft.TextField(
      label="Buscar Producto por modelo",
      width=300,
      autofocus=True,
    )
    async def validar_busqueda(e):
        if not campo_buscar.value.strip():
          page.open(ft.SnackBar(
          content=ft.Text("Por favor, ingrese un modelo para buscar."),
          bgcolor=ft.Colors.RED_400
      ))
        else:
            await buscar_en_firebase(page, campo_buscar.value, mostrar_productos_filtrados, dialogo_busqueda)

    dialogo_busqueda = ft.AlertDialog(
        title=ft.Text("Buscar Producto"),
        content=ft.Container(
          content=ft.Row(
              controls=[
                  campo_buscar,
                  ft.ElevatedButton(
                      text="Buscar",
                      on_click=validar_busqueda
                  )
              ]
          ),
          width=400,
          height=100,
        ),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: page.close(dialogo_busqueda)),
        ]
    )

    page.open(dialogo_busqueda)
    page.update()

async def buscar_en_firebase(page, busqueda, actualizar_tabla=None, dialogo_busqueda=None):
    try:
        referencia_productos = db.collection('productos')
        query = referencia_productos.where('modelo', '==', busqueda)
        resultados = query.stream()

        productos_encontrados = []
        for producto in resultados:
            data = producto.to_dict() #to.dict() para convertir el documento a diccionario
            data['firebase_id'] = producto.id  # Guardar el ID real de Firebase
            productos_encontrados.append(data)

        if productos_encontrados:
          page.close(dialogo_busqueda)  # Cerrar el dialog
          page.open(ft.SnackBar(
              content=ft.Text(f"Se encontraron {len(productos_encontrados)} productos"),
              bgcolor=ft.Colors.GREEN_400
          ))
          if actualizar_tabla:
              await actualizar_tabla(productos_encontrados)
        else:
            page.open(ft.SnackBar(
                content=ft.Text("No se encontraron productos con ese modelo."),
                bgcolor=ft.Colors.RED_400
            ))

    except Exception as e:
        print(f"Error al buscar productos: {str(e)}")
        page.open(ft.SnackBar(
            content=ft.Text("Error al buscar productos."),
            bgcolor=ft.Colors.RED_400
        ))
        page.update()
        
