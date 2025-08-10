import flet as ft
import asyncio
from app.utils.temas import GestorTemas
from app.funciones.sesiones import SesionManager
from app.utils.historial import GestorHistorial
from conexiones.firebase import db
from datetime import datetime
import uuid

async def crear_movimiento_ubicacion_dialog(page, callback_actualizar=None):
    """Crear diálogo específico SOLO para traslados físicos entre ubicaciones"""
    tema = GestorTemas.obtener_tema()
    
    # Variables para ubicaciones disponibles
    ubicaciones_disponibles = []
    
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
            ubicaciones_disponibles = []
    
    await cargar_ubicaciones_disponibles()
    
    # Texto informativo
    texto_info = ft.Text(
        "[PROCESO] Traslado físico entre ubicaciones\n" +
        "Mueva productos de una ubicación a otra sin cambiar la cantidad total de inventario",
        size=14,
        color=tema.TEXT_SECONDARY,
        text_align=ft.TextAlign.CENTER
    )
    
    # Dropdown para seleccionar ubicación origen
    dropdown_ubicacion_origen = ft.Dropdown(
        label="Ubicación de origen",
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        helper_text="Seleccione de dónde trasladar el producto",
        options=[
            ft.dropdown.Option(
                key=u.get('firebase_id', ''),
                text=f"{u.get('modelo', '')} - Alm.{u.get('almacen', '')}/{u.get('estanteria', '')} (Stock: {u.get('cantidad', 0)})"
            ) for u in ubicaciones_disponibles if u.get('cantidad', 0) > 0
        ]
    )
    
    # Campos para nueva ubicación destino
    campo_nuevo_almacen = ft.Dropdown(
        label="Almacén destino",
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        helper_text="Almacén donde colocar el producto",
        options=[
            ft.dropdown.Option(key="1", text="Almacén 1"),
            ft.dropdown.Option(key="2", text="Almacén 2"),
            ft.dropdown.Option(key="3", text="Almacén 3"),
        ]
    )
    
    campo_nueva_estanteria = ft.TextField(
        label="Estantería destino",
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        helper_text="Ejemplo: A1, B2, C3..."
    )
    
    campo_cantidad_mover = ft.TextField(
        label="Cantidad a trasladar",
        width=200,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        keyboard_type=ft.KeyboardType.NUMBER,
        helper_text="Cantidad que desea mover"
    )
    
    campo_motivo = ft.TextField(
        label="Motivo del traslado",
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        multiline=True,
        max_lines=2,
        helper_text="Reorganización, optimización de espacio, etc."
    )
    
    async def ejecutar_movimiento_ubicacion(e):
        """Ejecutar el movimiento entre ubicaciones"""
        try:
            # Validaciones
            if not dropdown_ubicacion_origen.value:
                page.open(ft.SnackBar(
                    content=ft.Text("[ERROR] Debe seleccionar una ubicación origen", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))
                return
            
            if not campo_nuevo_almacen.value or not campo_nueva_estanteria.value:
                page.open(ft.SnackBar(
                    content=ft.Text("[ERROR] Debe especificar almacén y estantería de destino", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))
                return
            
            if not campo_cantidad_mover.value:
                page.open(ft.SnackBar(
                    content=ft.Text("[ERROR] Debe especificar la cantidad a mover", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))
                return
            
            # Obtener datos de la ubicación origen
            ubicacion_origen_id = dropdown_ubicacion_origen.value
            ubicacion_origen = next((u for u in ubicaciones_disponibles if u.get('firebase_id') == ubicacion_origen_id), None)
            
            if not ubicacion_origen:
                page.open(ft.SnackBar(
                    content=ft.Text("[ERROR] Ubicación origen no encontrada", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))
                return
            
            cantidad_a_mover = int(campo_cantidad_mover.value)
            cantidad_actual = ubicacion_origen.get('cantidad', 0)
            
            if cantidad_a_mover <= 0 or cantidad_a_mover > cantidad_actual:
                page.open(ft.SnackBar(
                    content=ft.Text(f"[ERROR] Cantidad inválida. Disponible: {cantidad_actual}", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))
                return
            
            # Crear nueva ubicación destino
            nueva_ubicacion = {
                "modelo": ubicacion_origen.get('modelo', ''),
                "nombre_producto": ubicacion_origen.get('nombre_producto', ''),
                "tipo_producto": ubicacion_origen.get('tipo_producto', ''),
                "almacen": campo_nuevo_almacen.value.strip(),
                "estanteria": campo_nueva_estanteria.value.strip(),
                "cantidad": cantidad_a_mover,
                "observaciones": campo_motivo.value.strip() if campo_motivo.value else f"Movido desde {ubicacion_origen.get('almacen', '')}/{ubicacion_origen.get('estanteria', '')}",
                "fecha_asignacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "usuario_asignacion": SesionManager.obtener_usuario_actual().get('username', 'Usuario') if SesionManager.obtener_usuario_actual() else 'Sistema'
            }
            
            # Registrar movimiento en colección de movimientos
            movimiento = {
                "tipo": "movimiento_ubicacion",
                "modelo": ubicacion_origen.get('modelo', ''),
                "cantidad": cantidad_a_mover,
                "ubicacion_origen": f"{ubicacion_origen.get('almacen', '')}/{ubicacion_origen.get('estanteria', '')}",
                "ubicacion_destino": f"{campo_nuevo_almacen.value}/{campo_nueva_estanteria.value}",
                "motivo": campo_motivo.value.strip() if campo_motivo.value else "Traslado entre ubicaciones",
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "usuario": SesionManager.obtener_usuario_actual().get('username', 'Usuario') if SesionManager.obtener_usuario_actual() else 'Sistema'
            }
            
            # Guardar nueva ubicación
            db.collection("ubicaciones").add(nueva_ubicacion)
            
            # Guardar registro de movimiento
            db.collection("movimientos").add(movimiento)
            
            # *** INVALIDAR CACHE PARA FORZAR ACTUALIZACIÓN ***
            from app.utils.cache_firebase import cache_firebase
            cache_firebase.invalidar_cache_ubicaciones()
            cache_firebase.invalidar_cache_movimientos()  # ¡IMPORTANTE! Invalidar movimientos para que aparezcan en la vista
            
            # Actualizar ubicación origen
            doc_ref = db.collection('ubicaciones').document(ubicacion_origen_id)
            nueva_cantidad = cantidad_actual - cantidad_a_mover
            
            if nueva_cantidad > 0:
                doc_ref.update({
                    'cantidad': nueva_cantidad,
                    'fecha_modificacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            else:
                # Si se movió todo, eliminar ubicación original
                doc_ref.delete()
            
            # Invalidar caches
            from app.utils.cache_firebase import cache_firebase
            cache_firebase.invalidar_cache_ubicaciones()
            cache_firebase.invalidar_cache_movimientos()  # ¡IMPORTANTE! Invalidar movimientos para que aparezcan en la vista
            
            # Registrar en historial
            gestor_historial = GestorHistorial()
            usuario_actual = SesionManager.obtener_usuario_actual()
            
            await gestor_historial.agregar_actividad(
                tipo="movimiento_ubicacion",
                descripcion=f"Movió {cantidad_a_mover}x {ubicacion_origen.get('modelo', '')} de {ubicacion_origen.get('almacen', '')}/{ubicacion_origen.get('estanteria', '')} → {campo_nuevo_almacen.value}/{campo_nueva_estanteria.value}",
                usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
            )
            
            page.close(dialogo_movimiento)
            page.open(ft.SnackBar(
                content=ft.Text("[OK] Movimiento realizado exitosamente", color=tema.TEXT_COLOR),
                bgcolor=tema.SUCCESS_COLOR
            ))
            
            # Actualizar vistas
            if callback_actualizar:
                await callback_actualizar()
                
        except Exception as error:
            print(f"Error al realizar movimiento: {error}")
            page.open(ft.SnackBar(
                content=ft.Text(f"[ERROR] Error al realizar movimiento: {str(error)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
    
    # Diálogo de movimiento
    dialogo_movimiento = ft.AlertDialog(
        title=ft.Text("Traslado entre Ubicaciones", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content=ft.Container(
            content=ft.Column([
                texto_info,
                ft.Divider(color=tema.DIVIDER_COLOR),
                dropdown_ubicacion_origen,
                ft.Container(height=10),
                ft.Text("Ubicación destino:", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD),
                campo_nuevo_almacen,
                campo_nueva_estanteria,
                campo_cantidad_mover,
                campo_motivo,
                ft.Container(height=20),  # Espacio adicional antes de los botones
            ], spacing=15),
            width=450,
            height=500,  # Aumentamos la altura para evitar superposición
            padding=ft.Padding(20, 20, 20, 20)
        ),
        actions=[
            ft.ElevatedButton(
                "Realizar Movimiento",
                style=ft.ButtonStyle(
                    bgcolor=tema.BUTTON_SUCCESS_BG,
                    color=tema.BUTTON_TEXT,
                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                ),
                on_click=ejecutar_movimiento_ubicacion
            ),
            ft.TextButton(
                "Cancelar",
                style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                on_click=lambda e: page.close(dialogo_movimiento)
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,  # Alinear botones a la derecha
        modal=True,
    )
    
    page.open(dialogo_movimiento)
    page.update()

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
            
            # *** INVALIDAR CACHE PARA FORZAR ACTUALIZACIÓN ***
            from app.utils.cache_firebase import cache_firebase
            cache_firebase.invalidar_cache_ubicaciones()
            cache_firebase.invalidar_cache_movimientos()  # ¡IMPORTANTE! Invalidar movimientos para que aparezcan en la vista
            
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
        # Obtener TODOS los movimientos sin filtros problemáticos
        print("[BUSCAR] Consultando TODOS los movimientos de Firebase...")
        movimientos_ref = db.collection('movimientos')
        movimientos = movimientos_ref.stream()
        
        movimientos_data = []
        tipos_encontrados = []
        
        for movimiento in movimientos:
            data = movimiento.to_dict()
            data['firebase_id'] = movimiento.id
            
            # Normalizar el formato de fecha para consistencia
            if 'fecha' in data and 'fecha_movimiento' not in data:
                data['fecha_movimiento'] = data['fecha']
            elif 'fecha_movimiento' in data and 'fecha' not in data:
                data['fecha'] = data['fecha_movimiento']
            
            # Log para debug
            tipo_mov = data.get('tipo', 'sin_tipo')
            if tipo_mov not in tipos_encontrados:
                tipos_encontrados.append(tipo_mov)
                
            movimientos_data.append(data)
        
        # Ordenar por fecha después de obtener todos los datos
        try:
            movimientos_data.sort(key=lambda x: x.get('fecha_movimiento', ''), reverse=True)
        except Exception as e:
            print(f"[WARN] No se pudo ordenar movimientos: {e}")
        
        print(f"[CHART] MOVIMIENTOS ENCONTRADOS: {len(movimientos_data)} registros")
        print(f"[LISTA] TIPOS DETECTADOS: {tipos_encontrados}")
        
        return movimientos_data
        
    except Exception as e:
        print(f"[ERROR] Error al obtener movimientos: {e}")
        return []
