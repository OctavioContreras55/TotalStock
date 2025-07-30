import flet as ft
from app.utils.temas import GestorTemas

def login_view(page: ft.Page, on_login_success): #Función para la vista del login. Argumentos: page = pagina de Flet, on_login_success = función a ejecutar al iniciar sesión correctamente
    tema = GestorTemas.obtener_tema()
    
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
    
    #Texto de error en caso de campos vacíos
    mensaje_error = ft.Container(
      content=ft.Row(
          controls=[
              ft.Icon(name=ft.Icons.WARNING_ROUNDED, color=tema.ERROR_COLOR, size=20),
              ft.Text("Usuario o contraseña incorrectos", color=tema.ERROR_COLOR),
          ],
          alignment=ft.MainAxisAlignment.CENTER,
          spacing=10,

      ),
      visible=False,
      height=30,
      opacity=0,# Animación de opacidad al ocultar
      animate_opacity=300,  # Animación de opacidad al mostrar/ocultar
    )
    
    #Quitar si se quiere tener fondo blanco en el logo
    """def logo_con_borde():
        return ft.Container(
        content=ft.Image(src="assets/logo.png", width=150, height=150),
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        padding=10,
        alignment=ft.alignment.center
    )"""
    
    #Función para validar datos de inicio de sesión
    def validar_login(e):
        usuario = usuario_input.value
        contrasena = contrasena_input.value
        
        #TEMPORAL: Validación simple de usuario y contraseña
        if usuario == "admin" and contrasena == "admin":
            mensaje_error.visible = False
            vista_tarjeta.height = 430  # Ajusta la altura de la tarjeta al iniciar sesión correctamente
            on_login_success() # Llama a la función de éxito al iniciar sesión
            page.update()
        else:
            # Acceder al texto dentro del Row del Container
            mensaje_error.content.controls[1].value = "Usuario o contraseña incorrectos"
            mensaje_error.visible = True
            mensaje_error.opacity = 1 # Muestra el mensaje de error
            vista_tarjeta.height = 480  # Ajusta la altura de la tarjeta al mostrar el mensaje de error
            usuario_input.focus()
            contrasena_input.value = ""
            page.update() # Actualiza la página para mostrar los cambios
            
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
                mensaje_error,
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
    #Contenedor principal de la vista de login
    vista_login = ft.Column(
            controls=[
                ft.Container(
                  content=
                    ft.Text(
                        "Bienvenido a TotalStock", 
                        style=ft.TextThemeStyle.HEADLINE_LARGE, 
                        text_align=ft.TextAlign.CENTER,
                        color=tema.TEXT_COLOR
                    ),
                  alignment=ft.alignment.top_center,
                  padding= ft.padding.only(top=40),
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
