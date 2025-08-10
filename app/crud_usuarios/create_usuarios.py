import flet as ft
import re #librería para expresiones regulares
import threading #librería para manejar hilos
from conexiones.firebase import db  # Importar la conexión a Firestore
from app.utils.temas import GestorTemas
from app.utils.historial import GestorHistorial
from app.funciones.sesiones import SesionManager
import asyncio

def crear_usuario_firebase(nombre, contrasena, es_admin=False): # Función para crear un usuario en Firebase
    try: # try para manejar errores
        referencia_usuarios = db.collection('usuarios') # Crear referencia a la colección de usuarios
        
        # Crear un nuevo usuario
        nuevo_usuario = {
            'nombre': nombre,
            'contrasena': contrasena,
            'es_admin': es_admin
        }
        
        # Agregar el usuario a Firebase
        doc_ref = referencia_usuarios.add(nuevo_usuario)
        
        # Crear objeto completo del usuario con firebase_id para devolverlo
        usuario_creado = nuevo_usuario.copy()
        usuario_creado['firebase_id'] = doc_ref[1].id
        
        print(f"Usuario '{nombre}' creado exitosamente con ID: {doc_ref[1].id}")
        return usuario_creado  # Devolver el objeto completo del usuario
        
    except Exception as e:
        print(f"Error al crear usuario: {str(e)}")
        return False

async def obtener_usuarios_firebase(): # Función para obtener todos los usuarios de Firebase
    try:
        referencia_usuarios = db.collection('usuarios')
        usuarios = referencia_usuarios.stream() #stream para obtener los documentos
        
        lista_usuarios = []
        for i, usuario in enumerate(usuarios, start=1): # Enumerar para asignar ID secuencial
            data = usuario.to_dict() # Convertir el documento a diccionario
            
            # Validar y asignar valores por defecto para campos faltantes
            data['id'] = i  # Asignar un ID secuencial para la tabla
            data['firebase_id'] = usuario.id  # Guardar el ID real de Firebase
            data['nombre'] = data.get('nombre', 'Sin nombre')  # Valor por defecto si no existe
            data['contrasena'] = data.get('contrasena', '')  # Valor por defecto si no existe
            data['es_admin'] = data.get('es_admin', False)  # Valor por defecto si no existe
            
            lista_usuarios.append(data)
            
        return lista_usuarios
        
    except Exception as e:
        print(f"Error al obtener usuarios: {str(e)}")
        return []

