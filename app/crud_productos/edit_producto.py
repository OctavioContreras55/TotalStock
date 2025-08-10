import flet as ft
from app.utils.temas import GestorTemas
from app.utils.historial import GestorHistorial
from app.funciones.sesiones import SesionManager
from conexiones.firebase import db
import asyncio

#Plan para opcion editar producto:
#1. Crear una vista para editar productos que reciba el ID del producto a editar.
#2. Cargar los datos del producto desde Firestore.

async def on_click_editar_producto(page, producto_id, actualizar_tabla):
    tema = GestorTemas.obtener_tema()
    
    # Dimensiones responsivas para el dialog
    ancho_ventana = page.window.width or 1200
    alto_ventana = page.window.height or 800
    ancho_dialog = min(450, ancho_ventana * 0.85)   # Máximo 450px o 85% del ancho
    alto_dialog = min(350, alto_ventana * 0.6)      # Máximo 350px o 60% del alto (reducido)
    
    # Obtener datos actuales del producto
    try:
        doc_ref = db.collection("productos").document(producto_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            page.open(ft.SnackBar(
                content=ft.Text("Producto no encontrado", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return
            
        producto_data = doc.to_dict()
    except Exception as e:
        page.open(ft.SnackBar(
            content=ft.Text(f"Error al cargar producto: {str(e)}", color=tema.TEXT_COLOR),
            bgcolor=tema.ERROR_COLOR
        ))
        return
    
    # Campos del formulario con valores actuales
    campo_modelo = ft.TextField(
        label="Modelo", 
        value=producto_data.get('modelo', ''),
        autofocus=True,
        bgcolor=tema.INPUT_BG, 
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER, 
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    
    campo_tipo = ft.TextField(
        label="Tipo", 
        value=producto_data.get('tipo', ''),
        bgcolor=tema.INPUT_BG, 
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER, 
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    
    campo_nombre = ft.TextField(
        label="Nombre", 
        value=producto_data.get('nombre', ''),
        bgcolor=tema.INPUT_BG, 
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER, 
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    
    campo_precio = ft.TextField(
        label="Precio", 
        value=str(producto_data.get('precio', 0)),
        bgcolor=tema.INPUT_BG, 
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER, 
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    
    async def guardar_cambios(e):
        # Validar campos (sin cantidad)
        if not all([campo_modelo.value.strip(), campo_tipo.value.strip(), 
                   campo_nombre.value.strip(), campo_precio.value.strip()]):
            page.open(ft.SnackBar(
                content=ft.Text("Por favor, complete todos los campos", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return
        
        try:
            precio = float(campo_precio.value.strip())
        except ValueError:
            page.open(ft.SnackBar(
                content=ft.Text("El precio debe ser un número válido", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return
        
        try:
            nuevo_modelo = campo_modelo.value.strip()
            modelo_original = producto_data.get('modelo', '')
            
            # Solo verificar duplicados si el modelo cambió
            modelo_original_str = str(modelo_original) if modelo_original else ''
            if nuevo_modelo.lower() != modelo_original_str.lower():
                print(f"[BUSCAR] Verificando si el nuevo modelo '{nuevo_modelo}' ya existe...")
                
                # Obtener productos existentes desde cache
                from app.utils.cache_firebase import cache_firebase
                productos_existentes = await cache_firebase.obtener_productos()
                
                # Buscar si el nuevo modelo ya existe (case insensitive)
                modelo_normalizado = nuevo_modelo.lower()
                for producto in productos_existentes:
                    try:
                        modelo_existente = producto.get('modelo', '')
                        if modelo_existente and isinstance(modelo_existente, str):
                            if (modelo_existente.strip().lower() == modelo_normalizado and 
                                producto.get('firebase_id') != producto_id):
                                page.open(ft.SnackBar(
                                    content=ft.Text(f"[ERROR] El modelo '{nuevo_modelo}' ya existe en el inventario. No se permiten modelos duplicados.", color=tema.TEXT_COLOR),
                                    bgcolor=tema.ERROR_COLOR
                                ))
                                return
                    except Exception as ex:
                        print(f"Error al procesar producto en edición: {ex}")
                        continue
                        
                print(f"[OK] Nuevo modelo '{nuevo_modelo}' disponible - procediendo con la actualización...")
            
            # Actualizar en Firebase (sin cantidad)
            doc_ref = db.collection("productos").document(producto_id)
            doc_ref.update({
                'modelo': nuevo_modelo,
                'tipo': campo_tipo.value.strip(),
                'nombre': campo_nombre.value.strip(),
                'precio': precio
            })
            
            # Invalidar cache para forzar actualización inmediata
            from app.utils.cache_firebase import cache_firebase
            cache_firebase.invalidar_cache_productos()
            
            # Registrar actividad en el historial
            gestor_historial = GestorHistorial()
            usuario_actual = SesionManager.obtener_usuario_actual()
            
            await gestor_historial.agregar_actividad(
                tipo="editar_producto",
                descripcion=f"Editó producto '{campo_nombre.value.strip()}' (ID: {producto_id})",
                usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
            )
            
            page.open(ft.SnackBar(
                content=ft.Text("Producto actualizado exitosamente", color=tema.TEXT_COLOR),
                bgcolor=tema.SUCCESS_COLOR
            ))
            
            page.close(vista_editar)
            if actualizar_tabla:
                await actualizar_tabla()
                
        except Exception as e:
            page.open(ft.SnackBar(
                content=ft.Text(f"Error al actualizar producto: {str(e)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
    
    vista_editar = ft.AlertDialog(
        title=ft.Text("Editar Producto", color=tema.TEXT_COLOR),
        content=ft.Container(
            content=ft.Column(controls=[
                campo_modelo,
                campo_tipo,
                campo_nombre,
                campo_precio,
            ], scroll=ft.ScrollMode.AUTO),
            width=ancho_dialog,  # Ancho responsivo
            height=alto_dialog,  # Alto responsivo
        ),
        actions=[
            ft.TextButton("Cancelar", 
                style=ft.ButtonStyle(color=tema.BUTTON_ERROR_BG),
                on_click=lambda e: page.close(vista_editar)),
            ft.ElevatedButton(
                text="Guardar Cambios",
                style=ft.ButtonStyle(
                    bgcolor=tema.BUTTON_PRIMARY_BG,
                    color=tema.BUTTON_TEXT,
                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                ),
                on_click=guardar_cambios
            )
        ],
        bgcolor=tema.CARD_COLOR,
    )
    
    page.open(vista_editar)
    page.update()
  

def guardar_cambios(producto_id):
  pass