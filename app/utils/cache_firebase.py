import asyncio
from datetime import datetime, timedelta
from conexiones.firebase import db
from typing import Dict, List, Optional
from app.utils.monitor_firebase import monitor_firebase

class CacheFirebase:
    """
    Cache inteligente para minimizar consultas a Firebase.
    Guarda datos en memoria por un tiempo determinado.
    """
    
    def __init__(self): # Funcion para inicializar el cache
        self._cache_productos: List[Dict] = []
        self._cache_usuarios: List[Dict] = []
        self._ultimo_update_productos: Optional[datetime] = None
        self._ultimo_update_usuarios: Optional[datetime] = None
        self._duracion_cache = timedelta(minutes=5)  # Cache válido por 5 minutos
    
    def _cache_valido(self, ultimo_update: Optional[datetime]) -> bool:
        """Verifica si el cache sigue siendo válido"""
        if ultimo_update is None:
            return False
        return datetime.now() - ultimo_update < self._duracion_cache
    
    def tiene_productos_en_cache(self) -> bool:
        """Verifica si hay productos válidos en cache SIN hacer consultas"""
        return (len(self._cache_productos) > 0 and 
                self._cache_valido(self._ultimo_update_productos))
    
    def obtener_productos_inmediato(self) -> List[Dict]:
        """
        Obtiene productos inmediatamente desde cache si están disponibles.
        NO hace consultas a Firebase. Útil para carga instantánea de UI.
        """
        if self.tiene_productos_en_cache():
            print(f"⚡ CACHE INMEDIATO: {len(self._cache_productos)} productos (0ms)")
            return self._cache_productos.copy()
        return []
    
    async def obtener_productos(self, forzar_refresh: bool = False, mostrar_loading: bool = True) -> List[Dict]:
        """
        Obtiene productos con cache inteligente y ultra-rápido.
        Solo consulta Firebase si es necesario.
        
        Args:
            forzar_refresh: Fuerza actualización desde Firebase
            mostrar_loading: Si mostrar mensajes de loading (útil para UI)
        """
        # CACHE HIT: Retorno inmediato sin delays
        if not forzar_refresh and self._cache_valido(self._ultimo_update_productos):
            if mostrar_loading:
                print(f"⚡ CACHE HIT INMEDIATO: {len(self._cache_productos)} productos (0ms, 0 consultas Firebase)")
            
            # Retorno inmediato sin awaits innecesarios
            return self._cache_productos.copy()
        
        # CACHE MISS: Consultar Firebase
        if mostrar_loading:
            print("📡 CACHE MISS: Consultando Firebase para productos...")
            
        try:
            referencia_productos = db.collection('productos')
            productos = referencia_productos.stream()
            
            lista_productos = []
            count_docs = 0
            for producto in productos:
                data = producto.to_dict()
                data['firebase_id'] = producto.id
                data['nombre'] = data.get('nombre', 'Sin nombre')
                data['precio'] = data.get('precio', 0)
                data['modelo'] = data.get('modelo', 'Sin modelo')
                data['tipo'] = data.get('tipo', 'Sin tipo')
                data['cantidad'] = data.get('cantidad', 0)
                lista_productos.append(data)
                count_docs += 1
            
            # Registrar en el monitor
            monitor_firebase.registrar_consulta(
                tipo='lectura',
                coleccion='productos',
                descripcion=f'Cache miss - consulta completa productos',
                cantidad_docs=count_docs
            )
            
            # Actualizar cache
            self._cache_productos = lista_productos
            self._ultimo_update_productos = datetime.now()
            
            if mostrar_loading:
                print(f"✅ Cache actualizado con {len(lista_productos)} productos")
            return lista_productos.copy()
            
        except Exception as e:
            print(f"❌ Error al obtener productos: {str(e)}")
            # Si hay error, devolver cache anterior si existe
            if self._cache_productos:
                print("🔄 Devolviendo datos del cache anterior por error")
                return self._cache_productos.copy()
            return []
    
    async def obtener_usuarios(self, forzar_refresh: bool = False, mostrar_loading: bool = True) -> List[Dict]:
        """
        Obtiene usuarios con cache inteligente optimizado.
        """
        # CACHE HIT: Retorno inmediato
        if not forzar_refresh and self._cache_valido(self._ultimo_update_usuarios):
            if mostrar_loading:
                print(f"⚡ CACHE HIT INMEDIATO: {len(self._cache_usuarios)} usuarios (0ms, 0 consultas Firebase)")
            return self._cache_usuarios.copy()
        
        # CACHE MISS: Consultar Firebase
        if mostrar_loading:
            print("📡 CACHE MISS: Consultando usuarios en Firebase...")
        
        try:
            referencia_usuarios = db.collection('usuarios')
            usuarios = referencia_usuarios.stream()
            
            lista_usuarios = []
            count_docs = 0
            for usuario in usuarios:
                data = usuario.to_dict()
                data['firebase_id'] = usuario.id
                lista_usuarios.append(data)
                count_docs += 1
            
            # Registrar en el monitor
            monitor_firebase.registrar_consulta(
                tipo='lectura',
                coleccion='usuarios',
                descripcion=f'Obtener todos los usuarios (cache miss)',
                cantidad_docs=count_docs
            )
            
            # Actualizar cache
            self._cache_usuarios = lista_usuarios
            self._ultimo_update_usuarios = datetime.now()
            
            print(f"✅ Cache de usuarios actualizado con {len(lista_usuarios)} usuarios")
            return lista_usuarios.copy()
            
        except Exception as e:
            print(f"❌ Error al obtener usuarios: {str(e)}")
            if self._cache_usuarios:
                return self._cache_usuarios.copy()
            return []
    
    def invalidar_cache_productos(self):
        """Fuerza la actualización del cache de productos en la próxima consulta"""
        self._ultimo_update_productos = None
        print("🔄 Cache de productos invalidado")
    
    def invalidar_cache_usuarios(self):
        """Fuerza la actualización del cache de usuarios en la próxima consulta"""
        self._ultimo_update_usuarios = None
        print("🔄 Cache de usuarios invalidado")
    
    def limpiar_cache(self):
        """Limpia todo el cache"""
        self._cache_productos.clear()
        self._cache_usuarios.clear()
        self._ultimo_update_productos = None
        self._ultimo_update_usuarios = None
        print("🧹 Cache completo limpiado")

# Instancia global del cache
cache_firebase = CacheFirebase()
