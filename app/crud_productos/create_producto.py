import flet as ft
from conexiones.firebase import db
import asyncio

async def vista_crear_producto(page, callback_actualizar_tabla=None):
    # Campos del formulario
    campo_modelo = ft.TextField(label="Modelo", autofocus=True)
    campo_tipo = ft.TextField(label="Tipo")
    campo_nombre = ft.TextField(label="Nombre")
    campo_precio = ft.TextField(label="Precio", keyboard_type=ft.KeyboardType.NUMBER)
    campo_cantidad = ft.TextField(label="Cantidad", keyboard_type=ft.KeyboardType.NUMBER)

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
                content=ft.Text("Por favor, complete todos los campos correctamente."),
                bgcolor=ft.Colors.RED_400
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
                content=ft.Text(f"Producto '{nombre}' creado exitosamente con ID: {firebase_id}"),
                bgcolor=ft.Colors.GREEN_400
            ))
            if callback_actualizar_tabla:
                await callback_actualizar_tabla()
        except Exception as e:
            page.open(ft.SnackBar(
                content=ft.Text(f"Error al crear producto: {str(e)}"),
                bgcolor=ft.Colors.RED_400
            ))

    dialogo_crear_producto = ft.AlertDialog(
        title=ft.Text("Crear Producto"),
        content=ft.Container(
            content=ft.Column(controls=[
                campo_modelo,
                campo_tipo,
                campo_nombre,
                campo_precio,
                campo_cantidad,
                ft.ElevatedButton(text="Crear Producto", on_click=crear_producto)
            ]),
            width=400,
            height=300,
        ),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: page.close(dialogo_crear_producto)),
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