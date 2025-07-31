# 🎨 Widgets de Flet - Guía Completa y Detallada

## 📚 Introducción a Flet

**Flet** es un framework de Python que permite crear aplicaciones multiplataforma (desktop, web, mobile) usando **Flutter** como motor de renderizado, pero con la simplicidad de Python. Es como tener el poder de Flutter sin necesidad de aprender Dart.

### ¿Por qué elegimos Flet para TotalStock?

1. **Python Puro**: No necesitamos aprender otro lenguaje
2. **UI Moderna**: Interfaces atractivas y responsive
3. **Multiplataforma**: Desktop, web y móvil con el mismo código
4. **Componentes Ricos**: Widgets avanzados out-of-the-box
5. **Comunidad Activa**: Framework en crecimiento con buena documentación

---

## 🏗️ Arquitectura de Flet

### **Page** - El Contenedor Principal

```python
async def main(page: ft.Page):
    # Configuración global de la página
    page.title = "TotalStock: Sistema de Inventario"
    page.bgcolor = tema.BG_COLOR
    page.theme_mode = ft.ThemeMode.DARK
    page.window.maximized = True
    page.window.resizable = True
    
    # Dimensiones mínimas responsivas
    page.window.min_width = 900
    page.window.min_height = 650
```

**Propiedades importantes de Page:**
- `title`: Título de la ventana
- `bgcolor`: Color de fondo
- `theme_mode`: Tema claro/oscuro
- `window.*`: Propiedades de la ventana (tamaño, estado)
- `controls`: Lista de widgets que se muestran

**¿Por qué configurar estas propiedades?**
- **UX consistente**: La app se ve igual en diferentes dispositivos
- **Responsive**: Se adapta a diferentes tamaños de pantalla
- **Profesional**: Da una apariencia pulida y moderna

---

## 📦 Widgets de Layout (Organización)

### 1. **ft.Container** - La Caja Universal

Es el widget más versátil de Flet. Piensa en él como una "caja" que puede contener otros widgets y tener propiedades visuales.

```python
# app/ui/principal.py - Menú lateral
ft.Container(
    content=ft.Column([...]),           # ← Contenido interno
    width=ancho_menu,                   # ← Ancho fijo
    bgcolor=tema.SIDEBAR_COLOR,         # ← Color de fondo
    padding=ft.padding.all(20),         # ← Espaciado interno
    border_radius=tema.BORDER_RADIUS,   # ← Bordes redondeados
    border=ft.border.all(1, tema.PRIMARY_COLOR),  # ← Borde
    shadow=ft.BoxShadow(                # ← Sombra
        spread_radius=1,
        blur_radius=15,
        color=ft.Colors.BLACK54,
        offset=ft.Offset(0, 4)
    )
)
```

**¿Por qué usar Container?**
- **Diseño visual**: Colores, bordes, sombras, etc.
- **Espaciado**: Padding y margin para organizar elementos
- **Responsive**: Anchos y altos adaptables
- **Contenedor**: Puede tener un solo widget hijo

**Propiedades clave:**
- `content`: Widget hijo (solo uno)
- `width/height`: Dimensiones
- `bgcolor`: Color de fondo
- `padding`: Espaciado interno
- `margin`: Espaciado externo
- `border_radius`: Bordes redondeados
- `alignment`: Alineación del contenido interno

### 2. **ft.Column** - Organización Vertical

Organiza widgets uno debajo del otro (verticalmente).

```python
# app/ui_inicio.py - Dashboard vertical
ft.Column([
    # Header con fecha
    ft.Container(
        content=ft.Row([...]),
        bgcolor=tema.CARD_COLOR,
        border_radius=8,
        margin=ft.margin.only(bottom=16)
    ),
    
    # Fila superior - productos y estadísticas
    ft.Row([...]),
    
    # Fila inferior - pendientes e historial
    ft.Row([...])
], 
alignment=ft.MainAxisAlignment.START,           # ← Alineación vertical
horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # ← Alineación horizontal
spacing=20,                                     # ← Espacio entre elementos
scroll=ft.ScrollMode.AUTO                       # ← Scroll si es necesario
)
```

**¿Por qué Column?**
- **Layout vertical**: Para listas, formularios, dashboards
- **Flexible**: Los hijos pueden expandirse o tener tamaño fijo
- **Scrollable**: Maneja contenido que no cabe en pantalla

**Propiedades importantes:**
- `controls`: Lista de widgets hijos
- `spacing`: Espacio entre elementos
- `alignment`: Alineación vertical (START, CENTER, END, SPACE_BETWEEN, etc.)
- `horizontal_alignment`: Alineación horizontal de los hijos
- `scroll`: Comportamiento de scroll
- `expand`: Si debe tomar todo el espacio disponible

### 3. **ft.Row** - Organización Horizontal

Organiza widgets lado a lado (horizontalmente).

```python
# app/ui_inventario.py - Botones de acción
ft.Row([
    ft.Container(
        content=ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD, color=tema.ICON_BTN_COLOR),
                ft.Text("Agregar Producto", color=tema.BUTTON_TEXT)
            ]),
            on_click=vista_crear_producto_llamada
        ),
        width=ancho_boton,
        padding=ft.padding.symmetric(horizontal=5, vertical=20)
    ),
    ft.Container(
        content=ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.FILE_UPLOAD, color=tema.ICON_BTN_COLOR),
                ft.Text("Importar productos", color=tema.BUTTON_TEXT)
            ]),
            on_click=lambda e: on_click_importar_archivo(page)
        ),
        width=ancho_boton,
        padding=ft.padding.symmetric(horizontal=5, vertical=20)
    )
],
alignment=ft.MainAxisAlignment.SPACE_BETWEEN,    # ← Distribución horizontal
vertical_alignment=ft.CrossAxisAlignment.CENTER  # ← Alineación vertical
)
```

