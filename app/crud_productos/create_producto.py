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
        # Verificar que los campos básicos no estén vacíos
        if not all([
            campo_modelo.value and campo_modelo.value.strip(),
            campo_tipo.value and campo_tipo.value.strip(),
            campo_nombre.value and campo_nombre.value.strip(),
            campo_precio.value and campo_precio.value.strip(),
            campo_cantidad.value and campo_cantidad.value.strip(),
        ]):
            return False
        
        # Verificar que precio y cantidad sean números válidos
        try:
            float(campo_precio.value.strip())
            int(campo_cantidad.value.strip())
            return True
        except ValueError:
            return False

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
            
            print("✅ Producto creado - actualización manual con botón refresh")
            
            page.open(ft.SnackBar(
                content=ft.Text(f"Producto '{nombre}' creado exitosamente con ID: {firebase_id}", color=tema.TEXT_COLOR),
                bgcolor=tema.SUCCESS_COLOR
            ))
            if callback_actualizar_tabla:
                await callback_actualizar_tabla(forzar_refresh=True)  # Forzar refresh después de crear
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
    from app.utils.monitor_firebase import monitor_firebase
    
    # Crear un nuevo producto en la base de datos
    timestamp, producto_ref = db.collection("productos").add({
      "id": modelo,
      "modelo": modelo,
      "tipo": tipo,
      "nombre": nombre,
      "precio": precio,
      "cantidad": cantidad
    })
    
    # Registrar la escritura en el monitor
    monitor_firebase.registrar_consulta(
        tipo='escritura',
        coleccion='productos',
        descripcion=f'Crear producto: {nombre} (modelo: {modelo})',
        cantidad_docs=1
    )
    
    # IMPORTANTE: Invalidar cache para forzar refresh en próxima consulta
    from app.utils.cache_firebase import cache_firebase
    cache_firebase.invalidar_cache_productos()
    print("🔄 Cache invalidado después de crear producto")
    
    return producto_ref.id

async def obtener_productos_firebase():
    """
    Obtiene productos usando cache inteligente para minimizar consultas a Firebase.
    Solo consulta Firebase si es necesario (cache expirado o primera vez).
    """
    from app.utils.cache_firebase import cache_firebase
    return await cache_firebase.obtener_productos()