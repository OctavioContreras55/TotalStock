#!/usr/bin/env python3
"""
Modificación para ubicaciones de productos específicos
Basado en la estructura del Excel: Modelo -> Almacén -> Estantería
"""

import flet as ft
from conexiones.firebase import db
from app.utils.temas import GestorTemas
from app.utils.historial import GestorHistorial
from app.funciones.sesiones import SesionManager
from datetime import datetime
import uuid
import asyncio

async def crear_ubicacion_producto_dialog(page, callback_actualizar=None):
    """Crear diálogo para asignar ubicación a un producto específico"""
    tema = GestorTemas.obtener_tema()
    
    # Variables para productos disponibles
    productos_disponibles = []
    
    # Cargar productos disponibles
    async def cargar_productos_disponibles():
        """Cargar productos desde Firebase"""
        nonlocal productos_disponibles
        try:
            from app.crud_productos.create_producto import obtener_productos_firebase
            productos_disponibles = await obtener_productos_firebase()
        except Exception as e:
            print(f"Error al cargar productos: {e}")
            productos_disponibles = []
    
    # Cargar productos iniciales
    await cargar_productos_disponibles()
    
    # Campo de búsqueda y selección de producto
    producto_seleccionado_modelo = None
    
    # Campo de búsqueda por texto
    campo_buscar_tipo = ft.TextField(
        label="🔍 Buscar o escribir tipo de producto",
        hint_text="Escriba el tipo de producto (modelo) a asignar",
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        border_radius=tema.BORDER_RADIUS,
        label_style=ft.TextStyle(
            color=tema.TEXT_SECONDARY,
            size=14,
            weight=ft.FontWeight.W_500
        ),
        helper_text="Puede escribir un tipo nuevo o buscar uno existente"
    )
    
    # Campo para almacén
    campo_almacen = ft.TextField(
        label="🏢 Almacén (ej: 1, 2A, 2B, etc.)",
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        border_radius=tema.BORDER_RADIUS,
        label_style=ft.TextStyle(
            color=tema.TEXT_SECONDARY, 
            size=14, 
            weight=ft.FontWeight.W_500
        )
    )
    
    # Campo para estantería
    campo_estanteria = ft.TextField(
        label="📚 Estantería (ej: 2A, 1B, 10A, etc.)",
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        border_radius=tema.BORDER_RADIUS,
        label_style=ft.TextStyle(
            color=tema.TEXT_SECONDARY, 
            size=14, 
            weight=ft.FontWeight.W_500
        )
    )
    
    # Campo para cantidad en esa ubicación (opcional)
    campo_cantidad = ft.TextField(
        label="📊 Cantidad en esta ubicación",
        value="1",  # Valor por defecto
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        border_radius=tema.BORDER_RADIUS,
        keyboard_type=ft.KeyboardType.NUMBER,
        label_style=ft.TextStyle(
            color=tema.TEXT_SECONDARY, 
            size=14, 
            weight=ft.FontWeight.W_500
        ),
        helper_text="Ingrese la cantidad de productos en esta ubicación"
    )
    
    # Campo para observaciones (opcional)
    campo_observaciones = ft.TextField(
        label="📝 Observaciones (opcional)",
        width=400,
        multiline=True,
        min_lines=2,
        max_lines=3,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        border_radius=tema.BORDER_RADIUS,
        label_style=ft.TextStyle(
            color=tema.TEXT_SECONDARY, 
            size=14, 
            weight=ft.FontWeight.W_500
        ),
        helper_text="Notas adicionales sobre esta ubicación"
    )
    
    def validar_campos():
        """Validar que los campos requeridos estén completos"""
        if not campo_buscar_tipo.value or not campo_buscar_tipo.value.strip():
            return False, "Debe especificar el tipo de producto"
        
        if not campo_almacen.value or not campo_almacen.value.strip():
            return False, "Debe especificar el almacén"
        
        if not campo_estanteria.value or not campo_estanteria.value.strip():
            return False, "Debe especificar la estantería"
        
        return True, "OK"
    
    async def verificar_tipo_existe_en_ubicaciones(tipo_producto):
        """Verificar si el tipo ya existe en la tabla de ubicaciones"""
        try:
            ubicaciones_existentes = await obtener_ubicaciones_productos_firebase()
            for ubicacion in ubicaciones_existentes:
                if ubicacion.get('modelo', '').lower() == tipo_producto.lower():
                    return True, ubicacion
            return False, None
        except Exception as e:
            print(f"Error al verificar ubicaciones: {e}")
            return False, None
    
    async def crear_ubicacion_producto(e):
        """Crear nueva ubicación de producto"""
        es_valido, mensaje = validar_campos()
        if not es_valido:
            page.open(ft.SnackBar(
                content=ft.Text(mensaje, color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return
        
        # Obtener el tipo de producto desde el campo de texto
        tipo_producto = campo_buscar_tipo.value.strip()
        
        # Verificar si el tipo ya existe en ubicaciones
        existe, ubicacion_existente = await verificar_tipo_existe_en_ubicaciones(tipo_producto)
        
        if existe:
            # El tipo ya existe, mostrar mensaje y sugerir usar movimiento
            page.open(ft.SnackBar(
                content=ft.Text(
                    f"⚠️ El tipo '{tipo_producto}' ya está en la tabla de ubicaciones.\n"
                    f"Si desea mover o cambiar la ubicación, use el botón de 'Movimiento' en la tabla.",
                    color=tema.TEXT_COLOR
                ),
                bgcolor=tema.WARNING_COLOR,
                duration=5000
            ))
            return
        
        try:
            # El tipo no existe, crear nueva ubicación
            cantidad = 1  # Valor por defecto
            if campo_cantidad.value and campo_cantidad.value.strip():
                try:
                    cantidad = int(campo_cantidad.value.strip())
                except ValueError:
                    cantidad = 1
            
            observaciones = "Sin observaciones"  # Valor por defecto
            if campo_observaciones.value and campo_observaciones.value.strip():
                observaciones = campo_observaciones.value.strip()
            
            ubicacion_producto = {
                "id": str(uuid.uuid4()),
                "modelo": tipo_producto,  # Ahora usar el tipo escrito por el usuario
                "nombre_producto": f"Producto tipo {tipo_producto}",  # Nombre genérico
                "tipo_producto": tipo_producto,
                "almacen": campo_almacen.value.strip(),
                "estanteria": campo_estanteria.value.strip(),
                "cantidad": cantidad,
                "observaciones": observaciones,
                "fecha_asignacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "usuario_asignacion": SesionManager.obtener_usuario_actual().get('username', 'Usuario') if SesionManager.obtener_usuario_actual() else 'Sistema'
            }
            
            # Guardar en Firebase en colección 'ubicaciones'
            db.collection("ubicaciones").add(ubicacion_producto)
            
            # Registrar actividad
            gestor_historial = GestorHistorial()
            usuario_actual = SesionManager.obtener_usuario_actual()
            
            await gestor_historial.agregar_actividad(
                tipo="asignar_ubicacion",
                descripcion=f"Asignó ubicación: {ubicacion_producto['modelo']} → Almacén {ubicacion_producto['almacen']}, Estantería {ubicacion_producto['estanteria']}",
                usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
            )
            
            page.open(ft.SnackBar(
                content=ft.Text("Ubicación asignada exitosamente", color=tema.TEXT_COLOR),
                bgcolor=tema.SUCCESS_COLOR
            ))
            
            # Cerrar diálogo y actualizar tabla
            page.close(dialogo_crear)
            if callback_actualizar:
                await callback_actualizar()
                
        except Exception as ex:
            page.open(ft.SnackBar(
                content=ft.Text(f"Error al asignar ubicación: {str(ex)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
    
    dialogo_crear = ft.AlertDialog(
        title=ft.Text("Asignar Ubicación a Producto", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content=ft.Container(
            content=ft.Column([
                ft.Text("Basado en estructura: Tipo → Almacén → Estantería", 
                        color=tema.TEXT_SECONDARY, size=12),
                ft.Divider(color=tema.DIVIDER_COLOR),
                campo_buscar_tipo,  # Campo de búsqueda de tipo
                campo_almacen,
                campo_estanteria,
                campo_cantidad,
                campo_observaciones,
            ], spacing=20),
            width=520,
            height=480,  # Altura ajustada para mejor proporción
            padding=ft.Padding(25, 25, 25, 25)
        ),
        actions=[
            ft.ElevatedButton(
                "Asignar Ubicación",
                style=ft.ButtonStyle(
                    bgcolor=tema.BUTTON_SUCCESS_BG,
                    color=tema.BUTTON_TEXT,
                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                ),
                on_click=crear_ubicacion_producto
            ),
            ft.TextButton(
                "Cancelar",
                style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                on_click=lambda e: page.close(dialogo_crear)
            ),
        ],
        modal=True,
    )
    
    page.open(dialogo_crear)
    page.update()

async def obtener_ubicaciones_productos_firebase():
    """Obtener todas las ubicaciones de productos desde Firebase"""
    try:
        ubicaciones_ref = db.collection('ubicaciones')
        ubicaciones = ubicaciones_ref.stream()
        
        ubicaciones_data = []
        for ubicacion in ubicaciones:
            data = ubicacion.to_dict()
            data['firebase_id'] = ubicacion.id
            ubicaciones_data.append(data)
        
        return ubicaciones_data
        
    except Exception as e:
        print(f"Error al obtener ubicaciones de productos: {e}")
        # Datos de ejemplo basados en tu Excel
        return [
            {
                'firebase_id': '1',
                'modelo': 'Cadena 25',
                'almacen': 'Almacén Principal',
                'estanteria': '2A',
                'fecha_asignacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'observaciones': 'Asignación inicial'
            },
            {
                'firebase_id': '2',
                'modelo': 'Rodamiento 6204',
                'almacen': 'Almacén Secundario',
                'estanteria': '1B',
                'fecha_asignacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'observaciones': 'Stock de repuesto'
            }
        ]

async def eliminar_ubicacion_producto_firebase(ubicacion_id, page):
    """Eliminar ubicación de producto de Firebase"""
    try:
        # Eliminar de Firebase
        db.collection("ubicaciones").document(ubicacion_id).delete()
        
        # Registrar actividad
        gestor_historial = GestorHistorial()
        usuario_actual = SesionManager.obtener_usuario_actual()
        
        await gestor_historial.agregar_actividad(
            tipo="eliminar_ubicacion",
            descripcion=f"Eliminó asignación de ubicación con ID: {ubicacion_id}",
            usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
        )
        
        return True, "Ubicación eliminada exitosamente"
        
    except Exception as e:
        print(f"Error al eliminar ubicación: {e}")
        return False, f"Error al eliminar ubicación: {str(e)}"