**¿Por qué Row?**
- **Layout horizontal**: Para botones, controles, barras de herramientas
- **Distribución flexible**: SPACE_BETWEEN, SPACE_AROUND, CENTER, etc.
- **Responsive**: Los elementos se adaptan al ancho disponible

**Diferencia entre Column y Row:**
- **Column**: Eje principal vertical (height), eje cruzado horizontal (width)
- **Row**: Eje principal horizontal (width), eje cruzado vertical (height)

---

## 🎛️ Widgets de Input (Entrada de Datos)

### 1. **ft.TextField** - Campo de Texto

El widget más importante para capturar entrada del usuario.

```python
# app/ui/login.py - Campos de login
usuario_input = ft.TextField(
    label="Usuario",                            # ← Etiqueta flotante
    autofocus=True,                            # ← Focus automático
    bgcolor=tema.INPUT_BG,                     # ← Color de fondo
    color=tema.TEXT_COLOR,                     # ← Color del texto
    border_color=tema.INPUT_BORDER,            # ← Color del borde
    focused_border_color=tema.PRIMARY_COLOR,   # ← Color del borde al hacer focus
    label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)  # ← Estilo de la etiqueta
)

contrasena_input = ft.TextField(
    label="Contraseña",
    password=True,                             # ← Ocultar texto
    can_reveal_password=True,                  # ← Botón para mostrar/ocultar
    # ... resto de estilos igual
)
```

**¿Por qué estas propiedades?**
- `label`: Etiqueta flotante más moderna que placeholder
- `autofocus`: Mejor UX, el usuario puede empezar a escribir inmediatamente
- `bgcolor` y `color`: Consistencia visual con el tema
- `border_color`: Feedback visual del estado del campo
- `password=True`: Seguridad para campos sensibles

**Tipos de TextField:**
```python
# Campo numérico
precio_field = ft.TextField(
    label="Precio",
    keyboard_type=ft.KeyboardType.NUMBER,     # ← Teclado numérico en móvil
    input_filter=ft.NumbersOnlyInputFilter()  # ← Solo acepta números
)

# Campo multilínea
descripcion_field = ft.TextField(
    label="Descripción",
    multiline=True,                           # ← Múltiples líneas
    min_lines=3,                             # ← Altura mínima
    max_lines=5                              # ← Altura máxima
)
```

### 2. **ft.Checkbox** - Casilla de Verificación

```python
# app/ui_inicio.py - Lista de pendientes
ft.Checkbox(
    value=tarea.get('completada', False),      # ← Estado inicial
    on_change=lambda e, idx=i: toggle_pendiente(idx)  # ← Callback con closure
)

# app/crud_usuarios/create_usuarios.py - Checkbox de admin
campo_es_admin = ft.Checkbox(
    label="¿Es administrador?",                # ← Etiqueta
    value=False,                              # ← Valor por defecto
    fill_color=tema.PRIMARY_COLOR,            # ← Color cuando está marcado
    check_color=tema.BUTTON_TEXT              # ← Color del ícono de check
)
```

**¿Por qué usar Checkbox?**
- **Booleanos**: Perfecto para opciones sí/no
- **Listas de tareas**: Estado completado/pendiente
- **Configuraciones**: Opciones que se pueden activar/desactivar

### 3. **ft.Dropdown** - Lista Desplegable

```python
# Ejemplo de dropdown para categorías (no implementado aún)
categoria_dropdown = ft.Dropdown(
    label="Categoría",
    options=[
        ft.dropdown.Option("electronica", "Electrónica"),
        ft.dropdown.Option("ropa", "Ropa"),
        ft.dropdown.Option("hogar", "Hogar"),
    ],
    value="electronica",                       # ← Valor seleccionado
    on_change=lambda e: print(f"Seleccionado: {e.control.value}")
)
```

---

## 🎨 Widgets de Display (Mostrar Información)

### 1. **ft.Text** - Texto

El widget fundamental para mostrar texto.

```python
# app/ui_inicio.py - Diferentes estilos de texto
ft.Text(
    "TotalStock Dashboard",
    size=24,                                   # ← Tamaño de fuente
    weight=ft.FontWeight.BOLD,                # ← Peso de fuente
    color=tema.TEXT_COLOR,                    # ← Color
    text_align=ft.TextAlign.CENTER            # ← Alineación
)

ft.Text(
    datetime.now().strftime("%d/%m/%Y"),
    size=12,
    color=tema.TEXT_COLOR,
    italic=True                               # ← Texto en cursiva
)

# Texto condicional
ft.Text(
    ("✓ " if tarea.get('completada', False) else "") + tarea['texto'],
    expand=True,                              # ← Toma todo el espacio horizontal
    size=12,
    color=tema.SECONDARY_TEXT_COLOR if tarea.get('completada', False) else tema.TEXT_COLOR,
    italic=tarea.get('completada', False)     # ← Estilo condicional
)
```

**Propiedades de Text:**
- `value`: El texto a mostrar
- `size`: Tamaño de fuente
- `weight`: NORMAL, BOLD, W_100, W_200... W_900
- `color`: Color del texto
- `text_align`: LEFT, CENTER, RIGHT, JUSTIFY
- `italic`: Texto en cursiva
- `expand`: Si debe tomar todo el espacio disponible

### 2. **ft.Icon** - Iconos

Flet incluye todos los iconos de Material Design.

```python
# app/ui/principal.py - Iconos en menú
ft.Icon(ft.Icons.DASHBOARD, color=tema.PRIMARY_COLOR)
ft.Icon(ft.Icons.INVENTORY, color=tema.PRIMARY_COLOR)
ft.Icon(ft.Icons.PEOPLE, color=tema.PRIMARY_COLOR)

# app/ui_inicio.py - Iconos decorativos
ft.Icon(ft.Icons.INVENTORY, color=tema.WARNING_COLOR)
ft.Icon(ft.Icons.PIE_CHART, color=tema.PRIMARY_COLOR)
ft.Icon(ft.Icons.HISTORY, color=tema.SECONDARY_TEXT_COLOR)

# app/ui/principal.py - Icono de candado para usuarios sin permisos
ft.Icon(ft.Icons.LOCK, color=tema.ERROR_COLOR, size=16)
```

