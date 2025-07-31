# 📚 Documentación Completa del Sistema TotalStock

## 🎯 Descripción General

TotalStock es un sistema de gestión de inventario desarrollado en Python usando el framework **Flet** para la interfaz gráfica y **Firebase Firestore** como base de datos. El sistema permite gestionar productos, usuarios, ubicaciones, movimientos de inventario, y generar reportes completos con un historial detallado de actividades.

## 🚀 Funcionalidades Principales

- **👥 Gestión de Usuarios**: Registro, autenticación y administración de usuarios
- **📦 Gestión de Inventario**: CRUD completo de productos con categorías
- **📍 Sistema de Ubicaciones**: Gestión de almacenes, estantes y ubicaciones específicas
- **🔄 Movimientos de Productos**: Transferencias entre ubicaciones con historial detallado
- **📊 Sistema de Reportes**: 8 tipos de reportes con filtros y exportación
- **🎨 Temas Personalizables**: Tema Oscuro y Tema Azul por usuario
- **📂 Importación Excel**: Carga masiva de datos desde archivos Excel
- **🔍 Búsqueda Avanzada**: Filtros y búsquedas en tiempo real
- **📈 Dashboard**: Vista general del estado del sistema
- **💾 Exportación**: Reportes en formato JSON estructurado

## 🏗️ Arquitectura del Sistema

### 📁 Estructura de Directorios

```
TotalStock/
├── app/                           # Aplicación principal
│   ├── __init__.py               # Inicializador del paquete app
│   ├── main.py                   # Punto de entrada de la aplicación
│   ├── data.py                   # Funciones de datos (legacy)
│   ├── ui_*.py                   # Módulos de interfaz por sección
│   │
│   ├── crud_productos/           # Operaciones CRUD para productos
│   │   ├── create_producto.py    # Crear productos
│   │   ├── edit_producto.py      # Editar productos
│   │   ├── delete_producto.py    # Eliminar productos
│   │   └── search_producto.py    # Buscar productos
│   │
│   ├── crud_usuarios/            # Operaciones CRUD para usuarios
│   │   ├── create_usuarios.py    # Crear usuarios
│   │   ├── delete_usuarios.py    # Eliminar usuarios (con limpieza)
│   │   └── search_usuarios.py    # Buscar usuarios
│   │
│   ├── funciones/                # Funciones utilitarias
│   │   ├── carga_archivos.py     # Importación de archivos Excel
│   │   └── sesiones.py           # Gestión de sesiones de usuario
│   │
│   ├── tablas/                   # Componentes de tabla
│   │   ├── ui_tabla_productos.py # Tabla de productos
│   │   └── ui_tabla_usuarios.py  # Tabla de usuarios
│   │
│   ├── ui/                       # Componentes de interfaz principales
│   │   ├── barra_carga.py        # Componente de carga
│   │   ├── login.py              # Pantalla de login
│   │   └── principal.py          # Pantalla principal
│   │
│   └── utils/                    # Utilidades del sistema
│       ├── configuracion.py      # Gestión de configuración
│       ├── historial.py          # Gestión de historial
│       └── temas.py              # Gestión de temas
│
├── conexiones/                   # Conexiones externas
│   ├── firebase.py              # Configuración de Firebase
│   └── credenciales_firebase.json
│
├── data/                        # Archivos de datos locales
│   ├── config_usuario_*.json    # Configuraciones por usuario
│   ├── pendientes_*.json        # Pendientes por usuario
│   └── configuracion.json       # Configuración global
│
├── assets/                      # Recursos multimedia
│   └── logo.png
│
└── tests/                       # Archivos de prueba
    └── Inventario.xlsx
```

## 🧩 Componentes Principales

### 1. Sistema de Autenticación y Sesiones

