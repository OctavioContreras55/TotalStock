import flet as ft
import asyncio
from app.utils.temas import GestorTemas
from app.funciones.sesiones import SesionManager
from app.utils.historial import GestorHistorial
from conexiones.firebase import db
from datetime import datetime
import uuid

async def crear_ubicacion_dialog(page, callback_actualizar=None):
    """Crear diálogo para agregar nueva ubicación"""
    tema = GestorTemas.obtener_tema()
    
    # Campos del formulario
    campo_almacen = ft.Dropdown(
        label="Almacén",
        width=300,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        options=[
            ft.dropdown.Option("Almacén Principal"),
            ft.dropdown.Option("Almacén Secundario"),
            ft.dropdown.Option("Almacén de Repuestos"),
            ft.dropdown.Option("Bodega Externa"),
        ]
    )
    
    campo_ubicacion = ft.TextField(
        label="Ubicación específica (ej: Estante A-3, Nivel 2)",
        width=300,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    
    campo_descripcion = ft.TextField(
        label="Descripción (opcional)",
        width=300,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY),
        multiline=True,
        max_lines=3
    )
    
    campo_capacidad = ft.TextField(
        label="Capacidad máxima (opcional)",
        width=300,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY),
        keyboard_type=ft.KeyboardType.NUMBER
    )
    
    def validar_campos():
        """Validar que los campos requeridos estén completos"""
        if not campo_almacen.value or not campo_almacen.value.strip():
            return False, "Debe seleccionar un almacén"
        
        if not campo_ubicacion.value or not campo_ubicacion.value.strip():
            return False, "Debe especificar la ubicación"
        
        return True, "OK"
    
    async def crear_ubicacion(e):
        """Crear nueva ubicación"""
        es_valido, mensaje = validar_campos()
        if not es_valido:
            page.open(ft.SnackBar(
                content=ft.Text(mensaje, color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return
        
        try:
            # Crear ubicación
            ubicacion = {
                "id": str(uuid.uuid4()),
                "almacen": campo_almacen.value.strip(),
                "ubicacion": campo_ubicacion.value.strip(),
                "descripcion": campo_descripcion.value.strip() if campo_descripcion.value else "",
                "capacidad_maxima": int(campo_capacidad.value) if campo_capacidad.value and campo_capacidad.value.isdigit() else None,
                "productos_actuales": [],
                "capacidad_utilizada": 0,
                "fecha_creacion": datetime.now().isoformat(),
                "estado": "Activo"
            }
            
            # Guardar en Firebase
            db.collection("ubicaciones").add(ubicacion)
            
            # Registrar actividad
            gestor_historial = GestorHistorial()
            usuario_actual = SesionManager.obtener_usuario_actual()
            
            await gestor_historial.agregar_actividad(
                tipo="crear_ubicacion",
                descripcion=f"Creó ubicación: {ubicacion['almacen']} → {ubicacion['ubicacion']}",
                usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
            )
            
            page.open(ft.SnackBar(
                content=ft.Text("Ubicación creada exitosamente", color=tema.TEXT_COLOR),
                bgcolor=tema.SUCCESS_COLOR
            ))
            
            # Cerrar diálogo y actualizar tabla
            page.close(dialogo_crear)
            if callback_actualizar:
                await callback_actualizar()
                
        except Exception as ex:
            page.open(ft.SnackBar(
                content=ft.Text(f"Error al crear ubicación: {str(ex)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
    
    dialogo_crear = ft.AlertDialog(
        title=ft.Text("Crear Nueva Ubicación", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content=ft.Container(
            content=ft.Column([
                campo_almacen,
                campo_ubicacion,
                campo_descripcion,
                campo_capacidad,
            ], spacing=15),
            width=350,
            height=350,
            padding=ft.Padding(10, 10, 10, 10)
        ),
        actions=[
            ft.ElevatedButton(
                "Crear Ubicación",
                style=ft.ButtonStyle(
                    bgcolor=tema.BUTTON_SUCCESS_BG,
                    color=tema.BUTTON_TEXT,
                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                ),
                on_click=crear_ubicacion
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

async def obtener_ubicaciones_firebase():
    """Obtener todas las ubicaciones desde Firebase"""
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
        print(f"Error al obtener ubicaciones: {e}")
        # Datos de ejemplo como fallback
        return [
            {
                'firebase_id': '1',
                'almacen': 'Almacén Principal',
                'ubicacion': 'Estante A-3, Nivel 2',
                'descripcion': 'Zona de equipos de cómputo',
                'capacidad_maxima': 20,
                'capacidad_utilizada': 15,
                'productos_actuales': ['LAP001', 'MON001'],
                'estado': 'Activo'
            },
            {
                'firebase_id': '2',
                'almacen': 'Almacén Secundario',
                'ubicacion': 'Cajón B-1',
                'descripcion': 'Accesorios pequeños',
                'capacidad_maxima': 50,
                'capacidad_utilizada': 25,
                'productos_actuales': ['MOU002'],
                'estado': 'Activo'
            }
        ]

async def eliminar_ubicacion_firebase(ubicacion_id, page):
    """Eliminar ubicación de Firebase"""
    try:
        # Verificar si la ubicación tiene productos asignados
        # En una implementación real, verificaríamos en la colección de productos
        
        # Eliminar de Firebase
        db.collection("ubicaciones").document(ubicacion_id).delete()
        
        # Registrar actividad
        gestor_historial = GestorHistorial()
        usuario_actual = SesionManager.obtener_usuario_actual()
        
        await gestor_historial.agregar_actividad(
            tipo="eliminar_ubicacion",
            descripcion=f"Eliminó ubicación con ID: {ubicacion_id}",
            usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
        )
        
        return True, "Ubicación eliminada exitosamente"
        
    except Exception as e:
        print(f"Error al eliminar ubicación: {e}")
        return False, f"Error al eliminar ubicación: {str(e)}"