**¿Por qué usar iconos?**
- **Reconocimiento visual**: Los usuarios entienden iconos más rápido que texto
- **Ahorro de espacio**: Un icono comunica más que varias palabras
- **Consistencia**: Material Design es un estándar reconocido
- **Accesibilidad**: Los iconos ayudan a usuarios con diferentes idiomas

### 3. **ft.DataTable** - Tabla de Datos

Para mostrar información estructurada en formato tabular.

```python
# app/tablas/ui_tabla_productos.py
ft.DataTable(
    columns=[
        ft.DataColumn(ft.Text("Modelo", color=tema.TEXT_COLOR)),
        ft.DataColumn(ft.Text("Tipo", color=tema.TEXT_COLOR)),
        ft.DataColumn(ft.Text("Nombre", color=tema.TEXT_COLOR)),
        ft.DataColumn(ft.Text("Precio", color=tema.TEXT_COLOR)),
        ft.DataColumn(ft.Text("Cantidad", color=tema.TEXT_COLOR)),
        ft.DataColumn(ft.Text("Opciones", color=tema.TEXT_COLOR)),
    ],
    rows=[
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(producto.get('modelo')), color=tema.TEXT_COLOR)),
                ft.DataCell(ft.Text(producto.get('tipo'), color=tema.TEXT_COLOR)),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(producto.get('nombre'), color=tema.TEXT_COLOR),
                        width=300  # ← Ancho fijo para texto largo
                    )
                ),
                ft.DataCell(ft.Text(str(producto.get('precio')), color=tema.TEXT_COLOR)),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(str(producto.get('cantidad')), color=tema.TEXT_COLOR),
                        alignment=ft.alignment.center  # ← Centrar contenido
                    )
                ),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(ft.Icons.EDIT, on_click=lambda e: editar_producto()),
                        ft.IconButton(ft.Icons.DELETE, on_click=lambda e: eliminar_producto()),
                    ])
                )
            ],
            selected=False,
            on_select_changed=lambda e: print(f"Fila seleccionada: {e.data}")
        ) for producto in productos  # ← List comprehension para generar filas
    ],
    width=ancho_tabla
)
```

**Componentes de DataTable:**
- **DataColumn**: Define las columnas (headers)
- **DataRow**: Define las filas de datos
- **DataCell**: Define cada celda individual

**¿Por qué DataTable?**
- **Datos estructurados**: Perfecto para inventarios, usuarios, etc.
- **Interactividad**: Callbacks por fila, sorting, selection
- **Responsive**: Se adapta al contenido y tamaño de pantalla

### 4. **ft.ListTile** - Elemento de Lista

Para crear listas elegantes de elementos.

```python
# app/ui_inicio.py - Lista de productos con stock bajo
ft.ListTile(
    leading=ft.Container(
        content=ft.Text(str(producto['stock']), 
                       color=ft.Colors.WHITE, 
                       size=12, 
                       weight=ft.FontWeight.BOLD),
        bgcolor=tema.ERROR_COLOR if producto['stock'] < 10 else tema.WARNING_COLOR,
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=8, vertical=4)
    ),
    title=ft.Text(producto['nombre'], size=12, color=tema.TEXT_COLOR),
    subtitle=ft.Text(
        "Stock crítico" if producto['stock'] < 10 else "Stock bajo", 
        size=10, 
        color=tema.ERROR_COLOR if producto['stock'] < 10 else tema.WARNING_COLOR
    ),
    dense=True  # ← Versión más compacta
)
```

**Partes de ListTile:**
- `leading`: Widget al inicio (izquierda)
- `title`: Texto principal
- `subtitle`: Texto secundario
- `trailing`: Widget al final (derecha)
- `dense`: Versión más compacta

---

## 🔘 Widgets de Acción (Botones y Controles)

### 1. **ft.ElevatedButton** - Botón Principal

El botón más prominente, usado para acciones principales.

```python
# app/ui_inventario.py - Botón de agregar producto
ft.ElevatedButton(
    content=ft.Row([
        ft.Icon(ft.Icons.ADD, color=tema.ICON_BTN_COLOR),
        ft.Text("Agregar Producto", color=tema.BUTTON_TEXT)
    ]),
    style=ft.ButtonStyle(
        bgcolor=tema.BUTTON_BG,                # ← Color de fondo
        color=tema.BUTTON_TEXT,               # ← Color del texto
        shape=ft.RoundedRectangleBorder(      # ← Forma del botón
            radius=tema.BORDER_RADIUS
        )
    ),
    on_click=vista_crear_producto_llamada     # ← Callback al hacer click
)
```

**¿Por qué ElevatedButton?**
- **Jerarquía visual**: Se ve elevado (sombra)
- **Acción principal**: Llama la atención del usuario
- **Consistencia**: Estilo Material Design

### 2. **ft.TextButton** - Botón Secundario

Para acciones secundarias o menos importantes.

```python
# app/crud_productos/edit_producto.py - Botón cancelar
ft.TextButton(
    "Cancelar",
    style=ft.ButtonStyle(color=tema.BUTTON_ERROR_BG),
    on_click=lambda e: page.close(vista_editar)
)
```

**¿Cuándo usar TextButton?**
- Acciones secundarias (cancelar, cerrar)
- Cuando no quieres que el botón llame mucho la atención
- En diálogos para acciones menos importantes

### 3. **ft.IconButton** - Botón de Icono

Para acciones que se pueden representar con un icono.

