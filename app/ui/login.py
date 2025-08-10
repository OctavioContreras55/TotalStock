import flet as ft
from app.utils.temas import GestorTemas
from conexiones.firebase import db
from app.funciones.sesiones import SesionManager
from app.utils.sesiones_unicas import gestor_sesiones
from app.ui.barra_carga import progress_ring_pequeno
import asyncio
import os
import sys

def obtener_ruta_recurso(ruta_relativa):
    """Obtiene la ruta correcta para recursos, tanto en desarrollo como en ejecutable"""
    try:
        # PyInstaller crea una carpeta temporal _MEIPASS cuando ejecuta
        ruta_base = sys._MEIPASS
    except AttributeError:
        # En desarrollo, usar la ruta actual
        ruta_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    return os.path.join(ruta_base, ruta_relativa)

def login_view(page: ft.Page, on_login_success): #Función para la vista del login. Argumentos: page = pagina de Flet, on_login_success = función a ejecutar al iniciar sesión correctamente
    tema = GestorTemas.obtener_tema()
    
    # Función para cambiar tema en el login
    def cambiar_tema_login(e):
        nuevo_tema = "azul" if e.control.value else "oscuro"
        GestorTemas.cambiar_tema_login(nuevo_tema)
        # Recargar la vista de login con el nuevo tema
        login_view(page, on_login_success)
    
    # Dimensiones responsivas basadas en el tamaño de pantalla
    ancho_ventana = page.window.width or 1200
    alto_ventana = page.window.height or 800
    
    # Cálculos responsivos para diferentes elementos
    ancho_tarjeta = min(400, ancho_ventana * 0.85)  # Máximo 400px o 85% del ancho
    ancho_boton = min(200, ancho_tarjeta * 0.6)     # Proporcionalmente al ancho de la tarjeta
    
    # Función para manejar Enter en campos
    async def manejar_enter(e):
        """Ejecutar login cuando se presiona Enter"""
        await validar_login(e)
    
    #Campos de entrada para el usuario y la contraseña
    usuario_input = ft.TextField(
        label="Usuario", 
        autofocus=True,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY),
        on_submit=lambda e: page.run_task(manejar_enter, e)  # Enter en usuario
    )
    contrasena_input = ft.TextField(
        label="Contraseña", 
        password=True, 
        can_reveal_password=True,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY),
        on_submit=lambda e: page.run_task(manejar_enter, e)  # Enter en contraseña
    )

    # Configuración responsiva de ventana mínima
    min_width = max(450, int(ancho_ventana * 0.4))   # Más flexible para laptops
    min_height = max(600, int(alto_ventana * 0.8))   # Más flexible para laptops
    page.window.min_width = min_width
    page.window.min_height = min_height
    
    
    async def animar_error(campo):
        """Anima el campo con shake y lo marca en rojo"""
        campo.border_color = ft.Colors.RED
        for offset in [-10, 10, -6, 6, 0]:
            campo.offset = ft.Offset(offset, 0)
            page.update()
            await asyncio.sleep(0.05)
        campo.offset = ft.Offset(0, 0)
        page.update()
    
    async def animar_errores_simultaneos(campos):
        """Anima múltiples campos simultáneamente"""
        # Establecer color rojo para todos los campos
        for campo in campos:
            campo.border_color = ft.Colors.RED
        page.update()
        
        # Animar todos los campos al mismo tiempo
        for offset in [-10, 10, -6, 6, -3, 3, 0]:
            for campo in campos:
                campo.offset = ft.Offset(offset, 0)
            page.update()
            await asyncio.sleep(0.06)
        
        # Resetear posición
        for campo in campos:
            campo.offset = ft.Offset(0, 0)
        page.update()
    
    async def resetear_campos():
        """Resetea el color de los campos"""
        usuario_input.border_color = tema.INPUT_BORDER
        contrasena_input.border_color = tema.INPUT_BORDER
        page.update()
    
    # Contenedor para mostrar el progress ring durante validación con animación
    contenedor_progreso = ft.AnimatedSwitcher(
        content=ft.Container(height=0),  # Inicialmente invisible
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=300,
        reverse_duration=300,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN
    )

    async def precargar_datos_usuario():
        """
        Precarga datos en background después del login para optimizar navegación
        """
        try:
            print("PRECARGA: Iniciando carga de datos en background...")
            from app.utils.cache_firebase import cache_firebase
            
            # Precargar productos sin mostrar loading (background)
            productos = await cache_firebase.obtener_productos(forzar_refresh=False, mostrar_loading=False)
            print(f"[OK] PRECARGA: {len(productos)} productos cargados en cache")
            
            # Precargar usuarios si es necesario
            usuarios = await cache_firebase.obtener_usuarios(forzar_refresh=False)
            print(f"[OK] PRECARGA: {len(usuarios)} usuarios cargados en cache")
            
            print("[DART] PRECARGA COMPLETA: Navegación será instantánea")
            
        except Exception as e:
            print(f"[WARN] Error en precarga (no crítico): {e}")

    #Función para validar datos de inicio de sesión
    async def validar_login(e):
        usuario = usuario_input.value.strip()  # Eliminar espacios
        contrasena = contrasena_input.value
        
        # Resetear colores de campos antes de validar
        await resetear_campos()
        
        # Validar campos vacíos PRIMERO
        campos_vacios = []
        if not usuario:
            campos_vacios.append(usuario_input)
        if not contrasena:
            campos_vacios.append(contrasena_input)

        if campos_vacios:
            # Animar todos los campos vacíos simultáneamente
            await animar_errores_simultaneos(campos_vacios)
            page.open(ft.SnackBar(
                content=ft.Text("Por favor, complete todos los campos", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            page.update()
            return
        
        # Mostrar progress ring mientras se valida con animación
        print("[PROCESO] MOSTRANDO PROGRESS RING CON ANIMACIÓN...")
        
        # Mostrar progress ring con animación suave
        contenedor_progreso.content = ft.Container(
            content=progress_ring_pequeno("Verificando credenciales...", 12),
            height=60,
            width=300,
            alignment=ft.alignment.center
        )
        boton_elevated.disabled = True  # Deshabilitar botón durante validación
        page.update()
        print("[OK] Progress ring animado mostrado y botón deshabilitado")
        
        # Pequeño delay para asegurar que la animación se complete
        await asyncio.sleep(0.4)
        
        try:
            # Realizar la consulta a la base de datos para verificar las credenciales del usuario  
            from google.cloud.firestore_v1.base_query import FieldFilter
            referencia_usuarios = db.collection('usuarios')
            query = referencia_usuarios.where(filter=FieldFilter('nombre', '==', usuario)).where(filter=FieldFilter('contrasena', '==', contrasena)).limit(1).get()
            
            if query:
                # Credenciales válidas - verificar sesión única
                print("🔐 Credenciales válidas, verificando sesión única...")
                
                # Verificar si el usuario ya tiene una sesión activa
                resultado_sesion = gestor_sesiones.iniciar_sesion(usuario)
                
                if not resultado_sesion["exito"]:
                    # Ya existe una sesión activa
                    contenedor_progreso.content = ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE, size=24),
                            ft.Text("Sesión ya activa", color=ft.Colors.ORANGE, size=16, weight=ft.FontWeight.BOLD)
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        height=60,
                        width=300,
                        alignment=ft.alignment.center
                    )
                    page.update()
                    
                    await asyncio.sleep(1)
                    
                    # Mostrar diálogo de sesión existente
                    page.open(ft.AlertDialog(
                        title=ft.Text("[WARN] Sesión ya activa", weight=ft.FontWeight.BOLD),
                        content=ft.Text(resultado_sesion["mensaje"]),
                        actions=[
                            ft.TextButton("Cerrar", on_click=lambda e: page.close(e.control.parent))
                        ]
                    ))
                    
                    # Restaurar estado del botón
                    contenedor_progreso.content = ft.Container(height=0)
                    boton_elevated.disabled = False
                    page.update()
                    return
                
                # Sesión única OK - proceder con login exitoso
                usuario_doc = query[0]
                usuario_data = usuario_doc.to_dict()
                usuario_data['firebase_id'] = usuario_doc.id
                usuario_data['username'] = usuario_data.get('nombre', usuario)
                
                # Establecer la sesión del usuario
                SesionManager.establecer_usuario(usuario_data)
                
                # También actualizar variable global para limpieza automática
                import run
                if hasattr(run, '_usuario_actual_global'):
                    run._usuario_actual_global = usuario_data.get('username', usuario)
                    print(f"[USER] Usuario global actualizado en login: {run._usuario_actual_global}")
                
                print(f"Login exitoso para el usuario: {usuario}")
                
                # Mostrar palomita de validación exitosa
                contenedor_progreso.content = ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=24),
                        ft.Text("¡Acceso concedido!", color=ft.Colors.GREEN, size=16, weight=ft.FontWeight.BOLD)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    height=60,
                    width=300,
                    alignment=ft.alignment.center
                )
                page.update()
                
                # Esperar un momento para mostrar la validación exitosa
                await asyncio.sleep(0.8)
                
                # Ocultar indicador y proceder
                contenedor_progreso.content = ft.Container(height=0)
                boton_elevated.disabled = False
                page.update()
                
                # PRECARGA DE DATOS EN BACKGROUND para optimizar navegación
                asyncio.create_task(precargar_datos_usuario())
                
                # Proceder inmediatamente al login
                await on_login_success()
            else:
                # Credenciales incorrectas - animar ambos campos simultáneamente
                # Ocultar progress ring con animación primero
                print("[PROCESO] OCULTANDO PROGRESS RING (credenciales incorrectas)...")
                contenedor_progreso.content = ft.Container(height=0)  # Volver a estado invisible
                boton_elevated.disabled = False
                page.update()
                
                # Esperar animación antes de mostrar errores
                await asyncio.sleep(0.3)
                
                # Animar ambos campos simultáneamente
                await animar_errores_simultaneos([usuario_input, contrasena_input])
                page.open(ft.SnackBar(
                    content=ft.Text("Usuario o contraseña incorrectos", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))
                page.update()
                
        except Exception as error:
            print(f"Error al verificar las credenciales: {error}")
            # Ocultar progress ring con animación en caso de error
            print("[PROCESO] OCULTANDO PROGRESS RING (error de conexión)...")
            contenedor_progreso.content = ft.Container(height=0)  # Volver a estado invisible
            boton_elevated.disabled = False
            page.update()
            
            # Esperar animación antes de mostrar error
            await asyncio.sleep(0.3)
            
            page.open(ft.SnackBar(
                content=ft.Text("Error de conexión. Intente nuevamente.", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            page.update()
            
    #Boton de inicio de sesión - Responsivo
    boton_elevated = ft.ElevatedButton(
        text="Iniciar sesión",
        on_click=validar_login,
        style=ft.ButtonStyle(
            bgcolor=tema.BUTTON_PRIMARY_BG,
            color=tema.BUTTON_TEXT,
            shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
        )
    )
    
    boton_login = ft.Container(
      content=boton_elevated,
      padding=ft.padding.only(top=20, bottom=10),
      width=ancho_boton,  # Ancho responsivo
      height=80,
    )
    
    #Diseño de la vista de login - Responsivo
    vista_tarjeta = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(
                        "Ingrese sus credenciales", 
                        style=ft.TextThemeStyle.HEADLINE_MEDIUM, 
                        text_align=ft.TextAlign.CENTER,
                        color=tema.TEXT_COLOR
                    ),
                    padding=ft.padding.only(bottom=20, top=10),
                    alignment=ft.alignment.center,
                ),
                usuario_input,
                contrasena_input,
                contenedor_progreso,  # Agregar el contenedor de progreso aquí
                boton_login
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=30
        ),
        padding=30,
        width=ancho_tarjeta,  # Ancho responsivo
        border_radius=tema.BORDER_RADIUS,
        bgcolor=tema.CARD_COLOR,
        shadow=ft.BoxShadow(
            color=ft.Colors.BLACK54,
            blur_radius=15,
            spread_radius=5,
            offset=ft.Offset(4, 4)
        )
    )
    # Selector de tema para el login
    selector_tema = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.DARK_MODE, color=tema.TEXT_SECONDARY, size=16),
            ft.Switch(
                value=GestorTemas.obtener_tema_actual() == "azul",
                on_change=cambiar_tema_login,
                active_color=tema.PRIMARY_COLOR,
                inactive_track_color=tema.TEXT_DISABLED,
                width=40,
                height=20
            ),
            ft.Icon(ft.Icons.LIGHT_MODE, color=tema.TEXT_SECONDARY, size=16),
        ], 
        spacing=8,
        alignment=ft.MainAxisAlignment.CENTER
        ),
        padding=10,
        border_radius=tema.BORDER_RADIUS,
        bgcolor=ft.Colors.with_opacity(0.1, tema.TEXT_COLOR),
        tooltip="Cambiar tema de la aplicación"
    )

    #Contenedor principal de la vista de login
    vista_login = ft.Column(
            controls=[
                # Selector de tema en la parte superior
                ft.Container(
                    content=selector_tema,
                    alignment=ft.alignment.top_right,
                    padding=ft.padding.only(right=20, top=10)
                ),
                ft.Container(
                  content=
                    ft.Text(
                        "Bienvenido a TotalStock", 
                        style=ft.TextThemeStyle.HEADLINE_LARGE, 
                        text_align=ft.TextAlign.CENTER,
                        color=tema.TEXT_COLOR
                    ),
                  alignment=ft.alignment.top_center,
                  padding= ft.padding.only(top=10),
                ),
                ft.Container(
                  content=ft.Image(obtener_ruta_recurso("assets/logo.png"),
                      width=150,
                      height=150,
                      fit=ft.ImageFit.CONTAIN
                  ),
                  padding=ft.padding.only(bottom=10, top=10),
                ),
                ft.Row(
                    controls=[
                        vista_tarjeta
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )


    # Configurar el fondo de la página
    page.bgcolor = tema.BG_COLOR
    #Limpia la página y agrega la vista de login
    page.controls.clear()# Limpia los controles de la página
    page.add(vista_login)
    page.update()  # Actualiza la página para mostrar los cambios iniciales
