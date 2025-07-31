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
            stats = await GestorHistorial.obtener_estadisticas_hoy()  # Usar método estático
            
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
            return [
                {'nombre': 'Rodillo', 'stock': 6},
                {'nombre': 'Barra', 'stock': 32}
            ]
    
    # Función para obtener actividades recientes
    async def obtener_actividades_recientes():
        try:
            actividades = await GestorHistorial.obtener_actividades_recientes(5)  # Usar método estático
            return actividades
        except Exception as e:
            print(f"Error al obtener actividades: {e}")
            return []
    
    # Función para crear elementos de historial dinámicamente
    def crear_elementos_historial(actividades):
        if not actividades:
            return [ft.Text("No hay actividades recientes", size=11, color=tema.TEXT_SECONDARY)]
        
        elementos = []
        for actividad in actividades:
            # Determinar icono y color basado en el tipo de actividad
            if actividad.get('tipo') == 'crear_producto':
                icono = ft.Icons.ADD_CIRCLE
                color_icono = tema.SUCCESS_COLOR
            elif actividad.get('tipo') == 'eliminar_producto':
                icono = ft.Icons.DELETE
                color_icono = tema.ERROR_COLOR
            elif actividad.get('tipo') == 'editar_producto':
                icono = ft.Icons.EDIT
                color_icono = tema.WARNING_COLOR
            elif actividad.get('tipo') == 'crear_usuario':
                icono = ft.Icons.PERSON_ADD
                color_icono = tema.SUCCESS_COLOR
            elif actividad.get('tipo') == 'eliminar_usuario':
                icono = ft.Icons.PERSON_REMOVE
                color_icono = tema.ERROR_COLOR
            else:
                icono = ft.Icons.INFO
                color_icono = tema.PRIMARY_COLOR
            
            # Formatear timestamp
            timestamp = actividad.get('timestamp')
            if timestamp:
                try:
                    if hasattr(timestamp, 'strftime'):
                        fecha_str = timestamp.strftime("%H:%M")
                    else:
                        fecha_str = str(timestamp)[:5]  # Tomar solo primeros 5 caracteres
                except:
                    fecha_str = "Reciente"
            else:
                fecha_str = "Reciente"
            
            elementos.append(
                ft.ListTile(
                    leading=ft.Icon(icono, size=16, color=color_icono),
                    title=ft.Text(actividad.get('descripcion', 'Actividad sin descripción'), size=11, color=tema.TEXT_COLOR),
                    subtitle=ft.Text(f"{actividad.get('usuario', 'Usuario')} - {fecha_str}", size=9, color=tema.SECONDARY_TEXT_COLOR),
                    dense=True
                )
            )
        
        return elementos
    
    # Obtener datos
    # NOTA: Estos datos son GLOBALES - compartidos entre todos los usuarios
    stats = await obtener_estadisticas()                    # Estadísticas globales del sistema
    productos_bajo_stock = await obtener_productos_bajo_stock()  # Productos globales
    actividades_recientes = await obtener_actividades_recientes()  # Historial global del sistema
    
    # NOTA: Los pendientes son INDIVIDUALES - específicos de cada usuario
    # Se cargan y guardan en archivos separados por usuario_id
    
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
    
    # Panel de pendientes con persistencia por usuario
    import json
    import os
    from pathlib import Path
    
    # Obtener usuario actual para pendientes individuales
    usuario_actual = SesionManager.obtener_usuario_actual()
    usuario_id = usuario_actual.get('firebase_id', 'usuario_desconocido') if usuario_actual else 'usuario_desconocido'
    
    # Archivo específico para cada usuario
    pendientes_file = Path(f"data/pendientes_{usuario_id}.json")
    
    def cargar_pendientes():
        """Cargar pendientes desde archivo JSON del usuario actual"""
        try:
            # Crear directorio si no existe
            pendientes_file.parent.mkdir(exist_ok=True)
            
            if pendientes_file.exists():
                with open(pendientes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            print(f"Error al cargar pendientes para usuario {usuario_id}: {e}")
            return []
    
    def guardar_pendientes():
        """Guardar pendientes en archivo JSON del usuario actual"""
        try:
            # Crear directorio si no existe
            pendientes_file.parent.mkdir(exist_ok=True)
            
            with open(pendientes_file, 'w', encoding='utf-8') as f:
                json.dump(lista_pendientes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error al guardar pendientes para usuario {usuario_id}: {e}")
    
    # Cargar pendientes existentes del usuario actual
    lista_pendientes = cargar_pendientes()
    pendientes_container = ft.Column()
    
    def limpiar_completados():
        """Eliminar todos los pendientes completados"""
        global lista_pendientes
        lista_pendientes = [p for p in lista_pendientes if not p.get('completada', False)]
        actualizar_pendientes()
        guardar_pendientes()
    
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
                        ("✓ " if tarea.get('completada', False) else "") + tarea['texto'],
                        expand=True,
                        size=12,
                        color=tema.SECONDARY_TEXT_COLOR if tarea.get('completada', False) else tema.TEXT_COLOR,
                        italic=tarea.get('completada', False)
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        on_click=lambda e, idx=i: eliminar_pendiente(idx),
                        icon_size=16
                    )
                ])
            )
        
        pendientes_container.controls = items
        try:
            page.update()
        except:
            pass
    
    def toggle_pendiente(index):
        try:
            if index < len(lista_pendientes):
                lista_pendientes[index]['completada'] = not lista_pendientes[index].get('completada', False)
                actualizar_pendientes()
                guardar_pendientes()  # Guardar cambios
        except Exception as e:
            print(f"Error al toggle pendiente: {e}")
    
    def eliminar_pendiente(index):
        try:
            if index < len(lista_pendientes):
                lista_pendientes.pop(index)
                actualizar_pendientes()
                guardar_pendientes()  # Guardar cambios
        except Exception as e:
            print(f"Error al eliminar pendiente: {e}")
    
    def agregar_pendiente(e):
        if campo_pendiente.value.strip():
            nuevo_pendiente = {
                'texto': campo_pendiente.value.strip(),
                'completada': False,
                'fecha': datetime.now().strftime("%H:%M"),
                'fecha_creacion': datetime.now().isoformat(),
                'usuario_id': usuario_id,
                'usuario_nombre': usuario_actual.get('nombre', 'Usuario') if usuario_actual else 'Usuario'
            }
            lista_pendientes.append(nuevo_pendiente)
            campo_pendiente.value = ""
            actualizar_pendientes()
            guardar_pendientes()  # Guardar cambios
    
    campo_pendiente = ft.TextField(
        hint_text=f"Agregar pendiente para {usuario_actual.get('nombre', 'mi lista') if usuario_actual else 'mi lista'}...",
        on_submit=agregar_pendiente,
        expand=True,
        text_style=ft.TextStyle(color=tema.TEXT_COLOR)
    )
    
    # Cargar pendientes existentes al inicializar la vista
    actualizar_pendientes()
    
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
                                ft.Text("Productos con Menor Stock", weight=ft.FontWeight.BOLD, size=14, color=tema.TEXT_COLOR)
                            ]),
                            ft.Divider(color=tema.SECONDARY_TEXT_COLOR),
                            ft.Column([
                                ft.ListTile(
                                    leading=ft.Container(
                                        content=ft.Text(str(producto['stock']), color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                                        bgcolor=tema.ERROR_COLOR if producto['stock'] < 10 else tema.WARNING_COLOR if producto['stock'] < 30 else tema.SUCCESS_COLOR,
                                        border_radius=12,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4)
                                    ),
                                    title=ft.Text(producto['nombre'], size=12, color=tema.TEXT_COLOR),
                                    subtitle=ft.Text(
                                        "Stock crítico" if producto['stock'] < 10 else "Stock bajo" if producto['stock'] < 30 else "Stock normal", 
                                        size=10, 
                                        color=tema.ERROR_COLOR if producto['stock'] < 10 else tema.WARNING_COLOR if producto['stock'] < 30 else tema.SUCCESS_COLOR
                                    ),
                                    dense=True
                                ) for producto in productos_bajo_stock
                            ] if productos_bajo_stock else [
                                ft.Text("No hay productos con stock bajo", size=12, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER)
                            ])
                        ]),
                        padding=16
                    ),
                    color=tema.CARD_COLOR,
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
                                ft.Text("Estadísticas de Hoy", weight=ft.FontWeight.BOLD, size=14, color=tema.TEXT_COLOR)
                            ]),
                            ft.Container(
                                content=ft.Row([
                                    ft.Container(
                                        content=crear_grafico_estadisticas(),
                                        alignment=ft.alignment.center,
                                        padding=ft.padding.only(right=55)
                                    ),
                                    ft.Column([
                                        ft.Row([
                                            ft.Container(width=10, height=10, bgcolor=tema.PRIMARY_COLOR, border_radius=5),
                                            ft.Text(f"Total Productos: {stats['total_productos']}", size=10, color=tema.TEXT_COLOR)
                                        ], spacing=8),
                                        ft.Row([
                                            ft.Container(width=10, height=10, bgcolor=tema.SECONDARY_TEXT_COLOR, border_radius=5),
                                            ft.Text(f"Total Usuarios: {stats['total_usuarios']}", size=10, color=tema.TEXT_COLOR)
                                        ], spacing=8),
                                        ft.Row([
                                            ft.Container(width=10, height=10, bgcolor=tema.SUCCESS_COLOR, border_radius=5),
                                            ft.Text(f"Creados hoy: {stats['creados_hoy']}", size=10, color=tema.TEXT_COLOR)
                                        ], spacing=8),
                                        ft.Row([
                                            ft.Container(width=10, height=10, bgcolor=tema.WARNING_COLOR, border_radius=5),
                                            ft.Text(f"Editados hoy: {stats['editados_hoy']}", size=10, color=tema.TEXT_COLOR)
                                        ], spacing=8),
                                        ft.Row([
                                            ft.Container(width=10, height=10, bgcolor=tema.ERROR_COLOR, border_radius=5),
                                            ft.Text(f"Eliminados hoy: {stats['eliminados_hoy']}", size=10, color=tema.TEXT_COLOR)
                                        ], spacing=8),
                                        ft.Row([
                                            ft.Container(width=10, height=10, bgcolor=tema.PRIMARY_COLOR, border_radius=5),
                                            ft.Text(f"Importados hoy: {stats['importados_hoy']}", size=10, color=tema.TEXT_COLOR)
                                        ], spacing=8)
                                    ], spacing=4)
                                ], 
                                alignment=ft.MainAxisAlignment.CENTER,
                                
                            ),

                            ),
                        ]),
                        padding=16
                    ),
                    color=tema.CARD_COLOR,
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
                                    ft.Column([
                                        ft.Text("Mis Pendientes", weight=ft.FontWeight.BOLD, size=14, color=tema.TEXT_COLOR),
                                        ft.Text(f"Usuario: {usuario_actual.get('nombre', 'Usuario') if usuario_actual else 'Usuario'}", 
                                               size=10, color=tema.TEXT_SECONDARY)
                                    ], spacing=0),
                                    ft.Container(expand=True),
                                    ft.IconButton(
                                        icon=ft.Icons.CLEAR_ALL,
                                        icon_size=16,
                                        icon_color=tema.WARNING_COLOR,
                                        tooltip="Limpiar completados",
                                        on_click=lambda e: limpiar_completados()
                                    )
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
                        ),
                        color=tema.CARD_COLOR,
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
                                    ft.Text("Historial de Actividades", weight=ft.FontWeight.BOLD, size=14, color=tema.TEXT_COLOR),
                                    ft.Container(expand=True),
                                    ft.IconButton(icon=ft.Icons.REFRESH, icon_size=16, icon_color=tema.PRIMARY_COLOR)
                                ]),
                                ft.Column(
                                    controls=crear_elementos_historial(actividades_recientes)
                                )
                            ]),
                            padding=16
                        ),
                        color=tema.CARD_COLOR,
                    ),
                    expand=1,
                    margin=ft.margin.only(left=8)
                )
            ], spacing=16),
            margin=ft.margin.only(top=16)
        )
    ], spacing=16, scroll=ft.ScrollMode.AUTO)
