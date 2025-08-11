import flet as ft
from app.utils.temas import GestorTemas
from app.utils.historial import GestorHistorial
from app.funciones.sesiones import SesionManager
from conexiones.firebase import db
from datetime import datetime, timedelta
import json
import os
import asyncio

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

    # Container principal para el selector (para poder actualizarlo)
    contenedor_selector = ft.Container()
    
    # Lista para mantener referencia a las cards
    cards_reportes_list = []

    # Tipos de reportes disponibles
    tipos_reportes = {
        "movimientos": {
            "nombre": "Movimientos de Productos",
            "icono": ft.Icons.SWAP_HORIZ,
            "color": tema.PRIMARY_COLOR,
            "descripcion": "Reporte de los movimientos de productos",
            "requiere_fechas": True
        },
        "ubicaciones": {
            "nombre": "Estado de Ubicaciones",
            "icono": ft.Icons.LOCATION_ON,
            "color": tema.SUCCESS_COLOR,
            "descripcion": "Inventario actual por ubicaciones y almacenes",
            "requiere_fechas": False
        },
        "productos": {
            "nombre": "Inventario de Productos",
            "icono": ft.Icons.INVENTORY,
            "color": tema.PRIMARY_COLOR,
            "descripcion": "Estado completo del inventario de productos",
            "requiere_fechas": False
        },
        "altas": {
            "nombre": "Altas de Productos",
            "icono": ft.Icons.ADD_BOX,
            "color": tema.SUCCESS_COLOR,
            "descripcion": "Productos dados de alta en el sistema",
            "requiere_fechas": True
        },
        "bajas": {
            "nombre": "Bajas de Productos",
            "icono": ft.Icons.REMOVE_CIRCLE,
            "color": tema.ERROR_COLOR,
            "descripcion": "Productos dados de baja del sistema",
            "requiere_fechas": True
        },
        "usuarios": {
            "nombre": "Actividad de Usuarios",
            "icono": ft.Icons.PEOPLE,
            "color": tema.WARNING_COLOR,
            "descripcion": "Actividades realizadas por usuarios del sistema",
            "requiere_fechas": True
        },
        "stock_critico": {
            "nombre": "Stock Crítico",
            "icono": ft.Icons.WARNING,
            "color": tema.ERROR_COLOR,
            "descripcion": "Productos con stock bajo o crítico",
            "requiere_fechas": False
        },
        "rotacion": {
            "nombre": "Rotación de Inventario",
            "icono": ft.Icons.AUTORENEW,
            "color": tema.PRIMARY_COLOR,
            "descripcion": "Análisis de rotación y movimiento de productos",
            "requiere_fechas": False
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
        """Generar reporte de movimientos desde datos reales del sistema"""
        try:
            from app.utils.cache_firebase import cache_firebase
            
            # Obtener movimientos reales desde Firebase
            movimientos_firebase = await cache_firebase.obtener_movimientos()
            
            # También obtener del historial local para movimientos de ubicaciones
            historial_manager = GestorHistorial()
            historial_local = await historial_manager.obtener_historial_reciente(limite=1000)
            
            reporte_movimientos = []
            
            # Procesar movimientos de Firebase
            for mov in movimientos_firebase:
                # Verificar que mov sea un diccionario
                if not isinstance(mov, dict):
                    print(f"Elemento no es diccionario: {type(mov)} -> {mov}")
                    continue
                
                # Obtener información del usuario de forma más limpia
                usuario = mov.get('usuario', 'Sistema')
                if isinstance(usuario, dict):
                    # Si el usuario es un objeto complejo, extraer solo el nombre
                    usuario = usuario.get('nombre', usuario.get('username', usuario.get('email', 'Usuario')))
                
                # Obtener información del producto
                producto_info = "N/A"
                if mov.get('modelo'):
                    producto_info = mov.get('modelo')
                elif mov.get('producto_modelo'):
                    producto_info = mov.get('producto_modelo')
                elif mov.get('nombre_producto'):
                    producto_info = mov.get('nombre_producto')
                
                # Determinar origen y destino según el tipo de movimiento
                tipo_movimiento = mov.get('tipo', mov.get('tipo_movimiento', 'Transferencia'))
                origen_str = "N/A"
                destino_str = "N/A"
                motivo_str = "Movimiento de inventario"
                
                if tipo_movimiento == 'entrada_inventario':
                    origen_str = "Entrada Externa"
                    if mov.get('almacen_destino') and mov.get('estanteria_destino'):
                        destino_str = f"Almacén {mov.get('almacen_destino')}/{mov.get('estanteria_destino')}"
                    motivo_str = "Entrada de inventario"
                
                elif tipo_movimiento == 'salida_inventario':
                    if mov.get('almacen_origen') and mov.get('estanteria_origen'):
                        origen_str = f"Almacén {mov.get('almacen_origen')}/{mov.get('estanteria_origen')}"
                    destino_str = "Salida Externa"
                    motivo_str = "Salida de inventario"
                
                elif tipo_movimiento == 'ajuste_inventario':
                    if mov.get('almacen_destino') and mov.get('estanteria_destino'):
                        origen_str = f"Almacén {mov.get('almacen_destino')}/{mov.get('estanteria_destino')}"
                        destino_str = f"Almacén {mov.get('almacen_destino')}/{mov.get('estanteria_destino')}"
                    motivo_str = "Ajuste de inventario"
                
                elif tipo_movimiento == 'movimiento_ubicacion':
                    # Manejar ubicaciones origen y destino de forma segura
                    ubicacion_origen = mov.get('ubicacion_origen', {})
                    ubicacion_destino = mov.get('ubicacion_destino', {})
                    
                    if isinstance(ubicacion_origen, dict):
                        origen_str = f"Almacén {ubicacion_origen.get('almacen', 'N/A')}/{ubicacion_origen.get('ubicacion', 'N/A')}"
                    else:
                        origen_str = str(ubicacion_origen) if ubicacion_origen else "N/A"
                    
                    if isinstance(ubicacion_destino, dict):
                        destino_str = f"Almacén {ubicacion_destino.get('almacen', 'N/A')}/{ubicacion_destino.get('ubicacion', 'N/A')}"
                    else:
                        destino_str = str(ubicacion_destino) if ubicacion_destino else "N/A"
                    
                    motivo_str = "Traslado entre ubicaciones"
                
                # Usar comentarios si están disponibles para un motivo más específico
                if mov.get('comentarios'):
                    motivo_str = mov.get('comentarios')
                elif mov.get('motivo'):
                    motivo_str = mov.get('motivo')
                
                reporte_movimientos.append({
                    "fecha": mov.get("fecha_movimiento", mov.get("fecha", "N/A")),
                    "usuario": usuario,
                    "producto": producto_info,
                    "cantidad": mov.get("cantidad", 0),
                    "origen": origen_str,
                    "destino": destino_str,
                    "motivo": motivo_str,
                    "tipo": tipo_movimiento
                })
            
            # Procesar movimientos del historial local
            for actividad in historial_local:
                # Verificar que la actividad sea un diccionario
                if not isinstance(actividad, dict):
                    print(f"Actividad no es diccionario: {type(actividad)} -> {actividad}")
                    continue
                    
                if actividad.get("tipo") in ["movimiento_ubicacion", "mover_ubicacion"]:
                    desc = actividad.get("descripcion", "")
                    reporte_movimientos.append({
                        "fecha": actividad.get("fecha", "N/A"),
                        "usuario": actividad.get("usuario", "Sistema"),
                        "producto": desc,
                        "cantidad": "Ver descripción",
                        "origen": "Ver descripción",
                        "destino": "Ver descripción", 
                        "motivo": "Movimiento entre ubicaciones",
                        "tipo": "Transferencia"
                    })
            
            return reporte_movimientos[:100]  # Limitar a últimos 100
            
        except Exception as e:
            print(f"Error al generar reporte de movimientos: {e}")
            # Fallback a datos de ejemplo
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
                }
            ]

    async def generar_reporte_ubicaciones():
        """Generar reporte de ubicaciones agrupado por almacén y estantería"""
        try:
            from app.utils.cache_firebase import cache_firebase
            
            # Obtener ubicaciones directamente desde Firebase (tabla ubicaciones)
            ubicaciones_firebase = await cache_firebase.obtener_ubicaciones()
            
            reporte_ubicaciones = []
            
            for ubicacion in ubicaciones_firebase:
                # Verificar que ubicacion sea un diccionario
                if not isinstance(ubicacion, dict):
                    print(f"Ubicación no es diccionario: {type(ubicacion)} -> {ubicacion}")
                    continue
                
                almacen = ubicacion.get("almacen", "Sin almacén")
                estanteria = ubicacion.get("estanteria", "Sin estantería") 
                cantidad = ubicacion.get("cantidad", 0)
                modelo = ubicacion.get("modelo", "Sin modelo")
                fecha_asignacion = ubicacion.get("fecha_asignacion", "N/A")
                
                # Mostrar cada ubicación individual (sin agrupar)
                reporte_ubicaciones.append({
                    "almacen": f"Almacén {almacen}" if str(almacen).isdigit() else str(almacen),
                    "estanteria": str(estanteria),
                    "cantidad": int(cantidad) if cantidad else 0,
                    "modelo": str(modelo),
                    "fecha_asignacion": str(fecha_asignacion),
                    "estado": "Ocupado" if cantidad > 0 else "Disponible"
                })
            
            # Ordenar por almacén y luego por estantería
            reporte_ubicaciones.sort(key=lambda x: (x['almacen'], x['estanteria']))
            
            return reporte_ubicaciones
            
        except Exception as e:
            print(f"Error al generar reporte de ubicaciones: {e}")
            return []

    async def generar_reporte_productos():
        """Generar reporte completo de productos desde Firebase"""
        try:
            from app.crud_productos.create_producto import obtener_productos_firebase
            from app.funciones.sesiones import GestorHistorial
            
            productos_firebase = await obtener_productos_firebase()
            
            # Obtener historial para identificar quién dio de alta cada producto
            historial_manager = GestorHistorial()
            historial_actividades = await historial_manager.obtener_historial_reciente(limite=1000)
            
            # Crear diccionario de quién creó cada producto
            usuarios_creadores = {}
            for actividad in historial_actividades:
                if isinstance(actividad, dict) and actividad.get("tipo") == "crear_producto":
                    desc = actividad.get("descripcion", "")
                    usuario = actividad.get("usuario", "Sistema")
                    
                    # Extraer modelo de la descripción
                    if "(Modelo:" in desc:
                        try:
                            modelo = desc.split("(Modelo: ")[1].split(")")[0]
                            usuarios_creadores[modelo] = usuario
                        except:
                            pass
            
            reporte_productos = []
            for producto in productos_firebase:
                # Verificar que producto sea un diccionario
                if not isinstance(producto, dict):
                    print(f"Producto no es diccionario: {type(producto)} -> {producto}")
                    continue
                
                modelo = producto.get("modelo", "N/A")
                usuario_alta = usuarios_creadores.get(modelo, "Importación/Sistema")
                
                reporte_productos.append({
                    "modelo": modelo,
                    "nombre": producto.get("nombre", "N/A"),
                    "categoria": producto.get("categoria", "Sin categoría"),
                    "stock_actual": producto.get("cantidad", 0),
                    "fecha_ingreso": producto.get("fecha_registro", "N/A"),
                    "usuario_alta": usuario_alta,
                    "estado": producto.get("estado", "Activo")
                })
            
            return reporte_productos
            
        except Exception as e:
            print(f"Error al generar reporte de productos: {e}")
            return []

    async def generar_reporte_altas():
        """Generar reporte de productos dados de alta desde historial real"""
        try:
            historial_manager = GestorHistorial()
            historial_actividades = await historial_manager.obtener_historial_reciente(limite=1000)
            
            reporte_altas = []
            for actividad in historial_actividades:
                # Verificar que actividad sea un diccionario
                if not isinstance(actividad, dict):
                    print(f"Actividad altas no es diccionario: {type(actividad)} -> {actividad}")
                    continue
                    
                if actividad.get("tipo") == "crear_producto":
                    descripcion = actividad.get("descripcion", "")
                    # Extraer información de la descripción: "Creó producto 'nombre' (Modelo: modelo)"
                    try:
                        if "'" in descripcion and "(Modelo:" in descripcion:
                            nombre = descripcion.split("'")[1]
                            modelo = descripcion.split("(Modelo: ")[1].split(")")[0]
                        else:
                            nombre = "Ver descripción"
                            modelo = "Ver descripción"
                    except:
                        nombre = descripcion
                        modelo = "N/A"
                    
                    reporte_altas.append({
                        "fecha": actividad.get("fecha", "N/A"),
                        "usuario": actividad.get("usuario", "Sistema"),
                        "modelo": modelo,
                        "nombre": nombre,
                        "categoria": "Inventario General",
                        "cantidad_inicial": "Ver sistema",
                        "precio_unitario": 0.0,
                        "valor_total": 0.0,
                        "proveedor": "No especificado",
                        "motivo": "Alta de producto en sistema",
                        "ubicacion_asignada": "Por asignar"
                    })
            
            return reporte_altas[:50]  # Últimas 50 altas
            
        except Exception as e:
            print(f"Error al generar reporte de altas: {e}")
            # Fallback a datos de ejemplo
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
                }
            ]

    async def generar_reporte_bajas():
        """Generar reporte de productos dados de baja desde historial real"""
        try:
            historial_manager = GestorHistorial()
            historial_actividades = await historial_manager.obtener_historial_reciente(limite=1000)
            
            reporte_bajas = []
            for actividad in historial_actividades:
                # Verificar que actividad sea un diccionario
                if not isinstance(actividad, dict):
                    print(f"Actividad bajas no es diccionario: {type(actividad)} -> {actividad}")
                    continue
                    
                if actividad.get("tipo") in ["eliminar_producto", "eliminar_productos_multiple"]:
                    descripcion = actividad.get("descripcion", "")
                    
                    if "eliminar_productos_multiple" in actividad.get("tipo", ""):
                        # Para eliminaciones múltiples
                        try:
                            cantidad = int(descripcion.split("Eliminó ")[1].split(" productos")[0])
                            nombre = f"{cantidad} productos eliminados"
                            modelo = "Múltiple"
                        except:
                            cantidad = 1
                            nombre = descripcion
                            modelo = "N/A"
                    else:
                        # Para eliminaciones individuales: "Eliminó producto 'nombre' (ID: id)"
                        try:
                            if "'" in descripcion:
                                nombre = descripcion.split("'")[1]
                                modelo = "Ver sistema"
                            else:
                                nombre = descripcion
                                modelo = "N/A"
                            cantidad = 1
                        except:
                            nombre = descripcion
                            modelo = "N/A"
                            cantidad = 1
                    
                    reporte_bajas.append({
                        "fecha": actividad.get("fecha", "N/A"),
                        "usuario": actividad.get("usuario", "Sistema"),
                        "modelo": modelo,
                        "nombre": nombre,
                        "categoria": "Inventario General",
                        "cantidad_baja": cantidad,
                        "valor_perdido": 0.0,  # No disponible en historial
                        "motivo": "Eliminación desde sistema",
                        "ubicacion_origen": "Sistema",
                        "estado_final": "Eliminado",
                        "observaciones": descripcion
                    })
            
            return reporte_bajas[:50]  # Últimas 50 bajas
            
        except Exception as e:
            print(f"Error al generar reporte de bajas: {e}")
            # Fallback a datos de ejemplo
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
                }
            ]

    async def generar_reporte_usuarios():
        """Generar reporte de actividad de usuarios desde historial real"""
        try:
            historial_manager = GestorHistorial()
            historial_actividades = await historial_manager.obtener_historial_reciente(limite=200)
            
            reporte_usuarios = []
            for actividad in historial_actividades:
                # Verificar que actividad sea un diccionario
                if not isinstance(actividad, dict):
                    print(f"Actividad usuarios no es diccionario: {type(actividad)} -> {actividad}")
                    continue
                    
                # Convertir tipo de actividad a acción legible
                tipo = actividad.get("tipo", "")
                if "crear" in tipo:
                    accion = "Creación"
                elif "editar" in tipo:
                    accion = "Edición"
                elif "eliminar" in tipo:
                    accion = "Eliminación"
                elif "importar" in tipo:
                    accion = "Importación"
                elif "exportar" in tipo:
                    accion = "Exportación"
                elif "movimiento" in tipo or "mover" in tipo:
                    accion = "Movimiento"
                elif "asignar" in tipo:
                    accion = "Asignación"
                else:
                    accion = tipo.replace("_", " ").title()
                
                # Determinar módulo
                if "producto" in tipo:
                    modulo = "Inventario"
                elif "usuario" in tipo:
                    modulo = "Usuarios"
                elif "ubicacion" in tipo:
                    modulo = "Ubicaciones"
                elif "movimiento" in tipo:
                    modulo = "Movimientos"
                else:
                    modulo = "Sistema"
                
                reporte_usuarios.append({
                    "fecha": actividad.get("fecha", "N/A"),
                    "usuario": actividad.get("usuario", "Sistema"),
                    "accion": accion,
                    "detalle": actividad.get("descripcion", "Sin detalles"),
                    "modulo": modulo,
                    "ip_origen": "192.168.1.100",  # IP por defecto
                    "duracion_sesion": "N/A"
                })
            
            return reporte_usuarios
            
        except Exception as e:
            print(f"Error al generar reporte de usuarios: {e}")
            # Fallback a datos de ejemplo
            return [
                {
                    "fecha": "2024-01-15 14:30:25",
                    "usuario": "Admin",
                    "accion": "Movimiento de Producto",
                    "detalle": "Movió 5 unidades de 'Laptop Dell Inspiron'",
                    "modulo": "Movimientos",
                    "ip_origen": "192.168.1.100",
                    "duracion_sesion": "2h 15m"
                }
            ]

    async def generar_reporte_stock_critico():
        """Generar reporte de productos con stock crítico desde Firebase"""
        try:
            from app.crud_productos.create_producto import obtener_productos_firebase
            productos_firebase = await obtener_productos_firebase()
            
            productos_criticos = []
            for producto in productos_firebase:
                # Verificar que producto sea un diccionario
                if not isinstance(producto, dict):
                    print(f"Producto crítico no es diccionario: {type(producto)} -> {producto}")
                    continue
                    
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
        """Generar reporte de rotación de inventario - productos más activos"""
        try:
            from app.utils.cache_firebase import cache_firebase
            from app.funciones.sesiones import GestorHistorial
            
            # Obtener movimientos y historial para analizar actividad
            movimientos_firebase = await cache_firebase.obtener_movimientos()
            historial_manager = GestorHistorial()
            historial_actividades = await historial_manager.obtener_historial_reciente(limite=1000)
            
            # Contabilizar actividad por producto
            actividad_productos = {}
            
            # Procesar movimientos de Firebase
            for mov in movimientos_firebase:
                if isinstance(mov, dict):
                    modelo = mov.get('modelo', mov.get('producto_modelo', 'N/A'))
                    if modelo != 'N/A':
                        if modelo not in actividad_productos:
                            actividad_productos[modelo] = {
                                "modelo": modelo,
                                "entradas": 0,
                                "salidas": 0,
                                "movimientos_ubicacion": 0,
                                "total_movimientos": 0,
                                "nombre": mov.get('nombre_producto', 'Producto')
                            }
                        
                        tipo_mov = mov.get('tipo', mov.get('tipo_movimiento', ''))
                        cantidad = mov.get('cantidad', 0)
                        
                        if 'entrada' in tipo_mov:
                            actividad_productos[modelo]["entradas"] += cantidad
                        elif 'salida' in tipo_mov:
                            actividad_productos[modelo]["salidas"] += cantidad
                        elif 'movimiento' in tipo_mov:
                            actividad_productos[modelo]["movimientos_ubicacion"] += 1
                        
                        actividad_productos[modelo]["total_movimientos"] += 1
            
            # Procesar historial de actividades
            for actividad in historial_actividades:
                if isinstance(actividad, dict):
                    desc = actividad.get("descripcion", "")
                    tipo = actividad.get("tipo", "")
                    
                    # Buscar menciones de productos en las descripciones
                    if "producto" in tipo.lower() or "movimiento" in tipo.lower():
                        # Intentar extraer modelo de la descripción
                        palabras = desc.split()
                        for palabra in palabras:
                            if len(palabra) > 3 and palabra.isalnum():
                                # Considerar como posible modelo de producto
                                if palabra not in actividad_productos:
                                    actividad_productos[palabra] = {
                                        "modelo": palabra,
                                        "entradas": 0,
                                        "salidas": 0,
                                        "movimientos_ubicacion": 0,
                                        "total_movimientos": 0,
                                        "nombre": "Producto"
                                    }
                                
                                if "crear" in tipo:
                                    actividad_productos[palabra]["entradas"] += 1
                                elif "eliminar" in tipo:
                                    actividad_productos[palabra]["salidas"] += 1
                                elif "movimiento" in tipo:
                                    actividad_productos[palabra]["movimientos_ubicacion"] += 1
                                
                                actividad_productos[palabra]["total_movimientos"] += 1
                                break  # Solo procesar el primer modelo encontrado
            
            # Convertir a lista y calcular métricas de rotación
            reporte_rotacion = []
            for datos in actividad_productos.values():
                total_actividad = datos["total_movimientos"]
                if total_actividad > 0:  # Solo incluir productos con actividad
                    # Calcular clasificación según la actividad
                    if total_actividad >= 10:
                        clasificacion = "MUY ACTIVO"
                        tendencia = "ALTA ROTACIÓN"
                    elif total_actividad >= 5:
                        clasificacion = "ACTIVO"
                        tendencia = "ROTACIÓN MEDIA"
                    else:
                        clasificacion = "POCO ACTIVO"
                        tendencia = "BAJA ROTACIÓN"
                    
                    reporte_rotacion.append({
                        "modelo": datos["modelo"],
                        "nombre": datos["nombre"],
                        "entradas": datos["entradas"],
                        "salidas": datos["salidas"],
                        "movimientos_ubicacion": datos["movimientos_ubicacion"],
                        "total_movimientos": total_actividad,
                        "tendencia": tendencia,
                        "clasificacion": clasificacion
                    })
            
            # Ordenar por total de movimientos (más activos primero)
            reporte_rotacion.sort(key=lambda x: x["total_movimientos"], reverse=True)
            
            return reporte_rotacion[:50]  # Top 50 productos más activos
            
        except Exception as e:
            print(f"Error al generar reporte de rotación: {e}")
            return []

    # Componentes de la interfaz
    def crear_selector_tipo_reporte():
        """Crear selector de tipo de reporte con mejores efectos visuales"""
        cards_reportes_list.clear()
        
        for tipo_id, info in tipos_reportes.items():
            def crear_handler(tipo):
                async def handler(e):
                    nonlocal tipo_reporte_seleccionado
                    
                    # Efecto de clic inmediato
                    e.control.scale = 0.95
                    e.control.update()
                    
                    # Restaurar escala después de un breve delay
                    await asyncio.sleep(0.1)
                    e.control.scale = 1.0
                    e.control.update()
                    
                    # Actualizar selección
                    tipo_reporte_seleccionado = tipo
                    actualizar_selector_visual()
                    
                    # Actualizar visibilidad de filtros según el tipo de reporte
                    actualizar_visibilidad_filtros()
                    
                return handler

            esta_seleccionado = tipo_reporte_seleccionado == tipo_id
            
            # Colores dinámicos según selección
            if esta_seleccionado:
                color_fondo = tema.PRIMARY_COLOR
                color_icono = tema.CARD_COLOR
                color_texto = tema.CARD_COLOR
                color_descripcion = tema.CARD_COLOR
                borde = ft.border.all(3, tema.SUCCESS_COLOR)
                elevacion = 10
            else:
                color_fondo = tema.CARD_COLOR
                color_icono = info["color"]
                color_texto = tema.TEXT_COLOR
                color_descripcion = tema.SECONDARY_TEXT_COLOR
                borde = ft.border.all(1, tema.DIVIDER_COLOR)
                elevacion = 3
            
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(info["icono"], 
                               color=color_icono, 
                               size=36),
                        ft.Text(info["nombre"], 
                               weight=ft.FontWeight.BOLD, 
                               color=color_texto,
                               text_align=ft.TextAlign.CENTER,
                               size=13),
                        ft.Text(info["descripcion"],
                               color=color_descripcion,
                               text_align=ft.TextAlign.CENTER,
                               size=10)
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10),
                    padding=18,
                    width=180,
                    height=150,
                    bgcolor=color_fondo,
                    border=borde,
                    border_radius=12,
                    on_click=lambda e, tipo=tipo_id: page.run_task(crear_handler(tipo), e),
                    # Efecto hover
                    on_hover=lambda e, card_ref=None: hover_effect(e, card_ref)
                ),
                elevation=elevacion
            )
            
            # Guardar referencia
            card.content.on_hover = lambda e, card_container=card.content: hover_effect(e, card_container)
            cards_reportes_list.append(card)
        
        # Organizar en filas de 4
        filas = []
        for i in range(0, len(cards_reportes_list), 4):
            fila = ft.Row(
                cards_reportes_list[i:i+4],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            )
            filas.append(fila)
        
        return ft.Column(filas, spacing=20)

    def hover_effect(e, container):
        """Efecto hover para las cards"""
        if container and hasattr(container, 'scale'):
            if e.data == "true":  # Mouse enter
                container.scale = 1.05
            else:  # Mouse leave
                container.scale = 1.0
            container.update()

    def actualizar_selector_visual():
        """Actualizar el selector visual de reportes"""
        # Actualizar cada card existente
        for i, (tipo_id, info) in enumerate(tipos_reportes.items()):
            if i < len(cards_reportes_list):
                card = cards_reportes_list[i]
                esta_seleccionado = tipo_reporte_seleccionado == tipo_id
                
                # Colores según selección
                if esta_seleccionado:
                    color_fondo = tema.PRIMARY_COLOR
                    color_icono = tema.CARD_COLOR
                    color_texto = tema.CARD_COLOR
                    color_descripcion = tema.CARD_COLOR
                    borde = ft.border.all(3, tema.SUCCESS_COLOR)
                    elevacion = 10
                else:
                    color_fondo = tema.CARD_COLOR
                    color_icono = info["color"]
                    color_texto = tema.TEXT_COLOR
                    color_descripcion = tema.SECONDARY_TEXT_COLOR
                    borde = ft.border.all(1, tema.DIVIDER_COLOR)
                    elevacion = 3
                
                # Actualizar contenido de la card
                container = card.content
                container.bgcolor = color_fondo
                container.border = borde
                
                # Actualizar controles internos
                columna = container.content
                if len(columna.controls) >= 3:
                    columna.controls[0].color = color_icono  # Ícono
                    columna.controls[1].color = color_texto  # Nombre
                    columna.controls[2].color = color_descripcion  # Descripción
                
                # Actualizar elevación
                card.elevation = elevacion
                
                # Forzar actualización
                card.update()
        
        # Actualizar el contenedor principal
        contenedor_selector.update()

    # Inicializar el contenedor selector
    contenedor_selector.content = crear_selector_tipo_reporte()

    # FUNCIÓN REMOVIDA: analizar_disponibilidad_reportes()
    # Ya no se necesita analizar disponibilidad para snackbar

    # FUNCIÓN REMOVIDA: mostrar_info_reporte_seleccionado() 
    # Ya no se necesita mostrar snackbar al seleccionar reporte

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

    # Contenedor de filtros dinámico
    contenedor_filtros = ft.Container(
        visible=False,  # Inicialmente oculto
        content=ft.Column([
            ft.Text("Filtros de Búsqueda", 
                   size=16, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
            ft.Row([
                campo_fecha_inicio,
                campo_fecha_fin,
                dropdown_usuario,
                ft.ElevatedButton(
                    "Generar Reporte",
                    style=ft.ButtonStyle(
                        bgcolor=tema.BUTTON_SUCCESS_BG,
                        color=tema.BUTTON_TEXT,
                        shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                    ),
                    on_click=lambda e: page.run_task(generar_reporte, e)
                ),
                ft.ElevatedButton(
                    "📊 Exportar (PDF/Excel/JSON)",
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
    )

    # Contenedor de botones para reportes que no requieren fechas
    contenedor_botones_simple = ft.Container(
        visible=False,  # Inicialmente oculto
        content=ft.Row([
            ft.ElevatedButton(
                "Generar Reporte",
                style=ft.ButtonStyle(
                    bgcolor=tema.BUTTON_SUCCESS_BG,
                    color=tema.BUTTON_TEXT,
                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                ),
                on_click=lambda e: page.run_task(generar_reporte, e)
            ),
            ft.ElevatedButton(
                "📊 Exportar (PDF/Excel/JSON)",
                style=ft.ButtonStyle(
                    bgcolor=tema.BUTTON_BG,
                    color=tema.BUTTON_TEXT,
                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                ),
                on_click=lambda e: page.run_task(exportar_reporte, e)
            )
        ], spacing=15, alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=tema.CARD_COLOR,
        padding=20,
        border_radius=tema.BORDER_RADIUS,
        margin=ft.margin.only(bottom=20)
    )

    def actualizar_visibilidad_filtros():
        """Actualizar la visibilidad de filtros según el tipo de reporte seleccionado"""
        if tipo_reporte_seleccionado and tipo_reporte_seleccionado in tipos_reportes:
            requiere_fechas = tipos_reportes[tipo_reporte_seleccionado]["requiere_fechas"]
            
            if requiere_fechas:
                # Mostrar filtros completos con fechas
                contenedor_filtros.visible = True
                contenedor_botones_simple.visible = False
            else:
                # Mostrar solo botones sin filtros de fecha
                contenedor_filtros.visible = False
                contenedor_botones_simple.visible = True
        else:
            # Ocultar ambos si no hay selección
            contenedor_filtros.visible = False
            contenedor_botones_simple.visible = False
        
        page.update()

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
            column_spacing=15,  # Reducido para mejor ajuste
            horizontal_margin=10,  # Márgenes laterales
            show_checkbox_column=False  # Ocultar checkboxes si aparecen
        )

        # Estadísticas del reporte
        stats = obtener_estadisticas_reporte()
        
        contenedor_reporte.content = ft.Column([
            # Estadísticas centradas
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Total Registros", size=12, color=tema.TEXT_COLOR),
                            ft.Text(str(stats["total"]), size=20, weight=ft.FontWeight.BOLD, color=tema.PRIMARY_COLOR)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=tema.CARD_COLOR,
                        padding=15,
                        border_radius=8,
                        width=200  # Ancho fijo para consistencia
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Período", size=12, color=tema.TEXT_COLOR),
                            ft.Text(stats["periodo"], size=14, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=tema.CARD_COLOR,
                        padding=15,
                        border_radius=8,
                        width=300  # Ancho fijo para fechas
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Generado", size=12, color=tema.TEXT_COLOR),
                            ft.Text(datetime.now().strftime("%Y-%m-%d %H:%M"), 
                                   size=12, color=tema.TEXT_COLOR)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=tema.CARD_COLOR,
                        padding=15,
                        border_radius=8,
                        width=200  # Ancho fijo para fecha/hora
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),  # Centrar estadísticas
                margin=ft.margin.only(bottom=20)
            ),
            
            # Tabla del reporte centrada
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=tabla,
                        border=ft.border.all(1, tema.DIVIDER_COLOR),
                        border_radius=tema.BORDER_RADIUS,
                        padding=10,
                        width=min(1200, ancho_ventana * 0.9)  # Ancho responsivo, máximo 1200px
                    )
                ], alignment=ft.MainAxisAlignment.CENTER),  # Centrar horizontalmente
                margin=ft.margin.only(top=10)
            )
        ], 
        scroll=ft.ScrollMode.AUTO,
        height=600)
        
        page.update()

    def obtener_columnas_reporte():
        """Obtener columnas según el tipo de reporte"""
        if tipo_reporte_seleccionado == "movimientos":
            return [
                ft.DataColumn(ft.Text("Fecha/Hora", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Cantidad", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Origen", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Destino", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Motivo", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR))
            ]
        elif tipo_reporte_seleccionado == "ubicaciones":
            return [
                ft.DataColumn(ft.Text("Almacén", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Estantería", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Cantidad", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Modelo", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Fecha Asignación", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR))
            ]
        elif tipo_reporte_seleccionado == "productos":
            return [
                ft.DataColumn(ft.Text("Modelo", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Categoría", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Stock Actual", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Fecha Ingreso", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Usuario Alta", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR))
            ]
        elif tipo_reporte_seleccionado == "altas":
            return [
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Categoría", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Motivo", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR))
            ]
        elif tipo_reporte_seleccionado == "bajas":
            return [
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Cantidad", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Motivo", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR))
            ]
        elif tipo_reporte_seleccionado == "usuarios":
            return [
                ft.DataColumn(ft.Text("Fecha/Hora", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Acción", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Detalle", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Módulo", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR))
            ]
        elif tipo_reporte_seleccionado == "stock_critico":
            return [
                ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Stock Actual", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Prioridad", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Acción", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR))
            ]
        elif tipo_reporte_seleccionado == "rotacion":
            return [
                ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Entradas", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Salidas", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Mov. Ubicación", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Total Movimientos", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Tendencia", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR)),
                ft.DataColumn(ft.Text("Clasificación", weight=ft.FontWeight.BOLD, color=tema.CARD_COLOR))
            ]
        else:
            return []

    def obtener_filas_reporte():
        """Obtener filas según el tipo de reporte"""
        filas = []
        
        for item in datos_reporte[:100]:  # Limitar a 100 registros por performance
            if tipo_reporte_seleccionado == "movimientos":
                filas.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item["fecha"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["usuario"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["producto"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(str(item["cantidad"]), size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["origen"], size=10, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["destino"], size=10, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["motivo"], size=10, color=tema.TEXT_COLOR))
                ]))
            elif tipo_reporte_seleccionado == "ubicaciones":
                filas.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item["almacen"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["estanteria"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(str(item["cantidad"]), size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["modelo"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["fecha_asignacion"], size=10, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["estado"], size=11, color=tema.TEXT_COLOR))
                ]))
            elif tipo_reporte_seleccionado == "productos":
                filas.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item["modelo"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["nombre"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["categoria"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(str(item["stock_actual"]), size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["fecha_ingreso"], size=10, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["usuario_alta"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["estado"], size=11, color=tema.TEXT_COLOR))
                ]))
            elif tipo_reporte_seleccionado == "altas":
                filas.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item["fecha"][:16] if len(item["fecha"]) > 16 else item["fecha"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["usuario"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(f"{item['modelo']} - {item['nombre']}", size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["categoria"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["motivo"], size=10, color=tema.TEXT_COLOR))
                ]))
            elif tipo_reporte_seleccionado == "bajas":
                filas.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item["fecha"][:16] if len(item["fecha"]) > 16 else item["fecha"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["usuario"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(f"{item['modelo']} - {item['nombre']}", size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(str(item["cantidad_baja"]), size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["motivo"], size=10, color=tema.TEXT_COLOR))
                ]))
            elif tipo_reporte_seleccionado == "usuarios":
                filas.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item["fecha"][:16] if len(item["fecha"]) > 16 else item["fecha"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["usuario"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["accion"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["detalle"], size=10, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["modulo"], size=11, color=tema.TEXT_COLOR))
                ]))
            elif tipo_reporte_seleccionado == "stock_critico":
                color_prioridad = tema.ERROR_COLOR if item["prioridad"] == "CRÍTICA" else tema.WARNING_COLOR
                filas.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f"{item['modelo']} - {item['nombre']}", size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(str(item["stock_actual"]), size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["prioridad"], size=11, color=color_prioridad, weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(item["accion_sugerida"], size=10, color=tema.TEXT_COLOR))
                ]))
            elif tipo_reporte_seleccionado == "rotacion":
                # Color según clasificación
                color_clasificacion = tema.SUCCESS_COLOR if "MUY ACTIVO" in item["clasificacion"] else tema.WARNING_COLOR if "ACTIVO" in item["clasificacion"] else tema.TEXT_COLOR
                filas.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f"{item['modelo']} - {item['nombre']}", size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(str(item["entradas"]), size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(str(item["salidas"]), size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(str(item["movimientos_ubicacion"]), size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(str(item["total_movimientos"]), size=11, color=tema.PRIMARY_COLOR, weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(item["tendencia"], size=11, color=tema.TEXT_COLOR)),
                    ft.DataCell(ft.Text(item["clasificacion"], size=10, color=color_clasificacion, weight=ft.FontWeight.BOLD))
                ]))
        
        return filas

    def obtener_estadisticas_reporte():
        """Obtener estadísticas del reporte"""
        # Verificar si el reporte requiere fechas
        requiere_fechas = False
        if tipo_reporte_seleccionado and tipo_reporte_seleccionado in tipos_reportes:
            requiere_fechas = tipos_reportes[tipo_reporte_seleccionado]["requiere_fechas"]
        
        # Construir período según el tipo de reporte
        if requiere_fechas:
            periodo = f"{campo_fecha_inicio.value} al {campo_fecha_fin.value}"
        else:
            periodo = "Estado actual del sistema"
        
        return {
            "total": len(datos_reporte),
            "periodo": periodo,
            "tipo": tipos_reportes[tipo_reporte_seleccionado]["nombre"] if tipo_reporte_seleccionado else ""
        }

    async def exportar_reporte(e):
        """Exportar reporte con múltiples formatos (JSON, Excel, PDF)"""
        if not datos_reporte:
            page.open(ft.SnackBar(
                content=ft.Text("No hay datos para exportar", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return

        # Preparar metadatos del reporte
        metadata_reporte = {
            "tipo_reporte": tipo_reporte_seleccionado,
            "nombre_reporte": tipos_reportes[tipo_reporte_seleccionado]["nombre"] if tipo_reporte_seleccionado in tipos_reportes else "Reporte",
            "fecha_generacion": datetime.now().isoformat(),
            "fecha_inicio": campo_fecha_inicio.value,
            "fecha_fin": campo_fecha_fin.value,
            "usuario_filtro": dropdown_usuario.value,
            "total_registros": len(datos_reporte)
        }
        
        # Importar la nueva función de exportación
        from app.funciones.exportar_reportes import exportar_reporte_completo
        
        # Llamar a la función de exportación con múltiples formatos
        await exportar_reporte_completo(datos_reporte, metadata_reporte, page)

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
                        ft.Text("Selecciona el Tipo de Reporte", 
                               size=18, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                        contenedor_selector
                    ]),
                    bgcolor=tema.CARD_COLOR,
                    padding=20,
                    border_radius=tema.BORDER_RADIUS,
                    margin=ft.margin.only(bottom=20)
                ),

                # Controles de filtro dinámicos
                contenedor_filtros,
                contenedor_botones_simple,

                # Contenedor del reporte
                ft.Container(
                    content=ft.Column([
                        ft.Text("[LISTA] Resultados del Reporte", 
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
