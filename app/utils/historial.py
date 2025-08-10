import flet as ft
from conexiones.firebase import db
from datetime import datetime
import asyncio
import json
from pathlib import Path

# [ALERT] MODO ECONÓMICO: Deshabilitar escrituras a Firebase temporalmente
MODO_ECONOMICO = True  # Cambiar a False cuando se recupere la cuota de Firebase

class GestorHistorial:
    """Gestor para el historial de actividades del sistema"""
    
    def __init__(self):
        self.coleccion = "historial"
        # Archivo local para el historial en modo económico
        self.historial_local = Path("data/historial_local.json")
    
    async def agregar_actividad(self, tipo: str, descripcion: str, usuario: str, detalles: dict = None):
        """
        Agregar una nueva actividad al historial
        
        Args:
            tipo (str): Tipo de actividad (crear_producto, movimiento_producto, etc.)
            descripcion (str): Descripción legible de la actividad
            usuario (str): Usuario que realizó la actividad
            detalles (dict): Detalles adicionales de la actividad
        """
        try:
            actividad = {
                "tipo": tipo,
                "descripcion": descripcion,
                "usuario": usuario,
                "fecha": datetime.now().isoformat(),
                "timestamp": datetime.now().isoformat(),  # Como string para JSON local
                "detalles": detalles or {}
            }
            
            if MODO_ECONOMICO:
                # Guardar en archivo local para no consumir Firebase
                self._guardar_historial_local(actividad)
                print(f"[SAVE] [MODO ECONÓMICO] Actividad guardada localmente: {descripcion}")
            else:
                # Guardar en Firebase (cuando no estemos en modo económico)
                db.collection(self.coleccion).add(actividad)
                print(f"[OK] Actividad registrada en Firebase: {descripcion}")
            
        except Exception as e:
            print(f"[ERROR] Error al registrar actividad: {e}")
    
    def _guardar_historial_local(self, actividad):
        """Guardar actividad en archivo local JSON"""
        try:
            # Crear directorio si no existe
            self.historial_local.parent.mkdir(exist_ok=True)
            
            # Leer historial existente
            historial_existente = []
            if self.historial_local.exists():
                with open(self.historial_local, 'r', encoding='utf-8') as f:
                    historial_existente = json.load(f)
            
            # Agregar nueva actividad al inicio
            historial_existente.insert(0, actividad)
            
            # Mantener solo los últimos 100 registros para no llenar el disco
            if len(historial_existente) > 100:
                historial_existente = historial_existente[:100]
            
            # Guardar de vuelta
            with open(self.historial_local, 'w', encoding='utf-8') as f:
                json.dump(historial_existente, f, ensure_ascii=False, indent=2, default=str)
                
        except Exception as e:
            print(f"Error al guardar historial local: {e}")
    
    def _leer_historial_local(self, limite: int = 50):
        """Leer historial desde archivo local"""
        try:
            if not self.historial_local.exists():
                return []
            
            with open(self.historial_local, 'r', encoding='utf-8') as f:
                historial = json.load(f)
                return historial[:limite]
        except Exception as e:
            print(f"Error al leer historial local: {e}")
            return []
    
    async def obtener_historial_reciente(self, limite: int = 50) -> list:
        """
        Obtener el historial más reciente
        
        Args:
            limite (int): Número máximo de registros a obtener
            
        Returns:
            list: Lista de actividades del historial
        """
        if MODO_ECONOMICO:
            # Usar archivo local en modo económico
            return self._leer_historial_local(limite)
        
        try:
            # Obtener documentos ordenados por fecha descendente desde Firebase
            docs = (db.collection(self.coleccion)
                   .order_by("timestamp", direction="DESCENDING")
                   .limit(limite)
                   .get())
            
            actividades = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                actividades.append(data)
            
            return actividades
            
        except Exception as e:
            print(f"[ERROR] Error al obtener historial: {e}")
            return []
    
    async def obtener_historial_por_usuario(self, usuario: str, limite: int = 30) -> list:
        """
        Obtener historial filtrado por usuario
        
        Args:
            usuario (str): Nombre del usuario
            limite (int): Número máximo de registros
            
        Returns:
            list: Lista de actividades del usuario
        """
        try:
            from google.cloud.firestore_v1.base_query import FieldFilter
            # Obtener documentos ordenados por fecha descendente
            docs = (db.collection(self.coleccion)
                   .where(filter=FieldFilter("usuario", "==", usuario))
                   .order_by("timestamp", direction="DESCENDING")
                   .limit(limite)
                   .get())
            
            actividades = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                actividades.append(data)
            
            return actividades
            
        except Exception as e:
            print(f"[ERROR] Error al obtener historial por usuario: {e}")
            return []
    
    async def obtener_historial_por_tipo(self, tipo: str, limite: int = 30) -> list:
        """
        Obtener historial filtrado por tipo de actividad
        
        Args:
            tipo (str): Tipo de actividad
            limite (int): Número máximo de registros
            
        Returns:
            list: Lista de actividades del tipo especificado
        """
        try:
            from google.cloud.firestore_v1.base_query import FieldFilter
            docs = (db.collection(self.coleccion)
                   .where(filter=FieldFilter("tipo", "==", tipo))
                   .order_by("timestamp", direction="DESCENDING")
                   .limit(limite)
                   .get())
            
            actividades = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                actividades.append(data)
            
            return actividades
            
        except Exception as e:
            print(f"[ERROR] Error al obtener historial por tipo: {e}")
            return []
    
    @staticmethod
    def formatear_fecha(fecha_iso: str) -> str:
        """
        Formatear fecha ISO para mostrar de forma legible
        
        Args:
            fecha_iso (str): Fecha en formato ISO
            
        Returns:
            str: Fecha formateada
        """
        try:
            fecha = datetime.fromisoformat(fecha_iso.replace('Z', '+00:00'))
            return fecha.strftime("%d/%m/%Y %H:%M")
        except:
            return fecha_iso
    
    @staticmethod
    def obtener_icono_por_tipo(tipo: str) -> str:
        """
        Obtener icono correspondiente al tipo de actividad
        
        Args:
            tipo (str): Tipo de actividad
            
        Returns:
            str: Icono de Flet correspondiente
        """
        iconos = {
            "crear_producto": ft.Icons.ADD_CIRCLE,
            "editar_producto": ft.Icons.EDIT,
            "eliminar_producto": ft.Icons.DELETE,
            "movimiento_producto": ft.Icons.SWAP_HORIZ,
            "importar_excel": ft.Icons.UPLOAD_FILE,
            "crear_usuario": ft.Icons.PERSON_ADD,
            "login": ft.Icons.LOGIN,
            "logout": ft.Icons.LOGOUT,
            "crear_categoria": ft.Icons.CATEGORY,
            "crear_ubicacion": ft.Icons.LOCATION_ON,
            "error": ft.Icons.ERROR,
            "sistema": ft.Icons.SETTINGS
        }
        return iconos.get(tipo, ft.Icons.INFO)
    
    @staticmethod
    def obtener_color_por_tipo(tipo: str) -> str:
        """
        Obtener color correspondiente al tipo de actividad
        
        Args:
            tipo (str): Tipo de actividad
            
        Returns:
            str: Color correspondiente
        """
        colores = {
            "crear_producto": ft.Colors.GREEN,
            "editar_producto": ft.Colors.ORANGE,
            "eliminar_producto": ft.Colors.RED,
            "movimiento_producto": ft.Colors.BLUE,
            "importar_excel": ft.Colors.PURPLE,
            "crear_usuario": ft.Colors.TEAL,
            "login": ft.Colors.LIGHT_GREEN,
            "logout": ft.Colors.GREY,
            "crear_categoria": ft.Colors.INDIGO,
            "crear_ubicacion": ft.Colors.CYAN,
            "error": ft.Colors.RED_ACCENT,
            "sistema": ft.Colors.BLUE_GREY
        }
        return colores.get(tipo, ft.Colors.BLUE)

    @staticmethod
    async def obtener_actividades_recientes(limite=10):
        """Obtener las actividades más recientes"""
        try:
            gestor = GestorHistorial()
            return await gestor.obtener_historial_reciente(limite)
        except Exception as error:
            print(f"Error al obtener actividades: {error}")
            return []
    
    @staticmethod
    async def obtener_estadisticas_hoy():
        """Obtener estadísticas del día actual"""
        if MODO_ECONOMICO:
            # Obtener estadísticas desde archivo local
            try:
                gestor = GestorHistorial()
                actividades = gestor._leer_historial_local(100)  # Leer más registros para estadísticas
                
                fecha_hoy = datetime.now().strftime("%Y-%m-%d")
                estadisticas = {}
                
                # Comentar debug para limpiar terminal
                # print(f"[CHART] [DEBUG] Fecha hoy: {fecha_hoy}")
                # print(f"[CHART] [DEBUG] Total actividades leídas: {len(actividades)}")
                
                for actividad in actividades:
                    # Verificar si es del día actual (usando startswith para fechas ISO)
                    fecha_actividad = actividad.get('fecha', '')
                    tipo_actividad = actividad.get('tipo', 'otro')
                    # print(f"[CHART] [DEBUG] Actividad: fecha={fecha_actividad}, tipo={tipo_actividad}")
                    
                    if fecha_actividad.startswith(fecha_hoy):
                        estadisticas[tipo_actividad] = estadisticas.get(tipo_actividad, 0) + 1
                        # print(f"[OK] [DEBUG] Contada: {tipo_actividad} = {estadisticas[tipo_actividad]}")
                
                # print(f"[CHART] [DEBUG] Estadísticas finales: {estadisticas}")
                return estadisticas
            except Exception as error:
                print(f"Error al obtener estadísticas locales: {error}")
                return {}
        
        try:
            from google.cloud.firestore_v1.base_query import FieldFilter
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            docs = db.collection('historial').where(filter=FieldFilter('fecha', '>=', fecha_hoy)).get()
            
            estadisticas = {}
            for doc in docs:
                data = doc.to_dict()
                tipo = data.get('tipo', 'otro')
                estadisticas[tipo] = estadisticas.get(tipo, 0) + 1
            
            return estadisticas
            
        except Exception as error:
            print(f"Error al obtener estadísticas: {error}")
            return {}