#### **SesionManager** (`app/funciones/sesiones.py`)
```python
class SesionManager:
    """Clase para manejar la sesión del usuario actual"""
    
    @staticmethod
    def establecer_usuario(usuario_data):
        """Establece el usuario actual en la sesión"""
    
    @staticmethod
    def obtener_usuario_actual():
        """Obtiene los datos del usuario actual"""
    
    @staticmethod
    def limpiar_sesion():
        """Limpia la sesión actual"""
```

**¿Por qué usar métodos estáticos (@staticmethod)?**
- Los métodos estáticos no necesitan acceso a `self` ni `cls`
- Se comportan como funciones normales pero están organizadas dentro de la clase
- No requieren instanciar la clase para usarlos: `SesionManager.obtener_usuario_actual()`
- Son ideales para funciones utilitarias que están relacionadas conceptualmente con la clase

### 2. Sistema de Gestión de Configuración

#### **GestorConfiguracion** (`app/utils/configuracion.py`)
```python
class GestorConfiguracion:
    """Clase para manejar la configuración persistente de la aplicación"""
    
    _config_file = "data/configuracion.json"
    _config_default = {
        "tema": "oscuro",
        "idioma": "es",
        "notificaciones": True,
        "auto_backup": False,
        "ultima_actualizacion": None
    }
    
    @classmethod
    def cargar_configuracion(cls):
        """Carga la configuración desde el archivo JSON"""
    
    @classmethod
    def guardar_configuracion(cls, config):
        """Guarda la configuración en el archivo JSON"""
```

**¿Por qué usar métodos de clase (@classmethod)?**
- Los métodos de clase reciben `cls` como primer parámetro (la clase misma)
- Pueden acceder a atributos de clase como `_config_file`
- Se usan cuando la operación está relacionada con la clase pero no necesita una instancia específica
- Permiten crear "constructores alternativos" o métodos que operan a nivel de clase

#### **GestorConfiguracionUsuario** (`app/utils/configuracion.py`)
```python
class GestorConfiguracionUsuario:
    """Clase para manejar la configuración específica por usuario"""
    
    @classmethod
    def _obtener_archivo_config(cls, usuario_id):
        """Obtiene la ruta del archivo de configuración para un usuario específico"""
        return f"data/config_usuario_{usuario_id}.json"
    
    @classmethod
    def cargar_configuracion_usuario(cls, usuario_id):
        """Carga la configuración específica de un usuario"""
    
    @classmethod
    def guardar_configuracion_usuario(cls, usuario_id, config):
        """Guarda la configuración específica de un usuario"""
```

### 3. Sistema de Gestión de Temas

#### **GestorTemas** (`app/utils/temas.py`)
```python
class GestorTemas:
    """Clase para manejar el tema actual de la aplicación"""
    
    _tema_actual = None
    _tema_login = None
    
    @classmethod
    def obtener_tema(cls):
        """Obtiene el tema actual aplicado"""
    
    @classmethod
    def cambiar_tema(cls, nuevo_tema):
        """Cambia el tema y lo guarda según el contexto (login/usuario)"""
    
    @classmethod
    def cambiar_tema_login(cls, nuevo_tema):
        """Cambia el tema específicamente para el login"""
```

**Arquitectura Dual de Temas:**
- **Tema de Login**: Se guarda globalmente en la PC (para todos los usuarios)
- **Tema de Usuario**: Se guarda individualmente para cada usuario logueado
- **Cache en Memoria**: Uso de `_tema_actual` para evitar lecturas constantes de archivos

### 4. Sistema de Historial de Actividades

#### **GestorHistorial** (`app/utils/historial.py`)
```python
class GestorHistorial:
    @staticmethod
    async def agregar_actividad(tipo, descripcion, usuario="Usuario"):
        """Agregar una actividad al historial"""
        
    @staticmethod
    async def obtener_actividades_recientes(limite=10):
        """Obtener las actividades más recientes"""
        
    @staticmethod
    async def obtener_estadisticas_hoy():
        """Obtener estadísticas del día actual"""
        
    @staticmethod
    def obtener_productos_stock_bajo(limite=5):
        """Obtener productos con stock bajo desde Firebase"""
```

