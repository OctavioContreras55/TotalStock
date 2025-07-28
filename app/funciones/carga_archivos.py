import polars as pd
import flet as ft
from conexiones.firebase import db

def cargar_archivo_excel(ruta_archivo):
    archivo = pd.read_excel(ruta_archivo)
    productos = []
    for row in archivo.iter_rows(named=True):
        producto = {
            "modelo": row["Modelo"],
            "tipo": row["Tipo"],
            "nombre": row["Nombre"],
            "precio": row["Precio"],
            "cantidad": row["Cantidad"]
        }
        productos.append(producto)
    return productos

def guardar_productos_en_firebase(productos, page):
    
    mensaje_cargando = ft.AlertDialog(
        title=ft.Text("Aviso"),
        content= ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("Importando productos..."),
                    ft.ProgressRing(width=14, height=14, stroke_width=2, color=ft.Colors.BLUE_300)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=ft.Padding(20, 20, 10, 20),
        ),
        modal=True,
        
    )
    page.open(mensaje_cargando)
    page.update()
    
    mensaje_exito = ft.AlertDialog(
        title=ft.Text("Productos importados correctamente"),
        actions=[ft.TextButton("Aceptar", on_click=lambda e: page.close(mensaje_exito))],
        modal=True,
    )
    
    try:
        referencia_productos = db.collection("productos")
        for producto in productos:
            try:
                id_documento = f"{producto['modelo']}"
                doc_ref = referencia_productos.document(id_documento)
                doc_snapshot = doc_ref.get()
                if not all(key in producto for key in ["modelo", "tipo", "nombre", "precio", "cantidad"]):
                    print(f"Producto {producto} no tiene todos los campos requeridos.")
                    continue
                if doc_snapshot.exists:
                    print(f"El producto con ID: {id_documento} ya existe en Firebase. Se actualizará.")
                    doc_ref.set(producto)
                else:
                    doc_ref.set(producto)

            except Exception as e:
                print(f"Error al guardar el producto {producto['modelo']}: {e}")
        page.close(mensaje_cargando)
        page.open(mensaje_exito)
    except Exception as e:
        print(f"Error al conectar con Firebase: {e}")
        return False

def on_click_importar_archivo(page):

    productos_importados = []
    def picked_file(e: ft.FilePickerResultEvent):

        if e.files:
            ruta = e.files[0].path
            productos = cargar_archivo_excel(ruta)
            # Aquí puedes actualizar la tabla con los nuevos productos
            productos_importados.clear()
            productos_importados.extend(productos)
            selected_file.value = e.files[0].name
        else:
            selected_file.value = "No se ha seleccionado ningun archivo"
        selected_file.update()
        
    pick_files_window = ft.FilePicker(on_result=picked_file)
    selected_file = ft.TextField(label="Archivo seleccionado", width=250, read_only=True)
    page.overlay.append(pick_files_window)
    
    ventana = ft.AlertDialog(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "Seleccionar archivo",
                                icon=ft.Icons.FOLDER_OPEN,
                                on_click=lambda e: pick_files_window.pick_files(allow_multiple=False),
                            ),
                            selected_file,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        spacing=10,
                    ),
                    padding=ft.Padding(10, 10, 10, 10),
                ),
                ft.Container(
                    content=ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    "Importar",
                                    on_click=lambda e: [page.close(ventana), guardar_productos_en_firebase(productos_importados, page)],
                                    width=100,
                                    height=40,
                                ),
                                ft.ElevatedButton(
                                    "Cancelar",
                                    on_click=lambda e: page.close(ventana),
                                    width=100,
                                    height=40,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            spacing=10,
                        ),
                    padding=ft.Padding(10, 10, 10, 10),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            width=500,
            height=150,
        ),
        modal=True, 
        title=ft.Text("Importar Productos"), 
        actions_alignment=ft.MainAxisAlignment.END, 
    )

    page.open(ventana)
    page.update()
    
    
