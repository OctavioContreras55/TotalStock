from datetime import datetime
from typing import Dict, List
import json

class MonitorFirebase:
    """
    Monitor para rastrear todas las consultas a Firebase y analizar el consumo.
    """
    
    def __init__(self):
        self._consultas_sesion: List[Dict] = []
        self._contadores = {
            'lecturas': 0,
            'escrituras': 0,
            'eliminaciones': 0
        }
        self._inicio_sesion = datetime.now()
    
    def registrar_consulta(self, tipo: str, coleccion: str, descripcion: str = "", cantidad_docs: int = 1):
        """
        Registra una consulta a Firebase
        
        Args:
            tipo: 'lectura', 'escritura', 'eliminacion'
            coleccion: Nombre de la colección (ej: 'productos', 'usuarios')
            descripcion: Descripción de la operación
            cantidad_docs: Número de documentos afectados
        """
        timestamp = datetime.now()
        consulta = {
            'timestamp': timestamp.strftime("%H:%M:%S"),
            'tipo': tipo,
            'coleccion': coleccion,
            'descripcion': descripcion,
            'cantidad_docs': cantidad_docs,
            'tiempo_sesion': (timestamp - self._inicio_sesion).total_seconds()
        }
        
        self._consultas_sesion.append(consulta)
        
        # Actualizar contadores
        if tipo == 'lectura':
            self._contadores['lecturas'] += cantidad_docs
        elif tipo == 'escritura':
            self._contadores['escrituras'] += cantidad_docs
        elif tipo == 'eliminacion':
            self._contadores['eliminaciones'] += cantidad_docs
        
        # Print inmediato para debugging
        emoji = {'lectura': '📖', 'escritura': '✏️', 'eliminacion': '[ELIMINAR]'}.get(tipo, '❓')
        print(f"{emoji} FIREBASE: {tipo.upper()} - {coleccion} ({cantidad_docs} docs) - {descripcion}")
        self._mostrar_resumen_rapido()
    
    def _mostrar_resumen_rapido(self):
        """Muestra un resumen rápido después de cada consulta"""
        total = sum(self._contadores.values())
        print(f"   [CHART] Total sesión: {total} consultas ({self._contadores['lecturas']}L, {self._contadores['escrituras']}E, {self._contadores['eliminaciones']}D)")
        print(f"   ⏱️ Tiempo: {(datetime.now() - self._inicio_sesion).total_seconds():.1f}s")
        print("   " + "="*50)
    
    def obtener_resumen_completo(self):
        """Obtiene un resumen completo de la sesión"""
        tiempo_total = (datetime.now() - self._inicio_sesion).total_seconds()
        total_consultas = sum(self._contadores.values())
        
        return {
            'tiempo_sesion_segundos': tiempo_total,
            'tiempo_sesion_minutos': tiempo_total / 60,
            'total_consultas': total_consultas,
            'lecturas': self._contadores['lecturas'],
            'escrituras': self._contadores['escrituras'],
            'eliminaciones': self._contadores['eliminaciones'],
            'consultas_por_minuto': (total_consultas / (tiempo_total / 60)) if tiempo_total > 0 else 0,
            'porcentaje_limite_diario_lecturas': (self._contadores['lecturas'] / 50000) * 100,
            'porcentaje_limite_diario_escrituras': (self._contadores['escrituras'] / 20000) * 100,
            'historial_consultas': self._consultas_sesion
        }
    
    def mostrar_reporte_detallado(self):
        """Muestra un reporte detallado en consola"""
        resumen = self.obtener_resumen_completo()
        
        print("\n" + "="*60)
        print("[CHART] REPORTE DETALLADO DE CONSULTAS FIREBASE")
        print("="*60)
        print(f"⏱️  Tiempo de sesión: {resumen['tiempo_sesion_minutos']:.1f} minutos")
        print(f"[UP] Total consultas: {resumen['total_consultas']}")
        print(f"📖 Lecturas: {resumen['lecturas']} ({resumen['porcentaje_limite_diario_lecturas']:.2f}% del límite diario)")
        print(f"✏️  Escrituras: {resumen['escrituras']} ({resumen['porcentaje_limite_diario_escrituras']:.2f}% del límite diario)")
        print(f"[ELIMINAR]  Eliminaciones: {resumen['eliminaciones']}")
        print(f"[RAPIDO] Consultas/minuto: {resumen['consultas_por_minuto']:.1f}")
        
        if resumen['total_consultas'] > 0:
            print(f"\n[ALERT] PROYECCIÓN DIARIA:")
            lecturas_dia = (resumen['lecturas'] / (resumen['tiempo_sesion_minutos'] / (24 * 60)))
            escrituras_dia = (resumen['escrituras'] / (resumen['tiempo_sesion_minutos'] / (24 * 60)))
            print(f"   📖 Lecturas proyectadas/día: {lecturas_dia:.0f} (límite: 50,000)")
            print(f"   ✏️  Escrituras proyectadas/día: {escrituras_dia:.0f} (límite: 20,000)")
            
            if lecturas_dia > 50000:
                print(f"   [WARN]  ALERTA: Proyección de lecturas excede límite diario")
            if escrituras_dia > 20000:
                print(f"   [WARN]  ALERTA: Proyección de escrituras excede límite diario")
        
        print("\n[LISTA] ÚLTIMAS 5 CONSULTAS:")
        for consulta in self._consultas_sesion[-5:]:
            emoji = {'lectura': '📖', 'escritura': '✏️', 'eliminacion': '[ELIMINAR]'}.get(consulta['tipo'], '❓')
            print(f"   {emoji} {consulta['timestamp']} - {consulta['tipo']} - {consulta['coleccion']} - {consulta['descripcion']}")
        
        print("="*60)
    
    def reiniciar_sesion(self):
        """Reinicia el monitoreo para una nueva sesión"""
        self._consultas_sesion.clear()
        self._contadores = {
            'lecturas': 0,
            'escrituras': 0,
            'eliminaciones': 0
        }
        self._inicio_sesion = datetime.now()
        print("[PROCESO] Monitor Firebase reiniciado")

# Instancia global del monitor
monitor_firebase = MonitorFirebase()
