import flet as ft
from app.utils.temas import GestorTemas
from app.utils.configuracion import GestorConfiguracionUsuario
from app.funciones.sesiones import SesionManager
import asyncio

def vista_configuracion(nombre_seccion, contenido, page):
    tema = GestorTemas.obtener_tema()
    
    def mostrar_mensaje_guardado():
        """Muestra un mensaje temporal de que se guardó la configuración"""
        snack = ft.SnackBar(
            content=ft.Text("[OK] Tema guardado correctamente para tu usuario", color="#FFFFFF"),
            bgcolor=tema.SUCCESS_COLOR,
            duration=2000
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()
    
    def cambiar_tema_handler(e):
        # Obtener el tema seleccionado
        nuevo_tema = e.control.value
        
        # Cambiar el tema para el usuario actual y guardarlo
        GestorTemas.cambiar_tema(nuevo_tema)
        
        # Mostrar mensaje de confirmación
        mostrar_mensaje_guardado()
        
        # Reiniciar la vista principal para aplicar el nuevo tema
        asyncio.run(recargar_vista_principal())
    
    async def recargar_vista_principal():
        from app.ui.principal import principal_view
        page.controls.clear()
        await principal_view(page)
        page.update()
    
    # Crear el selector de tema
    selector_tema = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="oscuro", label="Tema Oscuro", label_style=ft.TextStyle(color=tema.TEXT_COLOR)),
            ft.Radio(value="azul", label="Tema Azul Claro", label_style=ft.TextStyle(color=tema.TEXT_COLOR)),
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
                                                   color=tema.TEXT_COLOR, 
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
            
            # Información de configuraciones guardadas
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.ANALYTICS, color=tema.PRIMARY_COLOR, size=24),
                                ft.Text("Monitor Firebase", 
                                       size=20, 
                                       color=tema.TEXT_COLOR,
                                       weight=ft.FontWeight.BOLD),
                            ],
                            spacing=10
                        ),
                        ft.Container(height=10),
                        ft.Text("[CHART] Monitoreo en tiempo real del uso de Firebase", 
                               color=tema.TEXT_SECONDARY),
                        ft.Text("[BUSCAR] Revisa la consola para ver las consultas en tiempo real", 
                               color=tema.TEXT_SECONDARY),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.ASSESSMENT, color=tema.ICON_BTN_COLOR),
                                ft.Text("Ver Reporte Detallado", color=tema.BUTTON_TEXT)
                            ]),
                            style=ft.ButtonStyle(
                                bgcolor=tema.BUTTON_BG,
                                color=tema.BUTTON_TEXT,
                                shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                            ),
                            on_click=lambda e: mostrar_reporte_firebase()
                        )
                    ]
                ),
                bgcolor=tema.CARD_COLOR,
                padding=30,
                border_radius=tema.BORDER_RADIUS,
                width=600,
                margin=ft.margin.only(bottom=20)
            ),
            
            # Estado de configuración
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.SAVE, color=tema.PRIMARY_COLOR, size=24),
                                ft.Text("Estado de Configuración", 
                                       size=20, 
                                       color=tema.TEXT_COLOR,
                                       weight=ft.FontWeight.BOLD),
                            ],
                            spacing=10
                        ),
                        ft.Container(height=10),
                        ft.Text("[OK] Las configuraciones se guardan automáticamente", 
                               color=tema.SUCCESS_COLOR),
                        ft.Text(f"[FOLDER] Archivo: data/configuracion.json", 
                               color=tema.TEXT_SECONDARY,
                               size=12),
                        ft.Text(f"[ART] Tema actual: {GestorTemas.obtener_tema_actual().title()}", 
                               color=tema.TEXT_SECONDARY),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.REFRESH, color=tema.ICON_BTN_COLOR),
                                ft.Text("Restablecer configuración", color=tema.BUTTON_TEXT)
                            ]),
                            style=ft.ButtonStyle(
                                bgcolor=tema.WARNING_COLOR,
                                color=tema.BUTTON_TEXT,
                                shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                            ),
                            on_click=lambda e: mostrar_dialogo_reset()
                        )
                    ]
                ),
                bgcolor=tema.CARD_COLOR,
                padding=30,
                border_radius=tema.BORDER_RADIUS,
                width=600,
                margin=ft.margin.only(bottom=20)
            ),
            
            # Futuras configuraciones
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.SETTINGS, color=tema.PRIMARY_COLOR, size=24),
                                ft.Text("Próximas Funcionalidades", 
                                       size=20, 
                                       color=tema.TEXT_COLOR,
                                       weight=ft.FontWeight.BOLD),
                            ],
                            spacing=10
                        ),
                        ft.Container(height=10),
                        ft.Text("[NOTIF] Configuración de notificaciones", 
                               color=tema.TEXT_SECONDARY),
                        ft.Text("🌐 Configuración de idioma", 
                               color=tema.TEXT_SECONDARY),
                        ft.Text("[SAVE] Configuración de respaldos automáticos", 
                               color=tema.TEXT_SECONDARY),
                        ft.Text("[CONFIG] Configuraciones avanzadas del sistema", 
                               color=tema.TEXT_SECONDARY),
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
        spacing=0,
        scroll=True
    )
    
    def mostrar_reporte_firebase():
        """Muestra el reporte detallado de Firebase en la consola"""
        from app.utils.monitor_firebase import monitor_firebase
        monitor_firebase.mostrar_reporte_detallado()
        
        # Mostrar también un snackbar para confirmar
        snack = ft.SnackBar(
            content=ft.Text("[CHART] Reporte mostrado en consola", color="#FFFFFF"),
            bgcolor=tema.SUCCESS_COLOR,
            duration=2000
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()
    
    def mostrar_dialogo_reset():
        """Muestra un diálogo de confirmación para restablecer configuración"""
        def confirmar_reset(e):
            # Restablecer a configuración por defecto para el usuario actual
            usuario_actual = SesionManager.obtener_usuario_actual()
            if usuario_actual and usuario_actual.get('firebase_id'):
                usuario_id = usuario_actual.get('firebase_id')
                GestorConfiguracionUsuario.actualizar_configuracion_usuario(
                    usuario_id,
                    tema="oscuro",
                    notificaciones=True,
                    mostrar_ayuda=True,
                    vista_compacta=False
                )
            GestorTemas.cambiar_tema("oscuro")
            
            # Cerrar diálogo
            dialog.open = False
            page.update()
            
            # Mostrar mensaje y recargar
            snack = ft.SnackBar(
                content=ft.Text("[PROCESO] Configuración restablecida", color="#FFFFFF"),
                bgcolor=tema.WARNING_COLOR,
                duration=2000
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()
            
            asyncio.run(recargar_vista_principal())
        
        def cancelar_reset(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Restablecer Configuración"),
            content=ft.Text("¿Estás seguro de que quieres restablecer toda la configuración a los valores por defecto?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar_reset),
                ft.TextButton("Restablecer", on_click=confirmar_reset, style=ft.ButtonStyle(color=tema.WARNING_COLOR)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
