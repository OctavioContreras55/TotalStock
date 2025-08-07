import flet as ft
import asyncio
from app.utils.temas import GestorTemas
from app.funciones.sesiones import SesionManager
from app.utils.historial import GestorHistorial
from conexiones.firebase import db
from datetime import datetime
import uuid

async def crear_movimiento_inventario_dialog(page, callback_actualizar=None):
    """Crear diálogo inteligente para movimientos de inventario"""
    tema = GestorTemas.obtener_tema()
    
    # Variables globales para datos
    productos_disponibles = []
    ubicaciones_disponibles = []
    
    async def cargar_datos_iniciales():
        """Cargar productos y ubicaciones desde Firebase"""
        nonlocal productos_disponibles, ubicaciones_disponibles
        try:
            # Cargar productos
            productos_ref = db.collection('productos')
            productos = productos_ref.stream()
            productos_disponibles = []
            for producto in productos:
                data = producto.to_dict()
                data['firebase_id'] = producto.id
                productos_disponibles.append(data)
            
            # Cargar ubicaciones
            ubicaciones_ref = db.collection('ubicaciones')
            ubicaciones = ubicaciones_ref.stream()
            ubicaciones_disponibles = []
            for ubicacion in ubicaciones:
                data = ubicacion.to_dict()
                data['firebase_id'] = ubicacion.id
                ubicaciones_disponibles.append(data)
                
        except Exception as e:
            print(f"Error al cargar datos: {e}")
    
    await cargar_datos_iniciales()
    
    # Dropdown tipo de movimiento (siempre visible)
    dropdown_tipo = ft.Dropdown(
        label="Tipo de movimiento",
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        options=[
            ft.dropdown.Option(key="entrada", text="Entrada de inventario"),
            ft.dropdown.Option(key="salida", text="Salida de inventario"),
            ft.dropdown.Option(key="ajuste", text="Ajuste de inventario"),
        ],
        on_change=lambda e: actualizar_campos_segun_tipo()
    )
    
    # Campos que cambian según el tipo
    campo_producto = ft.Dropdown(
        label="Seleccionar producto",
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        visible=False
    )
    
    campo_almacen = ft.Dropdown(
        label="Almacén",
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        options=[
            ft.dropdown.Option(key="1", text="Almacén 1"),
            ft.dropdown.Option(key="2", text="Almacén 2"),
            ft.dropdown.Option(key="3", text="Almacén 3"),
        ],
        visible=False
    )
    
    campo_estanteria = ft.TextField(
        label="Estantería",
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        helper_text="Ejemplo: A1, B2, C3...",
        visible=False
    )
    
    campo_cantidad = ft.TextField(
        label="Cantidad",
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        keyboard_type=ft.KeyboardType.NUMBER,
        visible=False
    )
    
    campo_comentarios = ft.TextField(
        label="Comentarios",
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        multiline=True,
        max_lines=3,
        helper_text="Proveedor, motivo, etc. (opcional)",
        visible=False
    )
    
    # Campos específicos para salida
    campo_ubicacion_origen = ft.Dropdown(
        label="Ubicación de origen (con existencias)",
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        helper_text="Solo ubicaciones con stock disponible",
        visible=False
    )
    
    # Texto informativo que cambia según el tipo
    texto_info = ft.Text(
        "",
        size=14,
        color=tema.TEXT_SECONDARY,
        visible=False
    )
    
    def actualizar_campos_segun_tipo():
        """Actualizar campos visibles según el tipo de movimiento seleccionado"""
        tipo_seleccionado = dropdown_tipo.value
        
        # Ocultar todos los campos primero
        campos = [campo_producto, campo_almacen, campo_estanteria, campo_cantidad, 
                 campo_comentarios, campo_ubicacion_origen, texto_info]
        for campo in campos:
            campo.visible = False
        
        if tipo_seleccionado == "entrada":
            # ENTRADA: Surtir mercancía
            texto_info.value = "➕ Entrada de inventario: Agregue productos recibidos del proveedor"
            texto_info.color = tema.SUCCESS_COLOR
            
            # Campos para entrada
            campo_producto.visible = True
            campo_producto.options = [
                ft.dropdown.Option(
                    key=p.get('firebase_id', ''),
                    text=f"{p.get('modelo', 'N/A')} - {p.get('marca', 'N/A')}"
                ) for p in productos_disponibles
            ]
            campo_producto.label = "Producto a recibir"
            
            campo_almacen.visible = True
            campo_estanteria.visible = True
            campo_cantidad.visible = True
            campo_cantidad.label = "Cantidad recibida"
            campo_comentarios.visible = True
            campo_comentarios.helper_text = "Proveedor, lote, factura, etc."
            
        elif tipo_seleccionado == "salida":
            # SALIDA: Vender/entregar mercancía
            texto_info.value = "➖ Salida de inventario: Registre productos vendidos o entregados"
            texto_info.color = tema.WARNING_COLOR
            
            # Campos para salida
            campo_ubicacion_origen.visible = True
            campo_ubicacion_origen.options = [
                ft.dropdown.Option(
                    key=u.get('firebase_id', ''),
                    text=f"{u.get('modelo', 'N/A')} - Alm.{u.get('almacen', '')}/{u.get('estanteria', '')} (Stock: {u.get('cantidad', 0)})"
                ) for u in ubicaciones_disponibles if u.get('cantidad', 0) > 0
            ]
            
            campo_cantidad.visible = True
            campo_cantidad.label = "Cantidad a entregar"
            campo_comentarios.visible = True
            campo_comentarios.helper_text = "Cliente, factura, destino, etc."
            
        elif tipo_seleccionado == "ajuste":
            # AJUSTE: Correcciones de inventario
            texto_info.value = "🔧 Ajuste de inventario: Corrija diferencias por conteo físico"
            texto_info.color = tema.PRIMARY_COLOR
            
            # Campos para ajuste
            campo_ubicacion_origen.visible = True
            campo_ubicacion_origen.options = [
                ft.dropdown.Option(
                    key=u.get('firebase_id', ''),
                    text=f"{u.get('modelo', 'N/A')} - Alm.{u.get('almacen', '')}/{u.get('estanteria', '')} (Stock actual: {u.get('cantidad', 0)})"
                ) for u in ubicaciones_disponibles
            ]
            campo_ubicacion_origen.label = "Ubicación a ajustar"
            
            campo_cantidad.visible = True
            campo_cantidad.label = "Nueva cantidad correcta"
            campo_cantidad.helper_text = "Cantidad real después del conteo físico"
            campo_comentarios.visible = True
            campo_comentarios.helper_text = "Motivo del ajuste (merma, error de conteo, etc.)"
        
        # Mostrar texto informativo
        texto_info.visible = True
        page.update()
    
    async def ejecutar_movimiento():
        """Ejecutar el movimiento según el tipo seleccionado"""
        try:
            tipo = dropdown_tipo.value
            if not tipo:
                page.open(ft.SnackBar(
                    content=ft.Text("⚠️ Seleccione un tipo de movimiento", color=tema.TEXT_COLOR),
                    bgcolor=tema.WARNING_COLOR
                ))
                return
            
            # Validaciones básicas
            cantidad = campo_cantidad.value
            if not cantidad or not cantidad.isdigit() or int(cantidad) <= 0:
                page.open(ft.SnackBar(
                    content=ft.Text("⚠️ Ingrese una cantidad válida", color=tema.TEXT_COLOR),
                    bgcolor=tema.WARNING_COLOR
                ))
                return
            
            cantidad = int(cantidad)
            usuario_actual = SesionManager.obtener_usuario_actual()
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if tipo == "entrada":
                await procesar_entrada(cantidad, usuario_actual, fecha_actual)
            elif tipo == "salida":
                await procesar_salida(cantidad, usuario_actual, fecha_actual)
            elif tipo == "ajuste":
                await procesar_ajuste(cantidad, usuario_actual, fecha_actual)
                
        except Exception as e:
            print(f"Error en movimiento: {e}")
            page.open(ft.SnackBar(
                content=ft.Text(f"❌ Error: {str(e)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
    
    async def procesar_entrada(cantidad, usuario, fecha):
        """Procesar entrada de inventario"""
        producto_id = campo_producto.value
        almacen = campo_almacen.value
        estanteria = campo_estanteria.value
        comentarios = campo_comentarios.value
        
        if not all([producto_id, almacen, estanteria]):
            page.open(ft.SnackBar(
                content=ft.Text("⚠️ Complete todos los campos obligatorios", color=tema.TEXT_COLOR),
                bgcolor=tema.WARNING_COLOR
            ))
            return
        
        # Buscar el producto
        producto = next((p for p in productos_disponibles if p.get('firebase_id') == producto_id), None)
        if not producto:
            page.open(ft.SnackBar(
                content=ft.Text("❌ Producto no encontrado", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return
        
        # Buscar si ya existe una ubicación para este producto
        ubicacion_existente = None
        for u in ubicaciones_disponibles:
            if (u.get('modelo') == producto.get('modelo') and 
                str(u.get('almacen')) == str(almacen) and 
                u.get('estanteria', '').upper() == estanteria.upper()):
                ubicacion_existente = u
                break
        
        if ubicacion_existente:
            # Actualizar cantidad existente
            nueva_cantidad = ubicacion_existente.get('cantidad', 0) + cantidad
            db.collection('ubicaciones').document(ubicacion_existente['firebase_id']).update({
                'cantidad': nueva_cantidad,
                'fecha_ultima_actualizacion': fecha
            })
        else:
            # Crear nueva ubicación
            nueva_ubicacion = {
                'modelo': producto.get('modelo'),
                'marca': producto.get('marca'),
                'almacen': int(almacen),
                'estanteria': estanteria.upper(),
                'cantidad': cantidad,
                'fecha_creacion': fecha,
                'fecha_ultima_actualizacion': fecha
            }
            db.collection('ubicaciones').add(nueva_ubicacion)
        
        # Actualizar el producto en inventario principal
        nueva_cantidad_producto = producto.get('cantidad', 0) + cantidad
        db.collection('productos').document(producto_id).update({
            'cantidad': nueva_cantidad_producto,
            'fecha_ultima_actualizacion': fecha
        })
        
        # Registrar movimiento
        movimiento = {
            'tipo': 'entrada_inventario',
            'usuario': usuario,
            'modelo': producto.get('modelo'),
            'cantidad': cantidad,
            'almacen_destino': int(almacen),
            'estanteria_destino': estanteria.upper(),
            'comentarios': comentarios,
            'fecha_movimiento': fecha,
            'estado': 'Completado'
        }
        db.collection('movimientos').add(movimiento)
        
        # *** INVALIDAR CACHE PARA FORZAR ACTUALIZACIÓN ***
        from app.utils.cache_firebase import cache_firebase
        cache_firebase.invalidar_cache_productos()
        cache_firebase.invalidar_cache_ubicaciones()
        cache_firebase.invalidar_cache_movimientos()  # ¡IMPORTANTE! Invalidar movimientos para que aparezcan en la vista
        
        page.open(ft.SnackBar(
            content=ft.Text(f"✅ Entrada registrada: +{cantidad} {producto.get('modelo')}", color=tema.TEXT_COLOR),
            bgcolor=tema.SUCCESS_COLOR
        ))
        
        page.close(dialogo_movimiento)
        if callback_actualizar:
            await callback_actualizar()
    
    async def procesar_salida(cantidad, usuario, fecha):
        """Procesar salida de inventario"""
        ubicacion_id = campo_ubicacion_origen.value
        comentarios = campo_comentarios.value
        
        if not ubicacion_id:
            page.open(ft.SnackBar(
                content=ft.Text("⚠️ Seleccione una ubicación de origen", color=tema.TEXT_COLOR),
                bgcolor=tema.WARNING_COLOR
            ))
            return
        
        # Buscar ubicación
        ubicacion = next((u for u in ubicaciones_disponibles if u.get('firebase_id') == ubicacion_id), None)
        if not ubicacion:
            page.open(ft.SnackBar(
                content=ft.Text("❌ Ubicación no encontrada", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return
        
        stock_actual = ubicacion.get('cantidad', 0)
        if cantidad > stock_actual:
            page.open(ft.SnackBar(
                content=ft.Text(f"❌ Stock insuficiente. Disponible: {stock_actual}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return
        
        # Actualizar cantidad en ubicación
        nueva_cantidad = stock_actual - cantidad
        db.collection('ubicaciones').document(ubicacion_id).update({
            'cantidad': nueva_cantidad,
            'fecha_ultima_actualizacion': fecha
        })
        
        # Buscar y actualizar el producto en inventario principal
        producto = next((p for p in productos_disponibles if p.get('modelo') == ubicacion.get('modelo')), None)
        if producto:
            nueva_cantidad_producto = producto.get('cantidad', 0) - cantidad
            db.collection('productos').document(producto['firebase_id']).update({
                'cantidad': nueva_cantidad_producto,
                'fecha_ultima_actualizacion': fecha
            })
        
        # Registrar movimiento
        movimiento = {
            'tipo': 'salida_inventario',
            'usuario': usuario,
            'modelo': ubicacion.get('modelo'),
            'cantidad': cantidad,
            'almacen_origen': ubicacion.get('almacen'),
            'estanteria_origen': ubicacion.get('estanteria'),
            'comentarios': comentarios,
            'fecha_movimiento': fecha,
            'estado': 'Completado'
        }
        db.collection('movimientos').add(movimiento)
        
        # *** INVALIDAR CACHE PARA FORZAR ACTUALIZACIÓN ***
        from app.utils.cache_firebase import cache_firebase
        cache_firebase.invalidar_cache_productos()
        cache_firebase.invalidar_cache_ubicaciones()
        cache_firebase.invalidar_cache_movimientos()  # ¡IMPORTANTE! Invalidar movimientos para que aparezcan en la vista
        
        page.open(ft.SnackBar(
            content=ft.Text(f"✅ Salida registrada: -{cantidad} {ubicacion.get('modelo')}", color=tema.TEXT_COLOR),
            bgcolor=tema.SUCCESS_COLOR
        ))
        
        page.close(dialogo_movimiento)
        if callback_actualizar:
            await callback_actualizar()
    
    async def procesar_ajuste(cantidad, usuario, fecha):
        """Procesar ajuste de inventario"""
        ubicacion_id = campo_ubicacion_origen.value
        comentarios = campo_comentarios.value
        
        if not ubicacion_id:
            page.open(ft.SnackBar(
                content=ft.Text("⚠️ Seleccione una ubicación a ajustar", color=tema.TEXT_COLOR),
                bgcolor=tema.WARNING_COLOR
            ))
            return
        
        # Buscar ubicación
        ubicacion = next((u for u in ubicaciones_disponibles if u.get('firebase_id') == ubicacion_id), None)
        if not ubicacion:
            page.open(ft.SnackBar(
                content=ft.Text("❌ Ubicación no encontrada", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return
        
        stock_anterior = ubicacion.get('cantidad', 0)
        diferencia = cantidad - stock_anterior
        
        # Actualizar cantidad en ubicación
        db.collection('ubicaciones').document(ubicacion_id).update({
            'cantidad': cantidad,
            'fecha_ultima_actualizacion': fecha
        })
        
        # Buscar y actualizar el producto en inventario principal
        producto = next((p for p in productos_disponibles if p.get('modelo') == ubicacion.get('modelo')), None)
        if producto:
            nueva_cantidad_producto = producto.get('cantidad', 0) + diferencia
            db.collection('productos').document(producto['firebase_id']).update({
                'cantidad': nueva_cantidad_producto,
                'fecha_ultima_actualizacion': fecha
            })
        
        # Registrar movimiento
        movimiento = {
            'tipo': 'ajuste_inventario',
            'usuario': usuario,
            'modelo': ubicacion.get('modelo'),
            'cantidad_anterior': stock_anterior,
            'cantidad_nueva': cantidad,
            'diferencia': diferencia,
            'almacen': ubicacion.get('almacen'),
            'estanteria': ubicacion.get('estanteria'),
            'comentarios': comentarios,
            'fecha_movimiento': fecha,
            'estado': 'Completado'
        }
        db.collection('movimientos').add(movimiento)
        
        # *** INVALIDAR CACHE PARA FORZAR ACTUALIZACIÓN ***
        from app.utils.cache_firebase import cache_firebase
        cache_firebase.invalidar_cache_productos()
        cache_firebase.invalidar_cache_ubicaciones()
        cache_firebase.invalidar_cache_movimientos()  # ¡IMPORTANTE! Invalidar movimientos para que aparezcan en la vista
        
        tipo_ajuste = "+" if diferencia > 0 else ""
        page.open(ft.SnackBar(
            content=ft.Text(f"✅ Ajuste registrado: {tipo_ajuste}{diferencia} {ubicacion.get('modelo')}", color=tema.TEXT_COLOR),
            bgcolor=tema.SUCCESS_COLOR
        ))
        
        page.close(dialogo_movimiento)
        if callback_actualizar:
            await callback_actualizar()
    
    # Crear contenedor principal
    contenido_dinamico = ft.Column([
        texto_info,
        dropdown_tipo,
        campo_producto,
        campo_ubicacion_origen,
        campo_almacen,
        campo_estanteria,
        campo_cantidad,
        campo_comentarios,
    ], spacing=15, scroll=ft.ScrollMode.AUTO)
    
    # Diálogo principal
    dialogo_movimiento = ft.AlertDialog(
        title=ft.Text("Movimiento de Inventario", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content=ft.Container(
            content=contenido_dinamico,
            width=450,
            height=500,
            padding=ft.Padding(20, 20, 20, 20)
        ),
        actions=[
            ft.ElevatedButton(
                "Registrar Movimiento",
                style=ft.ButtonStyle(
                    bgcolor=tema.BUTTON_SUCCESS_BG,
                    color=tema.BUTTON_TEXT,
                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                ),
                on_click=lambda e: page.run_task(ejecutar_movimiento)
            ),
            ft.TextButton(
                "Cancelar",
                style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                on_click=lambda e: page.close(dialogo_movimiento)
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        modal=True
    )
    
    page.open(dialogo_movimiento)
