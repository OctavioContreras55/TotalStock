import polars as pl
import flet as ft
from datetime import datetime
from conexiones.firebase import db
from app.utils.temas import GestorTemas
from app.utils.historial import GestorHistorial
from app.funciones.sesiones import SesionManager
import asyncio

def cargar_archivo_excel(ruta_archivo):
    archivo = pl.read_excel(ruta_archivo)
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
    
    async def importar_productos_handler(e, page, ventana, productos_importados):
        """Handler para importar productos de forma asíncrona"""
        page.close(ventana)
        await guardar_productos_en_firebase(productos_importados, page)
    
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
                                    on_click=lambda e: page.run_task(importar_productos_handler, e, page, ventana, productos_importados),
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
    """Cargar archivo Excel específico para ubicaciones usando Polars"""
    try:
        print(f"[DEBUG] Intentando cargar archivo: {ruta_archivo}")
        print(f"[DEBUG] Tipo de ruta_archivo: {type(ruta_archivo)}")
        
        # Leer archivo Excel con Polars
        df = pl.read_excel(ruta_archivo)
        print(f"[DEBUG] DataFrame cargado exitosamente")
        print(f"[DEBUG] Tipo de df: {type(df)}")
        print(f"[DEBUG] Shape del DataFrame: {df.shape}")
        
        ubicaciones = []
        
        print(f"Columnas encontradas en el archivo: {df.columns}")
        
        # Debug: mostrar los nombres exactos de las columnas para diagnosis
        print(f"[DEBUG] Columnas exactas: {list(df.columns)}")
        for i, col in enumerate(df.columns):
            print(f"[DEBUG] Columna {i}: '{col}' (tipo: {type(col)})")
        
        # Iterar sobre las filas con Polars
        for row in df.iter_rows(named=True):
            print(f"Procesando fila: {row}")
            print(f"[DEBUG] Claves disponibles en row: {list(row.keys())}")
            
            # Obtener valores con múltiples opciones de nombre de columna
            # Primero verificar valores directos
            modelo_directo = row.get("Modelo") or row.get("Material")  # Agregar "Material"
            modelo_minuscula = row.get("modelo") or row.get("material")  # Agregar "material"
            print(f"[DEBUG] Modelo directo: '{modelo_directo}' (tipo: {type(modelo_directo)})")
            print(f"[DEBUG] Modelo minúscula: '{modelo_minuscula}' (tipo: {type(modelo_minuscula)})")
            
            # Usar el nombre del material directamente como modelo
            modelo = None
            if modelo_directo and str(modelo_directo).strip() and str(modelo_directo).strip().lower() != 'none':
                modelo = str(modelo_directo).strip()
                print(f"[DEBUG] Usando modelo directo: '{modelo}'")
            elif modelo_minuscula and str(modelo_minuscula).strip() and str(modelo_minuscula).strip().lower() != 'none':
                modelo = str(modelo_minuscula).strip()
                print(f"[DEBUG] Usando modelo minúscula: '{modelo}'")
            else:
                modelo = f"MOD{len(ubicaciones)+1:03d}"
                print(f"[DEBUG] Generando código automático: '{modelo}'")
            
            print(f"[DEBUG] Modelo final: '{modelo}'")
            
            almacen = (row.get("Almacen") or row.get("Almacén") or 
                      row.get("almacen") or row.get("almacén") or "Sin asignar")
            estanteria = (row.get("Estanteria") or row.get("Estantería") or 
                         row.get("estanteria") or row.get("estantería") or 
                         row.get("Ubicacion") or row.get("Ubicación") or 
                         row.get("ubicacion") or row.get("ubicación") or "Sin asignar")
            observaciones = (row.get("Observaciones") or row.get("observaciones") or 
                           row.get("Notas") or row.get("notas") or "Sin observaciones")
            
            # Obtener cantidad si está disponible
            cantidad = 1  # Valor por defecto
            cantidad_raw = (row.get("Cantidad") or row.get("cantidad") or 
                           row.get("Qty") or row.get("qty") or "1")
            try:
                cantidad = int(cantidad_raw) if cantidad_raw else 1
            except (ValueError, TypeError):
                cantidad = 1
            
            # Convertir a tipos apropiados y crear estructura para nuevo sistema
            # Polars maneja nulos de forma diferente, usamos verificación directa
            ubicacion = {
                "modelo": str(modelo) if modelo is not None else "Sin modelo",
                "almacen": str(almacen) if almacen is not None else "Sin asignar",
                "estanteria": str(estanteria) if estanteria is not None else "Sin asignar",
                "cantidad": cantidad,
                "fecha_asignacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "observaciones": str(observaciones) if observaciones is not None else "Sin observaciones"
            }
            
            print(f"Ubicación procesada: {ubicacion}")
            ubicaciones.append(ubicacion)
        
        print(f"Total ubicaciones procesadas: {len(ubicaciones)}")
        return ubicaciones
        
    except Exception as e:
        print(f"Error al cargar archivo Excel de ubicaciones: {e}")
        print(f"[DEBUG] Tipo del error: {type(e)}")
        import traceback
        print(f"[DEBUG] Traceback completo: {traceback.format_exc()}")
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
                print(f"Ubicación guardada: {ubicacion.get('modelo', 'Sin modelo')} -> {ubicacion.get('almacen', 'Sin almacen')} / {ubicacion.get('estanteria', 'Sin estanteria')}")
                
            except Exception as e:
                errores += 1
                print(f"Error al guardar ubicación {ubicacion.get('modelo', 'Sin modelo')}: {e}")
        
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
            # Usar directamente la ruta del archivo seleccionado
            ruta_archivo = archivo_seleccionado.path
            
            # Cargar y procesar Excel de ubicaciones
            ubicaciones = cargar_archivo_excel_ubicaciones(ruta_archivo)
            
            if ubicaciones:
                page.close(ventana_ubicaciones)
                await guardar_ubicaciones_en_firebase(ubicaciones, page)
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

    # Diálogo para importar ubicaciones
    ventana_ubicaciones = ft.AlertDialog(
        title=ft.Text("Importar Ubicaciones desde Excel", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content=ft.Container(
            content=ft.Column([
                ft.Text("Seleccione un archivo Excel con las siguientes columnas:", color=tema.TEXT_COLOR),
                ft.Text("• Material/Modelo, Almacen/Almacén, Estanteria/Estantería/Ubicacion", 
                       color=tema.TEXT_SECONDARY, size=12),
                ft.Text("• Cantidad (opcional), Observaciones/Notas (opcional)", 
                       color=tema.TEXT_SECONDARY, size=12),
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Seleccionar archivo Excel",
                    icon=ft.Icon(ft.Icons.FOLDER_OPEN),
                    style=ft.ButtonStyle(
                        bgcolor=tema.BUTTON_BG,
                        color=tema.BUTTON_TEXT,
                        shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                    ),
                    on_click=lambda e: selector_archivo.pick_files(
                        allowed_extensions=["xlsx", "xls"]
                    )
                ),
                ft.Container(height=10),
                texto_archivo,
            ], spacing=10),
            width=450,
            height=250,
            padding=ft.Padding(15, 15, 15, 15)
        ),
        actions=[
            ft.ElevatedButton(
                "Importar Ubicaciones",
                style=ft.ButtonStyle(
                    bgcolor=tema.BUTTON_SUCCESS_BG,
                    color=tema.BUTTON_TEXT,
                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                ),
                on_click=procesar_archivo_ubicaciones
            ),
            ft.TextButton(
                "Cancelar",
                style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                on_click=lambda e: page.close(ventana_ubicaciones)
            ),
        ],
        modal=True,
    )
    
    page.open(ventana_ubicaciones)
    page.update()