import flet as ft
from app.utils.temas import GestorTemas
from app.utils.historial import GestorHistorial
from app.funciones.sesiones import SesionManager
from conexiones.firebase import db
from datetime import datetime, timedelta
import json
import os

async def vista_reportes(nombre_seccion, contenido, page):
    """Vista completa para generar y visualizar reportes del sistema"""
    tema = GestorTemas.obtener_tema()
    
    # Dimensiones responsivas
    ancho_ventana = page.window.width or 1200
    alto_ventana = page.window.height or 800

    # Estado del reporte
    tipo_reporte_seleccionado = None
    fecha_inicio = datetime.now() - timedelta(days=30)  # Último mes por defecto
    fecha_fin = datetime.now()
    usuario_filtro = "todos"
    datos_reporte = []

    # Tipos de reportes disponibles
    tipos_reportes = {
        "movimientos": {
            "nombre": "Movimientos de Productos",
            "icono": ft.Icons.SWAP_HORIZ,
            "color": tema.PRIMARY_COLOR,
            "descripcion": "Reporte detallado de todos los movimientos de productos entre ubicaciones"
        },
        "ubicaciones": {
            "nombre": "Estado de Ubicaciones",
            "icono": ft.Icons.LOCATION_ON,
            "color": tema.SUCCESS_COLOR,
            "descripcion": "Inventario actual por ubicaciones y almacenes"
        },
        "productos": {
            "nombre": "Inventario de Productos",
            "icono": ft.Icons.INVENTORY,
            "color": tema.PRIMARY_COLOR,
            "descripcion": "Estado completo del inventario de productos"
        },
        "altas": {
            "nombre": "Altas de Productos",
            "icono": ft.Icons.ADD_BOX,
            "color": tema.SUCCESS_COLOR,
            "descripcion": "Productos dados de alta en el sistema"
        },
        "bajas": {
            "nombre": "Bajas de Productos",
            "icono": ft.Icons.REMOVE_CIRCLE,
            "color": tema.ERROR_COLOR,
            "descripcion": "Productos dados de baja del sistema"
        },
        "usuarios": {
            "nombre": "Actividad de Usuarios",
            "icono": ft.Icons.PEOPLE,
            "color": tema.WARNING_COLOR,
            "descripcion": "Actividades realizadas por usuarios del sistema"
        },
        "stock_critico": {
            "nombre": "Stock Crítico",
            "icono": ft.Icons.WARNING,
            "color": tema.ERROR_COLOR,
            "descripcion": "Productos con stock bajo o crítico"
        },
        "rotacion": {
            "nombre": "Rotación de Inventario",
            "icono": ft.Icons.AUTORENEW,
            "color": tema.PRIMARY_COLOR,
            "descripcion": "Análisis de rotación y movimiento de productos"
        }
    }

    async def obtener_datos_reporte(tipo_reporte):
        """Obtener datos según el tipo de reporte seleccionado"""
        try:
            gestor_historial = GestorHistorial()
            
            if tipo_reporte == "movimientos":
                return await generar_reporte_movimientos()
            elif tipo_reporte == "ubicaciones":
                return await generar_reporte_ubicaciones()
            elif tipo_reporte == "productos":
                return await generar_reporte_productos()
            elif tipo_reporte == "altas":
                return await generar_reporte_altas()
            elif tipo_reporte == "bajas":
                return await generar_reporte_bajas()
            elif tipo_reporte == "usuarios":
                return await generar_reporte_usuarios()
            elif tipo_reporte == "stock_critico":
                return await generar_reporte_stock_critico()
            elif tipo_reporte == "rotacion":
                return await generar_reporte_rotacion()
            else:
                return []
                
        except Exception as e:
            print(f"Error al obtener datos del reporte: {e}")
            return []

    async def generar_reporte_movimientos():
        """Generar reporte de movimientos de productos"""
        # En implementación real, estos datos vendrían de Firebase
        return [
            {
                "fecha": "2024-01-15 14:30:25",
                "usuario": "Admin",
                "producto": "Laptop Dell Inspiron",
                "modelo": "LAP001",
                "cantidad": 5,
                "origen": "Almacén Principal → Estante A-3, Nivel 2",
                "destino": "Almacén Secundario → Estante B-2, Nivel 1",
                "motivo": "Redistribución de inventario",
                "tipo": "Transferencia"
            },
            {
                "fecha": "2024-01-15 10:15:12",
                "usuario": "Operador1",
                "producto": "Mouse Logitech MX",
                "modelo": "MOU002",
                "cantidad": 25,
                "origen": "Almacén Secundario → Cajón B-1",
                "destino": "Almacén Principal → Cajón A-5",
                "motivo": "Reposición de stock",
                "tipo": "Transferencia"
            },
            {
                "fecha": "2024-01-14 16:45:33",
                "usuario": "Supervisor",
                "producto": "Teclado Mecánico Corsair",
                "modelo": "TEC003",
                "cantidad": 10,
                "origen": "Recepción",
                "destino": "Almacén de Repuestos → Estante C-2",
                "motivo": "Ingreso de nueva mercancía",
                "tipo": "Ingreso"
            }
        ]

    async def generar_reporte_ubicaciones():
        """Generar reporte de estado de ubicaciones"""
        return [
            {
                "almacen": "Almacén Principal",
                "ubicacion": "Estante A-3, Nivel 2",
                "productos_total": 3,
                "productos": [
                    {"modelo": "LAP001", "nombre": "Laptop Dell Inspiron", "cantidad": 10},
                    {"modelo": "MON001", "nombre": "Monitor Samsung 24", "cantidad": 5},
                    {"modelo": "CPU001", "nombre": "CPU Intel i7", "cantidad": 8}
                ],
                "capacidad_utilizada": "75%",
                "ultima_actualizacion": "2024-01-15 14:30:25",
                "usuario_actualizacion": "Admin"
            },
            {
                "almacen": "Almacén Secundario",
                "ubicacion": "Cajón B-1",
                "productos_total": 2,
                "productos": [
                    {"modelo": "MOU002", "nombre": "Mouse Logitech MX", "cantidad": 25},
                    {"modelo": "PAD001", "nombre": "MousePad Gaming", "cantidad": 15}
                ],
                "capacidad_utilizada": "40%",
                "ultima_actualizacion": "2024-01-15 10:15:12",
                "usuario_actualizacion": "Operador1"
            }
        ]

    async def generar_reporte_productos():
        """Generar reporte completo de productos desde Firebase"""
        try:
            from app.crud_productos.create_producto import obtener_productos_firebase
            productos_firebase = await obtener_productos_firebase()
            
            reporte_productos = []
            for producto in productos_firebase:
                reporte_productos.append({
                    "modelo": producto.get("modelo", "N/A"),
                    "nombre": producto.get("nombre", "N/A"),
                    "categoria": producto.get("categoria", "Sin categoría"),
                    "stock_actual": producto.get("cantidad", 0),
                    "stock_minimo": producto.get("stock_min", 0),
                    "precio_unitario": producto.get("precio", 0.0),
                    "valor_total": producto.get("cantidad", 0) * producto.get("precio", 0.0),
                    "fecha_ingreso": producto.get("fecha_registro", "N/A"),
                    "estado": producto.get("estado", "Activo")
                })
            
            return reporte_productos
            
        except Exception as e:
            print(f"Error al generar reporte de productos: {e}")
            # Datos de ejemplo como fallback
            return [
                {
                    "modelo": "LAP001",
                    "nombre": "Laptop Dell Inspiron",
                    "categoria": "Equipos de Cómputo",
                    "stock_actual": 23,
                    "stock_minimo": 5,
                    "precio_unitario": 15000.00,
                    "valor_total": 345000.00,
                    "fecha_ingreso": "2024-01-10 09:00:00",
                    "estado": "Activo"
                }
            ]

    async def generar_reporte_altas():
        """Generar reporte de productos dados de alta"""
        return [
            {
                "fecha": "2024-01-15 09:15:30",
                "usuario": "Admin",
                "modelo": "TAB001",
                "nombre": "Tablet Samsung Galaxy",
                "categoria": "Dispositivos Móviles",
                "cantidad_inicial": 12,
                "precio_unitario": 8500.00,
                "valor_total": 102000.00,
                "proveedor": "Tech Solutions SA",
                "motivo": "Nuevo producto en catálogo",
                "ubicacion_asignada": "Almacén Principal → Estante D-1"
            },
            {
                "fecha": "2024-01-14 16:45:15",
                "usuario": "Supervisor",
                "modelo": "TEC003",
                "nombre": "Teclado Mecánico Corsair",
                "categoria": "Periféricos",
                "cantidad_inicial": 10,
                "precio_unitario": 2300.00,
                "valor_total": 23000.00,
                "proveedor": "Gaming Pro",
                "motivo": "Reposición de stock",
                "ubicacion_asignada": "Almacén de Repuestos → Estante C-2"
            }
        ]

    async def generar_reporte_bajas():
        """Generar reporte de productos dados de baja"""
        return [
            {
                "fecha": "2024-01-13 14:22:10",
                "usuario": "Admin",
                "modelo": "LAP999",
                "nombre": "Laptop HP Antigua",
                "categoria": "Equipos de Cómputo",
                "cantidad_baja": 3,
                "valor_perdido": 18000.00,
                "motivo": "Obsolescencia tecnológica",
                "ubicacion_origen": "Almacén Principal → Estante A-1",
                "estado_final": "Desechado",
                "observaciones": "Equipos con más de 5 años de uso"
            },
            {
                "fecha": "2024-01-12 10:30:45",
                "usuario": "Operador1",
                "modelo": "MOU999",
                "nombre": "Mouse Básico Genérico",
                "categoria": "Periféricos",
                "cantidad_baja": 8,
                "valor_perdido": 2400.00,
                "motivo": "Daño por uso",
                "ubicacion_origen": "Almacén Secundario → Cajón C-3",
                "estado_final": "Reparación/Reciclaje",
                "observaciones": "Fallas mecánicas recurrentes"
            }
        ]

    async def generar_reporte_usuarios():
        """Generar reporte de actividad de usuarios"""
        return [
            {
                "fecha": "2024-01-15 14:30:25",
                "usuario": "Admin",
                "accion": "Movimiento de Producto",
                "detalle": "Movió 5 unidades de 'Laptop Dell Inspiron' desde Almacén Principal hacia Almacén Secundario",
                "modulo": "Movimientos",
                "ip_origen": "192.168.1.100",
                "duracion_sesion": "2h 15m"
            },
            {
                "fecha": "2024-01-15 10:15:12",
                "usuario": "Operador1",
                "accion": "Alta de Producto",
                "detalle": "Registró nuevo producto 'Teclado Mecánico Corsair' con 10 unidades",
                "modulo": "Inventario",
                "ip_origen": "192.168.1.101",
                "duracion_sesion": "1h 45m"
            },
            {
                "fecha": "2024-01-15 08:00:00",
                "usuario": "Supervisor",
                "accion": "Inicio de Sesión",
                "detalle": "Acceso al sistema TotalStock",
                "modulo": "Autenticación",
                "ip_origen": "192.168.1.102",
                "duracion_sesion": "4h 30m"
            }
        ]

    async def generar_reporte_stock_critico():
        """Generar reporte de productos con stock crítico desde Firebase"""
        try:
            from app.crud_productos.create_producto import obtener_productos_firebase
            productos_firebase = await obtener_productos_firebase()
            
            productos_criticos = []
            for producto in productos_firebase:
                stock_actual = producto.get("cantidad", 0)
                stock_minimo = producto.get("stock_min", 0)
                
                # Solo incluir productos con stock por debajo del mínimo
                if stock_actual <= stock_minimo:
                    deficit = stock_minimo - stock_actual
                    
                    # Determinar prioridad
                    if stock_actual == 0:
                        prioridad = "CRÍTICA"
                        accion = "Reposición inmediata requerida"
                    elif stock_actual < stock_minimo * 0.5:
                        prioridad = "ALTA"
                        accion = "Compra urgente requerida"
                    else:
                        prioridad = "MEDIA"
                        accion = "Programar reposición"
                    
                    productos_criticos.append({
                        "modelo": producto.get("modelo", "N/A"),
                        "nombre": producto.get("nombre", "N/A"),
                        "categoria": producto.get("categoria", "Sin categoría"),
                        "stock_actual": stock_actual,
                        "stock_minimo": stock_minimo,
                        "deficit": deficit,
                        "prioridad": prioridad,
                        "accion_sugerida": accion,
                        "ubicacion": producto.get("ubicacion", "Sin ubicación"),
                        "ultima_actualizacion": producto.get("fecha_registro", "N/A")
                    })
            
            return productos_criticos
            
        except Exception as e:
            print(f"Error al generar reporte de stock crítico: {e}")
            # Datos de ejemplo como fallback
            return [
                {
                    "modelo": "RAM001",
                    "nombre": "Memoria RAM DDR4 8GB",
                    "categoria": "Componentes",
                    "stock_actual": 2,
                    "stock_minimo": 10,
                    "deficit": 8,
                    "prioridad": "CRÍTICA",
                    "accion_sugerida": "Compra urgente requerida",
                    "ubicacion": "Almacén Principal → Estante B-5"
                }
            ]

    async def generar_reporte_rotacion():
        """Generar reporte de rotación de inventario"""
        return [
            {
                "modelo": "LAP001",
                "nombre": "Laptop Dell Inspiron",
                "categoria": "Equipos de Cómputo",
                "entradas_mes": 15,
                "salidas_mes": 12,
                "rotacion_mensual": 0.52,  # 52% del stock se movió
                "dias_inventario": 30,
                "frecuencia_movimientos": 8,  # 8 movimientos en el mes
                "tendencia": "ESTABLE",
                "valor_rotado": 180000.00,
                "clasificacion": "ROTACIÓN NORMAL"
            },
            {
                "modelo": "MOU002",
                "nombre": "Mouse Logitech MX",
                "categoria": "Periféricos",
                "entradas_mes": 50,
                "salidas_mes": 45,
                "rotacion_mensual": 0.60,
                "dias_inventario": 25,
                "frecuencia_movimientos": 12,
                "tendencia": "ALTA ROTACIÓN",
                "valor_rotado": 42500.00,
                "clasificacion": "PRODUCTO ESTRELLA"
            }
        ]

    # Componentes de la interfaz
    def crear_selector_tipo_reporte():
        """Crear selector de tipo de reporte"""
        cards_reportes = []
        
        for tipo_id, info in tipos_reportes.items():
            def crear_handler(tipo):
                def handler(e):
                    nonlocal tipo_reporte_seleccionado
                    tipo_reporte_seleccionado = tipo
                    actualizar_selector_visual()
                    page.update()
                return handler

            esta_seleccionado = tipo_reporte_seleccionado == tipo_id
            
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(info["icono"], color=info["color"], size=32),
                        ft.Text(info["nombre"], 
                               weight=ft.FontWeight.BOLD, 
                               color=tema.TEXT_COLOR,
                               text_align=ft.TextAlign.CENTER,
                               size=12),
                        ft.Text(info["descripcion"],
                               color=tema.SECONDARY_TEXT_COLOR,
                               text_align=ft.TextAlign.CENTER,
                               size=10)
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8),
                    padding=15,
                    width=180,
                    height=140,
                    on_click=crear_handler(tipo_id)
                ),
                color=tema.PRIMARY_COLOR if esta_seleccionado else tema.CARD_COLOR,
                elevation=5 if esta_seleccionado else 2
            )
            cards_reportes.append(card)
        
        # Organizar en filas de 4
        filas = []
        for i in range(0, len(cards_reportes), 4):
            fila = ft.Row(
                cards_reportes[i:i+4],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15
            )
            filas.append(fila)
        
        return ft.Column(filas, spacing=15)

    selector_reportes = crear_selector_tipo_reporte()

    def actualizar_selector_visual():
        """Actualizar el selector visual de reportes"""
        nonlocal selector_reportes
        selector_reportes = crear_selector_tipo_reporte()

    # Controles de filtro de fechas
    campo_fecha_inicio = ft.TextField(
        label="Fecha Inicio (YYYY-MM-DD)",
        value=fecha_inicio.strftime("%Y-%m-%d"),
        width=200,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR
    )

    campo_fecha_fin = ft.TextField(
        label="Fecha Fin (YYYY-MM-DD)",
        value=fecha_fin.strftime("%Y-%m-%d"),
        width=200,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR
    )

    # Selector de usuario
    dropdown_usuario = ft.Dropdown(
        label="Filtrar por Usuario",
        value="todos",
        options=[
            ft.dropdown.Option("todos", "Todos los usuarios"),
            ft.dropdown.Option("Admin", "Admin"),
            ft.dropdown.Option("Operador1", "Operador1"),
            ft.dropdown.Option("Supervisor", "Supervisor")
        ],
        width=200,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR
    )

    # Contenedor para mostrar el reporte
    contenedor_reporte = ft.Container(
            content=ft.Text("Selecciona un tipo de reporte y haz clic en 'Generar Reporte'",
                           color=tema.SECONDARY_TEXT_COLOR,
                           italic=True),
            alignment=ft.alignment.center,
            height=400,
            bgcolor=tema.CARD_COLOR,
            border_radius=tema.BORDER_RADIUS,
            padding=20,
    )

    async def generar_reporte(e):
        """Generar el reporte seleccionado"""
        if not tipo_reporte_seleccionado:
            page.open(ft.SnackBar(
                content=ft.Text("Selecciona un tipo de reporte", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return

        # Mostrar indicador de carga
        contenedor_reporte.content = ft.Row([
            ft.ProgressRing(color=tema.PRIMARY_COLOR),
            ft.Text("Generando reporte...", color=tema.TEXT_COLOR)
        ], alignment=ft.MainAxisAlignment.CENTER)
        page.update()

        try:
            # Obtener datos del reporte
            nonlocal datos_reporte
            datos_reporte = await obtener_datos_reporte(tipo_reporte_seleccionado)
            
            # Construir tabla del reporte
            construir_tabla_reporte()
            
        except Exception as ex:
            contenedor_reporte.content = ft.Text(
                f"Error al generar reporte: {str(ex)}",
                color=tema.ERROR_COLOR
            )
            page.update()

    def construir_tabla_reporte():
        """Construir la tabla con los datos del reporte"""
        if not datos_reporte:
            contenedor_reporte.content = ft.Text(
                "No se encontraron datos para el reporte seleccionado",
                color=tema.SECONDARY_TEXT_COLOR
            )
            page.update()
            return

        # Crear columnas según el tipo de reporte
        columnas = obtener_columnas_reporte()
        filas = obtener_filas_reporte()

        tabla = ft.DataTable(
            columns=columnas,
            rows=filas,
            border=ft.border.all(1, tema.DIVIDER_COLOR),
            border_radius=tema.BORDER_RADIUS,
            bgcolor=tema.CARD_COLOR,
            heading_row_color=tema.PRIMARY_COLOR,
            heading_row_height=50,
            data_row_min_height=40,
            column_spacing=20
        )

        # Estadísticas del reporte
        stats = obtener_estadisticas_reporte()
        
        contenedor_reporte.content = ft.Column([
            # Estadísticas
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Total Registros", size=12, color=tema.SECONDARY_TEXT_COLOR),
                            ft.Text(str(stats["total"]), size=20, weight=ft.FontWeight.BOLD, color=tema.PRIMARY_COLOR)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=tema.BG_COLOR,
                        padding=15,
                        border_radius=8,
                        expand=True
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Período", size=12, color=tema.SECONDARY_TEXT_COLOR),
                            ft.Text(stats["periodo"], size=14, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=tema.BG_COLOR,
                        padding=15,
                        border_radius=8,
                        expand=True
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Generado", size=12, color=tema.SECONDARY_TEXT_COLOR),
                            ft.Text(datetime.now().strftime("%Y-%m-%d %H:%M"), 
                                   size=12, color=tema.TEXT_COLOR)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=tema.BG_COLOR,
                        padding=15,
                        border_radius=8,
                        expand=True
                    )
                ], spacing=10),
                margin=ft.margin.only(bottom=20)
            ),
            
            # Tabla del reporte
            ft.Container(
                content=tabla,
                border=ft.border.all(1, tema.DIVIDER_COLOR),
                border_radius=tema.BORDER_RADIUS,
                padding=10
            )
        ], 
        scroll=ft.ScrollMode.AUTO,
        height=600)
        
        page.update()

    def obtener_columnas_reporte():
        """Obtener columnas según el tipo de reporte"""
        if tipo_reporte_seleccionado == "movimientos":
            return [
                ft.DataColumn(ft.Text("Fecha/Hora", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Cantidad", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Origen", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Destino", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Motivo", weight=ft.FontWeight.BOLD))
            ]
        elif tipo_reporte_seleccionado == "ubicaciones":
            return [
                ft.DataColumn(ft.Text("Almacén", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ubicación", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Productos", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Capacidad", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Última Act.", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD))
            ]
        elif tipo_reporte_seleccionado == "productos":
            return [
                ft.DataColumn(ft.Text("Modelo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Stock Actual", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Stock Min/Max", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Valor Total", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD))
            ]
        elif tipo_reporte_seleccionado == "altas":
            return [
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Cantidad", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Valor Total", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Motivo", weight=ft.FontWeight.BOLD))
            ]
        elif tipo_reporte_seleccionado == "bajas":
            return [
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Cantidad", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Valor Perdido", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Motivo", weight=ft.FontWeight.BOLD))
            ]
        elif tipo_reporte_seleccionado == "usuarios":
            return [
                ft.DataColumn(ft.Text("Fecha/Hora", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acción", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Detalle", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Módulo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("IP", weight=ft.FontWeight.BOLD))
            ]
        elif tipo_reporte_seleccionado == "stock_critico":
            return [
                ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Stock Actual", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Stock Mínimo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Déficit", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Prioridad", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acción", weight=ft.FontWeight.BOLD))
            ]
        elif tipo_reporte_seleccionado == "rotacion":
            return [
                ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Entradas", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Salidas", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Rotación", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tendencia", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Clasificación", weight=ft.FontWeight.BOLD))
            ]
        else:
            return []

    def obtener_filas_reporte():
        """Obtener filas según el tipo de reporte"""
        filas = []
        
        for item in datos_reporte[:100]:  # Limitar a 100 registros por performance
            if tipo_reporte_seleccionado == "movimientos":
                filas.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item["fecha"], size=11)),
                    ft.DataCell(ft.Text(item["usuario"], size=11)),
                    ft.DataCell(ft.Text(f"{item['modelo']} - {item['producto']}", size=11)),
                    ft.DataCell(ft.Text(str(item["cantidad"]), size=11)),
                    ft.DataCell(ft.Text(item["origen"], size=10)),
                    ft.DataCell(ft.Text(item["destino"], size=10)),
                    ft.DataCell(ft.Text(item["motivo"], size=10))
                ]))
            elif tipo_reporte_seleccionado == "ubicaciones":
                filas.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item["almacen"], size=11)),
                    ft.DataCell(ft.Text(item["ubicacion"], size=11)),
                    ft.DataCell(ft.Text(str(item["productos_total"]), size=11)),
                    ft.DataCell(ft.Text(item["capacidad_utilizada"], size=11)),
                    ft.DataCell(ft.Text(item["ultima_actualizacion"], size=10)),
                    ft.DataCell(ft.Text(item["usuario_actualizacion"], size=11))
                ]))
            elif tipo_reporte_seleccionado == "productos":
                filas.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item["modelo"], size=11)),
                    ft.DataCell(ft.Text(item["nombre"], size=11)),
                    ft.DataCell(ft.Text(str(item["stock_actual"]), size=11)),
                    ft.DataCell(ft.Text(f"{item['stock_minimo']}/{item['stock_maximo']}", size=11)),
                    ft.DataCell(ft.Text(f"${item['valor_total']:,.2f}", size=11)),
                    ft.DataCell(ft.Text(item["estado"], size=11))
                ]))
            elif tipo_reporte_seleccionado == "altas":
                filas.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item["fecha"], size=11)),
                    ft.DataCell(ft.Text(item["usuario"], size=11)),
                    ft.DataCell(ft.Text(f"{item['modelo']} - {item['nombre']}", size=11)),
                    ft.DataCell(ft.Text(str(item["cantidad_inicial"]), size=11)),
                    ft.DataCell(ft.Text(f"${item['valor_total']:,.2f}", size=11)),
                    ft.DataCell(ft.Text(item["motivo"], size=10))
                ]))
            elif tipo_reporte_seleccionado == "bajas":
                filas.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item["fecha"], size=11)),
                    ft.DataCell(ft.Text(item["usuario"], size=11)),
                    ft.DataCell(ft.Text(f"{item['modelo']} - {item['nombre']}", size=11)),
                    ft.DataCell(ft.Text(str(item["cantidad_baja"]), size=11)),
                    ft.DataCell(ft.Text(f"${item['valor_perdido']:,.2f}", size=11)),
                    ft.DataCell(ft.Text(item["motivo"], size=10))
                ]))
            elif tipo_reporte_seleccionado == "usuarios":
                filas.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item["fecha"], size=11)),
                    ft.DataCell(ft.Text(item["usuario"], size=11)),
                    ft.DataCell(ft.Text(item["accion"], size=11)),
                    ft.DataCell(ft.Text(item["detalle"], size=10)),
                    ft.DataCell(ft.Text(item["modulo"], size=11)),
                    ft.DataCell(ft.Text(item["ip_origen"], size=11))
                ]))
            elif tipo_reporte_seleccionado == "stock_critico":
                color_prioridad = tema.ERROR_COLOR if item["prioridad"] == "CRÍTICA" else tema.WARNING_COLOR
                filas.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f"{item['modelo']} - {item['nombre']}", size=11)),
                    ft.DataCell(ft.Text(str(item["stock_actual"]), size=11)),
                    ft.DataCell(ft.Text(str(item["stock_minimo"]), size=11)),
                    ft.DataCell(ft.Text(str(item["deficit"]), size=11)),
                    ft.DataCell(ft.Text(item["prioridad"], size=11, color=color_prioridad)),
                    ft.DataCell(ft.Text(item["accion_sugerida"], size=10))
                ]))
            elif tipo_reporte_seleccionado == "rotacion":
                filas.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f"{item['modelo']} - {item['nombre']}", size=11)),
                    ft.DataCell(ft.Text(str(item["entradas_mes"]), size=11)),
                    ft.DataCell(ft.Text(str(item["salidas_mes"]), size=11)),
                    ft.DataCell(ft.Text(f"{item['rotacion_mensual']:.1%}", size=11)),
                    ft.DataCell(ft.Text(item["tendencia"], size=11)),
                    ft.DataCell(ft.Text(item["clasificacion"], size=10))
                ]))
        
        return filas

    def obtener_estadisticas_reporte():
        """Obtener estadísticas del reporte"""
        return {
            "total": len(datos_reporte),
            "periodo": f"{campo_fecha_inicio.value} al {campo_fecha_fin.value}",
            "tipo": tipos_reportes[tipo_reporte_seleccionado]["nombre"] if tipo_reporte_seleccionado else ""
        }

    async def exportar_reporte(e):
        """Exportar reporte a JSON/Excel"""
        if not datos_reporte:
            page.open(ft.SnackBar(
                content=ft.Text("No hay datos para exportar", color=tema.TEXT_COLOR),
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
            nombre_archivo = f"reporte_{tipo_reporte_seleccionado}_{timestamp}.json"
            ruta_archivo = os.path.join(export_dir, nombre_archivo)

            # Datos del reporte con metadatos
            datos_exportacion = {
                "metadata": {
                    "tipo_reporte": tipo_reporte_seleccionado,
                    "nombre_reporte": tipos_reportes[tipo_reporte_seleccionado]["nombre"],
                    "fecha_generacion": datetime.now().isoformat(),
                    "fecha_inicio": campo_fecha_inicio.value,
                    "fecha_fin": campo_fecha_fin.value,
                    "usuario_filtro": dropdown_usuario.value,
                    "total_registros": len(datos_reporte)
                },
                "datos": datos_reporte
            }

            # Guardar archivo
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(datos_exportacion, f, indent=2, ensure_ascii=False, default=str)

            page.open(ft.SnackBar(
                content=ft.Text(f"✅ Reporte exportado: {nombre_archivo}", color=tema.TEXT_COLOR),
                bgcolor=tema.SUCCESS_COLOR
            ))

        except Exception as ex:
            page.open(ft.SnackBar(
                content=ft.Text(f"Error al exportar: {str(ex)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))

    # Construir vista principal
    def construir_vista_reportes():
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ANALYTICS, color=tema.PRIMARY_COLOR, size=32),
                        ft.Text("Sistema de Reportes", size=28, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                    ]),
                    width=ancho_ventana * 0.9,
                    bgcolor=tema.CARD_COLOR,
                    padding=20,
                    alignment=ft.alignment.center,
                    border_radius=tema.BORDER_RADIUS,
                ),

                # Separador
                ft.Container(height=3, bgcolor=tema.DIVIDER_COLOR, margin=ft.margin.only(bottom=20, top=5)),

                # Selector de tipo de reporte
                ft.Container(
                    content=ft.Column([
                        ft.Text("📊 Selecciona el Tipo de Reporte", 
                               size=18, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                        selector_reportes
                    ]),
                    bgcolor=tema.CARD_COLOR,
                    padding=20,
                    border_radius=tema.BORDER_RADIUS,
                    margin=ft.margin.only(bottom=20)
                ),

                # Controles de filtro
                ft.Container(
                    content=ft.Column([
                        ft.Text("🔍 Filtros de Búsqueda", 
                               size=16, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                        ft.Row([
                            campo_fecha_inicio,
                            campo_fecha_fin,
                            dropdown_usuario,
                            ft.ElevatedButton(
                                "📊 Generar Reporte",
                                style=ft.ButtonStyle(
                                    bgcolor=tema.BUTTON_SUCCESS_BG,
                                    color=tema.BUTTON_TEXT,
                                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                ),
                                on_click=lambda e: page.run_task(generar_reporte, e)
                            ),
                            ft.ElevatedButton(
                                "💾 Exportar",
                                style=ft.ButtonStyle(
                                    bgcolor=tema.BUTTON_BG,
                                    color=tema.BUTTON_TEXT,
                                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                ),
                                on_click=lambda e: page.run_task(exportar_reporte, e)
                            )
                        ], spacing=15, alignment=ft.MainAxisAlignment.CENTER)
                    ]),
                    bgcolor=tema.CARD_COLOR,
                    padding=20,
                    border_radius=tema.BORDER_RADIUS,
                    margin=ft.margin.only(bottom=20)
                ),

                # Contenedor del reporte
                ft.Container(
                    content=ft.Column([
                        ft.Text("📋 Resultados del Reporte", 
                               size=16, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                        contenedor_reporte
                    ]),
                    bgcolor=tema.CARD_COLOR,
                    padding=20,
                    border_radius=tema.BORDER_RADIUS
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            ),
            padding=ft.padding.only(bottom=40),
            bgcolor=tema.BG_COLOR
        )

    # Mostrar vista
    contenido.content = construir_vista_reportes()
    page.update()
