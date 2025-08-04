# 🐍 Funciones Reservadas de Python - Guía Detallada

## 📚 Introducción

Este documento explica las **funciones reservadas de Python** (también llamadas **métodos especiales**, **métodos mágicos** o **dunder methods**) utilizadas en el sistema TotalStock, y el **por qué** de su uso en nuestro contexto específico.

## 🏗️ Métodos de Clase vs Métodos de Instancia vs Métodos Estáticos

### 🎯 **@staticmethod** - Métodos Estáticos

#### ¿Qué son?
Los métodos estáticos son funciones que pertenecen a una clase pero **NO** necesitan acceso a `self` (instancia) ni `cls` (clase). Se comportan como funciones normales pero están organizadas dentro de la clase por razones conceptuales.

#### ¿Cuándo usarlos?
- Cuando la función está relacionada conceptualmente con la clase
- Cuando no necesitas acceder a atributos de instancia o clase  
- Para funciones utilitarias que "pertenecen" a la clase

#### Ejemplos en nuestro sistema:

```python
# app/funciones/sesiones.py
class SesionManager:
    """Clase para manejar la sesión del usuario actual"""
    
    @staticmethod
    def establecer_usuario(usuario_data):
        """Establece el usuario actual en la sesión"""
        global _usuario_actual
        _usuario_actual = usuario_data
    
    @staticmethod
    def obtener_usuario_actual():
        """Obtiene los datos del usuario actual"""
        global _usuario_actual
        return _usuario_actual
    
    @staticmethod
    def limpiar_sesion():
        """Limpia la sesión actual"""
        global _usuario_actual
        _usuario_actual = None
```

**¿Por qué `@staticmethod` aquí?**
1. **No necesita `self`**: No hay instancias de `SesionManager`, solo funciones relacionadas
2. **No necesita `cls`**: No accede a atributos de clase
3. **Organización conceptual**: Estas funciones están relacionadas con gestión de sesiones
4. **Uso directo**: Se llaman como `SesionManager.obtener_usuario_actual()` sin instanciar

```python
# app/utils/historial.py
class GestorHistorial:
    @staticmethod
    async def agregar_actividad(tipo, descripcion, usuario="Usuario"):
        """Agregar una actividad al historial"""
        try:
            actividad = {
                'tipo': tipo,
                'descripcion': descripcion,
                'usuario': usuario,
                'timestamp': datetime.datetime.now(),
                'fecha': datetime.datetime.now().strftime("%Y-%m-%d"),
                'hora': datetime.datetime.now().strftime("%H:%M")
            }
            # Guardar en Firebase
            db.collection('historial').add(actividad)
        except Exception as error:
            print(f"Error al registrar actividad: {error}")
```

**¿Por qué `@staticmethod` para historial?**
1. **Funcionalidad pura**: Solo procesa los parámetros que recibe
2. **Sin estado**: No mantiene información entre llamadas
3. **Acceso global**: Se usa desde cualquier parte del sistema
4. **Firebase como storage**: El estado se guarda externamente

### 🏭 **@classmethod** - Métodos de Clase

#### ¿Qué son?
Los métodos de clase reciben `cls` como primer parámetro (la clase misma, no una instancia). Pueden acceder a atributos de clase y crear nuevas instancias.

#### ¿Cuándo usarlos?
- Para acceder/modificar atributos de clase
- Para crear "constructores alternativos"
- Para operaciones que afectan a toda la clase

#### Ejemplos en nuestro sistema:

```python
# app/utils/configuracion.py
class GestorConfiguracion:
    """Clase para manejar la configuración persistente de la aplicación"""
    
    _config_file = "data/configuracion.json"  # ← Atributo de clase
    _config_default = {                       # ← Atributo de clase
        "tema": "oscuro",
        "idioma": "es",
        "notificaciones": True
    }
    
    @classmethod
    def _asegurar_directorio(cls):
        """Crea el directorio data/ si no existe"""
        directorio = Path(cls._config_file).parent  # ← Usa cls para acceder a _config_file
        directorio.mkdir(exist_ok=True)
    
    @classmethod
    def cargar_configuracion(cls):
        """Carga la configuración desde el archivo JSON"""
        try:
            cls._asegurar_directorio()  # ← Llama a otro método de clase
            
            if os.path.exists(cls._config_file):  # ← Usa cls._config_file
                with open(cls._config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Fusionar con defaults para asegurar todas las claves
                    for clave, valor_default in cls._config_default.items():
                        if clave not in config:
                            config[clave] = valor_default
                    return config
            else:
                return cls._config_default.copy()  # ← Usa cls._config_default
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
            return cls._config_default.copy()
```