```python
# app/tablas/ui_tabla_productos.py - Botones de acción en tabla
ft.IconButton(
    ft.Icons.EDIT,
    icon_color=tema.PRIMARY_COLOR,
    on_click=lambda e, uid=producto.get('firebase_id', ''): editar_producto(uid)
)

ft.IconButton(
    ft.Icons.DELETE,
    icon_color=tema.ERROR_COLOR,
    on_click=lambda e, uid=producto.get('firebase_id', ''): eliminar_producto(uid)
)

# app/ui_inicio.py - Botón de agregar pendiente
ft.IconButton(
    icon=ft.Icons.ADD,
    on_click=agregar_pendiente,
    icon_color=tema.PRIMARY_COLOR
)
```

**¿Por qué IconButton?**
- **Ahorro de espacio**: Solo el icono, sin texto
- **Acciones rápidas**: Editar, eliminar, agregar
- **Interfaces compactas**: Barras de herramientas, tablas

---

## 🎭 Widgets de Diálogo y Overlay

### 1. **ft.AlertDialog** - Diálogo Modal

Para confirmaciones, formularios modales, y alertas.

```python
# app/crud_productos/edit_producto.py - Diálogo de edición
vista_editar = ft.AlertDialog(
    title=ft.Text("Editar Producto", color=tema.TEXT_COLOR),
    content=ft.Container(
        content=ft.Column([
            campo_modelo,
            campo_tipo,
            campo_nombre,
            campo_precio,
            campo_cantidad,
        ], scroll=ft.ScrollMode.AUTO),
        width=ancho_dialog,
        height=alto_dialog,
    ),
    actions=[
        ft.TextButton("Cancelar", on_click=lambda e: page.close(vista_editar)),
        ft.ElevatedButton("Guardar", on_click=guardar_cambios)
    ],
    actions_alignment=ft.MainAxisAlignment.END
)

page.open(vista_editar)  # ← Mostrar el diálogo
```

**Componentes de AlertDialog:**
- `title`: Título del diálogo
- `content`: Contenido principal (puede ser cualquier widget)
- `actions`: Lista de botones de acción
- `actions_alignment`: Alineación de los botones

**¿Cuándo usar AlertDialog?**
- Confirmaciones (¿Seguro que quieres eliminar?)
- Formularios pequeños (editar producto)
- Alertas importantes
- Cualquier contenido que necesite atención inmediata

### 2. **ft.SnackBar** - Mensaje Toast

Para notificaciones temporales no intrusivas.

```python
# app/crud_productos/edit_producto.py - Confirmación de éxito
page.open(ft.SnackBar(
    content=ft.Text("Producto actualizado exitosamente", color=tema.TEXT_COLOR),
    bgcolor=tema.SUCCESS_COLOR
))

# Error
page.open(ft.SnackBar(
    content=ft.Text(f"Error al cargar producto: {str(e)}", color=tema.TEXT_COLOR),
    bgcolor=tema.ERROR_COLOR
))
```

**¿Por qué SnackBar?**
- **No intrusivo**: No bloquea la UI
- **Temporal**: Desaparece automáticamente
- **Feedback**: Confirma que una acción se completó
- **Errores**: Informa errores sin detener el flujo

---

## 🎨 Widgets de Presentación Visual

### 1. **ft.Card** - Tarjeta

Para agrupar contenido relacionado con un fondo elevado.

```python
# app/ui_inicio.py - Tarjetas del dashboard
ft.Card(
    content=ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.INVENTORY, color=tema.WARNING_COLOR),
                ft.Text("Productos con Menor Stock", 
                       weight=ft.FontWeight.BOLD, 
                       size=14, 
                       color=tema.TEXT_COLOR)
            ]),
            ft.Divider(color=tema.SECONDARY_TEXT_COLOR),
            ft.Column([
                # ... contenido de la tarjeta
            ])
        ]),
        padding=16
    ),
    color=tema.CARD_COLOR,
)
```

**¿Por qué Card?**
- **Agrupación visual**: Separa contenido relacionado
- **Elevación**: Se ve como que "flota" sobre el fondo
- **Organización**: Estructura visual clara

### 2. **ft.Divider** - Separador

Para separar visualmente secciones de contenido.

```python
# app/ui_inicio.py - Separador en tarjeta
ft.Divider(color=tema.SECONDARY_TEXT_COLOR)

# app/crud_usuarios/create_usuarios.py - Separador con color del tema
ft.Divider(color=tema.PRIMARY_COLOR)
```

**¿Cuándo usar Divider?**
- Separar secciones en formularios
- Dividir contenido en tarjetas
- Crear separación visual sin usar espacios grandes

### 3. **ft.ProgressBar** / **ft.ProgressRing** - Indicadores de Progreso

```python
# app/ui/barra_carga.py - Barra de carga
def vista_carga():
    tema = GestorTemas.obtener_tema()
    return ft.Container(
        content=ft.Column([
            ft.ProgressRing(color=tema.PRIMARY_COLOR),  # ← Indicador circular
            ft.Text("Cargando...", color=tema.TEXT_COLOR, size=16)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        alignment=ft.alignment.center,
        bgcolor=tema.BG_COLOR,
        height=300
    )
```

**¿Cuándo usar indicadores de progreso?**
- Operaciones que toman tiempo (cargar datos de Firebase)
- Importar archivos Excel
- Cualquier operación donde el usuario debe esperar

---

## 🎯 Conceptos Avanzados de Flet

### 1. **Responsive Design** - Diseño Adaptativo

```python
# app/ui/principal.py - Cálculos responsivos
ancho_ventana = page.window.width or 1200
alto_ventana = page.window.height or 800

# Ancho del menú adaptativo
if ancho_ventana < 1200:      # Laptops
    ancho_menu = 220
elif ancho_ventana < 1600:    # Monitores medianos
    ancho_menu = 250  
else:                         # Monitores grandes
    ancho_menu = 280

# Dimensiones de componentes responsivos
ancho_tarjeta = min(400, ancho_ventana * 0.85)
ancho_boton = min(200, ancho_tarjeta * 0.6)
```

