# 📋 Documentación: Sistema de Temas en TotalStock

## 🎯 **¿Qué se hizo?**

Se implementó un sistema completo de cambio de temas dinámico que permite alternar entre:
- **Tema Oscuro**: Para trabajar en condiciones de poca luz
- **Tema Azul**: Basado en el diseño específico con colores corporativos

## 🏗️ **Arquitectura del Sistema**

### 1. **Estructura Central (`app/utils/temas.py`)**

```python
# Patrón de diseño: Clases de configuración
class TemaOscuro:
    BG_COLOR = "#1A1D21"
    SIDEBAR_COLOR = "#1E2124"
    TEXT_COLOR = "#F5F5F5"
    # ... más propiedades

class TemaAzul:
    BG_COLOR = "#E8F6FA"  # Extraído de la imagen de diseño
    SIDEBAR_COLOR = "#1B4B5A"  # Color exacto del sidebar
    TEXT_COLOR = "#1B365D"
    # ... más propiedades

# Patrón Singleton para gestión global
class GestorTemas:
    _tema_actual = "oscuro"
    
    @classmethod
    def obtener_tema(cls):
        # Factory Pattern: devuelve la instancia correcta
        if cls._tema_actual == "azul":
            return TemaAzul()
        else:
            return TemaOscuro()
```

### 2. **¿Por qué esta estructura?**

- **Separación de responsabilidades**: Cada tema es una clase independiente
- **Fácil mantenimiento**: Agregar un nuevo tema solo requiere crear una nueva clase
- **Centralización**: Un solo lugar para todos los colores
- **Flexibilidad**: Cada tema puede tener propiedades únicas

## 🎨 **Proceso de Extracción de Colores**

### **Del Diseño a Código:**

1. **Análisis de la imagen de diseño:**
   - Sidebar: `#1B4B5A` (azul oscuro)
   - Fondo principal: `#E8F6FA` (azul muy claro)
   - Headers de tabla: `#2E86AB` (azul medio)
   - Texto principal: `#1B365D` (azul oscuro legible)

2. **Creación de paleta coherente:**
```python
# Colores principales
BG_COLOR = "#E8F6FA"      # Fondo general
SIDEBAR_COLOR = "#1B4B5A"  # Menú lateral
PRIMARY_COLOR = "#2E86AB"  # Botones y acentos

# Problema resuelto: Contraste en sidebar
SIDEBAR_TEXT_COLOR = "#FFFFFF"     # Blanco sobre fondo oscuro
SIDEBAR_ICON_COLOR = "#B8E0F0"     # Azul claro para iconos
```

## 🔧 **Implementación Técnica**

### **1. Integración en Componentes UI**

**Antes (hardcodeado):**
```python
ft.Container(
    bgcolor="#FFFFFF",  # Color fijo
    child=ft.Text("Hola", color="#000000")  # Color fijo
)
```

**Después (dinámico):**
```python
tema = GestorTemas.obtener_tema()  # Obtiene tema actual
ft.Container(
    bgcolor=tema.CARD_COLOR,  # Color dinámico
    child=ft.Text("Hola", color=tema.TEXT_COLOR)  # Color dinámico
)
```

### **2. Sistema de Cambio Dinámico**

```python
# En ui_configuracion.py
def cambiar_tema_handler(tema_seleccionado):
    GestorTemas.cambiar_tema(tema_seleccionado)
    # Reinicia la interfaz para aplicar cambios
    page.go("/principal")
```

## 🎯 **Soluciones a Problemas Específicos**

### **Problema 1: Legibilidad en Sidebar**
- **Issue**: Texto apenas visible en sidebar oscuro
- **Solución**: Colores específicos para sidebar
```python
# Colores generales (para fondo claro)
TEXT_COLOR = "#1B365D"

# Colores específicos para sidebar (fondo oscuro)
SIDEBAR_TEXT_COLOR = "#FFFFFF"      # Máximo contraste
SIDEBAR_TEXT_SECONDARY = "#B8E0F0"  # Azul claro
```

### **Problema 2: Fidelidad al Diseño**
- **Issue**: Colores no coincidían con la imagen original
- **Solución**: Extracción pixel-perfect de colores
```python
# Análisis directo de la imagen
SIDEBAR_COLOR = "#1B4B5A"    # Color exacto extraído
TABLE_HEADER_BG = "#2E86AB"  # Color exacto de headers
```