**¿Por qué `@classmethod` aquí?**
1. **Acceso a atributos de clase**: Necesita `_config_file` y `_config_default`
2. **Operaciones a nivel de clase**: La configuración es global, no por instancia
3. **Sin instancias necesarias**: Se usa como `GestorConfiguracion.cargar_configuracion()`
4. **Consistencia**: Todos los métodos operan sobre los mismos archivos/rutas

```python
# app/utils/configuracion.py
class GestorConfiguracionUsuario:
    """Clase para manejar la configuración específica por usuario"""
    
    _config_default = {  # ← Atributo de clase compartido
        "tema": "oscuro",
        "notificaciones": True,
        "mostrar_ayuda": True,
        "vista_compacta": False
    }
    
    @classmethod
    def _obtener_archivo_config(cls, usuario_id):
        """Obtiene la ruta del archivo de configuración para un usuario específico"""
        return f"data/config_usuario_{usuario_id}.json"
    
    @classmethod
    def cargar_configuracion_usuario(cls, usuario_id):
        """Carga la configuración específica de un usuario"""
        try:
            cls._asegurar_directorio()  # ← Método de clase
            config_file = cls._obtener_archivo_config(usuario_id)  # ← Método de clase
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Asegurar que todas las claves necesarias existen
                    for clave, valor_default in cls._config_default.items():
                        if clave not in config:
                            config[clave] = valor_default
                    return config
            else:
                config_default = cls._config_default.copy()
                cls.guardar_configuracion_usuario(usuario_id, config_default)
                return config_default
        except Exception as e:
            print(f"Error al cargar configuración del usuario {usuario_id}: {e}")
            return cls._config_default.copy()
```

**¿Por qué `@classmethod` para configuración de usuarios?**
1. **Template compartido**: `_config_default` es usado por todos los usuarios
2. **Factory de archivos**: Genera rutas específicas por usuario
3. **Operaciones batch**: Puede crear configuraciones para múltiples usuarios
4. **Herencia**: Si extendemos la clase, los métodos siguen funcionando

### 🏃‍♀️ **Métodos de Instancia** (sin decorador)

#### ¿Qué son?
Los métodos normales que reciben `self` como primer parámetro. Pueden acceder y modificar atributos de la instancia específica.

#### ¿Cuándo usarlos?
- Cuando necesitas trabajar con datos específicos de una instancia
- Para modificar el estado del objeto
- Para comportamiento que varía entre instancias

#### Ejemplo conceptual (no usado en nuestro sistema actual):

```python
class Producto:
    def __init__(self, nombre, precio):
        self.nombre = nombre    # ← Atributo de instancia
        self.precio = precio   # ← Atributo de instancia
    
    def aplicar_descuento(self, porcentaje):  # ← Método de instancia
        """Aplica descuento a ESTE producto específico"""
        self.precio = self.precio * (1 - porcentaje/100)
        return self.precio
    
    def obtener_info(self):  # ← Método de instancia
        """Obtiene información de ESTE producto"""
        return f"{self.nombre}: ${self.precio}"

# Uso:
producto1 = Producto("Laptop", 1000)
producto2 = Producto("Mouse", 50)

producto1.aplicar_descuento(10)  # Solo afecta a producto1
print(producto1.obtener_info())  # "Laptop: $900"
print(producto2.obtener_info())  # "Mouse: $50" (sin cambios)
```

**¿Por qué NO usamos métodos de instancia en nuestro sistema?**
- **Arquitectura funcional**: Preferimos funciones stateless
- **Firebase como estado**: El estado se mantiene en la base de datos
- **Simplicidad**: Evitamos crear objetos innecesarios en memoria

---

## 🔧 Funciones Built-in de Python Utilizadas

