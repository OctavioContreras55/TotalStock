# 🚀 TotalStock - Sistema de Inventario

## 📁 Estructura del Proyecto

```
TotalStock/
├── 🚀 run.py                      # Punto de entrada principal
├── 🔧 build.py                    # Script maestro de construcción
├── 📋 requirements.txt            # Dependencias Python
├── ⚙️  TotalStock.spec             # Configuración PyInstaller
├── 🎯 TotalStock_OPTIMIZADO.bat   # Acceso rápido al ejecutable
├── 
├── 📁 app/                        # Código principal de la aplicación
│   ├── main.py                    # Aplicación principal
│   ├── data.py                    # Gestión de datos
│   ├── ui_*.py                    # Interfaces de usuario
│   ├── crud_*/                    # Operaciones CRUD
│   ├── tablas/                    # Componentes de tablas
│   ├── utils/                     # Utilidades (cache, configuración, etc.)
│   └── ui/                        # Componentes de interfaz
│
├── 📁 conexiones/                 # Configuración de Firebase
│   ├── firebase.py                # Cliente Firebase
│   └── credenciales_firebase.json # Credenciales (no incluido en git)
│
├── 📁 assets/                     # Recursos gráficos
│   ├── logo.png                   # Logo principal
│   └── logo.ico                   # Icono de aplicación
│
├── 📁 data/                       # Datos locales y configuración
│   ├── configuracion.json         # Configuración global
│   ├── usuarios.json              # Cache de usuarios
│   └── inventario.json            # Cache de inventario
│
├── 📁 scripts/                    # Scripts de construcción y utilidades
│   ├── crear_exe_final.py         # Crear ejecutable portátil
│   ├── crear_exe_optimizado.py    # Crear ejecutable optimizado
│   ├── test_velocidad.py          # Test de rendimiento
│   ├── diagnostico_sistema.py     # Diagnóstico del sistema
│   └── utils_limpieza_usuarios.py # Utilidades de limpieza
│
├── 📁 tests/                      # Tests y archivos de prueba
│   ├── test_*.py                  # Tests unitarios
│   └── *.xlsx                     # Archivos de prueba
│
├── 📁 docs/                       # Documentación completa
│   ├── GUIA_EJECUTABLES.md        # Guía de ejecutables
│   ├── RESUMEN_CONVERSION.md      # Resumen de conversión
│   └── *.md                       # Documentación técnica
│
├── 📁 dist/                       # Ejecutables generados
│   ├── TotalStock.exe              # Versión portátil
│   └── TotalStock/                 # Versión optimizada
│       └── TotalStock.exe          # ← Inicio súper rápido
│
└── 📁 build/                      # Archivos temporales de construcción
```

## 🚀 Inicio Rápido

### Desarrollo
```bash
python run.py
```

### Crear Ejecutables
```bash
# Script interactivo (RECOMENDADO)
python build.py

# O directamente:
python scripts/crear_exe_optimizado.py    # Versión rápida
python scripts/crear_exe_final.py         # Versión portátil
```

### Ejecutar Versión Compilada
```bash
# Versión optimizada (RÁPIDA - 2-3 segundos)
TotalStock_OPTIMIZADO.bat

# O manualmente:
cd dist/TotalStock && TotalStock.exe
```

## 📊 Versiones de Ejecutables

| Versión | Tamaño | Inicio | Uso Recomendado |
|---------|--------|--------|--------------  |
| 📦 Portátil | ~179 MB | 8-15s | Distribución, demos |
| ⚡ Optimizada | ~481 MB | 2-3s | Uso diario, empresa |

## 🔧 Características

- ✅ **Sistema completo de inventario** con Firebase
- ✅ **Interfaz moderna** con Flet UI
- ✅ **Cache inteligente** con invalidación automática
- ✅ **Múltiples usuarios** con roles y permisos
- ✅ **Reportes y exportaciones** en múltiples formatos
- ✅ **Temas personalizables** por usuario
- ✅ **Ejecutables optimizados** para distribución

## 📚 Documentación

Toda la documentación está organizada en la carpeta `docs/`:

- `GUIA_EJECUTABLES.md` - Guía completa de ejecutables
- `RESUMEN_CONVERSION.md` - Resumen del proceso de conversión
- `ARQUITECTURA_PATRONES.md` - Arquitectura del sistema
- `DOCUMENTACION_COMPLETA.md` - Documentación técnica completa

## 🛠️ Desarrollo

### Requisitos
- Python 3.13+
- Firebase Admin SDK
- Flet UI Framework
- PyInstaller 6.14.2+

### Instalación
```bash
pip install -r requirements.txt
```

### Tests
```bash
python -m pytest tests/
# O ejecutar tests individuales desde tests/
```

---
*Sistema desarrollado con ❤️ para gestión eficiente de inventarios*