### **Problema 3: Fatiga Visual**
- **Issue**: Colores muy intensos "calaban a la vista"
- **Solución**: Ajuste de saturación y contraste
```python
# Antes (muy intenso)
BG_COLOR = "#3498DB"

# Después (más suave)
BG_COLOR = "#E8F6FA"  # Azul muy claro y suave
```

## 📦 **Archivos Modificados**

```
app/utils/temas.py           → Sistema central de temas
app/ui/principal.py          → Sidebar con colores específicos
app/ui_configuracion.py      → Selector de temas
app/ui/*.py                  → Todas las vistas actualizadas
```

## 🔄 **Flujo de Cambio de Tema**

1. **Usuario selecciona tema** → `ui_configuracion.py`
2. **Se actualiza gestor** → `GestorTemas.cambiar_tema()`
3. **Se reinicia interfaz** → `page.go("/principal")`
4. **Todas las vistas se recrean** → Con `GestorTemas.obtener_tema()`
5. **Colores se aplican automáticamente** → En todos los componentes

## 🎨 **Ventajas del Sistema Implementado**

1. **Escalabilidad**: Agregar temas es trivial
2. **Mantenibilidad**: Un lugar para cada color
3. **Consistencia**: Mismo color siempre usa la misma variable
4. **Performance**: No recálculos, solo referencias
5. **Flexibilidad**: Cada tema puede ser completamente diferente

## 🚀 **Cómo Agregar un Nuevo Tema**

### **Paso 1: Crear la clase del tema**
```python
# En app/utils/temas.py
class TemaVerde:
    # Colores principales
    BG_COLOR = "#F0FFF0"
    CARD_COLOR = "#FFFFFF"
    SIDEBAR_COLOR = "#2E7D32"
    
    # Tabla
    TABLE_BG = "#FFFFFF"
    TABLE_HEADER_BG = "#4CAF50"
    TABLE_BORDER = "#A5D6A7"
    
    # Texto
    TEXT_COLOR = "#1B5E20"
    TEXT_SECONDARY = "#388E3C"
    SIDEBAR_TEXT_COLOR = "#FFFFFF"
    SIDEBAR_ICON_COLOR = "#C8E6C9"
    
    # Botones
    BUTTON_PRIMARY_BG = "#4CAF50"
    BUTTON_HOVER = "#45A049"
    
    # ... resto de propiedades
```

### **Paso 2: Actualizar el GestorTemas**
```python
@classmethod
def obtener_tema(cls):
    if cls._tema_actual == "azul":
        return TemaAzul()
    elif cls._tema_actual == "verde":  # Nueva opción
        return TemaVerde()
    else:
        return TemaOscuro()
```

### **Paso 3: Agregar opción en configuración**
```python
# En ui_configuracion.py
ft.RadioTile(
    value="verde", 
    title="Tema Verde",
    # ... resto de propiedades
)
```

## 💡 **Conceptos de Programación Aplicados**

### **Patrones de Diseño:**
- **Factory Pattern**: `GestorTemas.obtener_tema()` crea la instancia correcta
- **Singleton Pattern**: Estado global del tema actual
- **Strategy Pattern**: Diferentes estrategias de coloración
- **Observer Pattern**: UI se actualiza automáticamente al cambiar tema

### **Principios SOLID:**
- **Single Responsibility**: Cada clase tiene una responsabilidad clara
- **Open/Closed**: Abierto para extensión (nuevos temas), cerrado para modificación
- **Dependency Inversion**: UI depende de abstracciones, no de implementaciones concretas

## 🔍 **Estructura Detallada de Propiedades**

### **Categorías de Colores:**

```python
class Tema:
    # 1. COLORES PRINCIPALES
    BG_COLOR          # Fondo general de la aplicación
    CARD_COLOR        # Fondo de tarjetas y paneles
    SIDEBAR_COLOR     # Fondo del menú lateral
    
    # 2. TABLA
    TABLE_BG          # Fondo de la tabla
    TABLE_HEADER_BG   # Fondo de headers de tabla
    TABLE_BORDER      # Color de bordes de tabla
    TABLE_HOVER       # Color al pasar mouse sobre fila
    
    # 3. COLORES DE ACENTO
    PRIMARY_COLOR     # Color principal de la marca
    SUCCESS_COLOR     # Verde para acciones exitosas
    ERROR_COLOR       # Rojo para errores
    WARNING_COLOR     # Amarillo/naranja para advertencias
    
    # 4. TEXTO
    TEXT_COLOR        # Texto principal
    TEXT_SECONDARY    # Texto secundario
    TEXT_MUTED        # Texto deshabilitado
    
    # 5. TEXTO ESPECÍFICO SIDEBAR
    SIDEBAR_TEXT_COLOR      # Texto principal en sidebar
    SIDEBAR_TEXT_SECONDARY  # Texto secundario en sidebar
    SIDEBAR_ICON_COLOR      # Color de iconos en sidebar
    
    # 6. BOTONES
    BUTTON_BG         # Fondo de botones normales
    BUTTON_HOVER      # Fondo al hacer hover
    BUTTON_TEXT       # Texto de botones
    BUTTON_PRIMARY_BG # Fondo de botones primarios
    
    # 7. INPUTS
    INPUT_BG          # Fondo de campos de texto
    INPUT_BORDER      # Borde de inputs
    INPUT_FOCUS       # Color al enfocar input
    
    # 8. EFECTOS
    BORDER_RADIUS     # Radio de bordes redondeados
    SHADOW            # Sombra de elementos
    DIVIDER_COLOR     # Color de líneas divisorias
    
    # 9. ESTADOS
    DISABLED_COLOR    # Color de elementos deshabilitados
    SELECTED_COLOR    # Color de elementos seleccionados
```

