import flet as ft
from conexiones.firebase import db
from app.utils.temas import GestorTemas
from app.utils.historial import GestorHistorial
from app.funciones.sesiones import SesionManager
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
        """Validar todos los campos requeridos"""
        print("[BUSCAR] DEBUG: Validando campos...")
        
        # Debug: mostrar valores de campos
        print(f"Modelo: '{campo_modelo.value}'")
        print(f"Tipo: '{campo_tipo.value}'")
        print(f"Nombre: '{campo_nombre.value}'")
        print(f"Precio: '{campo_precio.value}'")
        print(f"Cantidad: '{campo_cantidad.value}'")
        
        # Verificar que los campos básicos no estén vacíos o None
        campos_requeridos = [
            (campo_modelo.value, "Modelo"),
            (campo_tipo.value, "Tipo"),
            (campo_nombre.value, "Nombre"),
            (campo_precio.value, "Precio"),
            (campo_cantidad.value, "Cantidad")
        ]
        
        for valor, nombre_campo in campos_requeridos:
            if not valor or not str(valor).strip():
                print(f"[ERROR] Campo {nombre_campo} está vacío")
                return False, f"El campo {nombre_campo} es requerido"
        
        # Verificar que precio y cantidad sean números válidos
        try:
            precio_valor = float(campo_precio.value.strip())
            if precio_valor < 0:
                return False, "El precio debe ser mayor o igual a 0"
        except (ValueError, AttributeError):
            return False, "El precio debe ser un número válido"
            
        try:
            cantidad_valor = int(campo_cantidad.value.strip())
            if cantidad_valor < 0:
                return False, "La cantidad debe ser mayor o igual a 0"
        except (ValueError, AttributeError):
            return False, "La cantidad debe ser un número entero válido"
        
        print("[OK] Validación exitosa")
        return True, "OK"
    
    # Contenedor para mostrar indicador de carga
    contenedor_progreso = ft.Container(
        content=ft.Row([
            ft.ProgressRing(width=16, height=16, stroke_width=2, color=tema.PRIMARY_COLOR),
            ft.Text("Creando producto...", color=tema.TEXT_COLOR, size=14)
        ], alignment=ft.MainAxisAlignment.CENTER),
        visible=False,
        height=0
    )
    
    # Definir el botón para poder referenciarlo
    boton_crear_producto = ft.ElevatedButton(
        text="Crear Producto", 
        on_click=None,  # Se asignará después
        style=ft.ButtonStyle(
            bgcolor=tema.BUTTON_PRIMARY_BG,
            color=tema.BUTTON_TEXT,
            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
        )
    )

    async def crear_producto(e):
        # Validar campos
        es_valido, mensaje = validar_campos()
        if not es_valido:
            page.open(ft.SnackBar(
                content=ft.Text(mensaje, color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return
        
        # Mostrar indicador de progreso
        contenedor_progreso.visible = True
        contenedor_progreso.height = 30
        boton_crear_producto.disabled = True
        page.update()

        modelo = campo_modelo.value.strip()
        tipo = campo_tipo.value.strip()
        nombre = campo_nombre.value.strip()
        precio = float(campo_precio.value.strip())
        cantidad = int(campo_cantidad.value.strip())

        try:
            firebase_id = await crear_producto_firebase(modelo, tipo, nombre, precio, cantidad)
            
            # Registrar actividad en el historial
            gestor_historial = GestorHistorial()
            usuario_actual = SesionManager.obtener_usuario_actual()
            
            await gestor_historial.agregar_actividad(
                tipo="crear_producto",
                descripcion=f"Creó producto '{nombre}' (Modelo: {modelo})",
                usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
            )
            
            # Actualizar dashboard dinámicamente - TEMPORALMENTE DESHABILITADO
            # from app.utils.actualizador_dashboard import actualizar_dashboard_sincrono
            # actualizar_dashboard_sincrono()
            
            print("[OK] Producto creado - actualización manual con botón refresh")
            
            page.open(ft.SnackBar(
                content=ft.Text(f"Producto '{nombre}' creado exitosamente con ID: {firebase_id}", color=tema.TEXT_COLOR),
                bgcolor=tema.SUCCESS_COLOR
            ))
            if callback_actualizar_tabla:
                await callback_actualizar_tabla(forzar_refresh=True)  # Forzar refresh después de crear
            
            # Cerrar el diálogo automáticamente después de crear exitosamente
            page.close(dialogo_crear_producto)
            print("[OK] Diálogo cerrado automáticamente después de crear producto")
        except Exception as e:
            page.open(ft.SnackBar(
                content=ft.Text(f"Error al crear producto: {str(e)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
        finally:
            # Ocultar indicador de progreso
            contenedor_progreso.visible = False
            contenedor_progreso.height = 0
            boton_crear_producto.disabled = False
            page.update()

    # Asignar la función al botón
    boton_crear_producto.on_click = crear_producto

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
                contenedor_progreso,
                boton_crear_producto
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
    from app.utils.monitor_firebase import monitor_firebase
    from app.utils.cache_firebase import cache_firebase
    
    # Verificar si el modelo ya existe
    print(f"[BUSCAR] Verificando si el modelo '{modelo}' ya existe...")
    
    # Obtener productos existentes desde cache o Firebase
    productos_existentes = await cache_firebase.obtener_productos()
    print(f"[BUSCAR] DEBUG: Obtenidos {len(productos_existentes)} productos para verificar duplicados")
    
    # Buscar si el modelo ya existe (case insensitive)
    modelo_normalizado = modelo.strip().lower()
    print(f"[BUSCAR] DEBUG: Buscando modelo normalizado: '{modelo_normalizado}'")
    
    for i, producto in enumerate(productos_existentes):
        try:
            # Verificación robusta para manejar None y tipos incorrectos
            modelo_producto = producto.get('modelo', '')
            if modelo_producto is None:
                modelo_producto = ''
            elif not isinstance(modelo_producto, str):
                modelo_producto = str(modelo_producto)
            
            modelo_existente = modelo_producto.strip().lower()
            
            if modelo_existente == modelo_normalizado:
                print(f"[ERROR] DEBUG: Modelo duplicado encontrado en posición {i}: '{producto.get('modelo')}'")
                raise Exception(f"[ERROR] El modelo '{modelo}' ya existe en el inventario. No se permiten modelos duplicados.")
            
            # Debug solo para los primeros 3 productos
            if i < 3:
                print(f"[BUSCAR] DEBUG: Producto {i}: '{producto.get('modelo')}' -> normalizado: '{modelo_existente}'")
        except Exception as e:
            if "ya existe en el inventario" in str(e):
                raise e  # Re-lanzar si es error de duplicado
            else:
                # Error de procesamiento, saltear este producto
                print(f"[WARN] DEBUG: Error procesando producto {i}: {str(e)} - Producto: {producto}")
                continue
    
    print(f"[OK] Modelo '{modelo}' disponible - procediendo con la creación...")
    
    print(f"[BUSCAR] DEBUG: Iniciando creación en Firebase con datos:")
    print(f"   - Modelo: {modelo}")
    print(f"   - Tipo: {tipo}")
    print(f"   - Nombre: {nombre}")
    print(f"   - Precio: {precio}")
    print(f"   - Cantidad: {cantidad}")
    
    # Crear un nuevo producto en la base de datos
    try:
        timestamp, producto_ref = db.collection("productos").add({
          "id": modelo,
          "modelo": modelo,
          "tipo": tipo,
          "nombre": nombre,
          "precio": precio,
          "cantidad": cantidad
        })
        print(f"[OK] DEBUG: Producto creado en Firebase con ID: {producto_ref.id}")
    except Exception as e:
        print(f"[ERROR] DEBUG: Error al crear en Firebase: {str(e)}")
        raise e
    
    # Registrar la escritura en el monitor
    monitor_firebase.registrar_consulta(
        tipo='escritura',
        coleccion='productos',
        descripcion=f'Crear producto: {nombre} (modelo: {modelo})',
        cantidad_docs=1
    )
    
    # IMPORTANTE: Invalidar cache para forzar refresh en próxima consulta
    cache_firebase.invalidar_cache_productos()
    print("[PROCESO] Cache invalidado después de crear producto")
    
    return producto_ref.id

async def obtener_productos_firebase():
    """
    Obtiene productos usando cache inteligente para minimizar consultas a Firebase.
    Solo consulta Firebase si es necesario (cache expirado o primera vez).
    """
    from app.utils.cache_firebase import cache_firebase
    return await cache_firebase.obtener_productos()