**Estrategias responsive:**
- **Breakpoints**: Diferentes tamaños para diferentes dispositivos
- **Porcentajes**: Usar `ancho_ventana * 0.8` en lugar de valores fijos
- **min/max**: `min(400, calculated_width)` para límites
- **Expand**: `expand=True` para que tomen el espacio disponible

### 2. **Event Handling** - Manejo de Eventos

```python
# Diferentes tipos de callbacks

# Callback simple
on_click=lambda e: print("Clicked")

# Callback con captura de variables (closure)
on_click=lambda e, idx=i: toggle_pendiente(idx)

# Callback con función separada
async def handle_login(e):
    # ... lógica compleja
    
on_click=handle_login

# Callback condicional
on_click=callback if es_admin else None
```

### 3. **State Management** - Gestión de Estado

```python
# app/ui_inicio.py - Gestión de estado de pendientes
lista_pendientes = []  # ← Estado local

def actualizar_pendientes():
    """Actualiza la UI basándose en el estado"""
    items = []
    for i, tarea in enumerate(lista_pendientes):
        items.append(crear_item_pendiente(tarea, i))
    
    pendientes_container.controls = items  # ← Actualizar UI
    try:
        page.update()  # ← Forzar re-render
    except:
        pass

def agregar_pendiente(e):
    """Modifica el estado y actualiza UI"""
    if campo_pendiente.value.strip():
        lista_pendientes.append({
            'texto': campo_pendiente.value.strip(),
            'completada': False
        })
        campo_pendiente.value = ""
        guardar_pendientes()  # ← Persistir estado
        actualizar_pendientes()  # ← Actualizar UI
```

**Patrón de estado:**
1. **Estado**: Variables que mantienen datos
2. **Modificación**: Funciones que cambian el estado
3. **UI Update**: Actualizar la interfaz basándose en el nuevo estado
4. **Persistencia**: Guardar el estado (archivo, base de datos)

### 4. **Animations** - Animaciones

```python
# app/ui/login.py - Animación de error
async def animar_error(campo):
    """Anima el campo con shake y lo marca en rojo"""
    campo.border_color = ft.Colors.RED
    for offset in [-10, 10, -6, 6, 0]:  # ← Secuencia de movimiento
        campo.offset = ft.Offset(offset, 0)
        page.update()
        await asyncio.sleep(0.05)  # ← Pausa entre frames
    campo.offset = ft.Offset(0, 0)
    page.update()
```

**¿Por qué animaciones?**
- **Feedback visual**: El usuario sabe que algo pasó
- **UX mejorada**: Las transiciones suaves se sienten más profesionales
- **Atención**: Dirige la atención a elementos importantes

### 5. **Theme Management** - Gestión de Temas

```python
# app/utils/temas.py - Definición de temas
class TemaOscuro:
    BG_COLOR = "#1a1a1a"
    CARD_COLOR = "#2d2d2d"
    PRIMARY_COLOR = "#bb86fc"
    TEXT_COLOR = "#ffffff"
    BUTTON_BG = "#bb86fc"
    # ... más colores

class TemaAzul:
    BG_COLOR = "#0d1117"
    CARD_COLOR = "#161b22"
    PRIMARY_COLOR = "#58a6ff"
    TEXT_COLOR = "#f0f6fc"
    BUTTON_BG = "#238636"
    # ... más colores

# Aplicación de tema
def aplicar_tema_a_widget():
    tema = GestorTemas.obtener_tema()
    return ft.Container(
        bgcolor=tema.CARD_COLOR,  # ← Usar color del tema
        content=ft.Text("Hola", color=tema.TEXT_COLOR)
    )
```

**Beneficios del sistema de temas:**
- **Consistencia**: Todos los widgets usan los mismos colores
- **Personalización**: Los usuarios pueden elegir su tema preferido
- **Mantenimiento**: Cambiar un color lo cambia en toda la app
- **Accesibilidad**: Temas claros/oscuros para diferentes necesidades

---

## 🚀 Best Practices para Flet

### 1. **Organización de Código**

```python
# ✅ BUENO: Funciones separadas para crear widgets complejos
def crear_boton_accion(texto, icono, callback):
    return ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(icono, color=tema.ICON_BTN_COLOR),
            ft.Text(texto, color=tema.BUTTON_TEXT)
        ]),
        style=ft.ButtonStyle(
            bgcolor=tema.BUTTON_BG,
            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
        ),
        on_click=callback
    )

# ❌ MALO: Todo en una sola función gigante
def crear_interfaz():
    return ft.Column([
        ft.Container(
            content=ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD),
                    ft.Text("Agregar")
                ]),
                # ... 50 líneas más de configuración
            )
        ),
        # ... más widgets anidados
    ])
```

### 2. **Responsive Design**

```python
# ✅ BUENO: Cálculos basados en tamaño de pantalla
def calcular_dimensiones(page):
    ancho = page.window.width or 1200
    return {
        'menu_width': 220 if ancho < 1200 else 250,
        'card_width': min(400, ancho * 0.8),
        'button_width': min(150, ancho * 0.2)
    }

# ❌ MALO: Valores fijos que no se adaptan
MENU_WIDTH = 250  # Se ve mal en pantallas pequeñas
CARD_WIDTH = 400  # Puede no caber en móviles
```

### 3. **Event Handling**

```python
# ✅ BUENO: Funciones async para operaciones lentas
async def guardar_producto(e):
    try:
        # Mostrar loading
        mostrar_loading()
        
        # Operación lenta
        await firebase_operation()
        
        # Feedback al usuario
        mostrar_exito()
    except Exception as ex:
        mostrar_error(str(ex))
    finally:
        ocultar_loading()

# ❌ MALO: Operación síncrona que bloquea la UI
def guardar_producto_sync(e):
    # La UI se congela durante esta operación
    firebase_operation_sync()
```

