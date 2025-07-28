import flet as ft
from conexiones.firebase import db
import asyncio

def crear_producto(nombre, descripcion, precio):
    # Crear un nuevo producto en la base de datos
    producto_ref = db.collection("productos").add({
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio
    })
    return producto_ref.id

async def obtener_productos_firebase():
    try:
        referencia_productos = db.collection('productos')
        productos = referencia_productos.stream()
        lista_productos = []
        for producto in productos:
            data = producto.to_dict()
            data['firebase_id'] = producto.id  # Guardar el ID real de Firebase
            data['nombre'] = data.get('nombre', 'Sin nombre')  # Valor por defecto si no existe
            data['descripcion'] = data.get('descripcion', 'Sin descripción')  # Valor por defecto si no existe
            data['precio'] = data.get('precio', 0)  # Valor por defecto si no existe
            lista_productos.append(data)
        return lista_productos
    except Exception as e:
        print(f"Error al obtener productos: {str(e)}")
        return []