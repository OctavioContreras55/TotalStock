import flet as ft
import re #librería para expresiones regulares
import time #librería para manejar tiempo
import threading #librería para manejar hilos
from conexiones.firebase import db  # Importar la conexión a Firestore

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
        
        print(f"Usuario '{nombre}' creado exitosamente con ID: {doc_ref[1].id}")
        return True, doc_ref[1].id
        
    except Exception as e:
        print(f"Error al crear usuario: {str(e)}")
        return False, str(e)

def obtener_usuarios_firebase(): # Función para obtener todos los usuarios de Firebase
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

    
    # Guardar el contenido actual de la página
    contenido_original = page.controls.copy()
    
    # Campos del formulario
    campo_nombre = ft.TextField(
        label="Nombre de usuario",
        width=300,
        border_color=ft.Colors.BLUE_400
    )
    
    campo_contrasena = ft.TextField(
        label="Contraseña",
        width=300,
        password=True,
        can_reveal_password=True,
        border_color=ft.Colors.BLUE_400
    )
    
    campo_es_admin = ft.Checkbox(
        label="Es administrador",
        value=False
    )
    
    mensaje_estado = ft.Text("", color=ft.Colors.RED_400, size=12)
    
    def crear_usuario_click(e):

        # Validar campos
        if not campo_nombre.value or not campo_contrasena.value:
            mensaje_estado.value = "Por favor, completa todos los campos"
            mensaje_estado.color = ft.Colors.RED_400
            page.update()
            return
        
        if not re.fullmatch(r'[A-Za-z0-9]{6,}', campo_contrasena.value): # Valida que la contraseña tenga al menos 6 caracteres y solo letras y números
            #La r es para indicar que es una expresión regular o sea que se toman literalmente los caracteres
            mensaje_estado.value = "La contraseña debe tener al menos 6 caracteres y solo letras y números"
            mensaje_estado.color = ft.Colors.RED_400
            page.update()
            return
            
        # Crear usuario
        exito, resultado = crear_usuario_firebase(
            campo_nombre.value,
            campo_contrasena.value,
            campo_es_admin.value
        )
        
        if exito:
            mensaje_estado.value = "Usuario creado exitosamente"
            mensaje_estado.color = ft.Colors.GREEN_400
            page.update()
            
            # Esperar un momento y restaurar la vista
            def restaurar_vista():
                time.sleep(1.5)
                # Restaurar contenido original
                page.controls.clear()
                page.controls.extend(contenido_original)
                page.update()
                # Actualizar la tabla si se proporciona el callback
                if callback_actualizar_tabla:
                    callback_actualizar_tabla()
            
            threading.Thread(target=restaurar_vista, daemon=True).start()
        else:
            mensaje_estado.value = f"Error: {resultado}"
            mensaje_estado.color = ft.Colors.RED_400
            page.update()
    
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
                                                        color=ft.Colors.WHITE)
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER
                                        ),
                                        ft.Divider(color=ft.Colors.BLUE_400),
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
                                                    bgcolor=ft.Colors.GREY_600,
                                                    color=ft.Colors.WHITE,
                                                    width=120
                                                ),
                                                ft.ElevatedButton(
                                                    "Crear Usuario",
                                                    on_click=crear_usuario_click,
                                                    bgcolor=ft.Colors.BLUE_600,
                                                    color=ft.Colors.WHITE,
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
                                bgcolor=ft.Colors.GREY_900,
                                padding=ft.padding.all(30),
                                border_radius=15,
                                width=450,
                                border=ft.border.all(2, ft.Colors.BLUE_400),
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
        expand=True
    )
    
    # Reemplazar todo el contenido de la página

    page.controls.clear()
    page.controls.append(ventana_registro)
    page.update()