### 1. **`global`** - Variables Globales

```python
# app/funciones/sesiones.py
_usuario_actual = None  # ← Variable global

class SesionManager:
    @staticmethod
    def establecer_usuario(usuario_data):
        global _usuario_actual  # ← Modificar variable global
        _usuario_actual = usuario_data
```

**¿Por qué usar `global`?**
- **Estado de sesión único**: Solo puede haber un usuario logueado a la vez
- **Acceso desde cualquier módulo**: Cualquier parte del sistema puede consultar la sesión
- **Simplicidad**: Evita pasar el usuario como parámetro en cada función

**⚠️ Advertencia**: Las variables globales pueden hacer el código más difícil de testear y debuggear. Usarlas con moderación.

### 2. **`async/await`** - Programación Asíncrona

```python
# app/utils/historial.py
class GestorHistorial:
    @staticmethod
    async def agregar_actividad(tipo, descripcion, usuario="Usuario"):
        """Agregar una actividad al historial"""
        try:
            # ... código ...
            # Guardar en Firebase (operación de red)
            db.collection('historial').add(actividad)
        except Exception as error:
            print(f"Error al registrar actividad: {error}")
```

**¿Por qué `async`?**
- **Operaciones de red**: Firebase requiere tiempo de respuesta
- **UI no bloqueante**: La interfaz sigue respondiendo mientras se guarda
- **Mejor experiencia**: El usuario no ve "congelamiento" de la app

**¿Cuándo usar `async`?**
- Operaciones de red (Firebase, APIs)
- Lectura/escritura de archivos grandes
- Operaciones que toman tiempo (importar Excel)

**¿Los métodos síncronos para qué?**
```python
@staticmethod
def obtener_productos_stock_bajo(limite=5):
    """Obtener productos con stock bajo desde Firebase"""
    # Este método NO es async porque se usa en contextos síncronos
    # donde no podemos esperar (await)
```

### 3. **`**kwargs`** - Argumentos de Palabra Clave

```python
# app/utils/configuracion.py
@classmethod
def actualizar_configuracion(cls, **kwargs):
    """
    Actualizar múltiples valores de configuración.
    Ejemplo: actualizar_configuracion(tema="azul", notificaciones=False)
    """
    config = cls.cargar_configuracion()
    config.update(kwargs)  # ← kwargs se convierte en diccionario
    return cls.guardar_configuracion(config)
```

**¿Por qué `**kwargs`?**
- **Flexibilidad**: Permite pasar cualquier cantidad de parámetros
- **API limpia**: `actualizar_configuracion(tema="azul", idioma="en")`
- **Extensibilidad**: Agregar nuevas opciones sin cambiar la función

### 4. **`try/except/finally`** - Manejo de Errores

```python
# Patrón usado en todo el sistema
try:
    # Operación que puede fallar
    resultado = operacion_riesgosa()
    
except SpecificException as e:
    # Manejo específico de un tipo de error
    print(f"Error específico: {e}")
    
except Exception as e:
    # Manejo general para cualquier error
    print(f"Error general: {e}")
    
finally:
    # Código que SIEMPRE se ejecuta (limpieza)
    cleanup_resources()
```

**Niveles de manejo de errores en nuestro sistema:**

1. **Nivel específico**: Capturar errores conocidos
```python
except FileNotFoundError:
    # Crear archivo con valores default
    return cls._config_default.copy()
```

2. **Nivel general**: Capturar cualquier error
```python
except Exception as e:
    print(f"Error inesperado: {e}")
    return None
```

3. **Nivel de limpieza**: Garantizar liberación de recursos
```python
finally:
    page.update()  # Siempre actualizar la UI
```

### 5. **`with`** - Context Managers

```python
# app/utils/configuracion.py
with open(cls._config_file, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=4, ensure_ascii=False)
```

**¿Por qué usar `with`?**
- **Cierre automático**: El archivo se cierra automáticamente
- **Manejo de errores**: Si hay excepción, el archivo se cierra igual
- **Código más limpio**: No necesitas recordar hacer `f.close()`

### 6. **`lambda`** - Funciones Anónimas