**¿Por qué algunos métodos son async y otros no?**
- `async`: Operaciones que interactúan con Firebase (red/I/O)
- `sync`: Operaciones que solo procesan datos en memoria

## 🎨 Sistema de Interfaz de Usuario (Flet)

### Conceptos Clave de Flet

#### **Page** - La Ventana Principal
```python
async def main(page: ft.Page):
    page.title = "TotalStock"
    page.bgcolor = tema.BG_COLOR
    page.window.maximized = True
```

#### **Controls** - Componentes de UI
- **ft.Container**: Caja contenedora con propiedades visuales
- **ft.Column**: Organiza elementos verticalmente
- **ft.Row**: Organiza elementos horizontalmente
- **ft.Text**: Texto con estilos
- **ft.TextField**: Campo de entrada de texto
- **ft.ElevatedButton**: Botón elevado
- **ft.DataTable**: Tabla de datos
- **ft.AlertDialog**: Diálogo modal

#### **Responsive Design**
```python
# Cálculos responsivos basados en tamaño de pantalla
ancho_ventana = page.window.width or 1200
alto_ventana = page.window.height or 800

# Adaptación de componentes
ancho_tarjeta = min(400, ancho_ventana * 0.85)
ancho_boton = min(200, ancho_tarjeta * 0.6)
```

### Sistema de Navegación Modular

#### **Estructura de Navegación**
```python
# En app/ui/principal.py
menu_items = [
    ("Inicio", ft.Icons.DASHBOARD, lambda: vista_inicio_modular(...)),
    ("Inventario", ft.Icons.INVENTORY, lambda: vista_inventario_modular(...)),
    ("Usuarios", ft.Icons.PEOPLE, lambda: vista_usuarios_modular(...)),
    ("Configuración", ft.Icons.SETTINGS, lambda: vista_configuracion(...)),
]
```

#### **Control de Acceso por Roles**
```python
def crear_menu_item(nombre, icono, callback, deshabilitado=False):
    """Crear elemento de menú con posible deshabilitación"""
    if deshabilitado:
        # Mostrar con candado y deshabilitado
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LOCK, color=tema.ERROR_COLOR, size=16),
                ft.Text(nombre, color=tema.TEXT_SECONDARY)
            ])
        )
    else:
        # Elemento normal funcional
        return ft.Container(
            content=ft.Row([
                ft.Icon(icono, color=tema.PRIMARY_COLOR),
                ft.Text(nombre, color=tema.TEXT_COLOR)
            ]),
            on_click=callback
        )
```

## 🔄 Operaciones CRUD

### Productos

#### **Crear Producto**
```python
async def crear_producto_firebase(modelo, tipo, nombre, precio, cantidad):
    """Crear un nuevo producto en Firebase"""
    try:
        producto_data = {
            'modelo': modelo,
            'tipo': tipo,
            'nombre': nombre,
            'precio': precio,
            'cantidad': cantidad,
            'fecha_creacion': datetime.now()
        }
        
        # Guardar en Firebase
        doc_ref = db.collection('productos').add(producto_data)
        
        # Registrar en historial
        await GestorHistorial.agregar_actividad(
            tipo="crear_producto",
            descripcion=f"Creó producto '{nombre}' (Modelo: {modelo})"
        )
        
        return True
    except Exception as e:
        print(f"Error al crear producto: {e}")
        return False
```

