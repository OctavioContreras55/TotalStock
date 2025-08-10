"""
Script para reemplazar todos los prints por safe_print en run_safe.py
"""

def fix_prints():
    with open('run.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Líneas que NO deben cambiarse (dentro de la función safe_print)
    lines = content.split('\n')
    fixed_lines = []
    
    inside_safe_print = False
    
    for line in lines:
        # Detectar inicio y fin de la función safe_print
        if 'def safe_print(' in line:
            inside_safe_print = True
        elif inside_safe_print and line.strip() and not line.startswith('    ') and not line.startswith('\t'):
            inside_safe_print = False
        
        # Reemplazar print por safe_print solo si no estamos dentro de safe_print
        if not inside_safe_print and 'print(' in line and 'safe_print(' not in line:
            line = line.replace('print(', 'safe_print(')
        
        fixed_lines.append(line)
    
    # Escribir archivo corregido
    with open('run.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("Archivo run.py corregido - todos los prints reemplazados por safe_print")

if __name__ == "__main__":
    fix_prints()
