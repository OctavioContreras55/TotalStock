#!/usr/bin/env python3
"""
Análisis de líneas de código del proyecto TotalStock
"""

import os
import sys
from pathlib import Path

def contar_lineas_archivo(archivo):
    """Contar líneas en un archivo"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            lineas = len(f.readlines())
        return lineas
    except Exception as e:
        try:
            # Intentar con encoding diferente
            with open(archivo, 'r', encoding='latin-1') as f:
                lineas = len(f.readlines())
            return lineas
        except:
            return 0

def analizar_directorio(directorio, extensiones):
    """Analizar archivos en un directorio"""
    archivos_analizados = []
    total_lineas = 0
    
    for root, dirs, files in os.walk(directorio):
        # Excluir directorios no relevantes
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'node_modules', 'dist', 'build']]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensiones):
                archivo_path = os.path.join(root, file)
                lineas = contar_lineas_archivo(archivo_path)
                
                if lineas > 0:
                    archivos_analizados.append({
                        'archivo': archivo_path,
                        'lineas': lineas,
                        'extension': os.path.splitext(file)[1]
                    })
                    total_lineas += lineas
    
    return archivos_analizados, total_lineas

def main():
    """Función principal de análisis"""
    print("📊 ANÁLISIS DE LÍNEAS DE CÓDIGO - TotalStock")
    print("=" * 60)
    
    # Verificar directorio actual
    if not os.path.exists('app'):
        print("❌ Error: Ejecuta este script desde el directorio raíz del proyecto")
        sys.exit(1)
    
    # Definir extensiones a analizar
    extensiones_codigo = ['.py']
    extensiones_config = ['.json', '.txt', '.md', '.bat', '.spec']
    extensiones_todas = extensiones_codigo + extensiones_config
    
    print("🔍 Analizando archivos...")
    
    # Análisis por categorías
    categorias = {
        'Código Python': extensiones_codigo,
        'Configuración y Docs': extensiones_config
    }
    
    total_general = 0
    resultados = {}
    
    for categoria, extensiones in categorias.items():
        archivos, total_lineas = analizar_directorio('.', extensiones)
        resultados[categoria] = {
            'archivos': archivos,
            'total_lineas': total_lineas,
            'total_archivos': len(archivos)
        }
        total_general += total_lineas
        
        print(f"\n📁 {categoria}:")
        print(f"   📄 Archivos: {len(archivos)}")
        print(f"   📝 Líneas: {total_lineas:,}")
    
    # Análisis detallado de código Python
    print("\n" + "=" * 60)
    print("🐍 DESGLOSE DETALLADO - CÓDIGO PYTHON")
    print("=" * 60)
    
    archivos_python = resultados['Código Python']['archivos']
    archivos_python.sort(key=lambda x: x['lineas'], reverse=True)
    
    # Archivos principales (top 15)
    print("\n📊 ARCHIVOS PRINCIPALES (Top 15):")
    print("-" * 60)
    for i, archivo in enumerate(archivos_python[:15]):
        nombre = archivo['archivo'].replace('.\\', '').replace('\\', '/')
        lineas = archivo['lineas']
        print(f"{i+1:2d}. {nombre:<45} {lineas:>6} líneas")
    
    # Análisis por directorios
    print(f"\n📁 ANÁLISIS POR DIRECTORIOS:")
    print("-" * 60)
    
    directorios = {}
    for archivo in archivos_python:
        directorio = os.path.dirname(archivo['archivo']).replace('.\\', '').replace('\\', '/') or 'Raíz'
        if directorio not in directorios:
            directorios[directorio] = {'archivos': 0, 'lineas': 0}
        directorios[directorio]['archivos'] += 1
        directorios[directorio]['lineas'] += archivo['lineas']
    
    # Ordenar directorios por líneas
    for directorio, datos in sorted(directorios.items(), key=lambda x: x[1]['lineas'], reverse=True):
        archivos_count = datos['archivos']
        lineas_count = datos['lineas']
        promedio = lineas_count // archivos_count if archivos_count > 0 else 0
        print(f"{directorio:<35} {archivos_count:>3} archivos {lineas_count:>6} líneas (promedio: {promedio:>3})")
    
    # Análisis de configuración y documentación
    print(f"\n📋 DESGLOSE - CONFIGURACIÓN Y DOCUMENTACIÓN:")
    print("-" * 60)
    
    archivos_config = resultados['Configuración y Docs']['archivos']
    archivos_config.sort(key=lambda x: x['lineas'], reverse=True)
    
    for archivo in archivos_config[:10]:  # Top 10
        nombre = archivo['archivo'].replace('.\\', '').replace('\\', '/')
        lineas = archivo['lineas']
        ext = archivo['extension']
        print(f"{nombre:<45} {lineas:>6} líneas ({ext})")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("🎯 RESUMEN FINAL")
    print("=" * 60)
    
    python_archivos = resultados['Código Python']['total_archivos']
    python_lineas = resultados['Código Python']['total_lineas']
    config_archivos = resultados['Configuración y Docs']['total_archivos']
    config_lineas = resultados['Configuración y Docs']['total_lineas']
    
    print(f"📊 CÓDIGO PYTHON:")
    print(f"   📄 Archivos: {python_archivos}")
    print(f"   📝 Líneas: {python_lineas:,}")
    print(f"   📈 Promedio: {python_lineas // python_archivos if python_archivos > 0 else 0} líneas/archivo")
    
    print(f"\n📊 CONFIGURACIÓN Y DOCS:")
    print(f"   📄 Archivos: {config_archivos}")
    print(f"   📝 Líneas: {config_lineas:,}")
    
    print(f"\n🎉 TOTAL GENERAL:")
    print(f"   📄 Archivos: {python_archivos + config_archivos}")
    print(f"   📝 Líneas: {total_general:,}")
    
    # Clasificación del proyecto
    print(f"\n📏 CLASIFICACIÓN DEL PROYECTO:")
    if python_lineas < 1000:
        clasificacion = "Pequeño"
        emoji = "🌱"
    elif python_lineas < 5000:
        clasificacion = "Mediano"
        emoji = "🌿"
    elif python_lineas < 15000:
        clasificacion = "Grande"
        emoji = "🌳"
    else:
        clasificacion = "Muy Grande"
        emoji = "🏢"
    
    print(f"   {emoji} {clasificacion} ({python_lineas:,} líneas de Python)")
    
    # Estimación de tiempo de desarrollo
    # Regla general: 10-50 líneas de código por día productivo
    dias_min = python_lineas // 50
    dias_max = python_lineas // 10
    print(f"\n⏱️ ESTIMACIÓN DE DESARROLLO:")
    print(f"   📅 Entre {dias_min} y {dias_max} días de desarrollo")
    print(f"   📅 Equivalente a {dias_min//30}-{dias_max//30} meses aprox.")

if __name__ == "__main__":
    main()
