import flet as ft
from app.utils.temas import GestorTemas
from conexiones.firebase import db
from app.funciones.sesiones import SesionManager
import asyncio

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
    
    #Campos de entrada para el usuario y la contraseña
    usuario_input = ft.TextField(
        label="Usuario", 
        autofocus=True,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    contrasena_input = ft.TextField(
        label="Contraseña", 
        password=True, 
        can_reveal_password=True,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
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
    
    async def resetear_campos():
        """Resetea el color de los campos"""
        usuario_input.border_color = tema.INPUT_BORDER
        contrasena_input.border_color = tema.INPUT_BORDER
        page.update()
    
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
            await animar_error(usuario_input)
        if not contrasena:
            campos_vacios.append(contrasena_input)
            await animar_error(contrasena_input)

        if campos_vacios:
            page.open(ft.SnackBar(
                content=ft.Text("Por favor, complete todos los campos", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            page.update()
            return
        
        try:
            # Realizar la consulta a la base de datos para verificar las credenciales del usuario  
            from google.cloud.firestore_v1.base_query import FieldFilter
            referencia_usuarios = db.collection('usuarios')
            query = referencia_usuarios.where(filter=FieldFilter('nombre', '==', usuario)).where(filter=FieldFilter('contrasena', '==', contrasena)).limit(1).get()
            
            if query:
                # Login exitoso - obtener datos del usuario
                usuario_doc = query[0]
                usuario_data = usuario_doc.to_dict()
                usuario_data['firebase_id'] = usuario_doc.id
                usuario_data['username'] = usuario_data.get('nombre', usuario)
                
                # Establecer la sesión del usuario
                SesionManager.establecer_usuario(usuario_data)
                
                print(f"Login exitoso para el usuario: {usuario}")
                await on_login_success()
            else:
                # Credenciales incorrectas - animar ambos campos
                await animar_error(usuario_input)
                await animar_error(contrasena_input)
                page.open(ft.SnackBar(
                    content=ft.Text("Usuario o contraseña incorrectos", color=tema.TEXT_COLOR),
                    bgcolor=tema.ERROR_COLOR
                ))
                page.update()
                
        except Exception as error:
            print(f"Error al verificar las credenciales: {error}")
            page.open(ft.SnackBar(
                content=ft.Text("Error de conexión. Intente nuevamente.", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
            page.update()
            
    #Boton de inicio de sesión - Responsivo
    boton_login = ft.Container(
      content=ft.ElevatedButton(
          text="Iniciar sesión",
          on_click=validar_login,
          style=ft.ButtonStyle(
              bgcolor=tema.BUTTON_PRIMARY_BG,
              color=tema.BUTTON_TEXT,
              shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
          )
      ),
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
                  padding= ft.padding.only(top=20),
                ),
                ft.Container(
                  content=ft.Image("assets/logo.png",
                      width=150,
                      height=150,
                      fit=ft.ImageFit.CONTAIN
                  ),
                  padding=ft.padding.only(bottom=20, top=20),
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