```python
# app/ui/principal.py - Sistema de navegación
menu_items = [
    ("Inicio", ft.Icons.DASHBOARD, lambda: vista_inicio_modular(...)),
    ("Inventario", ft.Icons.INVENTORY, lambda: vista_inventario_modular(...)),
    ("Usuarios", ft.Icons.PEOPLE, lambda: vista_usuarios_modular(...)),
]
```

**¿Por qué `lambda`?**
- **Callbacks simples**: Para funciones de una sola línea
- **Captura de variables**: `lambda e, idx=i: toggle_pendiente(idx)`
- **Código más conciso**: Evita definir funciones separadas

**Comparación:**
```python
# Con lambda (conciso)
boton = ft.Button("Click", on_click=lambda e: print("Clicked"))

# Sin lambda (más verboso)
def handle_click(e):
    print("Clicked")

boton = ft.Button("Click", on_click=handle_click)
```

### 7. **List Comprehensions** - Comprensiones de Lista

```python
# app/tablas/ui_tabla_productos.py
rows=[
    ft.DataRow(
        cells=[
            ft.DataCell(ft.Text(str(producto.get('modelo')), color=tema.TEXT_COLOR)),
            # ... más celdas ...
        ]
    ) for producto in productos  # ← List comprehension
]
```

**¿Por qué list comprehensions?**
- **Más pythónico**: Código más legible y eficiente
- **Menos líneas**: Evita bucles for explícitos
- **Mejor rendimiento**: Optimizado internamente por Python

**Comparación:**
```python
# Con list comprehension (pythónico)
rows = [crear_fila(producto) for producto in productos]

# Con bucle tradicional (más verboso)
rows = []
for producto in productos:
    rows.append(crear_fila(producto))
```

### 8. **`f-strings`** - Formateo de Strings

```python
# Usado extensivamente en el sistema
descripcion = f"Creó producto '{nombre}' (Modelo: {modelo})"
archivo_config = f"data/config_usuario_{usuario_id}.json"
mensaje_error = f"Error al cargar producto: {str(e)}"
```

**¿Por qué f-strings?**
- **Más legible**: Variables directamente en el string
- **Mejor rendimiento**: Más rápido que `.format()` o `%`
- **Expresiones**: Puedes poner código: `f"Total: {precio * cantidad}"`

---

## 🎨 Decoradores Personalizados (Conceptos Avanzados)

### ¿Qué son los decoradores?
Los decoradores son funciones que modifican o extienden el comportamiento de otras funciones. `@staticmethod` y `@classmethod` son decoradores built-in.

### Ejemplo de decorador personalizado que podríamos usar:

```python
# Decorador para logging automático
def log_actividad(tipo_actividad):
    def decorador(func):
        async def wrapper(*args, **kwargs):
            # Ejecutar función original
            resultado = await func(*args, **kwargs)
            
            # Log automático
            await GestorHistorial.agregar_actividad(
                tipo=tipo_actividad,
                descripcion=f"Ejecutó {func.__name__}",
                usuario=SesionManager.obtener_usuario_actual()
            )
            
            return resultado
        return wrapper
    return decorador

# Uso:
@log_actividad("crear_producto")
async def crear_producto(...):
    # Código de crear producto
    # El log se hace automáticamente
```

---

## 🔍 Introspección de Python

### `__name__` y `__main__`

```python
# En utils_limpieza_usuarios.py
if __name__ == "__main__":
    # Código que solo se ejecuta si el archivo se ejecuta directamente
    # No se ejecuta si se importa como módulo
    main()
```

**¿Por qué usar esto?**
- **Módulo vs Script**: El archivo puede ser importado O ejecutado
- **Testing**: Permite testing sin ejecutar el main
- **Flexibilidad**: Un archivo puede ser librería y programa

### `__file__` y `__doc__`

```python
print(f"Para ejecutar la limpieza real, ejecute:")
print(f"   python {__file__} --ejecutar")  # ← __file__ es el path del archivo actual
```

---

## 🧠 Conceptos Avanzados de Python

### 1. **Closure** - Clausuras

