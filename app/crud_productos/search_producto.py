import flet as ft
from conexiones.firebase import db
from app.utils.temas import GestorTemas
import asyncio

def mostrar_dialogo_busqueda(page, mostrar_productos_filtrados):
    tema = GestorTemas.obtener_tema()
    
    # Dimensiones responsivas para el dialog
    ancho_ventana = page.window.width or 1200
    ancho_dialog = min(400, ancho_ventana * 0.8)    # Máximo 400px o 80% del ancho
    
    campo_buscar = ft.TextField(
      label="Buscar Producto por modelo",
      width=min(300, ancho_dialog * 0.7),  # Campo responsivo
      autofocus=True,
      bgcolor=tema.INPUT_BG,
      color=tema.TEXT_COLOR,
      border_color=tema.INPUT_BORDER,
      focused_border_color=tema.PRIMARY_COLOR,
      label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    # Contenedor para mostrar indicador de carga
    contenedor_carga = ft.Container(
        content=ft.Row([
            ft.ProgressRing(width=16, height=16, stroke_width=2, color=tema.PRIMARY_COLOR),
            ft.Text("Buscando...", color=tema.TEXT_COLOR, size=14)
        ], alignment=ft.MainAxisAlignment.CENTER),
        visible=False,
        height=0
    )
    
    async def validar_busqueda(e):
        if not campo_buscar.value.strip():
            page.open(ft.SnackBar(
                content=ft.Text("Por favor, ingrese un modelo para buscar.", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
        else:
            # Mostrar indicador de carga
            contenedor_carga.visible = True
            contenedor_carga.height = 30
            boton_buscar.disabled = True
            page.update()
            
            try:
                await buscar_en_firebase(page, campo_buscar.value, mostrar_productos_filtrados, dialogo_busqueda)
            finally:
                # Ocultar indicador de carga
                contenedor_carga.visible = False
                contenedor_carga.height = 0
                boton_buscar.disabled = False
                page.update()
    
    boton_buscar = ft.ElevatedButton(
        text="Buscar",
        style=ft.ButtonStyle(
            bgcolor=tema.BUTTON_PRIMARY_BG,
            color=tema.BUTTON_TEXT,
            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
        ),
        on_click=validar_busqueda
    )

    async def recargar_tabla(e, callback_actualizar_tabla, dialogo):
        """Recargar la tabla completa con todos los productos"""
        try:
            # Cerrar el diálogo de búsqueda
            page.close(dialogo)
            
            # Mostrar mensaje de recarga
            page.open(ft.SnackBar(
                content=ft.Text("[PROCESO] Recargando tabla completa...", color=tema.TEXT_COLOR),
                bgcolor=tema.PRIMARY_COLOR,
                duration=2000
            ))
            
            # Obtener todos los productos desde cache/Firebase
            from app.utils.cache_firebase import cache_firebase
            todos_productos = await cache_firebase.obtener_productos()
            
            # Actualizar tabla con todos los productos
            if callback_actualizar_tabla:
                await callback_actualizar_tabla(todos_productos)
                
            print(f"[OK] Tabla recargada con {len(todos_productos)} productos")
            
        except Exception as error:
            print(f"Error al recargar tabla: {error}")
            page.open(ft.SnackBar(
                content=ft.Text("[ERROR] Error al recargar tabla", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))

    dialogo_busqueda = ft.AlertDialog(
        title=ft.Text("Buscar Producto", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content=ft.Container(
            content=ft.Column([
                ft.Row(
                    controls=[
                        campo_buscar,
                        boton_buscar,
                        ft.IconButton(
                            ft.Icons.REFRESH,
                            icon_color=tema.SECONDARY_TEXT_COLOR,
                            on_click=lambda e: recargar_tabla(e, mostrar_productos_filtrados, dialogo_busqueda),
                            tooltip="Recargar tabla completa"
                        )
                    ]
                ),
                contenedor_carga
            ]),
            width=ancho_dialog,   # Ancho responsivo
            height=120,
        ),
        actions=[
            ft.TextButton("Cerrar", 
                         style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                         on_click=lambda e: page.close(dialogo_busqueda)),
        ]
    )

    page.open(dialogo_busqueda)
    page.update()

async def buscar_en_firebase(page, busqueda, actualizar_tabla=None, dialogo_busqueda=None):
    tema = GestorTemas.obtener_tema()
    try:
        # OPTIMIZACIÓN: Buscar primero en cache local antes que en Firebase
        from app.utils.cache_firebase import cache_firebase
        from app.utils.monitor_firebase import monitor_firebase
        
        print(f"[BUSCAR] BÚSQUEDA INICIADA: '{busqueda}' - usando cache local (0 consultas Firebase)")
        todos_productos = await cache_firebase.obtener_productos()
        
        # Filtrar localmente (sin consulta a Firebase)
        productos_encontrados = []
        busqueda_lower = busqueda.lower().strip()
        
        for producto in todos_productos:
            # Convertir a string para evitar errores con tipos de datos
            modelo = str(producto.get('modelo', '')).lower()
            nombre = str(producto.get('nombre', '')).lower()
            tipo = str(producto.get('tipo', '')).lower()
            
            # Buscar en modelo, nombre y tipo
            if (busqueda_lower in modelo or 
                busqueda_lower in nombre or 
                busqueda_lower in tipo):
                productos_encontrados.append(producto)

        print(f"[DART] BÚSQUEDA COMPLETADA: {len(productos_encontrados)} productos encontrados (filtrado local)")

        if productos_encontrados:
            page.close(dialogo_busqueda)  # Cerrar el dialog
            page.open(ft.SnackBar(
                content=ft.Text(f"Se encontraron {len(productos_encontrados)} productos", color=tema.TEXT_COLOR),
                bgcolor=tema.SUCCESS_COLOR
            ))
            if actualizar_tabla:
                await actualizar_tabla(productos_encontrados)
        else:
            page.open(ft.SnackBar(
                content=ft.Text("No se encontraron productos con ese modelo.", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))

    except Exception as e:
        print(f"Error al buscar productos: {str(e)}")
        page.open(ft.SnackBar(
            content=ft.Text("Error al buscar productos.", color=tema.TEXT_COLOR),
            bgcolor=tema.ERROR_COLOR
        ))
        page.update()
        
