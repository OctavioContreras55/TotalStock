# 🚀 EJECUTABLES TOTALSTOCK - GUÍA COMPLETA

## 📊 VERSIONES DISPONIBLES

### ⚡ VERSIÓN OPTIMIZADA (--onedir) - RECOMENDADA
- **📁 Ubicación:** `dist/TotalStock/TotalStock.exe`
- **⏱️ Tiempo de inicio:** 2-3 segundos
- **📦 Tamaño:** ~481 MB (carpeta)
- **🎯 Uso:** Desarrollo, uso personal, instalación empresarial
- **✅ Ventajas:**
  - Inicio súper rápido
  - Sin descompresión en cada uso
  - Mejor rendimiento general
  - Acceso inmediato a archivos auxiliares

### 📦 VERSIÓN PORTÁTIL (--onefile)
- **📁 Ubicación:** `dist/TotalStock.exe`
- **⏱️ Tiempo de inicio:** 8-15 segundos
- **📦 Tamaño:** ~179 MB (archivo único)
- **🎯 Uso:** Distribución, demos, portabilidad
- **✅ Ventajas:**
  - Un solo archivo ejecutable
  - Fácil distribución
  - No requiere instalación
  - Portátil 100%

## 🚀 INSTRUCCIONES DE USO

### VERSIÓN OPTIMIZADA (Rápida)
```bash
# Opción 1: Ejecutar directamente
cd dist/TotalStock
./TotalStock.exe

# Opción 2: Usar acceso rápido
TotalStock_OPTIMIZADO.bat
```

### VERSIÓN PORTÁTIL
```bash
# Ejecutar directamente
./dist/TotalStock.exe
```

## 📋 COMPARACIÓN DETALLADA

| Característica | --onedir (Optimizada) | --onefile (Portátil) |
|---------------|----------------------|----------------------|
| ⏱️ Tiempo inicio | 2-3 segundos | 8-15 segundos |
| 📦 Distribución | Carpeta (~481 MB) | Archivo único (~179 MB) |
| 🔄 Descompresión | Solo al crear | En cada ejecución |
| 💾 Espacio temporal | Permanente | Temporal cada vez |
| 🚀 Rendimiento | Excelente | Bueno |
| 📤 Portabilidad | Media | Excelente |
| 🎯 Mejor para | Uso frecuente | Distribución/demos |

## 🛠️ DISTRIBUCIÓN

### Para Usuarios Finales (Versión Optimizada)
1. Comprimir carpeta `dist/TotalStock/` en un ZIP
2. Enviar el ZIP al usuario
3. Usuario descomprime y ejecuta `TotalStock.exe`
4. Crear acceso directo al escritorio si es necesario

### Para Demos/Portabilidad (Versión Portátil)
1. Enviar directamente `dist/TotalStock.exe`
2. Usuario ejecuta sin instalación
3. Esperar 8-15 segundos para inicio

## 🔧 ARCHIVOS DE CONFIGURACIÓN

Ambas versiones comparten:
- `data/configuracion.json` - Configuración global
- `data/usuarios.json` - Base de datos de usuarios
- `data/inventario.json` - Cache local de inventario
- `conexiones/credenciales_firebase.json` - Credenciales Firebase

## 💡 RECOMENDACIONES

### Para Desarrollo/Empresa
✅ **Usar versión OPTIMIZADA (--onedir)**
- Inicio rápido para uso diario
- Mejor experiencia de usuario
- Fácil acceso a logs y configuración

### Para Distribución/Marketing
✅ **Usar versión PORTÁTIL (--onefile)**
- Un solo archivo para enviar
- Sin complicaciones de instalación
- Ideal para demos y pruebas

## 🎯 SCRIPTS DISPONIBLES

- `crear_exe_final.py` - Crea versión portátil (--onefile)
- `crear_exe_optimizado.py` - Crea versión optimizada (--onedir)
- `TotalStock_OPTIMIZADO.bat` - Acceso rápido a versión optimizada
- `test_velocidad.py` - Test de rendimiento

## 🔥 MEJORES PRÁCTICAS

1. **Para uso frecuente:** Siempre usar versión optimizada
2. **Para distribución:** Comprimir carpeta completa en ZIP
3. **Para demos rápidos:** Usar versión portátil
4. **Monitoreo:** Revisar logs en caso de errores
5. **Actualizaciones:** Mantener credenciales Firebase actualizadas

---
*Documentación actualizada: Enero 2025*
*Sistema: TotalStock v2.0 Optimizado*
