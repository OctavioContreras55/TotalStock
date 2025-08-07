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
    
    # Crear lista de modelos disponibles para el dropdown
    modelos_disponibles = []
    if productos_disponibles:
        modelos_unicos = set()
        for producto in productos_disponibles:
            modelo = producto.get('modelo', '')
            if modelo and modelo not in modelos_unicos:
                modelos_unicos.add(modelo)
        # Convertir todos los modelos a string antes de ordenar para evitar errores de tipo
        modelos_disponibles = sorted(list(modelos_unicos), key=lambda x: str(x))
    
    # Dropdown con modelos disponibles
    dropdown_modelos = ft.Dropdown(
        label="📦 Seleccionar modelo del inventario",
        options=[
            ft.dropdown.Option(modelo, modelo) for modelo in modelos_disponibles
        ],
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY),
        text_style=ft.TextStyle(color=tema.TEXT_COLOR, size=14),
        on_change=lambda e: setattr(campo_buscar_tipo, 'value', e.control.value) or campo_buscar_tipo.update()
    )
    
    # Campo de búsqueda por texto (ahora como alternativa)
    campo_buscar_tipo = ft.TextField(
        label="🔍 O escribir modelo manualmente",
        hint_text="Escriba el modelo de producto a asignar",
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
        helper_text="Solo se permiten modelos que ya existan en el inventario"
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
        # Verificar que se haya seleccionado o escrito un modelo
        tiene_modelo_dropdown = dropdown_modelos.value and dropdown_modelos.value.strip()
        tiene_modelo_texto = campo_buscar_tipo.value and campo_buscar_tipo.value.strip()
        
        if not tiene_modelo_dropdown and not tiene_modelo_texto:
            return False, "Debe seleccionar o escribir un modelo de producto"
        
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
                # Convertir modelo a string antes de hacer lower() para evitar errores con tipos int
                modelo_ubicacion = str(ubicacion.get('modelo', '')).lower()
                if modelo_ubicacion == tipo_producto.lower():
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
        
        # Obtener el tipo de producto desde el dropdown o campo de texto
        tipo_producto = ""
        if dropdown_modelos.value and dropdown_modelos.value.strip():
            tipo_producto = dropdown_modelos.value.strip()
        elif campo_buscar_tipo.value and campo_buscar_tipo.value.strip():
            tipo_producto = campo_buscar_tipo.value.strip()
        
        if not tipo_producto:
            page.open(ft.SnackBar(
                content=ft.Text("Debe seleccionar o escribir un modelo de producto", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return
        
        # NUEVA VALIDACIÓN: Verificar que el modelo existe en el inventario
        modelo_existe_en_inventario = False
        for producto in productos_disponibles:
            # Convertir modelo a string antes de hacer lower() para evitar errores con tipos int
            modelo_producto = str(producto.get('modelo', '')).lower()
            if modelo_producto == tipo_producto.lower():
                modelo_existe_en_inventario = True
                break
        
        if not modelo_existe_en_inventario:
            page.open(ft.SnackBar(
                content=ft.Text(
                    f"❌ El modelo '{tipo_producto}' no existe en el inventario.\n"
                    f"Solo puede asignar ubicaciones a productos que ya estén registrados en el sistema.",
                    color=tema.TEXT_COLOR
                ),
                bgcolor=tema.ERROR_COLOR,
                duration=5000
            ))
            return
        
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
            
            # Invalidar cache para refrescar datos
            from app.utils.cache_firebase import cache_firebase
            cache_firebase.invalidar_cache_ubicaciones()
            
            # Sincronizar automáticamente las cantidades en el inventario
            from app.utils.sincronizacion_inventario import sincronizar_modelo
            await sincronizar_modelo(tipo_producto)
            
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
                ft.Text("Basado en estructura: Modelo → Almacén → Estantería", 
                        color=tema.TEXT_SECONDARY, size=12),
                ft.Text("Solo se pueden asignar ubicaciones a modelos que ya existan en el inventario", 
                        color=tema.WARNING_COLOR, size=11, weight=ft.FontWeight.W_500),
                ft.Divider(color=tema.DIVIDER_COLOR),
                dropdown_modelos,  # Dropdown con modelos disponibles
                campo_buscar_tipo,  # Campo alternativo de búsqueda de tipo
                campo_almacen,
                campo_estanteria,
                campo_cantidad,
                campo_observaciones,
            ], spacing=15),
            width=520,
            height=550,  # Altura ajustada para incluir dropdown
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
    """Obtener todas las ubicaciones de productos desde Firebase con cache optimizado"""
    try:
        from app.utils.cache_firebase import cache_firebase
        
        # Usar cache optimizado
        ubicaciones = await cache_firebase.obtener_ubicaciones()
        return ubicaciones
        
    except Exception as e:
        print(f"Error al obtener ubicaciones de productos: {e}")
        # Datos de ejemplo como fallback
        return [
            {
                'firebase_id': '1',
                'modelo': 'Cadena 25',
                'almacen': 'Almacén Principal',
                'estanteria': '2A',
                'cantidad': 5,
                'fecha_asignacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'observaciones': 'Asignación inicial'
            },
            {
                'firebase_id': '2', 
                'modelo': 'Rodamiento 6204',
                'almacen': 'Almacén Secundario',
                'estanteria': '1B',
                'cantidad': 3,
                'fecha_asignacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'observaciones': 'Stock de repuesto'
            }
        ]

async def eliminar_ubicacion_producto_firebase(ubicacion_id, page):
    """Eliminar ubicación de producto de Firebase"""
    try:
        # Primero obtener el modelo antes de eliminar
        doc_ref = db.collection("ubicaciones").document(ubicacion_id)
        doc = doc_ref.get()
        modelo_eliminado = None
        
        if doc.exists:
            modelo_eliminado = doc.to_dict().get('modelo')
        
        # Eliminar de Firebase
        doc_ref.delete()
        
        # Invalidar cache para refrescar datos
        from app.utils.cache_firebase import cache_firebase
        cache_firebase.invalidar_cache_ubicaciones()
        
        # Sincronizar automáticamente las cantidades en el inventario
        if modelo_eliminado:
            from app.utils.sincronizacion_inventario import sincronizar_modelo
            await sincronizar_modelo(modelo_eliminado)
        
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