#### **Editar Producto**
```python
async def on_click_editar_producto(page, producto_id, actualizar_tabla):
    """Muestra la ventana de edición de producto"""
    
    # 1. Cargar datos actuales del producto
    producto_ref = db.collection('productos').document(producto_id)
    producto_data = producto_ref.get().to_dict()
    
    # 2. Crear formulario con valores pre-cargados
    campo_modelo = ft.TextField(
        label="Modelo", 
        value=producto_data.get('modelo', ''),
        # ... configuración de estilo
    )
    
    # 3. Función para guardar cambios
    async def guardar_cambios(e):
        try:
            # Validar datos
            # Actualizar en Firebase
            # Registrar en historial
            # Mostrar confirmación
        except Exception as e:
            # Manejar errores
    
    # 4. Crear y mostrar diálogo
    vista_editar = ft.AlertDialog(
        title=ft.Text("Editar Producto"),
        content=ft.Container(content=ft.Column([...])),
        actions=[...]
    )
    
    page.open(vista_editar)
```

### Usuarios

#### **Eliminar Usuario con Limpieza Automática**
```python
def limpiar_archivos_usuario(id_usuario, nombre_usuario=None):
    """Elimina archivos relacionados con un usuario específico"""
    
    archivos_a_eliminar = [
        f"data/config_usuario_{id_usuario}.json",
        f"data/pendientes_{id_usuario}.json",
    ]
    
    archivos_eliminados = []
    errores = []
    
    for archivo in archivos_a_eliminar:
        try:
            if os.path.exists(archivo):
                os.remove(archivo)
                archivos_eliminados.append(archivo)
                print(f"✅ Archivo eliminado: {archivo}")
        except Exception as e:
            errores.append(f"Error al eliminar {archivo}: {str(e)}")
    
    return {
        "archivos_eliminados": archivos_eliminados,
        "errores": errores,
        "total_eliminados": len(archivos_eliminados),
        "total_errores": len(errores)
    }
```

## 🔥 Integración con Firebase

### Configuración
```python
# conexiones/firebase.py
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializar Firebase
cred = credentials.Certificate("conexiones/credenciales_firebase.json")
firebase_admin.initialize_app(cred)

# Obtener cliente de Firestore
db = firestore.client()
```

### Operaciones Comunes
```python
# Crear documento
db.collection('productos').add(data)

# Leer documento
doc = db.collection('productos').document(id).get()
data = doc.to_dict()

# Actualizar documento
db.collection('productos').document(id).update(data)

# Eliminar documento
db.collection('productos').document(id).delete()

# Consultas
productos = db.collection('productos').where('cantidad', '<', 10).get()
```

## 📊 Sistema de Persistencia Local

### Gestión de Archivos JSON

#### **Pendientes por Usuario**
```python
# Estructura: data/pendientes_{usuario_id}.json
{
    "pendientes": [
        {
            "texto": "Revisar inventario",
            "completada": false,
            "fecha_creacion": "2024-01-15"
        }
    ]
}
```

#### **Configuración por Usuario**
```python
# Estructura: data/config_usuario_{usuario_id}.json
{
    "tema": "oscuro",
    "notificaciones": true,
    "mostrar_ayuda": true,
    "vista_compacta": false
}
```

## 🎯 Patrones de Diseño Utilizados

### 1. **Singleton Pattern** (Patrón Singleton)
```python
class SesionManager:
    # Variable global única para almacenar la sesión
    _usuario_actual = None
    
    @staticmethod
    def establecer_usuario(usuario_data):
        global _usuario_actual
        _usuario_actual = usuario_data
```

### 2. **Factory Pattern** (Patrón Factoría)
```python
class GestorTemas:
    @classmethod
    def obtener_tema(cls):
        # Factory que retorna la instancia correcta de tema
        if cls._tema_actual == "azul":
            return TemaAzul()
        else:
            return TemaOscuro()
```

### 3. **Strategy Pattern** (Patrón Estrategia)
```python
# Diferentes estrategias de configuración según el contexto
def cambiar_tema(cls, nuevo_tema):
    usuario_actual = SesionManager.obtener_usuario_actual()
    if usuario_actual:
        # Estrategia: Configuración por usuario
        GestorConfiguracionUsuario.cambiar_tema_usuario(usuario_id, nuevo_tema)
    else:
        # Estrategia: Configuración global (login)
        GestorConfiguracion.cambiar_tema(nuevo_tema)
```

