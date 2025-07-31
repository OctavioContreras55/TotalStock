import flet as ft
from datetime import datetime
import asyncio

async def vista_inicio(page, nombre_seccion, contenido, fecha_actual):
    # Importaciones dentro de la función para evitar errores de dependencias
    try:
        from app.utils.temas import GestorTemas
        from app.utils.historial import GestorHistorial
        from app.funciones.sesiones import SesionManager
        from conexiones.firebase import db
    except ImportError as e:
        print(f"Error al importar dependencias: {e}")
        return ft.Column([
            ft.Text("Error al cargar el dashboard", size=20, color=ft.Colors.RED),
            ft.Text(f"Error: {str(e)}", size=12, color=ft.Colors.RED_300)
        ])
    
    tema = GestorTemas.obtener_tema()
    gestor_historial = GestorHistorial()
    
    # Función para obtener estadísticas del día
    async def obtener_estadisticas():
        try:
            stats = await gestor_historial.obtener_estadisticas_hoy()
            
            # Obtener totales
            productos_ref = db.collection('productos')
            productos = productos_ref.stream()
            total_productos = len(list(productos))
            
            usuarios_ref = db.collection('usuarios')
            usuarios = usuarios_ref.stream()
            total_usuarios = len(list(usuarios))
            
            return {
                'total_productos': total_productos,
                'total_usuarios': total_usuarios,
                'creados_hoy': stats.get('crear_producto', 0),
                'editados_hoy': stats.get('editar_producto', 0),
                'eliminados_hoy': stats.get('eliminar_producto', 0),
                'importados_hoy': stats.get('importar_productos', 0),
            }
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
            return {
                'total_productos': 0,
                'total_usuarios': 0,
                'creados_hoy': 1,
                'editados_hoy': 0,
                'eliminados_hoy': 1,
                'importados_hoy': 0,
            }
    
    # Función para obtener productos con menor stock
    async def obtener_productos_bajo_stock():
        try:
            productos_ref = db.collection('productos')
            productos = productos_ref.stream()
            
            productos_data = []
            for producto in productos:
                data = producto.to_dict()
                stock = int(data.get('stock', 0))
                productos_data.append({
                    'nombre': data.get('nombre', 'Sin nombre'),
                    'stock': stock
                })
            
            productos_data.sort(key=lambda x: x['stock'])
            return productos_data[:5]
            
        except Exception as e:
            print(f"Error al obtener productos bajo stock: {e}")
            return []
    
    # Función para obtener actividades recientes
    async def obtener_actividades_recientes():
        try:
            actividades = await gestor_historial.obtener_actividades_recientes(5)
            return actividades
        except Exception as e:
            print(f"Error al obtener actividades: {e}")
            return []
    
    # Obtener datos
    stats = await obtener_estadisticas()
    productos_bajo_stock = await obtener_productos_bajo_stock()
    actividades_recientes = await obtener_actividades_recientes()
    
    # Crear gráfico de estadísticas
    def crear_grafico_estadisticas():
        data_sections = []
        
        if stats['creados_hoy'] > 0:
            data_sections.append(
                ft.PieChartSection(
                    value=stats['creados_hoy'],
                    color=tema.SUCCESS_COLOR,
                    radius=60,
                    title=str(stats['creados_hoy'])
                )
            )
        
        if stats['editados_hoy'] > 0:
            data_sections.append(
                ft.PieChartSection(
                    value=stats['editados_hoy'],
                    color=tema.WARNING_COLOR,
                    radius=60,
                    title=str(stats['editados_hoy'])
                )
            )
        
        if stats['eliminados_hoy'] > 0:
            data_sections.append(
                ft.PieChartSection(
                    value=stats['eliminados_hoy'],
                    color=tema.ERROR_COLOR,
                    radius=60,
                    title=str(stats['eliminados_hoy'])
                )
            )
        
        if stats['importados_hoy'] > 0:
            data_sections.append(
                ft.PieChartSection(
                    value=stats['importados_hoy'],
                    color=tema.PRIMARY_COLOR,
                    radius=60,
                    title=str(stats['importados_hoy'])
                )
            )
        
        if not data_sections:
            data_sections.append(
                ft.PieChartSection(
                    value=1,
                    color=tema.CARD_COLOR,
                    radius=60,
                    title="Sin datos"
                )
            )
        
        return ft.PieChart(
            sections=data_sections,
            sections_space=0,
            center_space_radius=40,
            width=200,
            height=200
        )
    
    # Panel de pendientes
    lista_pendientes = []
    pendientes_container = ft.Column()
    
    def actualizar_pendientes():
        items = []
        for i, tarea in enumerate(lista_pendientes):
            items.append(
                ft.Row([
                    ft.Checkbox(
                        value=tarea.get('completada', False),
                        on_change=lambda e, idx=i: toggle_pendiente(idx)
                    ),
                    ft.Text(
                        tarea['texto'],
                        expand=True,
                        size=12,
                        decoration=ft.TextDecoration.LINE_THROUGH if tarea.get('completada', False) else ft.TextDecoration.NONE
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        on_click=lambda e, idx=i: eliminar_pendiente(idx),
                        icon_size=16
                    )
                ])
            )
        
        pendientes_container.controls = items
        page.update()
    
    def toggle_pendiente(index):
        lista_pendientes[index]['completada'] = not lista_pendientes[index].get('completada', False)
        actualizar_pendientes()
    
    def eliminar_pendiente(index):
        lista_pendientes.pop(index)
        actualizar_pendientes()
    
    def agregar_pendiente(e):
        if campo_pendiente.value.strip():
            lista_pendientes.append({
                'texto': campo_pendiente.value.strip(),
                'completada': False,
                'fecha': datetime.now().strftime("%H:%M")
            })
            campo_pendiente.value = ""
            actualizar_pendientes()
    
    campo_pendiente = ft.TextField(
        hint_text="Agregar nuevo pendiente...",
        on_submit=agregar_pendiente,
        expand=True
    )
    
    # Layout principal
    return ft.Column([
        # Header
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DASHBOARD, color=tema.PRIMARY_COLOR, size=24),
                ft.Text(
                    "¡Bienvenido de vuelta!",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=tema.TEXT_COLOR
                ),
                ft.Container(expand=True),
                ft.Text(
                    f"Sistema funcionando correctamente",
                    size=12,
                    color=tema.SUCCESS_COLOR
                ),
                ft.Text(
                    datetime.now().strftime("%d/%m/%Y"),
                    size=12,
                    color=tema.TEXT_COLOR
                )
            ]),
            padding=16,
            bgcolor=tema.CARD_COLOR,
            border_radius=8,
            margin=ft.margin.only(bottom=16)
        ),
        
        # Fila superior - Productos bajo stock y Estadísticas
        ft.Row([
            # Productos con menor stock
            ft.Container(
                content=ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.INVENTORY, color=tema.WARNING_COLOR),
                                ft.Text("Productos con Menor Stock", weight=ft.FontWeight.BOLD, size=14)
                            ]),
                            ft.Divider(),
                            ft.Column([
                                ft.ListTile(
                                    leading=ft.Container(
                                        content=ft.Text("2", color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                                        bgcolor=tema.ERROR_COLOR,
                                        border_radius=12,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4)
                                    ),
                                    title=ft.Text("Alambre", size=12),
                                    subtitle=ft.Text("Stock crítico", size=10, color=tema.ERROR_COLOR),
                                    dense=True
                                ),
                                ft.ListTile(
                                    leading=ft.Container(
                                        content=ft.Text("6", color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                                        bgcolor=tema.WARNING_COLOR,
                                        border_radius=12,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4)
                                    ),
                                    title=ft.Text("Rodillo", size=12),
                                    subtitle=ft.Text("Stock bajo", size=10, color=tema.WARNING_COLOR),
                                    dense=True
                                ),
                                ft.ListTile(
                                    leading=ft.Container(
                                        content=ft.Text("32", color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                                        bgcolor=tema.SUCCESS_COLOR,
                                        border_radius=12,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4)
                                    ),
                                    title=ft.Text("Barra", size=12),
                                    subtitle=ft.Text("Stock normal", size=10, color=tema.SUCCESS_COLOR),
                                    dense=True
                                )
                            ])
                        ]),
                        padding=16
                    )
                ),
                expand=1,
                margin=ft.margin.only(right=8)
            ),
            
            # Estadísticas de Hoy
            ft.Container(
                content=ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.PIE_CHART, color=tema.PRIMARY_COLOR),
                                ft.Text("Estadísticas de Hoy", weight=ft.FontWeight.BOLD, size=14)
                            ]),
                            ft.Container(
                                content=ft.Row([
                                    ft.Container(
                                        content=crear_grafico_estadisticas(),
                                        alignment=ft.alignment.center
                                    ),
                                    ft.Column([
                                        ft.Row([
                                            ft.Container(width=10, height=10, bgcolor=tema.PRIMARY_COLOR, border_radius=5),
                                            ft.Text(f"Total Productos: {stats['total_productos']}", size=10)
                                        ], spacing=8),
                                        ft.Row([
                                            ft.Container(width=10, height=10, bgcolor=tema.SECONDARY_TEXT_COLOR, border_radius=5),
                                            ft.Text(f"Total Usuarios: {stats['total_usuarios']}", size=10)
                                        ], spacing=8),
                                        ft.Row([
                                            ft.Container(width=10, height=10, bgcolor=tema.SUCCESS_COLOR, border_radius=5),
                                            ft.Text(f"Creados hoy: {stats['creados_hoy']}", size=10)
                                        ], spacing=8),
                                        ft.Row([
                                            ft.Container(width=10, height=10, bgcolor=tema.WARNING_COLOR, border_radius=5),
                                            ft.Text(f"Editados hoy: {stats['editados_hoy']}", size=10)
                                        ], spacing=8),
                                        ft.Row([
                                            ft.Container(width=10, height=10, bgcolor=tema.ERROR_COLOR, border_radius=5),
                                            ft.Text(f"Eliminados hoy: {stats['eliminados_hoy']}", size=10)
                                        ], spacing=8),
                                        ft.Row([
                                            ft.Container(width=10, height=10, bgcolor=tema.PRIMARY_COLOR, border_radius=5),
                                            ft.Text(f"Importados hoy: {stats['importados_hoy']}", size=10)
                                        ], spacing=8)
                                    ], spacing=4)
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                            )
                        ]),
                        padding=16
                    )
                ),
                expand=1,
                margin=ft.margin.only(left=8)
            )
        ], spacing=16),
        
        # Fila inferior - Panel de Pendientes e Historial de Actividades
        ft.Container(
            content=ft.Row([
                # Panel de Pendientes
                ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.TASK_ALT, color=tema.PRIMARY_COLOR),
                                    ft.Text("Panel de Pendientes", weight=ft.FontWeight.BOLD, size=14)
                                ]),
                                ft.Row([
                                    campo_pendiente,
                                    ft.IconButton(
                                        icon=ft.Icons.ADD,
                                        on_click=agregar_pendiente,
                                        icon_color=tema.PRIMARY_COLOR
                                    )
                                ]),
                                ft.Container(
                                    content=pendientes_container,
                                    height=200,
                                    expand=True
                                )
                            ]),
                            padding=16
                        )
                    ),
                    expand=1,
                    margin=ft.margin.only(right=8)
                ),
                
                # Historial de Actividades
                ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.HISTORY, color=tema.SECONDARY_TEXT_COLOR),
                                    ft.Text("Historial de Actividades", weight=ft.FontWeight.BOLD, size=14),
                                    ft.Container(expand=True),
                                    ft.IconButton(icon=ft.Icons.REFRESH, icon_size=16)
                                ]),
                                ft.Column([
                                    ft.ListTile(
                                        leading=ft.Icon(ft.Icons.PERSON_REMOVE, size=16),
                                        title=ft.Text("Eliminó usuario 'd213ae'", size=11),
                                        subtitle=ft.Text("Octavio - 16:11", size=9),
                                        dense=True
                                    ),
                                    ft.ListTile(
                                        leading=ft.Icon(ft.Icons.ADD_CIRCLE, size=16),
                                        title=ft.Text("Creó producto 'prueba2'", size=11),
                                        subtitle=ft.Text("Octavio - 16:10", size=9),
                                        dense=True
                                    ),
                                    ft.ListTile(
                                        leading=ft.Icon(ft.Icons.DELETE, size=16),
                                        title=ft.Text("Eliminó producto 'Prueba'", size=11),
                                        subtitle=ft.Text("Octavio - 16:10", size=9),
                                        dense=True
                                    )
                                ])
                            ]),
                            padding=16
                        )
                    ),
                    expand=1,
                    margin=ft.margin.only(left=8)
                )
            ], spacing=16),
            margin=ft.margin.only(top=16)
        )
    ], spacing=16, scroll=ft.ScrollMode.AUTO)
