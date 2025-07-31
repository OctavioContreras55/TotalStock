import polars as pd
import flet as ft
from conexiones.firebase import db
from app.utils.temas import GestorTemas
from app.utils.historial import GestorHistorial
from app.funciones.sesiones import SesionManager
import asyncio

def cargar_archivo_excel(ruta_archivo):
    archivo = pd.read_excel(ruta_archivo)
    productos = []
    for row in archivo.iter_rows(named=True):
        producto = {
            "modelo": row["Modelo"],
            "tipo": row["Tipo"],
            "nombre": row["Nombre"],
            "precio": row["Precio"],
            "cantidad": row["Cantidad"]
        }
        productos.append(producto)
    return productos

async def guardar_productos_en_firebase(productos, page):
    tema = GestorTemas.obtener_tema()
    
    mensaje_cargando = ft.AlertDialog(
        title=ft.Text("Aviso", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content= ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("Importando productos...", color=tema.TEXT_COLOR),
                    ft.ProgressRing(width=14, height=14, stroke_width=2, color=tema.PRIMARY_COLOR)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=ft.Padding(20, 20, 10, 20),
        ),
        modal=True,
        
    )
    page.open(mensaje_cargando)
    page.update()
    
    mensaje_exito = ft.AlertDialog(
        title=ft.Text("Productos importados correctamente", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        actions=[ft.TextButton("Aceptar", 
                               style=ft.ButtonStyle(color=tema.PRIMARY_COLOR),
                               on_click=lambda e: page.close(mensaje_exito))],
        modal=True,
    )
    
    
    try:
        referencia_productos = db.collection("productos")
        productos_importados_count = 0
        
        for producto in productos:
            try:
                id_documento = f"{producto['modelo']}"
                doc_ref = referencia_productos.document(id_documento)
                doc_snapshot = doc_ref.get()
                if not all(key in producto for key in ["modelo", "tipo", "nombre", "precio", "cantidad"]):
                    print(f"Producto {producto} no tiene todos los campos requeridos.")
                    continue
                if doc_snapshot.exists:
                    print(f"El producto con ID: {id_documento} ya existe en Firebase. Se actualizará.")
                    doc_ref.set(producto)
                else:
                    doc_ref.set(producto)
                productos_importados_count += 1

            except Exception as e:
                print(f"Error al guardar el producto {producto['modelo']}: {e}")
        
        # Registrar actividad en el historial
        gestor_historial = GestorHistorial()
        usuario_actual = SesionManager.obtener_usuario_actual()
        
        await gestor_historial.agregar_actividad(
            tipo="importar_productos",
            descripcion=f"Importó {productos_importados_count} productos desde archivo Excel",
            usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
        )
        
        page.close(mensaje_cargando)
        page.open(mensaje_exito)
    except Exception as e:
        print(f"Error al conectar con Firebase: {e}")
        return False

def on_click_importar_archivo(page):
    tema = GestorTemas.obtener_tema()

    productos_importados = []
    def picked_file(e: ft.FilePickerResultEvent):

        if e.files:
            ruta = e.files[0].path
            productos = cargar_archivo_excel(ruta)
            # Aquí puedes actualizar la tabla con los nuevos productos
            productos_importados.clear()
            productos_importados.extend(productos)
            selected_file.value = e.files[0].name
        else:
            selected_file.value = "No se ha seleccionado ningun archivo"
        selected_file.update()
        
    pick_files_window = ft.FilePicker(on_result=picked_file)
    selected_file = ft.TextField(
        label="Archivo seleccionado", 
        width=250, 
        read_only=True,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    page.overlay.append(pick_files_window)
    
    ventana = ft.AlertDialog(
        bgcolor=tema.CARD_COLOR,
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "Seleccionar archivo",
                                icon=ft.Icon(ft.Icons.FOLDER_OPEN, color=tema.PRIMARY_COLOR),
                                style=ft.ButtonStyle(
                                    bgcolor=tema.BUTTON_BG,
                                    color=tema.BUTTON_TEXT,
                                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                ),
                                on_click=lambda e: pick_files_window.pick_files(allow_multiple=False),
                            ),
                            selected_file,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        spacing=10,
                    ),
                    padding=ft.Padding(10, 10, 10, 10),
                ),
                ft.Container(
                    content=ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    "Importar",
                                    style=ft.ButtonStyle(
                                        bgcolor=tema.BUTTON_SUCCESS_BG,
                                        color=tema.BUTTON_TEXT,
                                        shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                    ),
                                    on_click=lambda e: [page.close(ventana), asyncio.create_task(guardar_productos_en_firebase(productos_importados, page))],
                                    width=100,
                                    height=40,
                                ),
                                ft.ElevatedButton(
                                    "Cancelar",
                                    style=ft.ButtonStyle(
                                        bgcolor=tema.BUTTON_BG,
                                        color=tema.BUTTON_TEXT,
                                        shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                    ),
                                    on_click=lambda e: page.close(ventana),
                                    width=100,
                                    height=40,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            spacing=10,
                        ),
                    padding=ft.Padding(10, 10, 10, 10),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            width=500,
            height=150,
        ),
        modal=True, 
        title=ft.Text("Importar Productos", color=tema.TEXT_COLOR), 
        actions_alignment=ft.MainAxisAlignment.END, 
    )

    page.open(ventana)
    page.update()


