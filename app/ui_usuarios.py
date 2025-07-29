import flet as ft
from app.tablas.ui_tabla_usuarios import mostrar_tabla_usuarios
from app.crud_usuarios.create_usuarios import mostrar_ventana_crear_usuario, obtener_usuarios_firebase
from app.utils.temas import GestorTemas
import asyncio
from app.ui.barra_carga import vista_carga

async def vista_usuarios(nombre_seccion, contenido, page=None):
    tema = GestorTemas.obtener_tema()
    contenido.content = vista_carga()  # Mostrar barra de carga mientras se carga la vista
    await obtener_usuarios_firebase()  # Cargar usuarios desde Firebase
    page.update()  # Actualizar la página para mostrar la barra de carga
    # Si no se pasa la página, intentar obtenerla del contenido
    if page is None:
        page = contenido.page
    
    usuarios_actuales = []  # Variable para mantener los usuarios actuales
    # Obtener usuarios iniciales
    try:
        usuarios_iniciales = await obtener_usuarios_firebase()
        usuarios_actuales = usuarios_iniciales  # Inicializar usuarios actuales
    except Exception as e:
        print(f"Error al obtener usuarios iniciales: {e}")
        usuarios_iniciales = []
        usuarios_actuales = []
    
    async def actualizar_tabla(): # Función para actualizar la tabla con datos de Firebase
        nonlocal usuarios_actuales # Esto es para que podamos modificar la variable usuarios_actuales
        try:
            print("Actualizando tabla usuarios")
            contenido.content = vista_carga()
            page.update()
            usuarios_actuales = await obtener_usuarios_firebase()
            contenido.content = construir_vista_usuario(usuarios_actuales)
            page.update()
        except Exception as e:
            print(f"Error al actualizar tabla: {e}")
            usuarios_actuales = []
            contenido.content = construir_vista_usuario([])  # Muestra la vista con tabla vacía
            page.update()
    
    def abrir_ventana_crear_usuario(e): # Función para abrir la ventana de crear usuario
        try:
            mostrar_ventana_crear_usuario(page, actualizar_tabla)
            print("Ventana de crear usuario llamada exitosamente")  # Debug
        except Exception as error:
            print(f"Error al abrir ventana: {error}")  # Debug
    
    def construir_vista_usuario(usuarios):
        return ft.Container(
          content=ft.Column(
              controls=[
                  ft.Container(
                      content=ft.Row(
                          controls=[
                              ft.Column(
                                  controls=[
                                      ft.Text(f"Bienvenido a la vista de {nombre_seccion}", size=24, color=tema.TEXT_COLOR),
                                      ft.Text("Gestión de los usuarios del sistema", size=16, color=tema.TEXT_SECONDARY),
                                  ],
                                  alignment=ft.MainAxisAlignment.START,
                                  horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                              ),
          
                          ],
                          alignment=ft.MainAxisAlignment.CENTER,
                          vertical_alignment=ft.CrossAxisAlignment.START
                      ),
                      width=600,
                      bgcolor=tema.CARD_COLOR,
                      padding=20,
                      alignment=ft.alignment.center,
                      border_radius=tema.BORDER_RADIUS,
                  ),
                  ft.Container(
                      height=3,
                      bgcolor=tema.DIVIDER_COLOR,
                      margin=ft.margin.only(bottom=20, top=5),
                  ),
                  ft.Row(
                      controls=[
                          ft.Container(
                              content=ft.ElevatedButton(
                                  content=ft.Row([
                                      ft.Icon(ft.Icons.ADD, color=tema.PRIMARY_COLOR),
                                      ft.Text("Agregar Usuario", color=tema.BUTTON_TEXT)
                                  ]),
                                  style=ft.ButtonStyle(
                                      bgcolor=tema.BUTTON_BG,
                                      color=tema.BUTTON_TEXT,
                                      shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                  ),
                                  on_click=abrir_ventana_crear_usuario
                              ),
                              width=200,
                              padding=ft.padding.symmetric(horizontal=5, vertical=20)
                          ),
                          ft.Container(
                              content=ft.ElevatedButton(
                                  content=ft.Row([
                                      ft.Icon(ft.Icons.SEARCH, color=tema.PRIMARY_COLOR),
                                      ft.Text("Buscar Usuario", color=tema.BUTTON_TEXT)
                                  ]),
                                  style=ft.ButtonStyle(
                                      bgcolor=tema.BUTTON_BG,
                                      color=tema.BUTTON_TEXT,
                                      shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                  )
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
                              
                              content=mostrar_tabla_usuarios(page, usuarios, actualizar_tabla),
                              padding=ft.padding.symmetric(horizontal=5, vertical=20),
                          )
                      ],
                      alignment=ft.MainAxisAlignment.CENTER,
                      vertical_alignment=ft.CrossAxisAlignment.START
                  )            
              ],
              alignment=ft.MainAxisAlignment.START,
              horizontal_alignment=ft.CrossAxisAlignment.CENTER,
          ),
          padding=ft.padding.only(bottom=40),  # Espacio abajo
          bgcolor=tema.BG_COLOR,
        )

    contenido.content = construir_vista_usuario(usuarios_iniciales)