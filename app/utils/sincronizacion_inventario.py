#!/usr/bin/env python3
"""
Sistema de sincronización automática entre inventario y ubicaciones.
Mantiene las cantidades del inventario actualizadas basándose en las ubicaciones.
"""

from typing import Dict, List
from conexiones.firebase import db
from app.utils.cache_firebase import cache_firebase
from app.utils.monitor_firebase import monitor_firebase
import asyncio

class SincronizadorInventario:
    """
    Clase para manejar la sincronización automática entre ubicaciones e inventario.
    """
    
    def __init__(self):
        self.debug_enabled = True
    
    def log(self, mensaje: str):
        """Función de logging para debug - DESHABILITADA para limpiar terminal"""
        pass
    
    async def calcular_cantidades_por_modelo(self) -> Dict[str, int]:
        """
        Calcula las cantidades totales por modelo sumando todas las ubicaciones.
        
        Returns:
            Dict con modelo como clave y cantidad total como valor
        """
        self.log("Calculando cantidades por modelo desde ubicaciones...")
        
        try:
            # Obtener todas las ubicaciones
            ubicaciones = await cache_firebase.obtener_ubicaciones()
            
            cantidades_por_modelo = {}
            
            for ubicacion in ubicaciones:
                modelo_raw = ubicacion.get('modelo', '')
                modelo = str(modelo_raw).strip() if modelo_raw is not None else ''
                cantidad = ubicacion.get('cantidad', 0)
                
                if modelo:  # Solo procesar si tiene modelo
                    try:
                        cantidad_int = int(cantidad) if cantidad else 0
                        if modelo in cantidades_por_modelo:
                            cantidades_por_modelo[modelo] += cantidad_int
                        else:
                            cantidades_por_modelo[modelo] = cantidad_int
                    except (ValueError, TypeError):
                        self.log(f"[WARN] Cantidad inválida para modelo {modelo}: {cantidad}")
                        continue
            
            self.log(f"Cantidades calculadas para {len(cantidades_por_modelo)} modelos")
            return cantidades_por_modelo
            
        except Exception as e:
            self.log(f"[ERROR] Error al calcular cantidades: {e}")
            return {}
    
    async def sincronizar_inventario_completo(self, mostrar_resultados: bool = True) -> Dict:
        """
        Sincroniza todo el inventario con las cantidades de ubicaciones.
        
        Args:
            mostrar_resultados: Si mostrar los resultados del proceso
            
        Returns:
            Dict con estadísticas del proceso
        """
        self.log("Iniciando sincronización completa del inventario...")
        
        try:
            # Calcular cantidades desde ubicaciones
            cantidades_ubicaciones = await self.calcular_cantidades_por_modelo()
            
            # Obtener productos del inventario
            productos = await cache_firebase.obtener_productos()
            
            # Estadísticas
            productos_actualizados = 0
            productos_sin_ubicacion = 0
            modelos_nuevos_en_ubicaciones = []
            errores = []
            
            # Actualizar productos existentes
            for producto in productos:
                modelo_raw = producto.get('modelo', '')
                modelo = str(modelo_raw).strip() if modelo_raw is not None else ''
                cantidad_actual = producto.get('cantidad', 0)
                firebase_id = producto.get('firebase_id')
                
                if not firebase_id or not modelo:
                    continue
                
                # Obtener cantidad desde ubicaciones
                cantidad_ubicaciones = cantidades_ubicaciones.get(modelo, 0)
                
                # Solo actualizar si las cantidades son diferentes
                if cantidad_actual != cantidad_ubicaciones:
                    try:
                        # Actualizar en Firebase
                        doc_ref = db.collection('productos').document(firebase_id)
                        doc_ref.update({'cantidad': cantidad_ubicaciones})
                        
                        self.log(f"  {modelo}: {cantidad_actual} → {cantidad_ubicaciones}")
                        productos_actualizados += 1
                        
                        # Registrar en monitor
                        monitor_firebase.registrar_consulta(
                            tipo='escritura',
                            coleccion='productos',
                            descripcion=f'Sync cantidad {modelo}: {cantidad_actual}→{cantidad_ubicaciones}',
                            cantidad_docs=1
                        )
                        
                    except Exception as e:
                        errores.append(f"Error actualizando {modelo}: {e}")
                        self.log(f"[ERROR] Error actualizando {modelo}: {e}")
                
                # Remover de cantidades_ubicaciones para detectar modelos nuevos
                if modelo in cantidades_ubicaciones:
                    del cantidades_ubicaciones[modelo]
                else:
                    productos_sin_ubicacion += 1
            
            # Detectar modelos en ubicaciones que no están en inventario
            modelos_nuevos_en_ubicaciones = list(cantidades_ubicaciones.keys())
            
            # Invalidar cache para refrescar datos
            cache_firebase.invalidar_cache_productos()
            
            # Preparar resultados
            resultado = {
                'productos_actualizados': productos_actualizados,
                'productos_sin_ubicacion': productos_sin_ubicacion,
                'modelos_nuevos': modelos_nuevos_en_ubicaciones,
                'errores': errores,
                'exito': len(errores) == 0
            }
            
            if mostrar_resultados:
                self.log("=" * 50)
                self.log("RESULTADOS DE SINCRONIZACIÓN:")
                self.log(f"  [CHART] Productos actualizados: {productos_actualizados}")
                self.log(f"  [WARN] Productos sin ubicación: {productos_sin_ubicacion}")
                if modelos_nuevos_en_ubicaciones:
                    self.log(f"  🆕 Modelos en ubicaciones no en inventario: {modelos_nuevos_en_ubicaciones}")
                if errores:
                    self.log(f"  [ERROR] Errores: {len(errores)}")
                self.log("=" * 50)
            
            return resultado
            
        except Exception as e:
            self.log(f"[ERROR] Error en sincronización completa: {e}")
            return {
                'productos_actualizados': 0,
                'productos_sin_ubicacion': 0,
                'modelos_nuevos': [],
                'errores': [str(e)],
                'exito': False
            }
    
    async def sincronizar_modelo_especifico(self, modelo: str) -> bool:
        """
        Sincroniza la cantidad de un modelo específico.
        
        Args:
            modelo: El modelo a sincronizar
            
        Returns:
            True si se sincronizó exitosamente
        """
        self.log(f"Sincronizando modelo específico: {modelo}")
        
        try:
            # Calcular cantidad para este modelo desde ubicaciones
            ubicaciones = await cache_firebase.obtener_ubicaciones()
            cantidad_total = 0
            
            for ubicacion in ubicaciones:
                try:
                    modelo_ubicacion = ubicacion.get('modelo', '')
                    if modelo_ubicacion and str(modelo_ubicacion).strip().lower() == str(modelo).lower():
                        try:
                            cantidad_total += int(ubicacion.get('cantidad', 0))
                        except (ValueError, TypeError):
                            continue
                except:
                    continue
            
            # Buscar el producto en inventario
            productos = await cache_firebase.obtener_productos()
            for producto in productos:
                try:
                    modelo_producto = producto.get('modelo', '')
                    if modelo_producto and str(modelo_producto).strip().lower() == str(modelo).lower():
                        firebase_id = producto.get('firebase_id')
                        cantidad_actual = producto.get('cantidad', 0)
                        
                        if firebase_id and cantidad_actual != cantidad_total:
                            # Actualizar en Firebase
                            doc_ref = db.collection('productos').document(firebase_id)
                            doc_ref.update({'cantidad': cantidad_total})
                            
                            self.log(f"  {modelo}: {cantidad_actual} → {cantidad_total}")
                            
                            # Invalidar cache
                            cache_firebase.invalidar_cache_productos()
                            
                            return True
                except Exception as ex:
                    print(f"Error procesando producto en sincronización: {ex}")
                    continue
            
            self.log(f"[WARN] Modelo {modelo} no encontrado en inventario")
            return False
            
        except Exception as e:
            self.log(f"[ERROR] Error sincronizando {modelo}: {e}")
            return False

# Instancia global del sincronizador
sincronizador_inventario = SincronizadorInventario()

# Funciones de conveniencia para usar desde otros módulos
async def sincronizar_inventario_completo(mostrar_resultados: bool = True):
    """Función de conveniencia para sincronización completa"""
    return await sincronizador_inventario.sincronizar_inventario_completo(mostrar_resultados)

async def sincronizar_modelo(modelo: str):
    """Función de conveniencia para sincronizar un modelo específico"""
    return await sincronizador_inventario.sincronizar_modelo_especifico(modelo)
