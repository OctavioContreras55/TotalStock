import flet as ft
import asyncio
import json
from app.utils.temas import GestorTemas
from conexiones.firebase import db

async def vista_categorias(nombre_seccion, contenido, page):
    """Vista completa para gestión de categorías y desglose de productos"""
    tema = GestorTemas.obtener_tema()
    
    # Dimensiones responsivas
    ancho_ventana = page.window.width or 1200
    alto_ventana = page.window.height or 800

    # Estado de la vista
    categoria_seleccionada = None
    productos_filtrados = []
    mostrar_gestion_categorias = False
    productos_inventario = []
    
    # Contenedores principales
    contenedor_resultados = ft.Column(spacing=10)
    contenedor_gestion_inner = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    contenedor_gestion = ft.Container(
        content=contenedor_gestion_inner,
        height=400,
        padding=10,
        bgcolor=tema.CARD_COLOR,
        border_radius=tema.BORDER_RADIUS,
        border=ft.border.all(1, tema.DIVIDER_COLOR),
        visible=False
    )
    dropdowns_visibles = []

    # ====== Categorías predefinidas (basado en el código original) ======
    categorias_config = {
        "cadenas": {
            "nombre": "Cadenas",
            "icono": ft.Icons.LINK,
            "color": tema.PRIMARY_COLOR,
            "opciones": ["Cadena 25", "Cadena 35", "Cadena 40", "Cadena 50", "Cadena 60", "Cadena 80", "Cadena 100"],
            "descripcion": "Cadenas industriales de diferentes pasos"
        },
        "catarinas": {
            "nombre": "Catarinas",
            "icono": ft.Icons.SETTINGS,
            "color": tema.WARNING_COLOR,
            "opciones": ["Paso 35", "Paso 40", "Paso 50", "Paso 60", "Paso 80", "Paso 100"],
            "descripcion": "Catarinas y engranajes por paso"
        },
        "chumaceras": {
            "nombre": "Chumaceras",
            "icono": ft.Icons.PRECISION_MANUFACTURING,
            "color": tema.SUCCESS_COLOR,
            "opciones": ["De piso", "De pared"],
            "descripcion": "Chumaceras de diferentes tipos de montaje"
        }
    }

    page.update()

    async def cargar_productos_inventario():
        """Cargar todos los productos del inventario para gestión de categorías - Prioriza caché"""
        try:
            nonlocal productos_inventario
            productos_inventario = []
            
            # 1. PRIORIDAD: Intentar cargar desde cache local
            try:
                with open('data/inventario.json', 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    if cache_data and len(cache_data) > 0:
                        # Usar datos del cache y formatear correctamente
                        for producto in cache_data:
                            if isinstance(producto, dict):
                                producto_id = producto.get("firebase_id") or producto.get("id") or producto.get("doc_id") or ""
                                if producto_id:
                                    productos_inventario.append({
                                        "id": str(producto_id).strip(),
                                        "modelo": str(producto.get("modelo", "N/A")),
                                        "nombre": str(producto.get("nombre", "N/A")),
                                        "categoria": str(producto.get("categoria", "Sin categoría")),
                                        "cantidad": producto.get("cantidad", 0),
                                        "precio": producto.get("precio", 0.0)
                                    })
                        
                        if len(productos_inventario) > 0:
                            print(f"[OK] Usando caché local: {len(productos_inventario)} productos")
                            return productos_inventario
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"[WARN] Cache local no disponible: {e}")
            
            # 2. RESPALDO: Si no hay cache válido, consultar Firebase
            print("[CONSULTA] Consultando Firebase como respaldo...")
            from app.crud_productos.create_producto import obtener_productos_firebase
            productos_firebase = await obtener_productos_firebase()
            
            for producto in productos_firebase:
                if isinstance(producto, dict):
                    producto_id = producto.get("firebase_id") or producto.get("id") or producto.get("doc_id") or ""
                    if not producto_id:
                        print(f"Advertencia: Producto sin ID: {producto.get('modelo', 'Sin modelo')}")
                        continue
                    
                    productos_inventario.append({
                        "id": str(producto_id).strip(),
                        "modelo": str(producto.get("modelo", "N/A")),
                        "nombre": str(producto.get("nombre", "N/A")),
                        "categoria": str(producto.get("categoria", "Sin categoría")),
                        "cantidad": producto.get("cantidad", 0),
                        "precio": producto.get("precio", 0.0)
                    })
            
            # 3. Actualizar cache para próximas consultas
            try:
                with open('data/inventario.json', 'w', encoding='utf-8') as f:
                    json.dump([p for p in productos_firebase], f, ensure_ascii=False, indent=2)
                print("[SAVE] Cache local actualizado desde Firebase")
            except Exception as e:
                print(f"[ERROR] Error guardando cache: {e}")
            
            print(f"[DOWNLOAD] Productos cargados desde Firebase: {len(productos_inventario)}")
            return productos_inventario
            
        except Exception as e:
            print(f"[ERROR] Error al cargar productos de inventario: {e}")
            return []

    async def actualizar_categoria_producto(producto_id, nueva_categoria, nueva_subcategoria=None):
        """Actualizar la categoría de un producto en Firebase"""
        try:
            # Validar que el producto_id no esté vacío
            if not producto_id or producto_id.strip() == "":
                print(f"Error: ID de producto vacío o inválido: '{producto_id}'")
                page.open(ft.SnackBar(
                    content=ft.Text("[ERROR] Error: ID de producto inválido", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))
                return False
            
            # Construir nueva categoría
            categoria_completa = nueva_categoria
            if nueva_subcategoria and nueva_subcategoria != nueva_categoria:
                categoria_completa = f"{nueva_categoria} - {nueva_subcategoria}"
            
            print(f"Actualizando producto ID: '{producto_id}' con categoría: '{categoria_completa}'")
            
            # Actualizar directamente en Firebase
            doc_ref = db.collection("productos").document(producto_id.strip())
            doc_ref.update({"categoria": categoria_completa})
            
            # Actualizar cache local directamente (más eficiente que invalidar)
            try:
                cache_file = 'data/inventario.json'
                import os
                if os.path.exists(cache_file):
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    # Actualizar el producto específico en cache
                    for idx, producto in enumerate(cache_data):
                        if isinstance(producto, dict):
                            p_id = producto.get("firebase_id") or producto.get("id") or producto.get("doc_id")
                            if str(p_id).strip() == str(producto_id).strip():
                                cache_data[idx]["categoria"] = categoria_completa
                                break
                    
                    # Guardar cache actualizado
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(cache_data, f, ensure_ascii=False, indent=2)
                    print("[SAVE] Cache local actualizado con nueva categoría")
                else:
                    print("[WARN] Cache local no existe, se actualizará en próxima carga")
                    
            except Exception as cache_error:
                print(f"[WARN] No se pudo actualizar cache local: {cache_error}")
            
            # Actualizar en la lista local
            for producto in productos_inventario:
                if producto.get("id") == producto_id:
                    producto["categoria"] = categoria_completa
                    break
            
            page.open(ft.SnackBar(
                content=ft.Text(f"[OK] Categoría actualizada", color=tema.TEXT_COLOR),
                bgcolor=tema.SUCCESS_COLOR
            ))
            return True
        except Exception as e:
            print(f"Error al actualizar categoría: {e}")
            page.open(ft.SnackBar(
                content=ft.Text(f"Error: {str(e)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            return False

    async def mostrar_gestion_categorias_productos():
        """Mostrar interfaz para gestionar categorías de productos"""
        nonlocal mostrar_gestion_categorias
        
        if not mostrar_gestion_categorias:
            # Cargar productos
            await cargar_productos_inventario()
            mostrar_gestion_categorias = True
            contenedor_gestion.visible = True
            
            # Construir interfaz de gestión
            contenedor_gestion_inner.controls.clear()
            
            # Encabezado
            contenedor_gestion_inner.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SETTINGS, color=tema.PRIMARY_COLOR, size=24),
                        ft.Text("Gestión de Categorías de Productos", 
                               size=18, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            tooltip="Cerrar gestión",
                            style=ft.ButtonStyle(bgcolor=tema.ERROR_COLOR),
                            on_click=lambda e: cerrar_gestion_categorias()
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=tema.PRIMARY_COLOR,
                    padding=15,
                    border_radius=tema.BORDER_RADIUS,
                    margin=ft.margin.only(bottom=15)
                )
            )
            
            # Filtros
            campo_busqueda = ft.TextField(
                hint_text="Buscar producto por modelo o nombre...",
                bgcolor=tema.INPUT_BG,
                color=tema.TEXT_COLOR,
                border_color=tema.INPUT_BORDER,
                focused_border_color=tema.PRIMARY_COLOR,
                width=300,
                on_change=lambda e: page.run_task(filtrar_productos_gestion_async, e.control.value, dropdown_categoria_filtro.value)
            )
            
            dropdown_categoria_filtro = ft.Dropdown(
                label="Filtrar por categoría actual",
                options=[
                    ft.dropdown.Option("todas", "Todas las categorías"),
                    ft.dropdown.Option("sin_categoria", "Sin categoría"),
                    ft.dropdown.Option("cadenas", "Cadenas"),
                    ft.dropdown.Option("catarinas", "Catarinas"),
                    ft.dropdown.Option("chumaceras", "Chumaceras")
                ],
                value="todas",
                width=200,
                bgcolor=tema.INPUT_BG,
                color=tema.TEXT_COLOR,
                on_change=lambda e: page.run_task(filtrar_productos_gestion_async, campo_busqueda.value, e.control.value)
            )
            
            contenedor_gestion_inner.controls.append(
                ft.Row([
                    campo_busqueda,
                    dropdown_categoria_filtro,
                    ft.ElevatedButton(
                        "[PROCESO] Refrescar desde Firebase",
                        style=ft.ButtonStyle(bgcolor=tema.WARNING_COLOR),
                        on_click=lambda e: page.run_task(forzar_recarga_firebase),
                        tooltip="Recargar datos directamente desde Firebase"
                    )
                ], spacing=10)
            )
            
            # Lista de productos para gestionar
            contenedor_lista_productos = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO, expand=True)
            contenedor_gestion_inner.controls.append(
                ft.Container(
                    content=contenedor_lista_productos,
                    bgcolor=tema.BG_COLOR,
                    border_radius=tema.BORDER_RADIUS,
                    padding=10,
                    expand=True
                )
            )
            
            # Mostrar todos los productos inicialmente
            await mostrar_productos_gestion(contenedor_lista_productos)
            
        page.update()

    async def mostrar_productos_gestion(contenedor, filtro_texto="", filtro_categoria="todas"):
        """Mostrar productos en la interfaz de gestión"""
        contenedor.controls.clear()
        
        # Filtrar productos
        productos_filtrados_gestion = productos_inventario.copy()
        
        if filtro_texto:
            productos_filtrados_gestion = [
                p for p in productos_filtrados_gestion
                if filtro_texto.lower() in str(p["modelo"]).lower() or filtro_texto.lower() in str(p["nombre"]).lower()
            ]
        
        if filtro_categoria != "todas":
            if filtro_categoria == "sin_categoria":
                productos_filtrados_gestion = [
                    p for p in productos_filtrados_gestion
                    if p["categoria"] in ["Sin categoría", ""]
                ]
            else:
                productos_filtrados_gestion = [
                    p for p in productos_filtrados_gestion
                    if filtro_categoria.lower() in p["categoria"].lower()
                ]
        
        # Mostrar productos (limitar a 50 por rendimiento)
        if not productos_filtrados_gestion:
            # Mostrar mensaje cuando no hay productos que coincidan con el filtro
            contenedor.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF, color=tema.SECONDARY_TEXT_COLOR, size=48),
                        ft.Text("No se encontraron productos", 
                               size=18, weight=ft.FontWeight.BOLD, color=tema.SECONDARY_TEXT_COLOR),
                        ft.Text("Prueba cambiando los filtros de búsqueda", 
                               size=14, color=tema.SECONDARY_TEXT_COLOR)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    bgcolor=tema.CARD_COLOR,
                    padding=40,
                    border_radius=tema.BORDER_RADIUS,
                    border=ft.border.all(1, tema.DIVIDER_COLOR),
                    alignment=ft.alignment.center
                )
            )
        else:
            for producto in productos_filtrados_gestion[:50]:
                await crear_card_producto_gestion(producto, contenedor)
        
        if len(productos_filtrados_gestion) > 50:
            contenedor.controls.append(
                ft.Container(
                    content=ft.Text(f"... y {len(productos_filtrados_gestion) - 50} productos más", 
                                   color=tema.SECONDARY_TEXT_COLOR, size=12),
                    padding=10
                )
            )
        
        page.update()

    async def crear_card_producto_gestion(producto, contenedor):
        """Crear card individual para gestión de producto"""
        
        # Determinar la categoría actual del producto
        categoria_producto = str(producto["categoria"])
        valor_dropdown = "Sin categoría"  # Default
        
        # Detectar la categoría principal del producto
        if "Cadenas" in categoria_producto or "Cadena" in categoria_producto:
            valor_dropdown = "Cadenas"
        elif "Catarinas" in categoria_producto or "Catarina" in categoria_producto:
            valor_dropdown = "Catarinas"
        elif "Chumaceras" in categoria_producto or "Chumacera" in categoria_producto:
            valor_dropdown = "Chumaceras"
        
        # Dropdown para seleccionar nueva categoría
        dropdown_categoria = ft.Dropdown(
            label="Categoría",
            options=[
                ft.dropdown.Option("Cadenas", "Cadenas"),
                ft.dropdown.Option("Catarinas", "Catarinas"),
                ft.dropdown.Option("Chumaceras", "Chumaceras"),
                ft.dropdown.Option("Sin categoría", "Sin categoría")
            ],
            value=valor_dropdown,
            width=120,
            bgcolor=tema.INPUT_BG,
            color=tema.TEXT_COLOR
        )
        
        # Dropdown para subcategoría (basado en las opciones existentes)
        dropdown_subcategoria = ft.Dropdown(
            label="Subcategoría",
            options=[],  # Se llena dinámicamente
            width=140,
            bgcolor=tema.INPUT_BG,
            color=tema.TEXT_COLOR
        )
        
        def actualizar_subcategorias(e):
            """Actualizar opciones de subcategoría según la categoría seleccionada"""
            categoria_sel = e.control.value
            dropdown_subcategoria.options.clear()
            
            if categoria_sel == "Cadenas":
                for opcion in categorias_config["cadenas"]["opciones"]:
                    dropdown_subcategoria.options.append(ft.dropdown.Option(opcion, opcion))
            elif categoria_sel == "Catarinas":
                for opcion in categorias_config["catarinas"]["opciones"]:
                    dropdown_subcategoria.options.append(ft.dropdown.Option(opcion, opcion))
            elif categoria_sel == "Chumaceras":
                for opcion in categorias_config["chumaceras"]["opciones"]:
                    dropdown_subcategoria.options.append(ft.dropdown.Option(opcion, opcion))
            
            dropdown_subcategoria.value = None
            page.update()
        
        dropdown_categoria.on_change = actualizar_subcategorias
        
        # Inicializar subcategorías
        categoria_actual = dropdown_categoria.value
        if categoria_actual == "Cadenas":
            for opcion in categorias_config["cadenas"]["opciones"]:
                dropdown_subcategoria.options.append(ft.dropdown.Option(opcion, opcion))
        elif categoria_actual == "Catarinas":
            for opcion in categorias_config["catarinas"]["opciones"]:
                dropdown_subcategoria.options.append(ft.dropdown.Option(opcion, opcion))
        elif categoria_actual == "Chumaceras":
            for opcion in categorias_config["chumaceras"]["opciones"]:
                dropdown_subcategoria.options.append(ft.dropdown.Option(opcion, opcion))
        
        async def guardar_categoria():
            """Guardar nueva categoría del producto"""
            nueva_categoria = dropdown_categoria.value
            nueva_subcategoria = dropdown_subcategoria.value
            
            print(f"DEBUG: Guardando producto - ID: '{producto['id']}', Modelo: '{producto['modelo']}', Nueva categoría: '{nueva_categoria}'")
            
            if await actualizar_categoria_producto(producto["id"], nueva_categoria, nueva_subcategoria):
                # Actualizar la card visualmente
                categoria_completa = nueva_categoria
                if nueva_subcategoria:
                    categoria_completa = f"{nueva_categoria} - {nueva_subcategoria}"
                
                texto_categoria_actual.value = f"📂 {categoria_completa}"
                texto_categoria_actual.color = tema.SUCCESS_COLOR
                
                # Actualizar el producto en la lista local para que el dropdown refleje el cambio
                producto["categoria"] = categoria_completa
                
                # Actualizar el valor del dropdown para reflejar la categoría guardada
                if categoria_completa.startswith("Cadenas"):
                    dropdown_categoria.value = "Cadenas"
                elif categoria_completa.startswith("Catarinas"):
                    dropdown_categoria.value = "Catarinas"
                elif categoria_completa.startswith("Chumaceras"):
                    dropdown_categoria.value = "Chumaceras"
                else:
                    dropdown_categoria.value = "Sin categoría"
                
                page.update()
        
        # Texto de categoría actual
        texto_categoria_actual = ft.Text(
            f"📂 {producto['categoria']}", 
            size=12, color=tema.SECONDARY_TEXT_COLOR
        )
        
        card_producto = ft.Container(
            content=ft.Row([
                # Información del producto
                ft.Column([
                    ft.Text(producto["modelo"], size=14, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                    ft.Text(producto["nombre"], size=12, color=tema.SECONDARY_TEXT_COLOR),
                    texto_categoria_actual
                ], expand=True, spacing=2),
                
                # Controles de categoría
                ft.Column([
                    ft.Row([dropdown_categoria, dropdown_subcategoria], spacing=5),
                    ft.ElevatedButton(
                        "[SAVE] Guardar",
                        style=ft.ButtonStyle(
                            bgcolor=tema.SUCCESS_COLOR,
                            color=tema.BUTTON_TEXT
                        ),
                        height=35,
                        on_click=lambda e: page.run_task(guardar_categoria)
                    )
                ], spacing=5)
            ], spacing=10),
            bgcolor=tema.CARD_COLOR,
            padding=10,
            border_radius=tema.BORDER_RADIUS,
            border=ft.border.all(1, tema.DIVIDER_COLOR),
            margin=ft.margin.only(bottom=5)
        )
        
        contenedor.controls.append(card_producto)

    def cerrar_gestion_categorias():
        """Cerrar la interfaz de gestión de categorías"""
        nonlocal mostrar_gestion_categorias
        mostrar_gestion_categorias = False
        contenedor_gestion.visible = False
        contenedor_gestion_inner.controls.clear()
        page.update()

    async def filtrar_productos_gestion_async(texto_filtro="", categoria_filtro="todas"):
        """Versión asíncrona del filtro de productos"""
        filtrar_productos_gestion(texto_filtro, categoria_filtro)

    def filtrar_productos_gestion(texto_filtro="", categoria_filtro="todas"):
        """Filtrar productos en la gestión"""
        if mostrar_gestion_categorias and contenedor_gestion_inner.controls:
            # Encontrar el contenedor de la lista
            for control in contenedor_gestion_inner.controls:
                if isinstance(control, ft.Container) and hasattr(control, 'content') and isinstance(control.content, ft.Column):
                    if len(control.content.controls) > 0:  # Es la lista de productos
                        # Usar page.run_task para manejar la función asíncrona
                        page.run_task(mostrar_productos_gestion, control.content, texto_filtro, categoria_filtro)
                        break

    async def forzar_recarga_firebase():
        """Forzar recarga de datos directamente desde Firebase (evitar cache)"""
        try:
            # Eliminar cache local para forzar consulta a Firebase
            import os
            cache_file = 'data/inventario.json'
            if os.path.exists(cache_file):
                os.remove(cache_file)
                print("[ELIMINAR] Cache local eliminado")
            
            # Recargar productos
            await cargar_productos_inventario()
            
            # Mostrar mensaje de éxito
            page.open(ft.SnackBar(
                content=ft.Text("[OK] Datos actualizados desde Firebase", color=tema.TEXT_COLOR),
                bgcolor=tema.SUCCESS_COLOR
            ))
            
            # Refrescar vista si está en gestión
            if mostrar_gestion_categorias:
                await mostrar_gestion_categorias_productos()
                
        except Exception as e:
            print(f"[ERROR] Error al forzar recarga: {e}")
            page.open(ft.SnackBar(
                content=ft.Text(f"[ERROR] Error al recargar: {str(e)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))

    async def recargar_productos_gestion():
        """Recargar la lista de productos forzando actualización desde Firebase"""
        try:
            # Invalidar cache antes de recargar
            from app.utils.cache_firebase import cache_firebase
            cache_firebase._ultimo_update_productos = None  # Forzar revalidación del cache
            print("Forzando recarga completa desde Firebase...")
            
            await cargar_productos_inventario()
            await mostrar_gestion_categorias_productos()
        except Exception as e:
            print(f"Error al recargar productos: {e}")
            page.open(ft.SnackBar(
                content=ft.Text(f"Error al recargar: {str(e)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))

    async def cargar_productos_categoria(tipo_seleccionado):
        """Cargar productos filtrados desde Firebase (adaptado del código original)"""
        contenedor_resultados.controls.clear()
        
        try:
            # Importar función para obtener productos desde Firebase
            from app.crud_productos.create_producto import obtener_productos_firebase
            productos_firebase = await obtener_productos_firebase()
            
            # Filtrar productos según el tipo seleccionado (lógica original)
            productos_encontrados = []
            
            for producto in productos_firebase:
                if not isinstance(producto, dict):
                    continue
                    
                modelo = str(producto.get("modelo", "")).upper()
                nombre = str(producto.get("nombre", "")).upper()
                
                # Aplicar filtros según tipo (lógica del código original)
                coincide = False
                
                if tipo_seleccionado.startswith("Cadena"):
                    # Buscar "CADENA 25", "CADENA 35", etc.
                    numero = tipo_seleccionado.replace("Cadena ", "")
                    if f"CADENA {numero}" in modelo or f"CADENA{numero}" in modelo:
                        coincide = True
                        
                elif tipo_seleccionado.startswith("Paso"):
                    # Buscar catarinas por paso: "35B", "40B", etc.
                    numero = tipo_seleccionado.split(" ")[1]
                    if modelo.startswith(f"{numero}B") or f"PASO {numero}" in modelo:
                        coincide = True
                        
                elif tipo_seleccionado in ["De piso", "De pared"]:
                    # Buscar chumaceras
                    tipo_buscar = tipo_seleccionado.upper()
                    if tipo_buscar in modelo or tipo_buscar in nombre or "CHUMACERA" in modelo:
                        coincide = True
                
                if coincide:
                    productos_encontrados.append(producto)
            
            # Mostrar resultados
            if not productos_encontrados:
                contenedor_resultados.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.SEARCH_OFF, color=tema.ERROR_COLOR, size=24),
                            ft.Text("No se encontraron productos para esta categoría", 
                                   color=tema.ERROR_COLOR, size=16, weight=ft.FontWeight.BOLD)
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        bgcolor=tema.CARD_COLOR,
                        padding=20,
                        border_radius=tema.BORDER_RADIUS,
                        border=ft.border.all(1, tema.ERROR_COLOR)
                    )
                )
            else:
                # Encabezado de resultados
                contenedor_resultados.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.INVENTORY, color=tema.PRIMARY_COLOR, size=24),
                            ft.Text(f"Productos encontrados: {len(productos_encontrados)}", 
                                   size=18, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                        ]),
                        bgcolor=tema.PRIMARY_COLOR,
                        padding=15,
                        border_radius=tema.BORDER_RADIUS,
                        margin=ft.margin.only(bottom=10)
                    )
                )
                
                # Lista de productos encontrados (diseño mejorado)
                for producto in productos_encontrados[:50]:  # Limitar a 50 por rendimiento
                    precio = producto.get("precio", 0)
                    cantidad = producto.get("cantidad", 0)
                    
                    # Determinar color del stock
                    color_stock = tema.SUCCESS_COLOR if cantidad > 10 else tema.WARNING_COLOR if cantidad > 0 else tema.ERROR_COLOR
                    
                    card_producto = ft.Container(
                        content=ft.Column([
                            ft.Row([
                                # Información principal
                                ft.Column([
                                    ft.Text(producto.get("modelo", "N/A"), 
                                           size=16, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                                    ft.Text(producto.get("nombre", "Sin nombre"), 
                                           size=14, color=tema.SECONDARY_TEXT_COLOR),
                                ], expand=True),
                                
                                # Precio
                                ft.Container(
                                    content=ft.Text(f"${precio:,.2f}", 
                                                   size=16, weight=ft.FontWeight.BOLD, color=tema.PRIMARY_COLOR),
                                    bgcolor=tema.BG_COLOR,
                                    padding=8,
                                    border_radius=5
                                ),
                                
                                # Stock
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.INVENTORY_2, color=color_stock, size=16),
                                        ft.Text(f"{cantidad}", size=16, weight=ft.FontWeight.BOLD, color=color_stock)
                                    ], spacing=5),
                                    bgcolor=tema.BG_COLOR,
                                    padding=8,
                                    border_radius=5
                                )
                            ], spacing=15),
                            
                            # Información adicional
                            ft.Row([
                                ft.Text(f"Categoría: {producto.get('categoria', 'Sin categoría')}", 
                                       size=12, color=tema.SECONDARY_TEXT_COLOR),
                                ft.Text(f"Ubicación: {producto.get('ubicacion', 'Sin asignar')}", 
                                       size=12, color=tema.SECONDARY_TEXT_COLOR),
                            ], spacing=20)
                        ], spacing=8),
                        bgcolor=tema.CARD_COLOR,
                        padding=15,
                        border_radius=tema.BORDER_RADIUS,
                        border=ft.border.all(1, tema.DIVIDER_COLOR),
                        margin=ft.margin.only(bottom=8)
                    )
                    contenedor_resultados.controls.append(card_producto)
                
        except Exception as e:
            print(f"Error al cargar productos de categoría: {e}")
            contenedor_resultados.controls.append(
                ft.Container(
                    content=ft.Text(f"Error al cargar productos: {str(e)}", 
                                   color=tema.ERROR_COLOR, size=14),
                    bgcolor=tema.CARD_COLOR,
                    padding=15,
                    border_radius=tema.BORDER_RADIUS
                )
            )
        
        page.update()

    def crear_selector_categoria(categoria_id, config):
        """Crear selector de categoría mejorado (basado en el código original)"""
        opciones_column = ft.Column(visible=False, spacing=5)
        dropdowns_visibles.append(opciones_column)
        
        # Estado de la categoría
        texto_estado = ft.Text(
            f"Selecciona {config['nombre'].lower()}", 
            size=14, color=tema.SECONDARY_TEXT_COLOR
        )

        async def mostrar_opciones(e):
            """Mostrar opciones disponibles"""
            # Ocultar otros dropdowns
            for d in dropdowns_visibles:
                d.visible = False
            
            # Mostrar el actual
            opciones_column.visible = True
            page.update()

        async def seleccionar_opcion(opcion):
            """Seleccionar una opción y cargar productos"""
            nonlocal categoria_seleccionada
            categoria_seleccionada = opcion
            
            texto_estado.value = f"[PACKAGE] {config['nombre']}: {opcion}"
            texto_estado.color = tema.PRIMARY_COLOR
            opciones_column.visible = False
            
            # Cargar productos de la categoría
            await cargar_productos_categoria(opcion)

        def actualizar_opciones():
            """Actualizar lista de opciones"""
            opciones_column.controls.clear()
            for opcion in config["opciones"]:
                opcion_container = ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ARROW_RIGHT, color=tema.PRIMARY_COLOR, size=16),
                        ft.Text(opcion, color=tema.TEXT_COLOR, size=14)
                    ], spacing=8),
                    bgcolor=tema.BG_COLOR,
                    padding=10,
                    border_radius=5,
                    border=ft.border.all(1, tema.DIVIDER_COLOR),
                    on_click=lambda e, op=opcion: page.run_task(seleccionar_opcion, op)
                )
                opciones_column.controls.append(opcion_container)

        # Inicializar opciones
        actualizar_opciones()

        # Gestión de opciones personalizadas (funcionalidad original mejorada)
        input_opcion = ft.TextField(
            hint_text="Nueva opción...",
            bgcolor=tema.INPUT_BG,
            color=tema.TEXT_COLOR,
            border_color=tema.INPUT_BORDER,
            focused_border_color=tema.PRIMARY_COLOR,
            width=160,
            height=40
        )

        async def agregar_opcion():
            nueva = input_opcion.value.strip()
            if nueva and nueva not in config["opciones"]:
                config["opciones"].append(nueva)
                input_opcion.value = ""
                actualizar_opciones()
                page.update()
                
                # Mostrar confirmación
                page.open(ft.SnackBar(
                    content=ft.Text(f"[OK] Opción '{nueva}' agregada", color=tema.TEXT_COLOR),
                    bgcolor=tema.SUCCESS_COLOR
                ))

        async def eliminar_opcion():
            borrar = input_opcion.value.strip()
            if borrar in config["opciones"]:
                config["opciones"].remove(borrar)
                input_opcion.value = ""
                actualizar_opciones()
                page.update()
                
                # Mostrar confirmación
                page.open(ft.SnackBar(
                    content=ft.Text(f"[ELIMINAR] Opción '{borrar}' eliminada", color=tema.TEXT_COLOR),
                    bgcolor=tema.WARNING_COLOR
                ))

        return ft.Container(
            content=ft.Column([
                # Encabezado de la categoría
                ft.Row([
                    ft.Icon(config["icono"], color=config["color"], size=28),
                    ft.Column([
                        ft.Text(config["nombre"], size=18, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                        ft.Text(config["descripcion"], size=12, color=tema.SECONDARY_TEXT_COLOR)
                    ], expand=True)
                ], spacing=10),
                
                # Botón principal
                ft.ElevatedButton(
                    f"Ver {config['nombre']}",
                    style=ft.ButtonStyle(
                        bgcolor=config["color"],
                        color=tema.BUTTON_TEXT,
                        shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                    ),
                    on_click=lambda e: page.run_task(mostrar_opciones, e),
                    width=200,
                    height=45
                ),
                
                # Lista de opciones
                opciones_column,
                
                # Estado actual
                texto_estado,
                
                # Gestión de opciones
                ft.Text("Gestionar Opciones:", size=12, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                ft.Row([
                    input_opcion,
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        tooltip="Agregar opción",
                        style=ft.ButtonStyle(bgcolor=tema.SUCCESS_COLOR),
                        on_click=lambda e: page.run_task(agregar_opcion)
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        tooltip="Eliminar opción",
                        style=ft.ButtonStyle(bgcolor=tema.ERROR_COLOR),
                        on_click=lambda e: page.run_task(eliminar_opcion)
                    )
                ], spacing=5)
            ], spacing=15),
            bgcolor=tema.CARD_COLOR,
            border_radius=12,
            padding=20,
            width=380,
            border=ft.border.all(1, tema.DIVIDER_COLOR)
        )

    # Construir vista principal
    def construir_vista_categorias():
        # Crear tarjetas de categorías
        tarjetas_categorias = []
        for cat_id, config in categorias_config.items():
            tarjeta = crear_selector_categoria(cat_id, config)
            tarjetas_categorias.append(tarjeta)

        return ft.Container(
            content=ft.Column([
                # Header principal
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CATEGORY, color=tema.PRIMARY_COLOR, size=32),
                        ft.Text("Gestión de Categorías", size=28, weight=ft.FontWeight.BOLD, color=tema.TEXT_COLOR),
                    ]),
                    width=ancho_ventana * 0.9,
                    bgcolor=tema.CARD_COLOR,
                    padding=20,
                    alignment=ft.alignment.center,
                    border_radius=tema.BORDER_RADIUS,
                ),

                # Separador
                ft.Container(height=3, bgcolor=tema.DIVIDER_COLOR, margin=ft.margin.only(bottom=20, top=5)),

                # Descripción
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Selecciona una categoría para explorar y filtrar productos específicos. "
                            "Puedes agregar o eliminar opciones personalizadas para cada categoría.",
                            size=14, color=tema.SECONDARY_TEXT_COLOR, text_align=ft.TextAlign.CENTER
                        ),
                        ft.Row([
                            ft.ElevatedButton(
                                "⚙️ Gestionar Categorías de Productos",
                                style=ft.ButtonStyle(
                                    bgcolor=tema.WARNING_COLOR,
                                    color=tema.BUTTON_TEXT,
                                    shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                ),
                                on_click=lambda e: page.run_task(mostrar_gestion_categorias_productos),
                                height=40
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER)
                    ]),
                    padding=10,
                    margin=ft.margin.only(bottom=20)
                ),

                # Tarjetas de categorías
                ft.Row(
                    tarjetas_categorias,
                    spacing=25,
                    alignment=ft.MainAxisAlignment.CENTER,
                    wrap=True
                ),

                # Contenedor de gestión de categorías (se muestra/oculta dinámicamente)
                contenedor_gestion,

                # Separador para resultados
                ft.Container(
                    content=ft.Row([
                        ft.Container(height=1, bgcolor=tema.DIVIDER_COLOR, expand=True),
                        ft.Text("RESULTADOS", size=16, weight=ft.FontWeight.BOLD, color=tema.PRIMARY_COLOR),
                        ft.Container(height=1, bgcolor=tema.DIVIDER_COLOR, expand=True),
                    ], spacing=10),
                    margin=ft.margin.only(top=30, bottom=20)
                ),

                # Contenedor de resultados
                ft.Container(
                    content=ft.Column([
                        contenedor_resultados
                    ]),
                    bgcolor=tema.BG_COLOR,
                    border_radius=tema.BORDER_RADIUS,
                    padding=10,
                    width=ancho_ventana * 0.95
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            ),
            padding=ft.padding.only(bottom=40),
            bgcolor=tema.BG_COLOR
        )

    # Mostrar vista inicial
    contenido.content = construir_vista_categorias()
    page.update()

# Función de compatibilidad para el sistema actual
def categorias_mostrar(nombre_seccion, contenido, page=None):
    """Función de compatibilidad con el sistema existente"""
    if page:
        # Si tenemos acceso a page, usar la vista completa
        return vista_categorias(nombre_seccion, contenido, page)
    else:
        # Fallback para compatibilidad
        tema = GestorTemas.obtener_tema()
        contenido.content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text("Vista de Categorías - Requiere página completa", 
                                   size=16, color=tema.TEXT_COLOR),
                    padding=20
                )
            ]
        )