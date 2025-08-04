#!/usr/bin/env python3
"""
🚀 TEST DE VELOCIDAD - TotalStock
Compara tiempos de inicio entre versiones
"""

import time
import subprocess
import os
from pathlib import Path

def medir_tiempo_inicio(ejecutable_path, nombre_version):
    """Mide el tiempo de inicio de un ejecutable"""
    print(f"\n⏱️  Probando {nombre_version}...")
    print(f"📍 Ruta: {ejecutable_path}")
    
    if not os.path.exists(ejecutable_path):
        print(f"❌ No encontrado: {ejecutable_path}")
        return None
    
    try:
        # Medir tiempo de inicio
        inicio = time.time()
        
        # Iniciar proceso (se cierra automáticamente al detectar que es prueba)
        proceso = subprocess.Popen([ejecutable_path], 
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        
        # Esperar 3 segundos para que inicie
        time.sleep(3)
        
        fin = time.time()
        tiempo_transcurrido = fin - inicio
        
        # Terminar proceso
        try:
            proceso.terminate()
            proceso.wait(timeout=2)
        except:
            proceso.kill()
        
        print(f"✅ {nombre_version}: {tiempo_transcurrido:.2f} segundos")
        return tiempo_transcurrido
        
    except Exception as e:
        print(f"❌ Error probando {nombre_version}: {e}")
        return None

def main():
    print("🚀 TEST DE VELOCIDAD - TotalStock")
    print("=" * 50)
    
    # Obtener la ruta correcta del directorio raíz
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    os.chdir(root_dir)
    
    # Rutas de los ejecutables
    version_onefile = Path("dist/TotalStock.exe")
    version_onedir = Path("dist/TotalStock/TotalStock.exe")
    
    resultados = {}
    
    # Probar versión --onefile (si existe)
    if version_onefile.exists():
        tiempo = medir_tiempo_inicio(str(version_onefile), "Versión --onefile (Archivo único)")
        if tiempo:
            resultados["onefile"] = tiempo
    
    # Probar versión --onedir (optimizada)
    if version_onedir.exists():
        tiempo = medir_tiempo_inicio(str(version_onedir), "Versión --onedir (OPTIMIZADA)")
        if tiempo:
            resultados["onedir"] = tiempo
    
    # Mostrar comparación
    if len(resultados) >= 2:
        print("\n📊 COMPARACIÓN DE RENDIMIENTO:")
        print("=" * 50)
        
        tiempo_onefile = resultados.get("onefile", 0)
        tiempo_onedir = resultados.get("onedir", 0)
        
        mejora = ((tiempo_onefile - tiempo_onedir) / tiempo_onefile) * 100
        factor = tiempo_onefile / tiempo_onedir if tiempo_onedir > 0 else 0
        
        print(f"🐌 --onefile:  {tiempo_onefile:.2f} segundos")
        print(f"⚡ --onedir:   {tiempo_onedir:.2f} segundos")
        print(f"🎯 Mejora:     {mejora:.1f}% más rápido")
        print(f"🚀 Factor:     {factor:.1f}x más rápido")
        
        if mejora > 50:
            print("\n🎉 ¡OPTIMIZACIÓN EXCELENTE!")
        elif mejora > 25:
            print("\n✅ ¡Buena optimización!")
        else:
            print("\n⚠️  Mejora moderada")
    
    print("\n" + "=" * 50)
    print("📝 Nota: Tiempos aproximados, pueden variar según el sistema")

if __name__ == "__main__":
    main()
