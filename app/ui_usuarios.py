import flet as ft
from app.tablas.ui_tabla_usuarios import mostrar_tabla_usuarios
from app.crud_usuarios.create_usuarios import mostrar_ventana_crear_usuario, obtener_usuarios_firebase
import asyncio
from app.ui.barra_carga import vista_carga

async def vista_usuarios(nombre_seccion, contenido, page=None):
    contenido.content = vista_carga()  # Mostrar barra de carga mientras se carga la vista
    await obtener_usuarios_firebase()  # Cargar usuarios desde Firebase
    page.update()  # Actualizar la página para mostrar la barra de carga


    # Si no se pasa la página, intentar obtenerla del contenido
    if page is None:
        page = contenido.page
    
    # Variable para almacenar la tabla actual
    tabla_container = ft.Ref[ft.Container]()

    async def actualizar_tabla(): # Función para actualizar la tabla con datos de Firebase
        try:
            print("Actualizando tabla usuarios")
            contenido.content = vista_carga()
            page.update()
            usuarios = await obtener_usuarios_firebase()
            contenido.content = construir_vista_usuario(usuarios)
            page.update()
        except Exception as e:
            print(f"Error al actualizar tabla: {e}")
            contenido.content = construir_vista_usuario([])  # Muestra la vista con tabla vacía
            page.update()
    
    def abrir_ventana_crear_usuario(e): # Función para abrir la ventana de crear usuario
        try:
            mostrar_ventana_crear_usuario(page, actualizar_tabla)
            print("Ventana de crear usuario llamada exitosamente")  # Debug
        except Exception as error:
            print(f"Error al abrir ventana: {error}")  # Debug
    
    # Obtener usuarios iniciales
    try:
        usuarios_iniciales = await obtener_usuarios_firebase()
    except Exception as e:
        print(f"Error al obtener usuarios iniciales: {e}")
        usuarios_iniciales = []
    
    def construir_vista_usuario(usuarios):
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24),
                                    ft.Text("Gestión de los usuarios del sistema", size=16,),
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
        
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.START
                    ),
                    width=600,
                    bgcolor=ft.Colors.GREY_900,
                    padding=20,
                    alignment=ft.alignment.center,
                    border_radius=10,
                ),
                ft.Container(
                    height=3,
                    bgcolor=ft.Colors.WHITE70,
                    margin=ft.margin.only(bottom=20, top=5),
                ),
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.ADD),
                                    ft.Text("Agregar Usuario")
                                ]),
                                on_click=abrir_ventana_crear_usuario
                            ),
                            width=200,
                            padding=ft.padding.symmetric(horizontal=5, vertical=20)
                        ),
                        ft.Container(
                            content=ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.SEARCH),
                                    ft.Text("Buscar Usuario")
                                ])
                            ),
                            width=200,
                            padding=ft.padding.symmetric(horizontal=5, vertical=20)
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=20
                ),
                ft.Row(
                    controls=[
                        ft.Container(
                            ref=tabla_container,
                            content=mostrar_tabla_usuarios(page, usuarios, actualizar_tabla),
                            padding=ft.padding.symmetric(horizontal=5, vertical=20),
                            height=800,  # Altura fija para activar el scroll interno de la tabla
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.START
                )            
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )

    contenido.content = construir_vista_usuario(usuarios_iniciales)