def mostrar_ventana_crear_usuario(page, callback_actualizar_tabla=None): # Función para mostrar la ventana flotante de crear usuario
    tema = GestorTemas.obtener_tema()
    
    # Guardar el contenido actual de la página
    contenido_original = page.controls.copy()
    
    # Campos del formulario
    campo_nombre = ft.TextField(
        label="Nombre de usuario",
        width=300,
        border_color=tema.INPUT_BORDER,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    
    campo_contrasena = ft.TextField(
        label="Contraseña",
        width=300,
        password=True,
        can_reveal_password=True,
        border_color=tema.INPUT_BORDER,
        bgcolor=tema.INPUT_BG,
        color=tema.TEXT_COLOR,
        focused_border_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_SECONDARY)
    )
    
    campo_es_admin = ft.Checkbox(
        label="Es administrador",
        value=False,
        check_color=tema.PRIMARY_COLOR,
        label_style=ft.TextStyle(color=tema.TEXT_COLOR)
    )
    
    mensaje_estado = ft.Text("", color=tema.ERROR_COLOR, size=12)
    
    async def crear_usuario_click(e):
        # Función síncrona que llama a la async internamente

        # Validar campos
        if not campo_nombre.value or not campo_contrasena.value:
            mensaje_estado.value = "Por favor, completa todos los campos"
            mensaje_estado.color = tema.ERROR_COLOR
            page.update()
            return
        
        if not re.fullmatch(r'[A-Za-z0-9]{6,}', campo_contrasena.value): # Valida que la contraseña tenga al menos 6 caracteres y solo letras y números
            #La r es para indicar que es una expresión regular o sea que se toman literalmente los caracteres
            mensaje_estado.value = "La contraseña debe tener al menos 6 caracteres y solo letras y números"
            mensaje_estado.color = tema.ERROR_COLOR
            page.update()
            return
            
        # Crear usuario
        resultado = crear_usuario_firebase(
            campo_nombre.value,
            campo_contrasena.value,
            campo_es_admin.value
        )
        
        if resultado and isinstance(resultado, dict):
            # Invalidar cache para asegurar datos frescos
            from app.utils.cache_firebase import cache_firebase
            cache_firebase._cache_usuarios = []
            cache_firebase._ultimo_update_usuarios = None
            print("[ELIMINAR] Cache de usuarios invalidado después de crear")
            
            # Registrar actividad en el historial
            gestor_historial = GestorHistorial()
            usuario_actual = SesionManager.obtener_usuario_actual()
            
            # Llamar directamente con await en lugar de page.run_task
            try:
                await gestor_historial.agregar_actividad(
                    tipo="crear_usuario",
                    descripcion=f"Creó nuevo usuario '{campo_nombre.value}' (Admin: {'Sí' if campo_es_admin.value else 'No'})",
                    usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
                )
                
                # Actualizar dashboard dinámicamente
                from app.utils.actualizador_dashboard import actualizar_dashboard
                try:
                    await actualizar_dashboard()
                    print("[OK] Dashboard actualizado automáticamente")
                except Exception as e:
                    print(f"[WARN] Error al actualizar dashboard: {e}")
                    # No fallar si el dashboard no se puede actualizar
                
            except Exception as e:
                print(f"Error al registrar actividad: {e}")
            
            mensaje_estado.value = "Usuario creado exitosamente"
            mensaje_estado.color = tema.SUCCESS_COLOR
            page.update()
            
            # Esperar un momento y restaurar la vista
            async def restaurar_vista(): # Función para restaurar la vista original
                await asyncio.sleep(2)
                page.controls.clear()
                page.controls.extend(contenido_original)
                page.update()
                
                # ACTUALIZACIÓN AUTOMÁTICA: Recargar tabla después de crear usuario
                if callback_actualizar_tabla:
                    print("[RAPIDO] Ejecutando actualización automática después de crear usuario")
                    try:
                        await callback_actualizar_tabla(forzar_refresh=True)  # Forzar refresh desde Firebase
                    except Exception as e:
                        print(f"Error en actualización automática: {e}")
                else:
                    print("[WARN] No hay callback de actualización disponible")

            # Usar página run_task con una corrutina
            page.run_task(restaurar_vista)
        else:
            mensaje_estado.value = f"Error al crear usuario"
            mensaje_estado.color = tema.ERROR_COLOR
            page.update()
    
    # Función wrapper para el botón
    async def manejar_click_crear():
        await crear_usuario_click(None)
    
    def cancelar_click(e):
        print("Cancelar presionado")  # Debug
        # Restaurar contenido original
        page.controls.clear()
        page.controls.extend(contenido_original)
        page.update()
    
    # Crear la ventana modal completa
    ventana_registro = ft.Container(
        content=ft.Column(
            controls=[
                # Fondo oscuro
                ft.Container(
                    bgcolor=ft.Colors.BLACK54,
                    expand=True,
                    content=ft.Column(
                        controls=[
                            ft.Container(height=100),  # Espaciado superior
                            # Ventana del formulario
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Text("Crear Nuevo Usuario", 
                                                        size=24, 
                                                        weight=ft.FontWeight.BOLD,
                                                        color=tema.TEXT_COLOR)
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER
                                        ),
                                        ft.Divider(color=tema.PRIMARY_COLOR),
                                        campo_nombre,
                                        campo_contrasena,
                                        campo_es_admin,
                                        mensaje_estado,
                                        ft.Container(height=20),  # Espaciado
                                        ft.Row(
                                            controls=[
                                                ft.ElevatedButton(
                                                    "Cancelar",
                                                    on_click=cancelar_click,
                                                    style=ft.ButtonStyle(
                                                        bgcolor=tema.BUTTON_BG,
                                                        color=tema.BUTTON_TEXT,
                                                        shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                                    ),
                                                    width=120
                                                ),
                                                ft.ElevatedButton(
                                                    "Crear Usuario",
                                                    on_click=lambda e: page.run_task(manejar_click_crear),
                                                    style=ft.ButtonStyle(
                                                        bgcolor=tema.BUTTON_PRIMARY_BG,
                                                        color=tema.BUTTON_TEXT,
                                                        shape=ft.RoundedRectangleBorder(radius=tema.BORDER_RADIUS)
                                                    ),
                                                    width=140
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            spacing=20
                                        )
                                    ],
                                    spacing=20,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                ),
                                bgcolor=tema.CARD_COLOR,
                                padding=ft.padding.all(30),
                                border_radius=tema.BORDER_RADIUS,
                                width=450,
                                border=ft.border.all(2, tema.PRIMARY_COLOR),
                                shadow=ft.BoxShadow(
                                    spread_radius=1,
                                    blur_radius=15,
                                    color=ft.Colors.BLACK54,
                                    offset=ft.Offset(0, 4)
                                )
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                )
            ],
            expand=True
        ),
        expand=True,
        bgcolor=tema.BG_COLOR
    )
    
    # Reemplazar todo el contenido de la página

    page.controls.clear()
    page.controls.append(ventana_registro)
    page.update()