## 🔧 Manejo de Errores y Logging

### Patrones de Manejo de Errores
```python
try:
    # Operación que puede fallar
    resultado = operacion_riesgosa()
    
except SpecificException as e:
    # Manejo específico
    print(f"Error específico: {e}")
    
except Exception as e:
    # Manejo general
    print(f"Error general: {e}")
    
finally:
    # Limpieza siempre ejecutada
    cleanup()
```

### Sistema de Logging de Actividades
```python
# Registro automático de actividades
await GestorHistorial.agregar_actividad(
    tipo="crear_producto",  # Categoría
    descripcion=f"Creó producto '{nombre}'",  # Descripción detallada
    usuario=usuario_actual.get('username', 'Sistema')  # Usuario responsable
)
```

## 🚀 Características Avanzadas

### 1. **Sistema de Limpieza Automática**
- Elimina automáticamente archivos de usuarios eliminados
- Mantiene la integridad del sistema
- Incluye utilidades de mantenimiento

### 2. **Temas Personalizados por Usuario**
- Cada usuario puede tener su tema preferido
- Persistencia individual de preferencias
- Tema global para pantalla de login

### 3. **Control de Acceso Basado en Roles**
- Usuarios administradores vs usuarios normales
- Restricción visual y funcional de módulos
- Feedback claro sobre permisos

### 4. **Responsive Design**
- Adaptación automática a diferentes tamaños de pantalla
- Optimización para laptops y monitores grandes
- Cálculos dinámicos de dimensiones

### 5. **Importación Masiva de Datos**
- Soporte para archivos Excel
- Validación de datos
- Feedback de progreso con barra de carga

## 📈 Métricas y Estadísticas

### Dashboard de Inicio
- **Productos con menor stock**: Top 5 productos con inventario bajo
- **Estadísticas del día**: Conteo de operaciones realizadas
- **Historial de actividades**: Últimas 10 actividades del sistema
- **Pendientes personales**: Lista de tareas por usuario

### Tipos de Estadísticas Recolectadas
- Productos creados, editados, eliminados
- Usuarios creados, eliminados
- Importaciones realizadas
- Actividades por día/usuario

## 🔒 Seguridad y Privacidad

### Autenticación
- Validación de credenciales contra Firebase
- Gestión de sesiones segura
- Cierre de sesión automático

### Privacidad de Datos
- Limpieza automática de datos personales al eliminar usuarios
- Configuraciones separadas por usuario
- No persistencia de contraseñas en archivos locales

### Control de Acceso
- Validación de permisos antes de mostrar funcionalidades
- Bloqueo visual y funcional de módulos restringidos
- Logging de todas las acciones para auditoría

## 🆕 Nuevos Módulos Implementados

### 📍 Módulo de Ubicaciones (ui_ubicaciones.py)
Sistema completo de gestión de ubicaciones físicas de productos:

**Características Principales:**
- **Gestión de Almacenes**: Control de múltiples almacenes con identificación única
- **Ubicaciones Específicas**: Posicionamiento detallado (estantes, niveles, cajones)
- **Importación Excel**: Carga masiva de ubicaciones desde archivos Excel
- **Búsqueda Avanzada**: Filtros por almacén, ubicación y estado
- **Integración Firebase**: Sincronización en tiempo real con la base de datos

**Estructura de Datos:**
```python
ubicacion_data = {
    "almacen": "Almacén Principal",
    "ubicacion": "Estante A-3, Nivel 2",
    "descripcion": "Ubicación para equipos de cómputo",
    "capacidad_maxima": 50,
    "productos_actuales": [
        {"modelo": "LAP001", "cantidad": 15},
        {"modelo": "MON001", "cantidad": 8}
    ],
    "fecha_creacion": datetime.now(),
    "usuario_creacion": "Admin"
}
```