### 4. **State Management**

```python
# ✅ BUENO: Estado centralizado con funciones de actualización
class EstadoProductos:
    def __init__(self):
        self.productos = []
        self.filtro_actual = ""
    
    def agregar_producto(self, producto):
        self.productos.append(producto)
        self.actualizar_ui()
    
    def filtrar_productos(self, filtro):
        self.filtro_actual = filtro
        self.actualizar_ui()
    
    def actualizar_ui(self):
        # Lógica de actualización centralizada
        pass

# ❌ MALO: Estado disperso y difícil de manejar
productos_globales = []  # Estado global
filtro_global = ""       # Más estado global
# ... actualización de UI en múltiples lugares
```

### 5. **Error Handling**

```python
# ✅ BUENO: Manejo de errores con feedback visual
async def operacion_con_errores():
    try:
        resultado = await operacion_riesgosa()
        
        # Feedback de éxito
        page.open(ft.SnackBar(
            content=ft.Text("Operación exitosa"),
            bgcolor=tema.SUCCESS_COLOR
        ))
        
    except SpecificError as e:
        # Error específico con solución
        page.open(ft.SnackBar(
            content=ft.Text(f"Error específico: {e}. Intenta X"),
            bgcolor=tema.WARNING_COLOR
        ))
        
    except Exception as e:
        # Error general
        page.open(ft.SnackBar(
            content=ft.Text(f"Error inesperado: {e}"),
            bgcolor=tema.ERROR_COLOR
        ))

# ❌ MALO: Errores silenciosos o no manejados
def operacion_sin_manejo():
    resultado = operacion_riesgosa()  # Puede fallar sin que el usuario sepa
    return resultado
```

---

## 🎯 Comparación: Flet vs Otras Tecnologías

### Flet vs Tkinter

| Aspecto | Flet | Tkinter |
|---------|------|---------|
| **UI Moderna** | ✅ Material Design | ❌ Look retro |
| **Responsive** | ✅ Adaptativo | ❌ Fijo |
| **Multiplataforma** | ✅ Desktop/Web/Mobile | ❌ Solo desktop |
| **Curva de aprendizaje** | 📚 Moderada | 📚 Fácil |
| **Rendimiento** | ⚡ Flutter engine | ⚡ Bueno |

### Flet vs Electron + Web

| Aspecto | Flet | Electron |
|---------|------|----------|
| **Tamaño del bundle** | ✅ Más pequeño | ❌ Muy grande |
| **Uso de memoria** | ✅ Eficiente | ❌ Mucha RAM |
| **Lenguaje** | ✅ Python puro | ❌ JS/HTML/CSS |
| **Ecosistema** | 📚 Python packages | 📚 NPM packages |
| **Desarrollo** | ✅ Más simple | ❌ Más complejo |

### Flet vs PyQt/PySide

| Aspecto | Flet | PyQt/PySide |
|---------|------|-------------|
| **Licencia** | ✅ Apache 2.0 | ⚠️ GPL/Comercial |
| **UI Moderna** | ✅ Material Design | ❌ Nativo del SO |
| **Facilidad** | ✅ Más simple | ❌ Más complejo |
| **Madurez** | ⚠️ Nuevo | ✅ Muy maduro |
| **Documentación** | ⚠️ En desarrollo | ✅ Extensa |

---

## 🔮 Futuro y Características Avanzadas

### Widgets que podríamos agregar:

1. **ft.Charts** - Para gráficos y analytics
2. **ft.Map** - Para mapas (ubicación de almacenes)
3. **ft.Calendar** - Para fechas de vencimiento de productos
4. **ft.FileUploader** - Para subir imágenes de productos
5. **ft.VideoPlayer** - Para tutoriales embedded

### Funcionalidades avanzadas:

```python
# Drag & Drop para reordenar productos
ft.Draggable(
    content=ft.Container(...),
    on_drag_complete=reordenar_productos
)

# Notificaciones push
ft.Notification(
    title="Stock Bajo",
    message="Producto X tiene solo 5 unidades",
    icon=ft.Icons.WARNING
)

# Temas personalizados dinámicos
ft.ThemeData(
    color_scheme=ft.ColorScheme.from_seed(
        seed_color=ft.Colors.PURPLE
    )
)
```

---

## 🆕 Widgets Avanzados Utilizados en Nuevos Módulos

### ft.DataTable - Reportes Empresariales
**Implementación Avanzada en Sistema de Reportes**

```python
# app/ui_reportes.py - Tabla con estilos profesionales
tabla_reporte = ft.DataTable(
    columns=[
        ft.DataColumn(ft.Text("Fecha/Hora", weight=ft.FontWeight.BOLD)),
        ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD)),
        ft.DataColumn(ft.Text("Producto", weight=ft.FontWeight.BOLD)),
        ft.DataColumn(ft.Text("Cantidad", weight=ft.FontWeight.BOLD)),
        ft.DataColumn(ft.Text("Origen", weight=ft.FontWeight.BOLD)),
        ft.DataColumn(ft.Text("Destino", weight=ft.FontWeight.BOLD)),
        ft.DataColumn(ft.Text("Motivo", weight=ft.FontWeight.BOLD))
    ],
    rows=filas_datos,
    border=ft.border.all(1, tema.DIVIDER_COLOR),
    border_radius=tema.BORDER_RADIUS,
    bgcolor=tema.CARD_COLOR,
    heading_row_color=tema.PRIMARY_COLOR,
    heading_row_height=50,
    data_row_min_height=40,
    column_spacing=20
)
```

**Características Profesionales:**
- `heading_row_color`: Color distintivo para encabezados
- `data_row_min_height`: Altura mínima legible
- `column_spacing`: Espaciado profesional
- `border_radius`: Esquinas redondeadas

