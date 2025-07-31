import datetime
from conexiones.firebase import db
import asyncio

class GestorHistorial:
    @staticmethod
    async def agregar_actividad(tipo, descripcion, usuario="Usuario"):
        """
        Agregar una actividad al historial
        tipo: 'crear_producto', 'editar_producto', 'eliminar_producto', 'crear_usuario', etc.
        descripcion: Descripción de la acción
        usuario: Usuario que realizó la acción
        """
        try:
            actividad = {
                'tipo': tipo,
                'descripcion': descripcion,
                'usuario': usuario,
                'timestamp': datetime.datetime.now(),
                'fecha': datetime.datetime.now().strftime("%Y-%m-%d"),
                'hora': datetime.datetime.now().strftime("%H:%M")
            }
            
            # Guardar en Firebase
            db.collection('historial').add(actividad)
            print(f"Actividad registrada: {descripcion}")
            
        except Exception as error:
            print(f"Error al registrar actividad: {error}")
    
    @staticmethod
    async def obtener_actividades_recientes(limite=10):
        """Obtener las actividades más recientes"""
        try:
            actividades = db.collection('historial').order_by('timestamp', direction='DESCENDING').limit(limite).get()
            return [actividad.to_dict() for actividad in actividades]
        except Exception as error:
            print(f"Error al obtener historial: {error}")
            return []
    
    @staticmethod
    async def obtener_estadisticas_hoy():
        """Obtener estadísticas del día actual"""
        try:
            fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
            actividades = db.collection('historial').where('fecha', '==', fecha_hoy).get()
            
            estadisticas = {}
            for actividad in actividades:
                data = actividad.to_dict()
                tipo = data.get('tipo', 'otro')
                estadisticas[tipo] = estadisticas.get(tipo, 0) + 1
            
            return estadisticas
            
        except Exception as error:
            print(f"Error al obtener estadísticas: {error}")
            return {}
    
    @staticmethod
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
