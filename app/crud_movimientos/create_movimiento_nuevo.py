import flet as ft
import asyncio
from app.utils.temas import GestorTemas
from app.funciones.sesiones import SesionManager
from app.utils.historial import GestorHistorial
from conexiones.firebase import db
from datetime import datetime
import uuid

async def crear_movimiento_dialog(page, callback_actualizar=None):
    """Crear diálogo para registrar movimiento de productos"""
    tema = GestorTemas.obtener_tema()
    
    # Variables para los productos y ubicaciones
    productos_disponibles = []
    ubicaciones_disponibles = []
    
    async def cargar_productos_disponibles():
        """Cargar productos desde Firebase"""
        nonlocal productos_disponibles
        try:
            productos_ref = db.collection('productos')
            productos = productos_ref.stream()
            
            productos_disponibles = []
            for producto in productos:
                data = producto.to_dict()
                data['firebase_id'] = producto.id
                productos_disponibles.append(data)
        except Exception as e:
            print(f"Error al cargar productos: {e}")
            # Datos de ejemplo
            productos_disponibles = [
                {"modelo": "LAP001", "nombre": "Laptop Dell", "cantidad": 10},
                {"modelo": "MOU002", "nombre": "Mouse Logitech", "cantidad": 25}
            ]
    
    async def cargar_ubicaciones_disponibles():
        """Cargar ubicaciones desde Firebase"""
        nonlocal ubicaciones_disponibles
        try:
            ubicaciones_ref = db.collection('ubicaciones')
            ubicaciones = ubicaciones_ref.stream()
            
            ubicaciones_disponibles = []
            for ubicacion in ubicaciones:
                data = ubicacion.to_dict()
                data['firebase_id'] = ubicacion.id
                ubicaciones_disponibles.append(data)
        except Exception as e:
            print(f"Error al cargar ubicaciones: {e}")
            # Datos de ejemplo
            ubicaciones_disponibles = [
                {"almacen": "Almacén Principal", "ubicacion": "Estante A-3"},
                {"almacen": "Almacén Secundario", "ubicacion": "Cajón B-1"}
            ]
    
    # Cargar datos iniciales
    await cargar_productos_disponibles()
    await cargar_ubicaciones_disponibles()
    
    # Campos del formulario
    dropdown_producto = ft.Dropdown(
        label="Seleccionar producto",
        width=350,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        options=[
            ft.dropdown.Option(
                key=p.get('modelo', ''),
                text=f"{p.get('modelo', '')} - {p.get('nombre', '')} (Stock: {p.get('cantidad', 0)})"
            ) for p in productos_disponibles
        ]
    )
    
    dropdown_origen = ft.Dropdown(
        label="Ubicación origen",
        width=350,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        options=[
            ft.dropdown.Option(
                key=f"{u.get('almacen', '')}|{u.get('ubicacion', '')}",
                text=f"{u.get('almacen', '')} → {u.get('ubicacion', '')}"
            ) for u in ubicaciones_disponibles
        ]
    )
    
    dropdown_destino = ft.Dropdown(
        label="Ubicación destino",
        width=350,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        options=[
            ft.dropdown.Option(
                key=f"{u.get('almacen', '')}|{u.get('ubicacion', '')}",
                text=f"{u.get('almacen', '')} → {u.get('ubicacion', '')}"
            ) for u in ubicaciones_disponibles
        ]
    )
    
    campo_cantidad = ft.TextField(
        label="Cantidad a mover",
        width=350,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        keyboard_type=ft.KeyboardType.NUMBER
    )
    
    campo_motivo = ft.TextField(
        label="Motivo del movimiento",
        width=350,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        multiline=True,
        max_lines=3
    )
    
    dropdown_tipo = ft.Dropdown(
        label="Tipo de movimiento",
        width=350,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        value="Traslado",
        options=[
            ft.dropdown.Option("Traslado", "Traslado entre ubicaciones"),
            ft.dropdown.Option("Entrada", "Entrada de inventario"),
            ft.dropdown.Option("Salida", "Salida de inventario"),
            ft.dropdown.Option("Ajuste", "Ajuste de inventario")
        ]
    )
    
    def validar_movimiento():
        """Validar datos del movimiento"""
        if not dropdown_producto.value:
            return False, "Debe seleccionar un producto"
        
        if not dropdown_origen.value:
            return False, "Debe seleccionar ubicación origen"
        
        if not dropdown_destino.value:
            return False, "Debe seleccionar ubicación destino"
        
        if dropdown_origen.value == dropdown_destino.value:
            return False, "La ubicación origen y destino no pueden ser iguales"
        
        if not campo_cantidad.value or not campo_cantidad.value.isdigit():
            return False, "Debe ingresar una cantidad válida"
        
        cantidad = int(campo_cantidad.value)
        if cantidad <= 0:
            return False, "La cantidad debe ser mayor a 0"
        
        # Verificar stock disponible
        producto_data = next((p for p in productos_disponibles if p.get('modelo') == dropdown_producto.value), None)
        if producto_data and cantidad > producto_data.get('cantidad', 0):
            return False, f"Stock insuficiente. Disponible: {producto_data.get('cantidad', 0)}"
        
        return True, "OK"
    
    async def registrar_movimiento(e):
        """Registrar movimiento en Firebase"""
        es_valido, mensaje = validar_movimiento()
        if not es_valido:
            page.open(ft.SnackBar(
                content=ft.Text(mensaje, color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return
        
        try:
            # Preparar datos del movimiento
            origen_partes = dropdown_origen.value.split('|')
            destino_partes = dropdown_destino.value.split('|')
            
            movimiento = {
                "id": str(uuid.uuid4()),
                "producto_modelo": dropdown_producto.value,
                "cantidad": int(campo_cantidad.value),
                "ubicacion_origen": {
                    "almacen": origen_partes[0],
                    "ubicacion": origen_partes[1] if len(origen_partes) > 1 else ""
                },
                "ubicacion_destino": {
                    "almacen": destino_partes[0],
                    "ubicacion": destino_partes[1] if len(destino_partes) > 1 else ""
                },
                "tipo_movimiento": dropdown_tipo.value,
                "motivo": campo_motivo.value.strip(),
                "fecha_movimiento": datetime.now().isoformat(),
                "estado": "Completado",
                "usuario": SesionManager.obtener_usuario_actual().get('username', 'Sistema') if SesionManager.obtener_usuario_actual() else 'Sistema'
            }
            
            # Guardar en Firebase
            db.collection("movimientos").add(movimiento)
            
            # Registrar en historial
            gestor_historial = GestorHistorial()
            usuario_actual = SesionManager.obtener_usuario_actual()
            
            await gestor_historial.agregar_actividad(
                tipo="movimiento_producto",
                descripcion=f"Movió {campo_cantidad.value} unidades de {dropdown_producto.value} desde {origen_partes[0]} a {destino_partes[0]}",
                usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
            )
            
            page.open(ft.SnackBar(
                content=ft.Text("Movimiento registrado exitosamente", color=tema.TEXT_COLOR),
                bgcolor=tema.SUCCESS_COLOR
            ))
            
            # Cerrar diálogo y actualizar
            page.close(dialogo_movimiento)
            if callback_actualizar:
                await callback_actualizar()
                
        except Exception as ex:
            page.open(ft.SnackBar(
                content=ft.Text(f"Error al registrar movimiento: {str(ex)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
    
    dialogo_movimiento = ft.AlertDialog(
        title=ft.Text("Registrar Movimiento", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content=ft.Container(
            content=ft.Column([
                dropdown_producto,
                dropdown_origen,
                dropdown_destino,
                campo_cantidad,
                dropdown_tipo,
                campo_motivo,
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            width=400,
            height=500,
            padding=ft.Padding(10, 10, 10, 10)
        ),
        actions=[
            ft.ElevatedButton(
                "Registrar Movimiento",
                style=ft.ButtonStyle(
                    bgcolor=tema.BUTTON_SUCCESS_BG,
                    color=tema.BUTTON_TEXT,
                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                ),
                on_click=registrar_movimiento
            ),
            ft.TextButton(
                "Cancelar",
                style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                on_click=lambda e: page.close(dialogo_movimiento)
            ),
        ],
        modal=True,
    )
    
    page.open(dialogo_movimiento)
    page.update()

async def obtener_movimientos_firebase():
    """Obtener historial de movimientos desde Firebase"""
    try:
        movimientos_ref = db.collection('movimientos').order_by('fecha_movimiento', direction='DESCENDING')
        movimientos = movimientos_ref.stream()
        
        movimientos_data = []
        for movimiento in movimientos:
            data = movimiento.to_dict()
            data['firebase_id'] = movimiento.id
            movimientos_data.append(data)
        
        return movimientos_data
        
    except Exception as e:
        print(f"Error al obtener movimientos: {e}")
        # Datos de ejemplo
        return [
            {
                'firebase_id': '1',
                'producto_modelo': 'LAP001',
                'cantidad': 5,
                'ubicacion_origen': {'almacen': 'Almacén Principal', 'ubicacion': 'Estante A-3'},
                'ubicacion_destino': {'almacen': 'Almacén Secundario', 'ubicacion': 'Estante B-1'},
                'tipo_movimiento': 'Traslado',
                'motivo': 'Reorganización de inventario',
                'fecha_movimiento': '2025-01-15T10:30:00',
                'estado': 'Completado',
                'usuario': 'admin'
            }
        ]