### ft.Dropdown - Filtros Inteligentes
**Sistema de Filtros para Reportes**

```python
# Selector avanzado con opciones dinámicas
dropdown_usuario = ft.Dropdown(
    label="Filtrar por Usuario",
    value="todos",
    options=[
        ft.dropdown.Option("todos", "Todos los usuarios"),
        ft.dropdown.Option("Admin", "Admin"),
        ft.dropdown.Option("Operador1", "Operador1"),
        ft.dropdown.Option("Supervisor", "Supervisor")
    ],
    width=200,
    bgcolor=tema.INPUT_BG,
    color=tema.TEXT_COLOR,
    border_color=tema.INPUT_BORDER,
    focused_border_color=tema.PRIMARY_COLOR,
    on_change=lambda e: aplicar_filtro_usuario(e.control.value)
)
```

### ft.ProgressRing - Indicadores de Carga
**Feedback Visual para Operaciones Asíncronas**

```python
# Indicador de carga con texto descriptivo
indicador_generando = ft.Row([
    ft.ProgressRing(
        color=tema.PRIMARY_COLOR,
        stroke_width=3,
        width=24,
        height=24
    ),
    ft.Text("Generando reporte...", color=tema.TEXT_COLOR)
], alignment=ft.MainAxisAlignment.CENTER)

# Mostrar durante operación
contenedor_reporte.content = indicador_generando
page.update()

# Ocultar cuando termina
contenedor_reporte.content = tabla_resultados
page.update()
```

### Selectores Visuales Personalizados
**Selección de Almacenes en Movimientos**

```python
def crear_selector_almacen(almacen):
    """Selector visual tipo card para almacenes"""
    
    def seleccionar_almacen(e):
        nonlocal ubicacion_destino
        ubicacion_destino = {"almacen": almacen["nombre"]}
        actualizar_seleccion_visual()

    esta_seleccionado = (ubicacion_destino and 
                       ubicacion_destino.get("almacen") == almacen["nombre"])

    return ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Icon(almacen["icono"], color=almacen["color"], size=24),
                ft.Text(almacen["nombre"], 
                       color=tema.TEXT_COLOR,
                       size=12,
                       text_align=ft.TextAlign.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
            width=120,
            on_click=seleccionar_almacen  # ⚠️ IMPORTANTE: on_click en Container
        ),
        color=tema.PRIMARY_COLOR if esta_seleccionado else tema.CARD_COLOR,
        elevation=5 if esta_seleccionado else 2
    )
```

**⚠️ Importante sobre ft.Card y Eventos:**
- `ft.Card` NO acepta directamente `on_click`
- Usar `ft.Container` dentro del Card
- El Container maneja el evento `on_click`
- Cambiar `elevation` para feedback visual

### Grid Responsivo de Selección
**8 Tipos de Reportes Organizados**

```python
def crear_grid_tipos_reporte():
    """Grid responsivo para tipos de reporte"""
    cards_reportes = []
    
    # Crear cards para cada tipo de reporte
    for tipo_id, info in tipos_reportes.items():
        card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(info["icono"], color=info["color"], size=32),
                    ft.Text(info["nombre"], 
                           weight=ft.FontWeight.BOLD, 
                           color=tema.TEXT_COLOR,
                           text_align=ft.TextAlign.CENTER,
                           size=12),
                    ft.Text(info["descripcion"],
                           color=tema.SECONDARY_TEXT_COLOR,
                           text_align=ft.TextAlign.CENTER,
                           size=10)
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8),
                padding=15,
                width=180,
                height=140,
                on_click=lambda e, tipo=tipo_id: seleccionar_tipo_reporte(tipo)
            ),
            color=tema.PRIMARY_COLOR if esta_seleccionado else tema.CARD_COLOR,
            elevation=5 if esta_seleccionado else 2
        )
        cards_reportes.append(card)
    
    # Organizar en filas de 4 (responsivo)
    filas = []
    for i in range(0, len(cards_reportes), 4):
        fila = ft.Row(
            cards_reportes[i:i+4],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15
        )
        filas.append(fila)
    
    return ft.Column(filas, spacing=15)
```

### Workflow Visual Guiado
**Movimientos de Productos con Pasos Visuales**

```python
# Panel visual de movimiento paso a paso
def construir_workflow_movimiento():
    """Construir interfaz de workflow visual"""
    return ft.Column([
        # 1. Información del producto
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.INVENTORY, color=tema.PRIMARY_COLOR),
                ft.Column([
                    ft.Text(f"{producto['modelo']} - {producto['nombre']}", 
                           weight=ft.FontWeight.BOLD),
                    ft.Text(f"Disponible: {producto['cantidad']} unidades", 
                           color=tema.SECONDARY_TEXT_COLOR)
                ], spacing=2)
            ], spacing=10),
            bgcolor=tema.BG_COLOR,
            padding=10,
            border_radius=8,
            border=ft.border.all(1, tema.PRIMARY_COLOR)
        ),

        # 2. Origen (actual)
        ft.Container(
            content=ft.Column([
                ft.Text("� DESDE (Ubicación actual):", 
                       weight=ft.FontWeight.BOLD),
                ft.Text(f"{origen['almacen']} → {origen['ubicacion']}")
            ]),
            padding=10,
            bgcolor=tema.CARD_COLOR,
            border_radius=8
        ),

        # 3. Flecha direccional
        ft.Container(
            content=ft.Icon(ft.Icons.ARROW_DOWNWARD, 
                          color=tema.PRIMARY_COLOR, size=32),
            alignment=ft.alignment.center
        ),

        # 4. Destino (interactivo)
        ft.Container(
            content=ft.Column([
                ft.Text("📍 HACIA (Seleccionar destino):", 
                       weight=ft.FontWeight.BOLD),
                ft.Row([
                    crear_selector_almacen(almacen) 
                    for almacen in almacenes_disponibles
                ], spacing=10)
            ]),
            padding=10,
            bgcolor=tema.CARD_COLOR,
            border_radius=8
        )
    ], spacing=15)
```

