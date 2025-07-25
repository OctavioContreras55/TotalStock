import pandas as pd
import flet as ft

def cargar_archivo_excel(ruta_archivo):
    archivo = pd.read_excel(ruta_archivo)
    productos = []
    for _, row in archivo.iterrows():
        producto = {
            "id": row["ID"],
            "nombre": row["Nombre"],
            "precio": row["Precio"],
            "cantidad": row["Cantidad"]
        }
        productos.append(producto)
    print(producto)
    return productos

def guardar_productos_en_firebase(productos):
    # Aquí va la lógica para guardar cada producto en Firebase
    pass

def on_click_importar_archivo(page, actualizar_tabla_productos):

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
                                    on_click=lambda e: [page.close(ventana), guardar_productos_en_firebase(productos_importados)],
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
    
    
