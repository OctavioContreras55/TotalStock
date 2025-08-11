#!/usr/bin/env python3
"""
Script para verificar el contenido exacto de la línea 207 en carga_archivos.py
"""

def verificar_linea_207():
    try:
        archivo_path = "app/funciones/carga_archivos.py"
        
        with open(archivo_path, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        print(f"Total de líneas en el archivo: {len(lineas)}")
        print(f"Línea 207 (índice 206): {repr(lineas[206])}")
        
        # Mostrar contexto alrededor de la línea 207
        print("\n=== CONTEXTO DE LA LÍNEA 207 ===")
        for i in range(204, 212):  # Líneas 205-212
            if i < len(lineas):
                print(f"Línea {i+1}: {repr(lineas[i])}")
        
        # Buscar cualquier ocurrencia de dialog_title
        print("\n=== BÚSQUEDA DE 'dialog_title' ===")
        for i, linea in enumerate(lineas):
            if 'dialog_title' in linea:
                print(f"Línea {i+1}: {repr(linea)}")
                
        # Buscar FilePicker con cualquier parámetro
        print("\n=== BÚSQUEDA DE FilePicker ===")
        for i, linea in enumerate(lineas):
            if 'FilePicker(' in linea:
                print(f"Línea {i+1}: {repr(linea)}")
                # Mostrar las siguientes 3 líneas para ver los parámetros
                for j in range(1, 4):
                    if i+j < len(lineas):
                        print(f"Línea {i+1+j}: {repr(lineas[i+j])}")
                print("---")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verificar_linea_207()