### 🚚 Módulo de Movimientos (ui_movimientos.py)
Interfaz intuitiva para transferencias de productos entre ubicaciones:

**Características Principales:**
- **Búsqueda de Productos**: Localización rápida por modelo o nombre
- **Workflow Visual**: Interface de dos columnas (origen → destino)
- **Selección de Destino**: Selectores visuales de almacenes con iconos distintivos
- **Validación de Cantidad**: Control de stock disponible y límites
- **Registro de Historial**: Seguimiento completo de movimientos con timestamp
- **Confirmación Visual**: Feedback inmediato de operaciones exitosas

**Flujo de Operación:**
```python
# 1. Búsqueda de producto
termino_busqueda → productos_disponibles → seleccion_producto

# 2. Configuración de movimiento
ubicacion_origen + ubicacion_destino + cantidad + motivo

# 3. Validación y ejecución
validar_stock() → ejecutar_movimiento() → registrar_historial()

# 4. Actualización de datos
actualizar_firebase() → mostrar_confirmacion() → limpiar_formulario()
```

### 📊 Módulo de Reportes (ui_reportes.py)
Sistema completo de generación de reportes empresariales:

**8 Tipos de Reportes Disponibles:**

1. **Reportes de Movimientos**
   - Historial completo de transferencias
   - Filtros por fecha, usuario y tipo de movimiento
   - Detalles: fecha/hora, usuario, producto, cantidades, ubicaciones, motivos

2. **Estado de Ubicaciones**
   - Inventario actual por ubicación
   - Capacidad utilizada vs. disponible
   - Productos almacenados por ubicación
   - Última actualización y usuario responsable

3. **Inventario de Productos**
   - Stock actual, mínimo y máximo
   - Múltiples ubicaciones por producto
   - Valores monetarios totales
   - Estado y fecha de ingreso

4. **Altas de Productos**
   - Productos dados de alta en el sistema
   - Información de proveedores
   - Valores de inversión inicial
   - Ubicaciones de asignación

5. **Bajas de Productos**
   - Productos retirados del sistema
   - Motivos de baja (obsolescencia, daño, etc.)
   - Valores perdidos
   - Estados finales (desechado, reparación)

6. **Actividad de Usuarios**
   - Acciones realizadas por cada usuario
   - Duración de sesiones
   - IP de origen
   - Módulos utilizados

7. **Stock Crítico**
   - Productos por debajo del stock mínimo
   - Niveles de prioridad (crítica, media, baja)
   - Días estimados sin stock
   - Acciones sugeridas

8. **Rotación de Inventario**
   - Análisis de movimiento de productos
   - Ratios de rotación mensual
   - Tendencias de uso
   - Clasificación de productos (estrella, normal, lento)

**Características del Sistema de Reportes:**
```python
# Filtros avanzados
filtros = {
    "fecha_inicio": "2024-01-01",
    "fecha_fin": "2024-01-31", 
    "usuario": "Admin",
    "tipo_reporte": "movimientos"
}

# Exportación con metadatos
datos_exportacion = {
    "metadata": {
        "tipo_reporte": "movimientos",
        "fecha_generacion": datetime.now().isoformat(),
        "total_registros": len(datos),
        "filtros_aplicados": filtros
    },
    "datos": datos_reporte
}
```

## 🔧 Funcionalidades Técnicas Avanzadas

### Sistema de Historial Mejorado
```python
# app/utils/historial.py - Versión mejorada
class GestorHistorial:
    @staticmethod
    async def obtener_historial_reciente(limite=50):
        """Obtener historial con consultas Firebase optimizadas"""
        try:
            actividades_ref = db.collection('actividades')
            query = actividades_ref.order_by(
                FieldFilter('fecha', '=='), 
                direction=firestore.Query.DESCENDING
            ).limit(limite)
            
            docs = query.stream()
            actividades = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                actividades.append(data)
            
            return actividades
        except Exception as e:
            print(f"Error al obtener historial: {e}")
            return []
```

