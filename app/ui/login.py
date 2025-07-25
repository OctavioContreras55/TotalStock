import flet as ft

def login_view(page: ft.Page, on_login_success): #Función para la vista del login. Argumentos: page = pagina de Flet, on_login_success = función a ejecutar al iniciar sesión correctamente

    #Campos de entrada para el usuario y la contraseña
    usuario_input = ft.TextField(label="Usuario", autofocus=True)
    contrasena_input = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)
    

    min_width = max(510, int(page.window.width * 0.45))
    min_height = max(800, int(page.window.height * 1))
    page.window.min_width = min_width
    page.window.min_height = min_height
    
    #Texto de error en caso de campos vacíos
    mensaje_error = ft.Container(
      content=ft.Row(
          controls=[
              ft.Icon(name=ft.Icons.WARNING_ROUNDED, color=ft.Colors.RED_400, size=20),
              ft.Text("Usuario o contraseña incorrectos", color=ft.Colors.RED_400),
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
            
    #Boton de inicio de sesión
    boton_login = ft.Container(
      content=ft.ElevatedButton(text="Iniciar sesión",on_click=validar_login),
      padding=ft.padding.only(top=20, bottom=10),
      width=200,
      height=80,
    )
    
    #Diseño de la vista de login
    vista_tarjeta = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text("Ingrese sus credenciales", style=ft.TextThemeStyle.HEADLINE_MEDIUM, text_align=ft.TextAlign.CENTER),
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
        width=370,
        border_radius=15,
        bgcolor=ft.Colors.GREY_900 + "CC",
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
                    ft.Text("Bienvenido a TotalStock", style=ft.TextThemeStyle.HEADLINE_LARGE, text_align=ft.TextAlign.CENTER),
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


    
    #Limpia la página y agrega la vista de login
    page.controls.clear()# Limpia los controles de la página
    page.add(vista_login)
    page.update()  # Actualiza la página para mostrar los cambios iniciales