# Funciones de utilidad para registrar actividades comunes
class RegistroActividades:
    """Funciones de utilidad para registrar actividades específicas"""
    
    @staticmethod
    async def producto_creado(modelo: str, nombre: str, usuario: str):
        """Registrar creación de producto"""
        gestor = GestorHistorial()
        await gestor.agregar_actividad(
            tipo="crear_producto",
            descripcion=f"Creó el producto '{modelo} - {nombre}'",
            usuario=usuario,
            detalles={"modelo": modelo, "nombre": nombre}
        )
    
    @staticmethod
    async def producto_modificado(modelo: str, cambios: dict, usuario: str):
        """Registrar modificación de producto"""
        gestor = GestorHistorial()
        cambios_texto = ", ".join([f"{k}: {v}" for k, v in cambios.items()])
        await gestor.agregar_actividad(
            tipo="editar_producto",
            descripcion=f"Modificó el producto '{modelo}': {cambios_texto}",
            usuario=usuario,
            detalles={"modelo": modelo, "cambios": cambios}
        )
    
    @staticmethod
    async def producto_eliminado(modelo: str, usuario: str):
        """Registrar eliminación de producto"""
        gestor = GestorHistorial()
        await gestor.agregar_actividad(
            tipo="eliminar_producto",
            descripcion=f"Eliminó el producto '{modelo}'",
            usuario=usuario,
            detalles={"modelo": modelo}
        )
    
    @staticmethod
    async def usuario_logueado(username: str):
        """Registrar inicio de sesión"""
        gestor = GestorHistorial()
        await gestor.agregar_actividad(
            tipo="login",
            descripcion=f"Inició sesión en el sistema",
            usuario=username
        )
    
    @staticmethod
    async def usuario_deslogueado(username: str):
        """Registrar cierre de sesión"""
        gestor = GestorHistorial()
        await gestor.agregar_actividad(
            tipo="logout",
            descripcion=f"Cerró sesión en el sistema",
            usuario=username
        )
    
    @staticmethod
    async def archivo_importado(tipo_archivo: str, cantidad_registros: int, usuario: str):
        """Registrar importación de archivo"""
        gestor = GestorHistorial()
        await gestor.agregar_actividad(
            tipo="importar_excel",
            descripcion=f"Importó {cantidad_registros} registros desde archivo {tipo_archivo}",
            usuario=usuario,
            detalles={"tipo_archivo": tipo_archivo, "cantidad": cantidad_registros}
        )
    
    @staticmethod
    async def movimiento_realizado(producto: str, origen: str, destino: str, cantidad: int, usuario: str):
        """Registrar movimiento de producto"""
        gestor = GestorHistorial()
        await gestor.agregar_actividad(
            tipo="movimiento_producto",
            descripcion=f"Movió {cantidad} unidades de '{producto}' desde {origen} hacia {destino}",
            usuario=usuario,
            detalles={
                "producto": producto,
                "origen": origen,
                "destino": destino,
                "cantidad": cantidad
            }
        )
    
    @staticmethod
    async def error_sistema(descripcion_error: str, usuario: str = "Sistema"):
        """Registrar error del sistema"""
        gestor = GestorHistorial()
        await gestor.agregar_actividad(
            tipo="error",
            descripcion=f"Error: {descripcion_error}",
            usuario=usuario,
            detalles={"error": descripcion_error}
        )

    # Mantener compatibilidad con versión anterior
    @staticmethod
    async def agregar_actividad(tipo, descripcion, usuario="Usuario"):
        """Método de compatibilidad con versión anterior"""
        gestor = GestorHistorial()
        await gestor.agregar_actividad(tipo, descripcion, usuario)
    
    @staticmethod
    async def obtener_actividades_recientes(limite=10):
        """Método de compatibilidad con versión anterior - Usar nueva instancia"""
        gestor = GestorHistorial()
        return await gestor.obtener_historial_reciente(limite)
    
    # Funciones estáticas adicionales para compatibilidad
    def obtener_productos_stock_bajo(limite=5):
        """Obtener productos con stock bajo desde Firebase"""
        try:
            productos = db.collection('productos').order_by('cantidad').limit(limite).get()
            productos_stock_bajo = []
            
            for producto in productos:
                data = producto.to_dict()
                productos_stock_bajo.append({
                    'nombre': data.get('nombre', 'Sin nombre'),
                    'cantidad': data.get('cantidad', 0),
                    'modelo': data.get('modelo', 'Sin modelo')
                })
            
            return productos_stock_bajo
            
        except Exception as error:
            print(f"Error al obtener productos con stock bajo: {error}")
            return []
