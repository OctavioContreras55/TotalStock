import os
import json
import polars as pl
import flet as ft
import asyncio
from datetime import datetime
from app.utils.temas import GestorTemas
from app.funciones.sesiones import SesionManager
from app.utils.historial import GestorHistorial

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

async def exportar_productos_excel(productos, page):
    """Exportar productos a archivo Excel con selección de ubicación"""
    tema = GestorTemas.obtener_tema()
    
    if not productos:
        page.open(ft.SnackBar(
            content=ft.Text("No hay productos para exportar", color=tema.TEXT_COLOR),
            bgcolor=tema.ERROR_COLOR
        ))
        return
    
    # Selector de directorio
    directorio_seleccionado = None
    
    def seleccionar_directorio(e: ft.FilePickerResultEvent):
        nonlocal directorio_seleccionado
        if e.path:
            directorio_seleccionado = e.path
            campo_ruta.value = e.path
            campo_ruta.update()
    
    selector_directorio = ft.FilePicker(on_result=seleccionar_directorio)
    page.overlay.append(selector_directorio)
    
    campo_ruta = ft.TextField(
        label="Directorio de destino",
        value="exports",
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        read_only=True
    )
    
    async def procesar_exportacion(e):
        # Usar directorio seleccionado o por defecto
        export_dir = directorio_seleccionado or "exports"
        
        # Mostrar indicador de carga
        mensaje_cargando = ft.AlertDialog(
            title=ft.Text("Exportando", color=tema.TEXT_COLOR),
            bgcolor=tema.CARD_COLOR,
            content=ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("Exportando productos...", color=tema.TEXT_COLOR),
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
        page.close(dialogo_ruta)
        page.update()
        
        try:
            # Crear directorio si no existe
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            
            # Nombre del archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"productos_{timestamp}.xlsx"
            ruta_archivo = os.path.join(export_dir, nombre_archivo)
            
            # Preparar datos para Excel
            datos_excel = []
            for producto in productos:
                datos_excel.append({
                    'ID': producto.get('id', ''),
                    'Modelo': producto.get('modelo', ''),
                    'Tipo': producto.get('tipo', ''),
                    'Nombre': producto.get('nombre', ''),
                    'Descripción': producto.get('descripcion', ''),
                    'Categoría': producto.get('categoria', ''),
                    'Ubicación': producto.get('ubicacion', ''),
                    'Stock Mínimo': producto.get('stock_min', 0),
                    'Stock Actual': producto.get('stock_act', 0),
                    'Precio': producto.get('precio', 0.0),
                    'Estado': producto.get('estado', 'Activo'),
                    'Fecha Registro': producto.get('fecha_registro', '')
                })
            
            # Crear DataFrame con Polars y guardar en Excel
            df = pl.DataFrame(datos_excel)
            df.write_excel(ruta_archivo, worksheet="Productos")
            
            # Registrar actividad en el historial
            gestor_historial = GestorHistorial()
            usuario_actual = SesionManager.obtener_usuario_actual()
            
            await gestor_historial.agregar_actividad(
                tipo="exportar_productos",
                descripcion=f"Exportó {len(productos)} productos a Excel ({nombre_archivo})",
                usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
            )
            
            # Cerrar indicador de carga
            page.close(mensaje_cargando)
            
            # Mostrar mensaje de éxito
            mensaje_exito = ft.AlertDialog(
                title=ft.Text("Exportación exitosa", color=tema.TEXT_COLOR),
                bgcolor=tema.CARD_COLOR,
                content=ft.Text(f"Productos exportados correctamente a:\n{ruta_archivo}", color=tema.TEXT_COLOR),
                actions=[
                    ft.TextButton(
                        "Aceptar", 
                        style=ft.ButtonStyle(color=tema.PRIMARY_COLOR),
                        on_click=lambda e: page.close(mensaje_exito)
                    )
                ],
                modal=True,
            )
            page.open(mensaje_exito)
            
        except Exception as e:
            # Cerrar indicador de carga
            page.close(mensaje_cargando)
            
            page.open(ft.SnackBar(
                content=ft.Text(f"Error al exportar productos: {str(e)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
    
    # Diálogo para seleccionar ruta
    dialogo_ruta = ft.AlertDialog(
        title=ft.Text("Seleccionar ubicación", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content=ft.Container(
            content=ft.Column([
                ft.Text("Seleccione el directorio donde guardar el archivo:", color=tema.TEXT_COLOR),
                ft.Row([
                    campo_ruta,
                    ft.ElevatedButton(
                        "Explorar",
                        style=ft.ButtonStyle(
                            bgcolor=tema.BUTTON_BG,
                            color=tema.BUTTON_TEXT,
                        ),
                        on_click=lambda e: selector_directorio.get_directory_path()
                    )
                ], spacing=10)
            ], spacing=15),
            padding=ft.Padding(10, 10, 10, 10),
            width=500,
            height=120
        ),
        actions=[
            ft.ElevatedButton(
                "Exportar",
                style=ft.ButtonStyle(
                    bgcolor=tema.BUTTON_SUCCESS_BG,
                    color=tema.BUTTON_TEXT,
                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                ),
                on_click=procesar_exportacion
            ),
            ft.TextButton(
                "Cancelar",
                style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                on_click=lambda e: page.close(dialogo_ruta)
            ),
        ],
        modal=True,
    )
    
    page.open(dialogo_ruta)
    page.update()

async def exportar_productos_json(productos, page):
    """Exportar productos a archivo JSON"""
    tema = GestorTemas.obtener_tema()
    
    if not productos:
        page.open(ft.SnackBar(
            content=ft.Text("No hay productos para exportar", color=tema.TEXT_COLOR),
            bgcolor=tema.ERROR_COLOR
        ))
        return
    
    try:
        # Crear directorio de exportación
        export_dir = "exports"
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        # Nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"productos_{timestamp}.json"
        ruta_archivo = os.path.join(export_dir, nombre_archivo)
        
        # Datos de exportación con metadatos
        datos_exportacion = {
            "metadata": {
                "fecha_exportacion": datetime.now().isoformat(),
                "total_productos": len(productos),
                "version": "1.0"
            },
            "productos": productos
        }
        
        # Guardar archivo JSON
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos_exportacion, f, indent=2, ensure_ascii=False, default=str)
        
        # Registrar actividad en el historial
        gestor_historial = GestorHistorial()
        usuario_actual = SesionManager.obtener_usuario_actual()
        
        await gestor_historial.agregar_actividad(
            tipo="exportar_productos",
            descripcion=f"Exportó {len(productos)} productos a JSON ({nombre_archivo})",
            usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
        )
        
        page.open(ft.SnackBar(
            content=ft.Text(f"Productos exportados a: {nombre_archivo}", color=tema.TEXT_COLOR),
            bgcolor=tema.SUCCESS_COLOR
        ))
        
    except Exception as e:
        page.open(ft.SnackBar(
            content=ft.Text(f"Error al exportar productos: {str(e)}", color=tema.TEXT_COLOR),
            bgcolor=tema.ERROR_COLOR
        ))

async def exportar_productos_pdf(productos, page):
    """Exportar productos a archivo PDF"""
    tema = GestorTemas.obtener_tema()
    
    if not PDF_AVAILABLE:
        page.open(ft.SnackBar(
            content=ft.Text("ReportLab no está instalado. Use pip install reportlab", color=tema.TEXT_COLOR),
            bgcolor=tema.ERROR_COLOR
        ))
        return
    
    if not productos:
        page.open(ft.SnackBar(
            content=ft.Text("No hay productos para exportar", color=tema.TEXT_COLOR),
            bgcolor=tema.ERROR_COLOR
        ))
        return

    # Selector de directorio
    directorio_seleccionado = None
    
    def seleccionar_directorio(e: ft.FilePickerResultEvent):
        nonlocal directorio_seleccionado
        if e.path:
            directorio_seleccionado = e.path
            campo_ruta.value = e.path
            campo_ruta.update()
    
    selector_directorio = ft.FilePicker(on_result=seleccionar_directorio)
    page.overlay.append(selector_directorio)
    
    campo_ruta = ft.TextField(
        label="Directorio de destino",
        value="exports",
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        read_only=True
    )
    
    async def procesar_exportacion_pdf(e):
        # Usar directorio seleccionado o por defecto
        export_dir = directorio_seleccionado or "exports"
        
        # Mostrar indicador de carga
        mensaje_cargando = ft.AlertDialog(
            title=ft.Text("Exportando PDF", color=tema.TEXT_COLOR),
            bgcolor=tema.CARD_COLOR,
            content=ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("Generando PDF...", color=tema.TEXT_COLOR),
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
        page.close(dialogo_ruta_pdf)
        page.update()
        
        try:
            # Crear directorio si no existe
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            
            # Nombre del archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"productos_{timestamp}.pdf"
            ruta_archivo = os.path.join(export_dir, nombre_archivo)
            
            # Crear documento PDF
            doc = SimpleDocTemplate(ruta_archivo, pagesize=A4)
            story = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Center
            )
            
            # Título
            story.append(Paragraph("Reporte de Productos - TotalStock", title_style))
            story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
            story.append(Paragraph(f"Total de productos: {len(productos)}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Preparar datos para la tabla
            datos_tabla = [['Modelo', 'Nombre', 'Tipo', 'Stock', 'Precio']]
            
            for producto in productos:
                fila = [
                    str(producto.get('modelo', ''))[:15],  # Limitar longitud
                    str(producto.get('nombre', ''))[:20],
                    str(producto.get('tipo', ''))[:15],
                    str(producto.get('stock_act', 0)),
                    f"${producto.get('precio', 0.0):.2f}"
                ]
                datos_tabla.append(fila)
            
            # Crear tabla
            tabla = Table(datos_tabla)
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(tabla)
            doc.build(story)
            
            # Registrar actividad en el historial
            gestor_historial = GestorHistorial()
            usuario_actual = SesionManager.obtener_usuario_actual()
            
            await gestor_historial.agregar_actividad(
                tipo="exportar_productos",
                descripcion=f"Exportó {len(productos)} productos a PDF ({nombre_archivo})",
                usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
            )
            
            # Cerrar indicador de carga
            page.close(mensaje_cargando)
            
            # Mostrar mensaje de éxito
            mensaje_exito = ft.AlertDialog(
                title=ft.Text("Exportación PDF exitosa", color=tema.TEXT_COLOR),
                bgcolor=tema.CARD_COLOR,
                content=ft.Text(f"Productos exportados correctamente a:\n{ruta_archivo}", color=tema.TEXT_COLOR),
                actions=[
                    ft.TextButton(
                        "Aceptar", 
                        style=ft.ButtonStyle(color=tema.PRIMARY_COLOR),
                        on_click=lambda e: page.close(mensaje_exito)
                    )
                ],
                modal=True,
            )
            page.open(mensaje_exito)
            
        except Exception as e:
            # Cerrar indicador de carga
            page.close(mensaje_cargando)
            
            page.open(ft.SnackBar(
                content=ft.Text(f"Error al exportar PDF: {str(e)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
    
    # Diálogo para seleccionar ruta PDF
    dialogo_ruta_pdf = ft.AlertDialog(
        title=ft.Text("Exportar a PDF", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content=ft.Container(
            content=ft.Column([
                ft.Text("Seleccione el directorio donde guardar el archivo PDF:", color=tema.TEXT_COLOR),
                ft.Row([
                    campo_ruta,
                    ft.ElevatedButton(
                        "Explorar",
                        style=ft.ButtonStyle(
                            bgcolor=tema.BUTTON_BG,
                            color=tema.BUTTON_TEXT,
                        ),
                        on_click=lambda e: selector_directorio.get_directory_path()
                    )
                ], spacing=10)
            ], spacing=15),
            padding=ft.Padding(10, 10, 10, 10),
            width=500,
            height=120
        ),
        actions=[
            ft.ElevatedButton(
                "Exportar PDF",
                style=ft.ButtonStyle(
                    bgcolor=tema.BUTTON_SUCCESS_BG,
                    color=tema.BUTTON_TEXT,
                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                ),
                on_click=procesar_exportacion_pdf
            ),
            ft.TextButton(
                "Cancelar",
                style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                on_click=lambda e: page.close(dialogo_ruta_pdf)
            ),
        ],
        modal=True,
    )
    
    page.open(dialogo_ruta_pdf)
    page.update()

def mostrar_dialogo_exportar(productos, page):
    """Mostrar diálogo para seleccionar formato de exportación"""
    tema = GestorTemas.obtener_tema()
    
    async def exportar_excel_handler(e):
        page.close(dialogo_exportar)
        await exportar_productos_excel(productos, page)
    
    async def exportar_json_handler(e):
        page.close(dialogo_exportar)
        await exportar_productos_json(productos, page)
    
    async def exportar_pdf_handler(e):
        page.close(dialogo_exportar)
        await exportar_productos_pdf(productos, page)
    
    dialogo_exportar = ft.AlertDialog(
        title=ft.Text("Exportar Productos", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content=ft.Container(
            content=ft.Column([
                ft.Text(f"Se exportarán {len(productos)} productos.", color=tema.TEXT_COLOR),
                ft.Text("Seleccione el formato:", color=tema.TEXT_SECONDARY, size=14),
            ], spacing=10),
            padding=ft.Padding(10, 10, 10, 10),
            width=300,
            height=100
        ),
        actions=[
            ft.ElevatedButton(
                "Excel (.xlsx)",
                style=ft.ButtonStyle(
                    bgcolor=tema.BUTTON_SUCCESS_BG,
                    color=tema.BUTTON_TEXT,
                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                ),
                on_click=exportar_excel_handler
            ),
            ft.ElevatedButton(
                "PDF",
                style=ft.ButtonStyle(
                    bgcolor="#FF5722",  # Color naranja para PDF
                    color=tema.BUTTON_TEXT,
                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                ),
                on_click=exportar_pdf_handler
            ),
            ft.ElevatedButton(
                "JSON",
                style=ft.ButtonStyle(
                    bgcolor=tema.BUTTON_BG,
                    color=tema.BUTTON_TEXT,
                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                ),
                on_click=exportar_json_handler
            ),
            ft.TextButton(
                "Cancelar",
                style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                on_click=lambda e: page.close(dialogo_exportar)
            ),
        ],
        modal=True,
    )
    
    page.open(dialogo_exportar)
    page.update()


async def exportar_ubicaciones(ubicaciones, page):
    """Exportar ubicaciones a archivo Excel, JSON o PDF con selección de ubicación"""
    tema = GestorTemas.obtener_tema()
    
    if not ubicaciones:
        page.open(ft.SnackBar(
            content=ft.Text("No hay ubicaciones para exportar", color=tema.TEXT_COLOR),
            bgcolor=tema.ERROR_COLOR
        ))
        return
    
    # Selector de directorio
    directorio_seleccionado = None
    
    def seleccionar_directorio(e: ft.FilePickerResultEvent):
        nonlocal directorio_seleccionado
        if e.path:
            directorio_seleccionado = e.path
            campo_ruta.value = e.path
            campo_ruta.update()
    
    selector_directorio = ft.FilePicker(on_result=seleccionar_directorio)
    page.overlay.append(selector_directorio)
    
    campo_ruta = ft.TextField(
        label="Directorio de destino",
        value="exports",
        width=400,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    
    # Dropdown para formato con mejor visibilidad
    dropdown_formato = ft.Dropdown(
        label="Formato de exportación",
        options=[
            ft.dropdown.Option("excel", "Excel (.xlsx)"),
            ft.dropdown.Option("json", "JSON (.json)"),
            ft.dropdown.Option("pdf", "PDF (.pdf)") if PDF_AVAILABLE else None,
        ],
        value="excel",
        width=200,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY),
        text_style=ft.TextStyle(color=tema.TEXT_COLOR, size=14)  # Mejorar visibilidad del texto
    )
    
    # Remover None si PDF no está disponible
    if not PDF_AVAILABLE:
        dropdown_formato.options = [opt for opt in dropdown_formato.options if opt is not None]
    
    async def realizar_exportacion(e):
        ruta_destino = campo_ruta.value or "exports"
        formato = dropdown_formato.value
        
        # Crear directorio si no existe
        os.makedirs(ruta_destino, exist_ok=True)
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            if formato == "excel":
                await exportar_ubicaciones_excel_archivo(ubicaciones, ruta_destino, timestamp, page)
            elif formato == "json":
                await exportar_ubicaciones_json_archivo(ubicaciones, ruta_destino, timestamp, page)
            elif formato == "pdf" and PDF_AVAILABLE:
                await exportar_ubicaciones_pdf_archivo(ubicaciones, ruta_destino, timestamp, page)
                
            page.close(dialogo_exportar)
            
        except Exception as e:
            print(f"Error en exportación: {e}")
            page.open(ft.SnackBar(
                content=ft.Text(f"Error al exportar: {str(e)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
    
    dialogo_exportar = ft.AlertDialog(
        title=ft.Text("Exportar Ubicaciones", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content=ft.Container(
            content=ft.Column([
                ft.Text("Seleccione el directorio y formato para exportar", color=tema.TEXT_COLOR),
                ft.Container(height=10),
                ft.Row([
                    campo_ruta,
                    ft.IconButton(
                        ft.Icons.FOLDER_OPEN,
                        icon_color=tema.PRIMARY_COLOR,
                        on_click=lambda e: selector_directorio.get_directory_path(),
                        tooltip="Seleccionar directorio"
                    )
                ]),
                ft.Container(height=10),
                dropdown_formato,
                ft.Container(height=10),
                ft.Text(f"Se exportarán {len(ubicaciones)} ubicaciones", 
                       color=tema.TEXT_SECONDARY, size=12),
            ], spacing=5),
            width=500,
            height=250,
            padding=ft.Padding(15, 15, 15, 15)
        ),
        actions=[
            ft.ElevatedButton(
                "Exportar",
                style=ft.ButtonStyle(
                    bgcolor=tema.BUTTON_BG,
                    color=tema.BUTTON_TEXT,
                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                ),
                on_click=realizar_exportacion
            ),
            ft.TextButton(
                "Cancelar",
                style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                on_click=lambda e: page.close(dialogo_exportar)
            ),
        ],
        modal=True,
    )
    
    page.open(dialogo_exportar)
    page.update()


async def exportar_ubicaciones_excel_archivo(ubicaciones, ruta_destino, timestamp, page):
    """Exportar ubicaciones a archivo Excel"""
    tema = GestorTemas.obtener_tema()
    nombre_archivo = f"ubicaciones_{timestamp}.xlsx"
    ruta_completa = os.path.join(ruta_destino, nombre_archivo)
    
    # Preparar datos para Polars
    datos = []
    for ubicacion in ubicaciones:
        datos.append({
            "Modelo": ubicacion.get("modelo", ""),
            "Almacén": ubicacion.get("almacen", ""),
            "Estantería": ubicacion.get("estanteria", ""),
            "Fecha Asignación": ubicacion.get("fecha_asignacion", ""),
            "Observaciones": ubicacion.get("observaciones", "")
        })
    
    # Crear DataFrame con Polars y exportar
    df = pl.DataFrame(datos)
    df.write_excel(ruta_completa, worksheet="Ubicaciones")
    
    # Registrar actividad
    usuario_actual = SesionManager.obtener_usuario_actual()
    gestor_historial = GestorHistorial()
    await gestor_historial.agregar_actividad(
        tipo="exportar_ubicaciones",
        descripcion=f"Exportó {len(ubicaciones)} ubicaciones a Excel: {nombre_archivo}",
        usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
    )
    
    page.open(ft.SnackBar(
        content=ft.Text(f"Ubicaciones exportadas: {ruta_completa}", color=tema.TEXT_COLOR),
        bgcolor=tema.SUCCESS_COLOR
    ))


async def exportar_ubicaciones_json_archivo(ubicaciones, ruta_destino, timestamp, page):
    """Exportar ubicaciones a archivo JSON"""
    tema = GestorTemas.obtener_tema()
    nombre_archivo = f"ubicaciones_{timestamp}.json"
    ruta_completa = os.path.join(ruta_destino, nombre_archivo)
    
    # Preparar datos
    datos_exportacion = {
        "fecha_exportacion": datetime.now().isoformat(),
        "total_ubicaciones": len(ubicaciones),
        "ubicaciones": ubicaciones
    }
    
    # Exportar JSON
    with open(ruta_completa, 'w', encoding='utf-8') as f:
        json.dump(datos_exportacion, f, ensure_ascii=False, indent=2)
    
    # Registrar actividad
    usuario_actual = SesionManager.obtener_usuario_actual()
    gestor_historial = GestorHistorial()
    await gestor_historial.agregar_actividad(
        tipo="exportar_ubicaciones",
        descripcion=f"Exportó {len(ubicaciones)} ubicaciones a JSON: {nombre_archivo}",
        usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
    )
    
    page.open(ft.SnackBar(
        content=ft.Text(f"Ubicaciones exportadas: {ruta_completa}", color=tema.TEXT_COLOR),
        bgcolor=tema.SUCCESS_COLOR
    ))


async def exportar_ubicaciones_pdf_archivo(ubicaciones, ruta_destino, timestamp, page):
    """Exportar ubicaciones a archivo PDF"""
    if not PDF_AVAILABLE:
        page.open(ft.SnackBar(
            content=ft.Text("ReportLab no está instalado", color=tema.TEXT_COLOR),
            bgcolor=tema.ERROR_COLOR
        ))
        return
    
    tema = GestorTemas.obtener_tema()
    nombre_archivo = f"ubicaciones_{timestamp}.pdf"
    ruta_completa = os.path.join(ruta_destino, nombre_archivo)
    
    # Crear documento PDF
    doc = SimpleDocTemplate(ruta_completa, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Centrado
    )
    
    # Título
    title = Paragraph("Reporte de Ubicaciones", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Información del reporte
    info_style = styles['Normal']
    fecha_info = Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", info_style)
    total_info = Paragraph(f"Total de ubicaciones: {len(ubicaciones)}", info_style)
    elements.append(fecha_info)
    elements.append(total_info)
    elements.append(Spacer(1, 20))
    
    # Preparar datos para la tabla
    data = [["Modelo", "Nombre", "Almacén", "Ubicación", "Cantidad"]]
    
    for ubicacion in ubicaciones:
        data.append([
            ubicacion.get("modelo", "")[:20],  # Limitar longitud
            ubicacion.get("nombre", "")[:25],
            ubicacion.get("almacen", "")[:15],
            ubicacion.get("ubicacion", "")[:15],
            str(ubicacion.get("cantidad", 0))
        ])
    
    # Crear tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Generar PDF
    doc.build(elements)
    
    # Registrar actividad
    usuario_actual = SesionManager.obtener_usuario_actual()
    gestor_historial = GestorHistorial()
    await gestor_historial.agregar_actividad(
        tipo="exportar_ubicaciones",
        descripcion=f"Exportó {len(ubicaciones)} ubicaciones a PDF: {nombre_archivo}",
        usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
    )
    
    page.open(ft.SnackBar(
        content=ft.Text(f"Ubicaciones exportadas: {ruta_completa}", color=tema.TEXT_COLOR),
        bgcolor=tema.SUCCESS_COLOR
    ))