```python
# app/ui_inicio.py
def actualizar_pendientes():
    # Esta función "captura" variables del scope exterior
    items = []
    for i, tarea in enumerate(lista_pendientes):  # ← lista_pendientes del scope exterior
        items.append(
            ft.Row([
                ft.Checkbox(
                    on_change=lambda e, idx=i: toggle_pendiente(idx)  # ← Closure: captura 'i'
                ),
                # ...
            ])
        )
```

**¿Qué es un closure?**
- Una función que "recuerda" variables del scope donde fue definida
- Útil para callbacks que necesitan acceso a variables locales

### 2. **Duck Typing** - Tipado de Pato

> "If it looks like a duck and quacks like a duck, it's a duck"

```python
# En nuestro sistema, cualquier objeto que tenga los métodos correctos
# puede ser usado, sin importar su tipo exacto

def procesar_config(config_manager):
    # No importa si es GestorConfiguracion o GestorConfiguracionUsuario
    # Si tiene cargar_configuracion(), funciona
    config = config_manager.cargar_configuracion()
    return config
```

### 3. **Monkey Patching** (No usado, pero importante conocer)

```python
# Modificar clases en tiempo de ejecución (¡PELIGROSO!)
import datetime

# Agregar método a clase existente
datetime.datetime.to_spanish = lambda self: self.strftime("%d de %B de %Y")

# Ahora TODOS los datetime tienen este método
fecha = datetime.datetime.now()
print(fecha.to_spanish())  # "15 de Enero de 2024"
```

**¿Por qué NO lo usamos?**
- **Difícil de debuggear**: El código se modifica en tiempo de ejecución
- **Efectos secundarios**: Afecta a TODO el código, no solo el nuestro
- **Mantenimiento**: Muy difícil de mantener y entender

---

## 📝 Resumen: ¿Cuándo usar cada tipo de método?

### Usa `@staticmethod` cuando:
- ✅ La función está relacionada conceptualmente con la clase
- ✅ NO necesitas acceso a `self` o `cls`
- ✅ La función es "pura" (mismo input → mismo output)
- ✅ Quieres organizar funciones relacionadas

**Ejemplo**: `SesionManager.obtener_usuario_actual()`

### Usa `@classmethod` cuando:
- ✅ Necesitas acceder a atributos de clase
- ✅ Quieres crear "constructores alternativos"
- ✅ La operación afecta a toda la clase, no a instancias específicas
- ✅ Trabajas con configuración o factory methods

**Ejemplo**: `GestorConfiguracion.cargar_configuracion()`

### Usa métodos de instancia cuando:
- ✅ Necesitas acceder/modificar atributos de la instancia
- ✅ El comportamiento varía entre instancias
- ✅ Trabajas con estado mutable por objeto

**Ejemplo**: `producto.aplicar_descuento(10)` (cada producto es diferente)

---

## 🚀 Consejos para el Futuro

### 1. **Type Hints** (Recomendado para proyectos grandes)
```python
from typing import Dict, List, Optional

@classmethod
def cargar_configuracion(cls) -> Dict[str, any]:
    """Carga la configuración desde el archivo JSON"""
    # ...

@staticmethod
async def agregar_actividad(
    tipo: str, 
    descripcion: str, 
    usuario: str = "Usuario"
) -> None:
    """Agregar una actividad al historial"""
    # ...
```

### 2. **Docstrings consistentes**
```python
def funcion_ejemplo(param1: str, param2: int = 0) -> bool:
    """
    Descripción breve de la función.
    
    Args:
        param1 (str): Descripción del parámetro 1
        param2 (int, optional): Descripción del parámetro 2. Defaults to 0.
    
    Returns:
        bool: Descripción de lo que retorna
    
    Raises:
        ValueError: Cuándo se lanza esta excepción
    """
    pass
```

### 3. **Logging profesional** (en lugar de print)
```python
import logging

logger = logging.getLogger(__name__)

@staticmethod
async def agregar_actividad(tipo, descripcion, usuario="Usuario"):
    try:
        # ... código ...
        logger.info(f"Actividad registrada: {descripcion}")
    except Exception as error:
        logger.error(f"Error al registrar actividad: {error}")
```

---

*Esta documentación cubre las funciones reservadas y conceptos avanzados de Python utilizados en TotalStock. Entender estos conceptos te permitirá escribir código más limpio, eficiente y mantenible.*
