"""
Script para reemplazar caracteres Unicode problemáticos en todo el proyecto
"""

import os
import re
import glob

# Mapeo de caracteres problemáticos a versiones seguras
UNICODE_REPLACEMENTS = {
    '[OK]': '[OK]',
    '[ERROR]': '[ERROR]',
    '[PROCESO]': '[PROCESO]',
    '[RAPIDO]': '[RAPIDO]',
    '[LIMPIEZA]': '[LIMPIEZA]',
    '[INICIO]': '[INICIO]',
    '[ESPERA]': '[ESPERA]',
    '[PACKAGE]': '[BUILD]',
    '[CONSULTA]': '[CONSULTA]',
    '[DART]': '[TARGET]',
    '[CONFIG]': '[CONFIG]',
    '[LISTA]': '[LISTA]',
    '[ART]': '[STYLE]',
    '[BUSCAR]': '[BUSCAR]',
    '[ELIMINAR]': '[ELIMINAR]',
    '[CHECK]': '[CHECK]',
    '[SEGURIDAD]': '[SEGURIDAD]',
    '[CHART]': '[STATS]',
    '[LOCK]': '[LOCK]',
    '[SAVE]': '[SAVE]',
    '[UP]': '[GRAPH]',
    '[WARN]': '[WARN]',
    '[ALERT]': '[ALERT]',
    '[FOLDER]': '[FOLDER]',
    '[FILE]': '[FILE]',
    '[KEY]': '[KEY]',
    '[STAR]': '[STAR]',
    '[IDEA]': '[IDEA]',
    '[SUCCESS]': '[SUCCESS]',
    '[EDIT]': '[EDIT]',
    '[TAB]': '[TAB]',
    '[LINK]': '[LINK]',
    '[UPLOAD]': '[UPLOAD]',
    '[DOWNLOAD]': '[DOWNLOAD]',
    '[NOTIF]': '[NOTIF]',
    '[STAR]': '[STAR]',
    '[HOME]': '[HOME]',
    '[USER]': '[USER]',
    '[USERS]': '[USERS]',
    '[PACKAGE]': '[PACKAGE]',
    '[FUTURE]': '[FUTURE]',
    '[MASK]': '[MASK]',
    '[EVENT]': '[CIRCUS]',
    '[ART]': '[ART]',
    '[DART]': '[DART]',
    '[TOOL]': '[TOOL]',
    '[RULER]': '[RULER]',
    '[CHART]': '[CHART]',
    '[UP]': '[UP]',
    '[DOWN]': '[DOWN]',
    '[DATE]': '[DATE]',
    '[CAL]': '[CAL]',
    '[TIME]': '[TIME]',
    '[CLOCK]': '[CLOCK]',
    '[EVENT]': '[EVENT]',
    '[INFO]': '[INFO]',  # Este también puede causar problemas
}

def reemplazar_unicode_en_archivo(archivo_path):
    """Reemplaza caracteres Unicode en un archivo específico"""
    try:
        # Leer archivo
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        contenido_original = contenido
        
        # Aplicar reemplazos
        for unicode_char, reemplazo in UNICODE_REPLACEMENTS.items():
            contenido = contenido.replace(unicode_char, reemplazo)
        
        # Solo escribir si hubo cambios
        if contenido != contenido_original:
            with open(archivo_path, 'w', encoding='utf-8') as f:
                f.write(contenido)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error procesando {archivo_path}: {e}")
        return False

def encontrar_archivos_python():
    """Encuentra todos los archivos Python en el proyecto"""
    archivos = []
    
    # Buscar archivos .py
    for root, dirs, files in os.walk('.'):
        # Excluir directorios problemáticos
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'build', 'dist', 'venv', 'env']]
        
        for file in files:
            if file.endswith('.py'):
                archivos.append(os.path.join(root, file))
    
    return archivos

def main():
    print("=" * 60)
    print("Script de Limpieza Unicode")
    print("=" * 60)
    
    archivos_python = encontrar_archivos_python()
    print(f"Encontrados {len(archivos_python)} archivos Python")
    
    archivos_modificados = 0
    
    for archivo in archivos_python:
        if reemplazar_unicode_en_archivo(archivo):
            print(f"  [MODIFICADO] {archivo}")
            archivos_modificados += 1
        else:
            print(f"  [SIN CAMBIOS] {archivo}")
    
    print()
    print(f"Resumen:")
    print(f"  - Archivos procesados: {len(archivos_python)}")
    print(f"  - Archivos modificados: {archivos_modificados}")
    print(f"  - Archivos sin cambios: {len(archivos_python) - archivos_modificados}")
    
    if archivos_modificados > 0:
        print()
        print("Caracteres Unicode reemplazados:")
        for unicode_char, reemplazo in UNICODE_REPLACEMENTS.items():
            print(f"  {unicode_char} → {reemplazo}")

if __name__ == "__main__":
    main()