### Gestión de Ubicaciones con Excel
```python
# app/ui_ubicaciones.py - Importación Excel
async def importar_ubicaciones_excel(archivo_excel):
    """Importar ubicaciones desde archivo Excel"""
    try:
        df = pd.read_excel(archivo_excel)
        
        # Validar columnas requeridas
        columnas_requeridas = ['almacen', 'ubicacion', 'descripcion']
        for col in columnas_requeridas:
            if col not in df.columns:
                raise ValueError(f"Falta columna requerida: {col}")
        
        # Procesar cada fila
        ubicaciones_creadas = 0
        for index, row in df.iterrows():
            ubicacion_data = {
                'almacen': row['almacen'],
                'ubicacion': row['ubicacion'],
                'descripcion': row.get('descripcion', ''),
                'capacidad_maxima': row.get('capacidad_maxima', 100),
                'fecha_creacion': datetime.now(),
                'usuario_creacion': usuario_actual
            }
            
            # Guardar en Firebase
            db.collection('ubicaciones').add(ubicacion_data)
            ubicaciones_creadas += 1
        
        return {
            'exito': True,
            'total_creadas': ubicaciones_creadas,
            'mensaje': f"Se importaron {ubicaciones_creadas} ubicaciones"
        }
        
    except Exception as e:
        return {
            'exito': False,
            'error': str(e),
            'mensaje': f"Error al importar: {str(e)}"
        }
```

### Interfaz Responsiva Mejorada
```python
# Cálculos dinámicos de dimensiones
ancho_ventana = page.window.width or 1200
alto_ventana = page.window.height or 800

# Distribución responsiva
if ancho_ventana >= 1400:
    # Pantallas grandes: 3 columnas
    columnas_layout = 3
    ancho_card = ancho_ventana * 0.28
elif ancho_ventana >= 900:
    # Pantallas medianas: 2 columnas  
    columnas_layout = 2
    ancho_card = ancho_ventana * 0.42
else:
    # Pantallas pequeñas: 1 columna
    columnas_layout = 1
    ancho_card = ancho_ventana * 0.85
```

## 🎨 Mejoras en la Experiencia de Usuario

### Feedback Visual Mejorado
```python
# Notificaciones contextuales
page.open(ft.SnackBar(
    content=ft.Text(f"✅ Movimiento registrado exitosamente", 
                   color=tema.TEXT_COLOR),
    bgcolor=tema.SUCCESS_COLOR,
    duration=ft.Duration(milliseconds=3000)
))

# Indicadores de progreso
ft.ProgressRing(color=tema.PRIMARY_COLOR, stroke_width=3)

# Estados visuales diferenciados
color_prioridad = (tema.ERROR_COLOR if item["prioridad"] == "CRÍTICA" 
                  else tema.WARNING_COLOR)
```

### Navegación Intuitiva
```python
# Workflow guiado paso a paso
workflow_steps = [
    "1. Seleccionar producto",
    "2. Confirmar ubicación origen", 
    "3. Elegir destino",
    "4. Validar cantidad",
    "5. Ejecutar movimiento"
]

# Breadcrumbs visuales
ft.Row([
    ft.Icon(ft.Icons.SEARCH, color=tema.SUCCESS_COLOR),  # Completado
    ft.Icon(ft.Icons.ARROW_FORWARD, color=tema.PRIMARY_COLOR),
    ft.Icon(ft.Icons.LOCATION_ON, color=tema.PRIMARY_COLOR),  # Actual
    ft.Icon(ft.Icons.ARROW_FORWARD, color=tema.DISABLED_COLOR),
    ft.Icon(ft.Icons.CHECK_CIRCLE, color=tema.DISABLED_COLOR)  # Pendiente
])
```

---

## � Sistema de Reportes Avanzado