## 🎨 **Guía de Colores Hexadecimales**

### **Tema Azul:**
```
Primarios:
├── Fondo: #E8F6FA (azul muy claro)
├── Tarjetas: #FFFFFF (blanco)
└── Sidebar: #1B4B5A (azul oscuro)

Acentos:
├── Primario: #2E86AB (azul medio)
├── Éxito: #27AE60 (verde)
├── Error: #E74C3C (rojo)
└── Advertencia: #F39C12 (naranja)

Texto:
├── Principal: #1B365D (azul oscuro)
├── Secundario: #34495E (gris azulado)
├── Sidebar: #FFFFFF (blanco)
└── Iconos Sidebar: #B8E0F0 (azul claro)
```

### **Tema Oscuro:**
```
Primarios:
├── Fondo: #1A1D21 (gris muy oscuro)
├── Tarjetas: #25282C (gris oscuro)
└── Sidebar: #1E2124 (gris oscuro)

Acentos:
├── Primario: #7B8FDB (azul suave)
├── Éxito: #4CBB17 (verde vibrante)
├── Error: #F55757 (rojo suave)
└── Advertencia: #FFA726 (naranja suave)

Texto:
├── Principal: #F5F5F5 (blanco suave)
├── Secundario: #B9BBBE (gris claro)
├── Sidebar: #FFFFFF (blanco)
└── Iconos Sidebar: #B9BBBE (gris claro)
```

## 🛠️ **Consejos para Mantenimiento**

### **1. Naming Convention:**
- Usa nombres descriptivos: `SIDEBAR_TEXT_COLOR` mejor que `COLOR_1`
- Agrupa por funcionalidad: `TABLE_*`, `BUTTON_*`, `TEXT_*`
- Mantén consistencia entre temas

### **2. Testing de Colores:**
```python
# Función útil para probar contraste
def verificar_contraste(color_fondo, color_texto):
    # Implementar cálculo de contraste WCAG
    ratio = calcular_ratio(color_fondo, color_texto)
    return ratio >= 4.5  # Estándar AA
```

### **3. Documentación de Cambios:**
```python
# Comentar el propósito de cada color
BG_COLOR = "#E8F6FA"  # Azul muy claro - extraído del diseño corporativo
SIDEBAR_COLOR = "#1B4B5A"  # Azul oscuro - matches mockup exactly
```

## 📚 **Recursos Adicionales**

### **Herramientas Recomendadas:**
- **Coolors.co**: Para generar paletas armoniosas
- **Contrast Checker**: Para verificar accesibilidad
- **Adobe Color**: Para extraer colores de imágenes
- **Material Design Colors**: Para inspiración

### **Estándares de Accesibilidad:**
- **WCAG AA**: Contraste mínimo 4.5:1 para texto normal
- **WCAG AAA**: Contraste mínimo 7:1 para texto normal
- **Color Blind Friendly**: Evitar depender solo del color para información

---

## 📝 **Notas del Desarrollador**

**Fecha de implementación**: 29 de julio de 2025  
**Framework**: Flet (Python)  
**Versión**: 1.0  
**Estado**: Funcional y testeado  

**Próximas mejoras sugeridas:**
- [ ] Persistencia del tema seleccionado en archivo de configuración
- [ ] Más opciones de personalización (tamaño de fuente, espaciado)
- [ ] Tema automático basado en hora del día
- [ ] Exportar/importar temas personalizados

---

*Esta documentación fue generada automáticamente basada en la implementación del sistema de temas en TotalStock.*