### Scroll Optimizado para Listas Grandes
**Historial de Movimientos con Performance**

```python
# Lista con scroll y altura limitada
historial_movimientos = ft.Column(
    controls=[],  # Se llena dinámicamente
    spacing=10,
    height=600,  # Altura fija para scroll
    scroll=ft.ScrollMode.AUTO,
    auto_scroll=False  # Control manual del scroll
)

# Función optimizada para agregar elementos
def agregar_movimiento_a_historial(movimiento):
    """Agregar movimiento con control de memoria"""
    tarjeta = crear_tarjeta_movimiento(movimiento)
    historial_movimientos.controls.append(tarjeta)
    
    # Limitar elementos en memoria (virtualization manual)
    if len(historial_movimientos.controls) > 100:
        # Remover elementos más antiguos
        historial_movimientos.controls = historial_movimientos.controls[-50:]
    
    page.update()
```

### Validación en Tiempo Real
**Campos con Feedback Inmediato**

```python
def crear_campo_cantidad_validado():
    """Campo de cantidad con validación en tiempo real"""
    
    def validar_cantidad(e):
        try:
            cantidad = int(e.control.value)
            max_disponible = producto_seleccionado["cantidad_disponible"]
            
            if cantidad <= 0:
                e.control.error_text = "Cantidad debe ser mayor a 0"
                e.control.bgcolor = tema.ERROR_BG
            elif cantidad > max_disponible:
                e.control.error_text = f"Máximo disponible: {max_disponible}"
                e.control.bgcolor = tema.ERROR_BG
            else:
                e.control.error_text = None
                e.control.bgcolor = tema.INPUT_BG
                
        except ValueError:
            e.control.error_text = "Debe ser un número válido"
            e.control.bgcolor = tema.ERROR_BG
        
        page.update()

    return ft.TextField(
        label="Cantidad a mover",
        keyboard_type=ft.KeyboardType.NUMBER,
        on_change=validar_cantidad,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR
    )
```

## 🔧 Patrones Avanzados de Interacción

### Manejo de Estado Complejo
```python
class EstadoMovimiento:
    """Clase para manejar estado complejo de movimientos"""
    
    def __init__(self):
        self.producto_seleccionado = None
        self.ubicacion_origen = None
        self.ubicacion_destino = None
        self.cantidad_validada = False
        self.listeners = []  # Callbacks para cambios de estado
    
    def seleccionar_producto(self, producto):
        self.producto_seleccionado = producto
        self.ubicacion_origen = {
            "almacen": producto["almacen_actual"],
            "ubicacion": producto["ubicacion_actual"]
        }
        self.notificar_cambio("producto_seleccionado")
    
    def seleccionar_destino(self, destino):
        self.ubicacion_destino = destino
        self.notificar_cambio("destino_seleccionado")
    
    def notificar_cambio(self, tipo_cambio):
        """Notificar a todos los listeners sobre cambios"""
        for callback in self.listeners:
            callback(tipo_cambio, self)
    
    def agregar_listener(self, callback):
        """Agregar callback para cambios de estado"""
        self.listeners.append(callback)

# Uso del estado
estado_movimiento = EstadoMovimiento()

def actualizar_interfaz(tipo_cambio, estado):
    """Callback para actualizar interfaz según cambios de estado"""
    if tipo_cambio == "producto_seleccionado":
        panel_movimiento.content = construir_panel_movimiento(estado)
    elif tipo_cambio == "destino_seleccionado":
        boton_ejecutar.disabled = False
    
    page.update()

# Registrar el callback
estado_movimiento.agregar_listener(actualizar_interfaz)
```

### Animaciones y Transiciones
```python
# Animación de carga suave
def mostrar_carga_animada():
    """Mostrar indicador de carga con animación"""
    
    # Estado inicial
    indicador = ft.ProgressRing(
        color=tema.PRIMARY_COLOR,
        width=0,  # Empieza invisible
        height=0
    )
    
    # Animación de aparición
    indicador.width = 24
    indicador.height = 24
    page.update()
    
    return indicador

# Feedback visual de éxito
def mostrar_exito_animado(mensaje):
    """Mostrar mensaje de éxito con animación"""
    
    snackbar = ft.SnackBar(
        content=ft.Row([
            ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
            ft.Text(mensaje, color=ft.Colors.WHITE)
        ]),
        bgcolor=tema.SUCCESS_COLOR,
        duration=ft.Duration(milliseconds=3000),
        behavior=ft.SnackBarBehavior.FLOATING
    )
    
    page.open(snackbar)
```

---

## �📚 Recursos para Seguir Aprendiendo

### Documentación Oficial:
- **Flet.dev**: https://flet.dev/docs/
- **Flutter Widgets**: https://docs.flutter.dev/ui/widgets (Flet usa los mismos)
- **Material Design**: https://m3.material.io/

### Comunidad:
- **Discord de Flet**: Soporte directo de desarrolladores
- **GitHub**: https://github.com/flet-dev/flet
- **Ejemplos**: https://github.com/flet-dev/examples

### Cursos recomendados:
1. **Python para interfaces gráficas**
2. **Diseño UI/UX fundamentals**
3. **Flutter conceptos básicos** (transferibles a Flet)
4. **Firebase para aplicaciones web**
5. **Principios de UX para sistemas empresariales**

---

*Esta documentación cubre los widgets de Flet utilizados en TotalStock, incluyendo las nuevas funcionalidades de Ubicaciones, Movimientos y Reportes. Flet es una tecnología en evolución, así que mantente actualizado con las nuevas versiones y funcionalidades.*