### Vista de Reportes (ui_reportes.py)
Módulo completo de generación de reportes con 8 tipos diferentes y capacidades de exportación profesional.

#### **🎯 Tipos de Reportes Disponibles:**

1. **📊 Movimientos de Productos**
   - Historial detallado de transferencias entre ubicaciones
   - Filtros por fecha, usuario y tipo de movimiento
   - Incluye: origen, destino, cantidad, motivo, responsable

2. **📍 Estado de Ubicaciones** 
   - Inventario actual por almacén y ubicación específica
   - Porcentaje de capacidad utilizada
   - Última actualización y usuario responsable

3. **📦 Inventario de Productos**
   - Estado completo del stock por producto
   - Comparativa con niveles mínimos y máximos
   - Valor total del inventario y distribución por ubicaciones

4. **⬆️ Altas de Productos**
   - Productos incorporados al sistema
   - Información de proveedores y costos
   - Motivos de incorporación y ubicaciones asignadas

5. **⬇️ Bajas de Productos** 
   - Productos retirados del sistema
   - Motivos de baja (obsolescencia, daños, etc.)
   - Valor económico impactado y responsables

6. **👥 Actividad de Usuarios**
   - Historial de acciones por usuario
   - Tiempo de sesión y ubicación (IP)
   - Módulos utilizados y patrones de uso

7. **⚠️ Stock Crítico**
   - Productos con stock bajo o crítico
   - Días estimados sin stock
   - Priorización automática y acciones sugeridas

8. **🔄 Rotación de Inventario**
   - Análisis de movimiento de productos
   - Identificación de productos estrella
   - Patrones de rotación mensual y clasificación por performance

#### **🎨 Interfaz Profesional:**
```python
# Selector visual de reportes
tipos_reportes = {
    "movimientos": {
        "nombre": "Movimientos de Productos",
        "icono": ft.Icons.SWAP_HORIZ,
        "color": tema.PRIMARY_COLOR,
        "descripcion": "Reporte detallado de todos los movimientos"
    }
    # ... 7 tipos más con iconos y colores diferenciados
}
```

#### **⚡ Características Avanzadas:**
- **Filtros Temporales**: Rango de fechas personalizable
- **Filtros de Usuario**: Análisis por responsable específico
- **Exportación JSON**: Estructura completa con metadatos
- **Tablas Responsivas**: Columnas adaptadas por tipo de reporte
- **Estadísticas en Tiempo Real**: Totales, períodos y timestamps
- **Indicadores Visuales**: Colores diferenciados por prioridad
- **Performance Optimizada**: Limitación a 100 registros por tabla

#### **💾 Estructura de Exportación:**
```json
{
  "metadata": {
    "tipo_reporte": "rotacion",
    "nombre_reporte": "Rotación de Inventario", 
    "fecha_generacion": "2025-07-31T12:33:54.605235",
    "fecha_inicio": "2025-07-01",
    "fecha_fin": "2025-07-31",
    "usuario_filtro": "todos",
    "total_registros": 2
  },
  "datos": [
    {
      "modelo": "LAP001",
      "nombre": "Laptop Dell Inspiron",
      "rotacion_mensual": 0.52,
      "tendencia": "ESTABLE",
      "clasificacion": "ROTACIÓN NORMAL"
    }
  ]
}
```

---

## �📚 Próximos Pasos para Ampliar el Sistema

1. **Sistema de Backup Automático**
2. **Notificaciones Push**
3. **Reportes en PDF**
4. **API REST para integración externa**
5. **Sistema de alertas por stock bajo**
6. **Historial de cambios por producto**
7. **Dashboard de análisis avanzado**
8. **Códigos de barras/QR para productos**
9. **Sistema de reservas de productos**
10. **Integración con sistemas ERP externos**

---

*Esta documentación cubre los aspectos fundamentales del sistema TotalStock. Para información específica sobre funciones reservadas de Python y widgets de Flet, consulte los archivos complementarios de documentación.*