def cargar_archivo_excel_ubicaciones(ruta_archivo):
    """Cargar archivo Excel específico para ubicaciones"""
    import pandas as pd
    
    try:
        # Leer archivo Excel
        df = pd.read_excel(ruta_archivo)
        ubicaciones = []
        
        for index, row in df.iterrows():
            ubicacion = {
                "modelo": str(row.get("Modelo", f"MOD{index:03d}")),
                "nombre": str(row.get("Nombre", row.get("Producto", "Sin nombre"))),
                "almacen": str(row.get("Almacen", row.get("Almacén", "Sin asignar"))),
                "ubicacion": str(row.get("Ubicacion", row.get("Ubicación", "Sin ubicación"))),
                "cantidad": int(row.get("Cantidad", 0))
            }
            ubicaciones.append(ubicacion)
        
        return ubicaciones
        
    except Exception as e:
        print(f"Error al cargar archivo Excel de ubicaciones: {e}")
        return []


async def guardar_ubicaciones_en_firebase(ubicaciones, page):
    """Guardar ubicaciones masivamente en Firebase"""
    tema = GestorTemas.obtener_tema()
    
    try:
        from conexiones.firebase import db
        from app.utils.historial import GestorHistorial
        from app.funciones.sesiones import SesionManager
        
        print(f"Guardando {len(ubicaciones)} ubicaciones en Firebase...")
        
        # Mostrar progreso
        total = len(ubicaciones)
        guardados = 0
        errores = 0
        
        for ubicacion in ubicaciones:
            try:
                # Guardar en colección 'ubicaciones'
                db.collection('ubicaciones').add(ubicacion)
                guardados += 1
                print(f"Ubicación guardada: {ubicacion.get('nombre', 'Sin nombre')}")
                
            except Exception as e:
                errores += 1
                print(f"Error al guardar ubicación {ubicacion.get('nombre', 'Sin nombre')}: {e}")
        
        # Registrar en historial
        gestor_historial = GestorHistorial()
        usuario_actual = SesionManager.obtener_usuario_actual()
        
        await gestor_historial.agregar_actividad(
            tipo="importar_ubicaciones",
            descripcion=f"Importó {guardados} ubicaciones desde Excel (Errores: {errores})",
            usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
        )
        
        # Mostrar resultado
        if guardados > 0:
            page.open(ft.SnackBar(
                content=ft.Text(f"✅ {guardados} ubicaciones importadas exitosamente", color=tema.TEXT_COLOR),
                bgcolor=tema.SUCCESS_COLOR
            ))
        
        if errores > 0:
            page.open(ft.SnackBar(
                content=ft.Text(f"⚠️ {errores} ubicaciones tuvieron errores", color=tema.TEXT_COLOR),
                bgcolor=tema.WARNING_COLOR
            ))
            
    except Exception as e:
        print(f"Error al guardar ubicaciones en Firebase: {e}")
        page.open(ft.SnackBar(
            content=ft.Text(f"Error al importar ubicaciones: {str(e)}", color=tema.TEXT_COLOR),
            bgcolor=tema.ERROR_COLOR
        ))


