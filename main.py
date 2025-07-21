import flet as ft
from app.ui_login import login_view
from app.ui_principal import principal_view
from conexiones.firebase_database import db  # Importar la conexión a Firestore

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK  # Establece el modo de tema
    page.window.maximized = True
    page.window.resizable = True
    page.title = "TotalStock: Sistema de Inventario"

    #Función a ejecutar al iniciar sesión correctamente
    def cargar_pantalla_principal():
        page.controls.clear()               # <-- limpiar la pantalla
        principal_view(page)                # <-- mostrar vista principal
        page.update()
    
    #Prueba de conexión a Firestore
    def obtener_productos():
        productos_ref = db.collection('productos')
        docs = productos_ref.stream()

        for doc in docs:
            print(f'{doc.id} => {doc.to_dict()}')
        
    #Mostrar la vista de login
    login_view(page, on_login_success=cargar_pantalla_principal)
    obtener_productos()  # Llamada para probar la conexión a Firestore
#Ejecutar la aplicación Flet como escritorio
ft.app(target=main)