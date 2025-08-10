"""
Sistema para garantizar que solo haya una sesión activa por usuario
"""
import json
import os
import time
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

class SesionManager:
    def __init__(self):
        self.sesiones_file = os.path.join(tempfile.gettempdir(), "totalstock_sesiones.json")
        self.timeout_minutos = 5  # Timeout más agresivo de 5 minutos
        
    def limpiar_sesiones_por_proceso(self):
        """Limpiar sesiones de procesos que ya no existen"""
        sesiones = self._cargar_sesiones()
        sesiones_limpias = {}
        
        for usuario, info_sesion in sesiones.items():
            proceso_id = info_sesion.get('proceso_id')
            if proceso_id:
                try:
                    # Verificar si el proceso existe en Windows
                    import subprocess
                    result = subprocess.run(['tasklist', '/FI', f'PID eq {proceso_id}'], 
                                          capture_output=True, text=True)
                    if f'{proceso_id}' not in result.stdout:
                        print(f"[LIMPIEZA] Proceso {proceso_id} no existe, eliminando sesión de {usuario}")
                        continue  # No agregar esta sesión
                except Exception as e:
                    print(f"Error verificando proceso {proceso_id}: {e}")
            
            sesiones_limpias[usuario] = info_sesion
        
        if len(sesiones_limpias) != len(sesiones):
            self._guardar_sesiones(sesiones_limpias)
            print(f"[LIMPIEZA] Limpiadas {len(sesiones) - len(sesiones_limpias)} sesiones zombie")
        
        return sesiones_limpias
        
    def _cargar_sesiones(self):
        """Cargar sesiones activas desde archivo"""
        try:
            if os.path.exists(self.sesiones_file):
                with open(self.sesiones_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error cargando sesiones: {e}")
            return {}
            
    def _guardar_sesiones(self, sesiones):
        """Guardar sesiones activas en archivo"""
        try:
            with open(self.sesiones_file, 'w', encoding='utf-8') as f:
                json.dump(sesiones, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando sesiones: {e}")
            
    def _limpiar_sesiones_expiradas(self, sesiones):
        """Eliminar sesiones expiradas"""
        ahora = datetime.now()
        sesiones_limpias = {}
        
        for usuario, info_sesion in sesiones.items():
            try:
                ultima_actividad = datetime.fromisoformat(info_sesion['ultima_actividad'])
                if ahora - ultima_actividad < timedelta(minutes=self.timeout_minutos):
                    sesiones_limpias[usuario] = info_sesion
                else:
                    print(f"Sesión expirada para usuario: {usuario}")
            except Exception as e:
                print(f"Error procesando sesión de {usuario}: {e}")
                
        return sesiones_limpias
        
    def iniciar_sesion(self, nombre_usuario):
        """Iniciar sesión para un usuario"""
        sesiones = self._cargar_sesiones()
        sesiones = self._limpiar_sesiones_expiradas(sesiones)
        
        # Verificar si el usuario ya tiene una sesión activa
        if nombre_usuario in sesiones:
            info_sesion = sesiones[nombre_usuario]
            return {
                "exito": False,
                "mensaje": f"El usuario '{nombre_usuario}' ya tiene una sesión activa.\n"
                          f"Iniciada: {info_sesion['fecha_inicio']}\n"
                          f"Última actividad: {info_sesion['ultima_actividad']}\n\n"
                          f"Si necesitas acceder, cierra la otra sesión primero.",
                "sesion_existente": True
            }
            
        # Crear nueva sesión
        ahora = datetime.now()
        sesiones[nombre_usuario] = {
            "fecha_inicio": ahora.isoformat(),
            "ultima_actividad": ahora.isoformat(),
            "proceso_id": os.getpid()
        }
        
        self._guardar_sesiones(sesiones)
        
        return {
            "exito": True,
            "mensaje": f"Sesión iniciada exitosamente para {nombre_usuario}",
            "sesion_existente": False
        }
        
    def actualizar_actividad(self, nombre_usuario):
        """Actualizar última actividad del usuario"""
        sesiones = self._cargar_sesiones()
        
        if nombre_usuario in sesiones:
            sesiones[nombre_usuario]['ultima_actividad'] = datetime.now().isoformat()
            self._guardar_sesiones(sesiones)
            
    def cerrar_sesion(self, nombre_usuario):
        """Cerrar sesión de un usuario"""
        sesiones = self._cargar_sesiones()
        
        if nombre_usuario in sesiones:
            del sesiones[nombre_usuario]
            self._guardar_sesiones(sesiones)
            print(f"Sesión cerrada para usuario: {nombre_usuario}")
            
    def obtener_sesiones_activas(self):
        """Obtener lista de sesiones activas con limpieza automática"""
        sesiones = self._cargar_sesiones()
        sesiones = self._limpiar_sesiones_expiradas(sesiones)
        
        # También limpiar por procesos inexistentes
        sesiones = self.limpiar_sesiones_por_proceso()
        
        return sesiones
        
    def forzar_cierre_sesion(self, nombre_usuario):
        """Forzar cierre de sesión (para administradores)"""
        sesiones = self._cargar_sesiones()
        
        if nombre_usuario in sesiones:
            del sesiones[nombre_usuario]
            self._guardar_sesiones(sesiones)
            return {
                "exito": True,
                "mensaje": f"Sesión de '{nombre_usuario}' cerrada forzadamente"
            }
        else:
            return {
                "exito": False,
                "mensaje": f"No se encontró sesión activa para '{nombre_usuario}'"
            }
            
    def obtener_usuario_actual_desde_archivo(self):
        """Obtener el usuario que tiene sesión activa en este proceso"""
        sesiones = self._cargar_sesiones()
        proceso_actual = os.getpid()
        
        for usuario, info_sesion in sesiones.items():
            if info_sesion.get('proceso_id') == proceso_actual:
                return usuario
        
        return None
        
    def limpiar_todas_las_sesiones(self):
        """Limpiar todas las sesiones (para casos de emergencia)"""
        try:
            if os.path.exists(self.sesiones_file):
                os.remove(self.sesiones_file)
                print("[LIMPIEZA] Todas las sesiones han sido limpiadas")
                return True
        except Exception as e:
            print(f"Error limpiando sesiones: {e}")
            return False

# Instancia global
gestor_sesiones = SesionManager()
