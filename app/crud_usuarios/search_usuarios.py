import flet as ft
from app.utils.temas import GestorTemas
import asyncio

async def mostrar_dialogo_busqueda_usuarios(page, actualizar_tabla_usuarios=None):
    """Mostrar diálogo de búsqueda de usuarios"""
    tema = GestorTemas.obtener_tema()
    
    campo_busqueda = ft.TextField(
        label="Buscar por nombre o username",
        width=300,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        border_color=tema.INPUT_BORDER,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    
    # Contenedor para mostrar indicador de carga
    contenedor_carga = ft.Container(
        content=ft.Row([
            ft.ProgressRing(width=16, height=16, stroke_width=2, color=tema.PRIMARY_COLOR),
            ft.Text("Buscando usuarios...", color=tema.TEXT_COLOR, size=14)
        ], alignment=ft.MainAxisAlignment.CENTER),
        visible=False,
        height=0
    )
    
    async def buscar_usuarios_handler(e):
        """Manejar búsqueda de usuarios"""
        termino = campo_busqueda.value.strip()
        if not termino:
            page.open(ft.SnackBar(
                content=ft.Text("Ingrese un término de búsqueda", color=tema.TEXT_COLOR),
                bgcolor=tema.WARNING_COLOR
            ))
            return
        
        # Mostrar indicador de carga
        contenedor_carga.visible = True
        contenedor_carga.height = 30
        page.update()
        
        try:
            usuarios_encontrados = await buscar_usuarios_firebase(termino)
            
            # Ocultar indicador de carga
            contenedor_carga.visible = False
            contenedor_carga.height = 0
            page.update()
            
            if usuarios_encontrados:
                page.close(dialogo_busqueda)
                page.open(ft.SnackBar(
                    content=ft.Text(f"Se encontraron {len(usuarios_encontrados)} usuarios", color=tema.TEXT_COLOR),
                    bgcolor=tema.SUCCESS_COLOR
                ))
                if actualizar_tabla_usuarios:
                    await actualizar_tabla_usuarios(usuarios_encontrados)
            else:
                page.open(ft.SnackBar(
                    content=ft.Text("No se encontraron usuarios con ese término", color=tema.TEXT_COLOR),
                    bgcolor=tema.WARNING_COLOR
                ))
                
        except Exception as error:
            # Ocultar indicador de carga
            contenedor_carga.visible = False
            contenedor_carga.height = 0
            page.update()
            
            page.open(ft.SnackBar(
                content=ft.Text(f"Error en la búsqueda: {str(error)}", color=tema.TEXT_COLOR),
                bgcolor=tema.ERROR_COLOR
            ))
    
    dialogo_busqueda = ft.AlertDialog(
        title=ft.Text("Buscar Usuarios", color=tema.TEXT_COLOR),
        bgcolor=tema.CARD_COLOR,
        content=ft.Container(
            content=ft.Column([
                campo_busqueda,
                contenedor_carga,
                ft.ElevatedButton(
                    "Buscar",
                    style=ft.ButtonStyle(
                        bgcolor=tema.BUTTON_PRIMARY_BG,
                        color=tema.BUTTON_TEXT,
                        shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                    ),
                    on_click=buscar_usuarios_handler
                )
            ], spacing=15),
            width=350,
            height=150,
            padding=ft.Padding(10, 10, 10, 10)
        ),
        actions=[
            ft.TextButton("Cerrar", 
                         style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                         on_click=lambda e: page.close(dialogo_busqueda)),
        ]
    )

    page.open(dialogo_busqueda)
    page.update()

async def buscar_usuarios_firebase(termino_busqueda):
    """Buscar usuarios en Firebase por nombre o username"""
    try:
        from app.utils.cache_firebase import cache_firebase
        
        # Obtener usuarios desde cache
        todos_usuarios = await cache_firebase.obtener_usuarios()
        
        # Filtrar localmente
        usuarios_encontrados = []
        termino_lower = termino_busqueda.lower().strip()
        
        for usuario in todos_usuarios:
            # Convertir a string para evitar errores con tipos de datos
            nombre = str(usuario.get('nombre', '')).lower()
            username = str(usuario.get('username', '')).lower()
            email = str(usuario.get('email', '')).lower()
            
            # Buscar en nombre, username y email
            if (termino_lower in nombre or 
                termino_lower in username or 
                termino_lower in email):
                usuarios_encontrados.append(usuario)
        
        return usuarios_encontrados
        
    except Exception as e:
        print(f"Error al buscar usuarios: {e}")
        return []

def buscar_usuarios(page, actualizar_tabla=None):
    """Función de compatibilidad - redirige a la nueva implementación"""
    try:
        page.run_task(mostrar_dialogo_busqueda_usuarios, page, actualizar_tabla)
    except Exception as error:
        print(f"Error al buscar usuarios: {error}")