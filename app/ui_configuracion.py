import flet as ft
from app.utils.temas import GestorTemas
import asyncio

def vista_configuracion(nombre_seccion, contenido, page):
    tema = GestorTemas.obtener_tema()
    
    def cambiar_tema_handler(e):
        # Obtener el tema seleccionado
        nuevo_tema = e.control.value
        
        # Cambiar el tema globalmente
        GestorTemas.cambiar_tema(nuevo_tema)
        
        # Reiniciar la vista principal para aplicar el nuevo tema sin mensaje
        asyncio.run(recargar_vista_principal())
    
    async def recargar_vista_principal():
        from app.ui.principal import principal_view
        page.controls.clear()
        await principal_view(page)
        page.update()
    
    # Crear el selector de tema
    selector_tema = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="oscuro", label="Tema Oscuro"),
            ft.Radio(value="azul", label="Tema Azul Claro"),
        ]),
        value=GestorTemas.obtener_tema_actual(),
        on_change=cambiar_tema_handler
    )
    
    contenido.content = ft.Column(
        controls=[
            # Header de la sección
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(f"Bienvenido a la vista de {nombre_seccion}", 
                                       size=24, color=tema.TEXT_COLOR),
                                ft.Text("Personaliza la apariencia y configuración del sistema", 
                                       size=16, color=tema.TEXT_SECONDARY),
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
                margin=ft.margin.only(bottom=30)
            ),
            
            # Sección de temas
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.PALETTE, color=tema.PRIMARY_COLOR, size=24),
                                ft.Text("Seleccionar Tema", 
                                       size=20, 
                                       color=tema.TEXT_COLOR,
                                       weight=ft.FontWeight.BOLD),
                            ],
                            spacing=10
                        ),
                        ft.Container(height=10),
                        ft.Text("Elige el tema que prefieras para personalizar la interfaz:", 
                               color=tema.TEXT_SECONDARY),
                        ft.Container(height=20),
                        selector_tema,
                        ft.Container(height=20),
                        ft.Row(
                            controls=[
                                # Vista previa del tema oscuro
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Text("Tema Oscuro", 
                                                   color="#FFFFFF", 
                                                   size=14,
                                                   text_align=ft.TextAlign.CENTER),
                                            ft.Container(
                                                bgcolor="#181A1B",
                                                height=60,
                                                border_radius=8,
                                                content=ft.Row(
                                                    controls=[
                                                        ft.Container(
                                                            bgcolor="#23272A",
                                                            width=20,
                                                            height=40,
                                                            border_radius=4
                                                        ),
                                                        ft.Container(
                                                            bgcolor="#7289DA",
                                                            width=30,
                                                            height=20,
                                                            border_radius=4
                                                        )
                                                    ],
                                                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                                                ),
                                                padding=10
                                            )
                                        ],
                                        spacing=5,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                    ),
                                    width=120,
                                    padding=10,
                                    bgcolor=tema.CARD_COLOR,
                                    border_radius=tema.BORDER_RADIUS,
                                    border=ft.border.all(2, "#7289DA" if GestorTemas.obtener_tema_actual() == "oscuro" else tema.INPUT_BORDER)
                                ),
                                
                                ft.Container(width=20),  # Espaciado
                                
                                # Vista previa del tema azul
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Text("Tema Azul", 
                                                   color=tema.TEXT_COLOR, 
                                                   size=14,
                                                   text_align=ft.TextAlign.CENTER),
                                            ft.Container(
                                                bgcolor="#F4F8FC",  # Nuevo color de fondo más suave
                                                height=60,
                                                border_radius=8,
                                                content=ft.Row(
                                                    controls=[
                                                        ft.Container(
                                                            bgcolor="#34495E",  # Nuevo color del sidebar más suave
                                                            width=20,
                                                            height=40,
                                                            border_radius=4
                                                        ),
                                                        ft.Container(
                                                            bgcolor="#5DADE2",  # Nuevo color principal más suave
                                                            width=30,
                                                            height=20,
                                                            border_radius=4
                                                        )
                                                    ],
                                                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                                                ),
                                                padding=10
                                            )
                                        ],
                                        spacing=5,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                    ),
                                    width=120,
                                    padding=10,
                                    bgcolor=tema.CARD_COLOR,
                                    border_radius=tema.BORDER_RADIUS,
                                    border=ft.border.all(2, "#5DADE2" if GestorTemas.obtener_tema_actual() == "azul" else tema.INPUT_BORDER)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        )
                    ],
                    spacing=5
                ),
                bgcolor=tema.CARD_COLOR,
                padding=30,
                border_radius=tema.BORDER_RADIUS,
                width=600,
                margin=ft.margin.only(bottom=20)
            ),
            
            # Otras configuraciones (placeholder para futuras funcionalidades)
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.SETTINGS, color=tema.PRIMARY_COLOR, size=24),
                                ft.Text("Otras Configuraciones", 
                                       size=20, 
                                       color=tema.TEXT_COLOR,
                                       weight=ft.FontWeight.BOLD),
                            ],
                            spacing=10
                        ),
                        ft.Container(height=10),
                        ft.Text("Próximamente disponibles más opciones de configuración...", 
                               color=tema.TEXT_SECONDARY,
                               style=ft.TextStyle(italic=True)),
                    ]
                ),
                bgcolor=tema.CARD_COLOR,
                padding=30,
                border_radius=tema.BORDER_RADIUS,
                width=600
            )
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
        spacing=0
    )
