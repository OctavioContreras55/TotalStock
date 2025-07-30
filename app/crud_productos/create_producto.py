import flet as ft
from conexiones.firebase import db
from app.utils.temas import GestorTemas
import asyncio

async def vista_crear_producto(page, callback_actualizar_tabla=None):
    tema = GestorTemas.obtener_tema()
    
    # Dimensiones responsivas para el dialog
    ancho_ventana = page.window.width or 1200
    alto_ventana = page.window.height or 800
    ancho_dialog = min(450, ancho_ventana * 0.85)   # Máximo 450px o 85% del ancho
    alto_dialog = min(400, alto_ventana * 0.6)      # Máximo 400px o 60% del alto
    
    # Campos del formulario
    campo_modelo = ft.TextField(
        label="Modelo", 
        autofocus=True,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    campo_tipo = ft.TextField(
        label="Tipo",
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    campo_nombre = ft.TextField(
        label="Nombre",
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    campo_precio = ft.TextField(
        label="Precio", 
        keyboard_type=ft.KeyboardType.NUMBER,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    campo_cantidad = ft.TextField(
        label="Cantidad", 
        keyboard_type=ft.KeyboardType.NUMBER,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )

    def validar_campos():
        return all([
            campo_modelo.value.strip(),
            campo_tipo.value.strip(),
            campo_nombre.value.strip(),
            campo_precio.value.strip().isdigit(),
            campo_cantidad.value.strip().isdigit()
        ])

    async def crear_producto(e):
        if not validar_campos():
            page.open(ft.SnackBar(
                content=ft.Text("Por favor, complete todos los campos correctamente.", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return

        modelo = campo_modelo.value.strip()
        tipo = campo_tipo.value.strip()
        nombre = campo_nombre.value.strip()
        precio = float(campo_precio.value.strip())
        cantidad = int(campo_cantidad.value.strip())

        try:
            firebase_id = await crear_producto_firebase(modelo, tipo, nombre, precio, cantidad)
            page.open(ft.SnackBar(
                content=ft.Text(f"Producto '{nombre}' creado exitosamente con ID: {firebase_id}", color=tema.TEXT_COLOR),
                bgcolor=tema.SUCCESS_COLOR
            ))
            if callback_actualizar_tabla:
                await callback_actualizar_tabla()
        except Exception as e:
            page.open(ft.SnackBar(
                content=ft.Text(f"Error al crear producto: {str(e)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))

    dialogo_crear_producto = ft.AlertDialog(
        title=ft.Text("Crear Producto", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content=ft.Container(
            content=ft.Column(controls=[
                campo_modelo,
                campo_tipo,
                campo_nombre,
                campo_precio,
                campo_cantidad,
                ft.ElevatedButton(
                    text="Crear Producto", 
                    on_click=crear_producto,
                    style=ft.ButtonStyle(
                        bgcolor=tema.BUTTON_PRIMARY_BG,
                        color=tema.BUTTON_TEXT,
                        shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                    )
                )
            ]),
            width=ancho_dialog,   # Ancho responsivo
            height=alto_dialog,   # Alto responsivo
        ),
        actions=[
            ft.TextButton("Cerrar", 
                         style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                         on_click=lambda e: page.close(dialogo_crear_producto)),
        ]
    )

    page.open(dialogo_crear_producto)
    page.update()

async def crear_producto_firebase(modelo,tipo, nombre, precio, cantidad):
    # Crear un nuevo producto en la base de datos
    timestamp, producto_ref = db.collection("productos").add({
      "id": modelo,
      "modelo": modelo,
      "tipo": tipo,
      "nombre": nombre,
      "precio": precio,
      "cantidad": cantidad
    })
    return producto_ref.id

async def obtener_productos_firebase():
    try:
        referencia_productos = db.collection('productos')
        productos = referencia_productos.stream()
        lista_productos = []
        for producto in productos:
            data = producto.to_dict()
            data['firebase_id'] = producto.id
            data['nombre'] = data.get('nombre', 'Sin nombre')
            data['precio'] = data.get('precio', 0)
            data['modelo'] = data.get('modelo', 'Sin modelo')
            data['tipo'] = data.get('tipo', 'Sin tipo')
            data['cantidad'] = data.get('cantidad', 0)
            lista_productos.append(data)
        return lista_productos
    except Exception as e:
        print(f"Error al obtener productos: {str(e)}")
        return []