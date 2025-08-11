import polars as pl
import flet as ft
from datetime import datetime
from conexiones.firebase import db
from app.utils.temas import GestorTemas
from app.utils.historial import GestorHistorial
from app.funciones.sesiones import SesionManager
import asyncio

def cargar_archivo_excel(ruta_archivo):
    """
    Cargar archivo Excel para inventario - SIN CANTIDAD.
    La cantidad se calcula automáticamente desde ubicaciones.
    """
    archivo = pl.read_excel(ruta_archivo)
    productos = []
    for row in archivo.iter_rows(named=True):
        producto = {
            "modelo": row["Modelo"],
            "tipo": row["Tipo"],
            "nombre": row["Nombre"],
            "precio": row["Precio"],
            "cantidad": 0  # Cantidad inicial 0 - se calcula desde ubicaciones
        }
        productos.append(producto)
    return productos

async def guardar_productos_en_firebase(productos, page):
    tema = GestorTemas.obtener_tema()
    
    print(f"[ALERT] DEBUG: Iniciando guardar_productos_en_firebase con {len(productos)} productos")
    
    # Mostrar progreso INMEDIATAMENTE
    mensaje_cargando = ft.AlertDialog(
        title=ft.Text("Importando productos", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content= ft.Container(
            content=ft.Row(
                controls=[
                    ft.ProgressRing(width=16, height=16, stroke_width=2, color=tema.PRIMARY_COLOR),
                    ft.Text(f"Procesando {len(productos)} productos...", color=tema.TEXT_COLOR)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=ft.Padding(15, 10, 15, 10),
        ),
        modal=True,
    )
    
    print("[ALERT] DEBUG: AlertDialog creado, intentando abrir...")
    page.open(mensaje_cargando)
    print("[ALERT] DEBUG: page.open() ejecutado")
    page.update()
    print("[ALERT] DEBUG: page.update() ejecutado - AlertDialog debería estar visible")
    
    # Delay mínimo para que el AlertDialog sea visible
    await asyncio.sleep(1.0)  # 1 segundo mínimo
    
    # Mensaje de éxito
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
        productos_nuevos_count = 0
        productos_actualizados_count = 0
        
        for producto in productos:
            try:
                id_documento = f"{producto['modelo']}"
                doc_ref = referencia_productos.document(id_documento)
                doc_snapshot = doc_ref.get()
                if not all(key in producto for key in ["modelo", "tipo", "nombre", "precio", "cantidad"]):
                    continue
                
                if doc_snapshot.exists:
                    # Producto ya existe - actualizar
                    doc_ref.set(producto)
                    productos_actualizados_count += 1
                else:
                    # Producto nuevo - crear
                    doc_ref.set(producto)
                    productos_nuevos_count += 1
                
                # Pequeño delay para hacer visible el progreso
                if (productos_nuevos_count + productos_actualizados_count) % 10 == 0:  # Cada 10 productos
                    await asyncio.sleep(0.1)  # 100ms para mostrar progreso

            except Exception as e:
                pass
        
        productos_total_count = productos_nuevos_count + productos_actualizados_count
        
        # Registrar actividad en el historial
        gestor_historial = GestorHistorial()
        usuario_actual = SesionManager.obtener_usuario_actual()
        
        await gestor_historial.agregar_actividad(
            tipo="importar_productos",
            descripcion=f"Importó {productos_total_count} productos desde archivo Excel - {productos_nuevos_count} nuevos, {productos_actualizados_count} actualizados",
            usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
        )
        
        # [PROCESO] SINCRONIZACIÓN AUTOMÁTICA después de importar productos
        try:
            from app.utils.sincronizacion_inventario import sincronizar_inventario_completo
            resultado = await sincronizar_inventario_completo(mostrar_resultados=True)
            
            # Invalidar cache para refrescar datos
            from app.utils.cache_firebase import cache_firebase
            cache_firebase.invalidar_cache_productos()
            
            # Crear mensaje detallado de importación
            mensaje_detalle = f"[OK] {productos_nuevos_count} productos nuevos\n✏️ {productos_actualizados_count} productos actualizados"
            
            sync_mensaje = ""
            if resultado['productos_actualizados'] > 0:
                sync_mensaje = f"\n[PROCESO] {resultado['productos_actualizados']} cantidades sincronizadas desde ubicaciones"
            
            mensaje_exito.title = ft.Text("Importación completada", color=tema.TEXT_COLOR)
            mensaje_exito.content = ft.Text(f"{mensaje_detalle}{sync_mensaje}", color=tema.TEXT_COLOR)
            
        except Exception as sync_error:
            # Si falla la sincronización, mostrar solo los datos de importación
            mensaje_detalle = f"[OK] {productos_nuevos_count} productos nuevos\n✏️ {productos_actualizados_count} productos actualizados"
            mensaje_exito.title = ft.Text("Productos importados correctamente", color=tema.TEXT_COLOR)
            mensaje_exito.content = ft.Text(mensaje_detalle, color=tema.TEXT_COLOR)
        
        print("[ALERT] DEBUG: Cerrando AlertDialog de carga y mostrando éxito...")
        # Delay mínimo antes de cerrar para asegurar visibilidad
        await asyncio.sleep(0.5)  # Medio segundo adicional
        page.close(mensaje_cargando)
        page.open(mensaje_exito)
    except Exception as e:
        print(f"[ALERT] DEBUG: Error en guardar_productos_en_firebase: {e}")
        page.close(mensaje_cargando)
        return False

def on_click_importar_archivo(page, callback_actualizar_tabla=None):
    tema = GestorTemas.obtener_tema()

    productos_importados = []
    
    async def importar_productos_handler(e, page, ventana, productos_importados):
        """Handler para importar productos de forma asíncrona"""
        print("[ALERT] DEBUG: importar_productos_handler iniciado")
        page.close(ventana)
        print("[ALERT] DEBUG: Ventana de selección cerrada, llamando guardar_productos_en_firebase")
        await guardar_productos_en_firebase(productos_importados, page)
        
        # Actualizar la tabla después de la importación
        if callback_actualizar_tabla:
            print("[PROCESO] DEBUG: Actualizando tabla después de importación...")
            await callback_actualizar_tabla(forzar_refresh=True)
    
    def picked_file(e: ft.FilePickerResultEvent):
        """Manejar selección de archivo - CORREGIDO para ejecutables"""
        print(f"[DEBUG] picked_file llamado - e.files: {e.files}")
        
        if e.files and len(e.files) > 0:
            try:
                archivo_seleccionado = e.files[0]
                ruta = archivo_seleccionado.path
                nombre = archivo_seleccionado.name
                
                print(f"[DEBUG] Archivo seleccionado: {nombre}")
                print(f"[DEBUG] Ruta: {ruta}")
                
                # Verificar que el archivo existe
                import os
                if not os.path.exists(ruta):
                    print(f"[ERROR] Archivo no existe: {ruta}")
                    selected_file.value = "Error: Archivo no encontrado"
                    selected_file.update()
                    return
                
                # Cargar productos del Excel
                productos = cargar_archivo_excel(ruta)
                print(f"[DEBUG] Productos cargados: {len(productos)}")
                
                # Actualizar lista global y UI
                productos_importados.clear()
                productos_importados.extend(productos)
                selected_file.value = f"{nombre} ({len(productos)} productos)"
                
                print(f"[SUCCESS] Archivo cargado exitosamente: {nombre}")
                
            except Exception as e:
                print(f"[ERROR] Error al procesar archivo: {e}")
                selected_file.value = f"Error: {str(e)}"
        else:
            print("[DEBUG] No se seleccionó ningún archivo")
            selected_file.value = "No se ha seleccionado ningun archivo"
        
        # Actualizar UI
        selected_file.update()
        
    # FilePicker mejorado para ejecutables - MÁXIMA COMPATIBILIDAD
    try:
        pick_files_window = ft.FilePicker(on_result=picked_file)
    except TypeError as e:
        print(f"[ERROR] Error creando FilePicker: {e}")
        # Fallback más simple
        pick_files_window = ft.FilePicker()
        pick_files_window.on_result = picked_file
    
    selected_file = ft.TextField(
        label="Archivo seleccionado", 
        value="Ningún archivo seleccionado",  # Valor inicial claro
        width=250, 
        read_only=True,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    
    # IMPORTANTE: Agregar FilePicker a overlay ANTES de usar
    page.overlay.append(pick_files_window)
    page.update()  # Actualizar para asegurar que el overlay esté listo
    
    def abrir_selector_archivo():
        """Función específica para abrir selector de archivos - Compatible con ejecutables"""
        try:
            print("[DEBUG] Iniciando selector de archivos...")
            pick_files_window.pick_files(
                allow_multiple=False,
                allowed_extensions=["xlsx", "xls"]  # Solo archivos Excel
            )
            print("[DEBUG] Selector de archivos abierto")
        except Exception as e:
            print(f"[ERROR] Error al abrir selector: {e}")
            selected_file.value = f"Error al abrir selector: {str(e)}"
            selected_file.update()
    
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
                                # CORREGIDO: Usar función específica para ejecutables
                                on_click=lambda e: abrir_selector_archivo(),
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
    """
    Cargar archivo Excel específico para UBICACIONES.
    Formato esperado: Modelo, Almacen, Estanteria, Cantidad, Comentarios (opcional)
    """
    try:
        # Leer archivo Excel con Polars
        df = pl.read_excel(ruta_archivo)
        
        ubicaciones = []
        
        # Iterar sobre las filas
        for row in df.iter_rows(named=True):
            # 1. MODELO (requerido) - La información del producto
            modelo = None
            modelo_opciones = ["Modelo", "modelo", "Material", "material", "Producto", "producto"]
            for opcion in modelo_opciones:
                if row.get(opcion) and str(row.get(opcion)).strip() and str(row.get(opcion)).strip().lower() != 'none':
                    modelo = str(row.get(opcion)).strip()
                    break
            
            if not modelo:
                # Si no hay modelo, generar uno automático
                modelo = f"UBICACION{len(ubicaciones)+1:03d}"
            
            # 2. ALMACÉN (requerido)
            almacen = None
            almacen_opciones = ["Almacen", "Almacén", "almacen", "almacén", "Deposito", "deposito"]
            for opcion in almacen_opciones:
                if row.get(opcion) and str(row.get(opcion)).strip():
                    almacen = str(row.get(opcion)).strip()
                    break
            
            if not almacen:
                almacen = "Almacén Principal"  # Valor por defecto
            
            # 3. ESTANTERÍA (requerido)
            estanteria = None
            estanteria_opciones = ["Estanteria", "Estantería", "estanteria", "estantería", 
                                 "Ubicacion", "Ubicación", "ubicacion", "ubicación", 
                                 "Pasillo", "pasillo", "Rack", "rack"]
            for opcion in estanteria_opciones:
                if row.get(opcion) and str(row.get(opcion)).strip():
                    estanteria = str(row.get(opcion)).strip()
                    break
            
            if not estanteria:
                estanteria = "A1"  # Valor por defecto
            
            # 4. CANTIDAD (requerido, default 1)
            cantidad = 1
            cantidad_opciones = ["Cantidad", "cantidad", "Qty", "qty", "Stock", "stock"]
            for opcion in cantidad_opciones:
                if row.get(opcion):
                    try:
                        cantidad = int(float(str(row.get(opcion))))  # Convertir a float primero por si hay decimales
                        if cantidad <= 0:
                            cantidad = 1  # Cantidad mínima 1
                        break
                    except (ValueError, TypeError):
                        continue
            
            # 5. COMENTARIOS (opcional)
            comentarios = "Sin observaciones"
            comentarios_opciones = ["Comentarios", "comentarios", "Observaciones", "observaciones", 
                                   "Notas", "notas", "Comentario", "comentario"]
            for opcion in comentarios_opciones:
                if row.get(opcion) and str(row.get(opcion)).strip():
                    comentarios = str(row.get(opcion)).strip()
                    break
            
            # Crear registro de ubicación
            ubicacion = {
                "modelo": modelo,
                "almacen": almacen,
                "estanteria": estanteria,
                "cantidad": cantidad,
                "observaciones": comentarios,
                "fecha_asignacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "usuario_asignacion": "Sistema de importación"
            }
            
            ubicaciones.append(ubicacion)
        
        return ubicaciones
        
    except Exception as e:
        return []


async def guardar_ubicaciones_en_firebase(ubicaciones, page):
    """Guardar ubicaciones masivamente en Firebase"""
    tema = GestorTemas.obtener_tema()
    
    print(f"[ALERT] DEBUG: Iniciando guardar_ubicaciones_en_firebase con {len(ubicaciones)} ubicaciones")
    
    # Mostrar progreso INMEDIATAMENTE
    mensaje_cargando = ft.AlertDialog(
        title=ft.Text("Importando ubicaciones", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content= ft.Container(
            content=ft.Row(
                controls=[
                    ft.ProgressRing(width=16, height=16, stroke_width=2, color=tema.PRIMARY_COLOR),
                    ft.Text(f"Procesando {len(ubicaciones)} ubicaciones...", color=tema.TEXT_COLOR)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=ft.Padding(15, 10, 15, 10),
        ),
        modal=True,
    )
    
    print("[ALERT] DEBUG: AlertDialog ubicaciones creado, intentando abrir...")
    page.open(mensaje_cargando)
    print("[ALERT] DEBUG: page.open() ejecutado para ubicaciones")
    page.update()
    print("[ALERT] DEBUG: page.update() ejecutado para ubicaciones - AlertDialog debería estar visible")
    
    # Delay mínimo para que el AlertDialog sea visible
    await asyncio.sleep(1.0)  # 1 segundo mínimo
    
    # Mensaje de éxito
    mensaje_exito = ft.AlertDialog(
        title=ft.Text("Ubicaciones importadas correctamente", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        actions=[ft.TextButton("Aceptar", 
                               style=ft.ButtonStyle(color=tema.PRIMARY_COLOR),
                               on_click=lambda e: page.close(mensaje_exito))],
        modal=True,
    )
    
    try:
        from conexiones.firebase import db
        from app.utils.historial import GestorHistorial
        from app.funciones.sesiones import SesionManager
        
        guardados = 0
        errores = 0
        
        for ubicacion in ubicaciones:
            try:
                # Guardar en colección 'ubicaciones'
                db.collection('ubicaciones').add(ubicacion)
                guardados += 1
                
                # Pequeño delay para hacer visible el progreso
                if guardados % 5 == 0:  # Cada 5 ubicaciones
                    await asyncio.sleep(0.1)  # 100ms para mostrar progreso
                
            except Exception as e:
                errores += 1
        
        # Registrar en historial
        gestor_historial = GestorHistorial()
        usuario_actual = SesionManager.obtener_usuario_actual()
        
        await gestor_historial.agregar_actividad(
            tipo="importar_ubicaciones",
            descripcion=f"Importó {guardados} ubicaciones desde Excel (Errores: {errores})",
            usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
        )
        
        # [PROCESO] SINCRONIZACIÓN AUTOMÁTICA después de importar ubicaciones
        if guardados > 0:
            try:
                # Invalidar cache de ubicaciones
                from app.utils.cache_firebase import cache_firebase
                cache_firebase.invalidar_cache_ubicaciones()
                
                # Ejecutar sincronización completa
                from app.utils.sincronizacion_inventario import sincronizar_inventario_completo
                resultado = await sincronizar_inventario_completo(mostrar_resultados=True)
                
                # Invalidar cache de productos también
                cache_firebase.invalidar_cache_productos()
                
                # Mensaje combinado de éxito
                sync_mensaje = ""
                if resultado['productos_actualizados'] > 0:
                    sync_mensaje = f" | {resultado['productos_actualizados']} cantidades sincronizadas"
                
                mensaje_exito.title = ft.Text(f"Ubicaciones importadas y sincronizadas{sync_mensaje}", color=tema.TEXT_COLOR)
                
            except Exception as sync_error:
                pass
        
        print("[ALERT] DEBUG: Cerrando AlertDialog de ubicaciones y mostrando éxito...")
        # Delay mínimo antes de cerrar para asegurar visibilidad
        await asyncio.sleep(0.5)  # Medio segundo adicional
        page.close(mensaje_cargando)
        page.open(mensaje_exito)
        
        return True
        
    except Exception as e:
        print(f"[ALERT] DEBUG: Error en guardar_ubicaciones_en_firebase: {e}")
        page.close(mensaje_cargando)
        page.open(ft.SnackBar(
            content=ft.Text(f"Error al importar ubicaciones: {e}"),
            bgcolor=tema.ERROR_COLOR
        ))
        return False
async def on_click_importar_archivo_ubicaciones(page, callback_actualizar=None):
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
        print("[ALERT] DEBUG: procesar_archivo_ubicaciones iniciado")
        if not archivo_seleccionado:
            page.open(ft.SnackBar(
                content=ft.Text("Por favor selecciona un archivo", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return

        try:
            print("[ALERT] DEBUG: Procesando archivo de ubicaciones...")
            # Usar directamente la ruta del archivo seleccionado
            ruta_archivo = archivo_seleccionado.path
            
            # Cargar y procesar Excel de ubicaciones
            ubicaciones = cargar_archivo_excel_ubicaciones(ruta_archivo)
            
            if ubicaciones:
                print("[ALERT] DEBUG: Ubicaciones cargadas, cerrando ventana y llamando guardar...")
                page.close(ventana_ubicaciones)
                exito = await guardar_ubicaciones_en_firebase(ubicaciones, page)
                
                # Actualizar tabla si se proporcionó callback y la importación fue exitosa
                if exito and callback_actualizar:
                    await callback_actualizar(forzar_refresh=True)
            else:
                page.open(ft.SnackBar(
                    content=ft.Text("Error al procesar el archivo de ubicaciones", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))
                
        except Exception as e:
            print(f"[ALERT] DEBUG: Error al procesar archivo de ubicaciones: {e}")
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