def on_click_importar_archivo_ubicaciones(page):
    """Importar archivo Excel específico para ubicaciones"""
    tema = GestorTemas.obtener_tema()
    archivo_seleccionado = None
    
    def seleccionar_archivo(e):
        nonlocal archivo_seleccionado
        archivo_seleccionado = e.files[0] if e.files else None
        if archivo_seleccionado:
            texto_archivo.value = f"Archivo seleccionado: {archivo_seleccionado.name}"
            texto_archivo.update()

    selector_archivo = ft.FilePicker(on_result=seleccionar_archivo)
    page.overlay.append(selector_archivo)

    texto_archivo = ft.Text("No se ha seleccionado ningún archivo", color=tema.TEXT_COLOR)

    async def procesar_archivo_ubicaciones(e):
        if not archivo_seleccionado:
            page.open(ft.SnackBar(
                content=ft.Text("Por favor selecciona un archivo", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return

        try:
            # Ruta temporal para el archivo
            ruta_temporal = f"temp_ubicaciones_{archivo_seleccionado.name}"
            
            # Guardar archivo temporalmente
            with open(ruta_temporal, "wb") as f:
                f.write(archivo_seleccionado.read())
            
            # Cargar y procesar Excel de ubicaciones
            ubicaciones = cargar_archivo_excel_ubicaciones(ruta_temporal)
            
            if ubicaciones:
                page.close(ventana_ubicaciones)
                await guardar_ubicaciones_en_firebase(ubicaciones, page)
                
                # Limpiar archivo temporal
                import os
                if os.path.exists(ruta_temporal):
                    os.remove(ruta_temporal)
            else:
                page.open(ft.SnackBar(
                    content=ft.Text("Error al procesar el archivo de ubicaciones", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))
                
        except Exception as e:
            print(f"Error al procesar archivo de ubicaciones: {e}")
            page.open(ft.SnackBar(
                content=ft.Text(f"Error: {str(e)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))

    # Crear diálogo para importar ubicaciones
    ventana_ubicaciones = ft.AlertDialog(
        content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.LOCATION_ON, color=tema.PRIMARY_COLOR),
                    ft.Text("Importar Ubicaciones desde Excel", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD)
                ]),
                ft.Divider(color=tema.DIVIDER_COLOR),
                ft.Text("Formato esperado del Excel:", color=tema.TEXT_COLOR, size=12),
                ft.Text("• Modelo, Nombre/Producto, Almacen/Almacén, Ubicacion/Ubicación, Cantidad", 
                       color=tema.SECONDARY_TEXT_COLOR, size=10),
                ft.Container(height=10),
                texto_archivo,
                ft.Row([
                    ft.ElevatedButton(
                        "Seleccionar Archivo",
                        icon=ft.Icons.FILE_OPEN,
                        on_click=lambda _: selector_archivo.pick_files(
                            allowed_extensions=["xlsx", "xls"]
                        ),
                        style=ft.ButtonStyle(
                            bgcolor=tema.BUTTON_BG,
                            color=tema.BUTTON_TEXT,
                            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                        )
                    )
                ]),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Importar Ubicaciones",
                            style=ft.ButtonStyle(
                                bgcolor=tema.BUTTON_SUCCESS_BG,
                                color=tema.BUTTON_TEXT,
                                shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                            ),
                            on_click=lambda e: asyncio.create_task(procesar_archivo_ubicaciones(e)),
                            width=140,
                            height=40,
                        ),
                        ft.ElevatedButton(
                            "Cancelar",
                            style=ft.ButtonStyle(
                                bgcolor=tema.BUTTON_BG,
                                color=tema.BUTTON_TEXT,
                                shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                            ),
                            on_click=lambda e: page.close(ventana_ubicaciones),
                            width=100,
                            height=40,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=10,
                ),
            ],
            padding=ft.Padding(10, 10, 10, 10),
        ),
        modal=True, 
        title=ft.Text("Importar Ubicaciones", color=tema.TEXT_COLOR), 
        actions_alignment=ft.MainAxisAlignment.END, 
    )

    page.open(ventana_ubicaciones)
    page.update()