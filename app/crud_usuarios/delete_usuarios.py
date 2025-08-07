import flet as ft
from conexiones.firebase import db
from app.utils.temas import GestorTemas
from app.utils.historial import GestorHistorial
from app.funciones.sesiones import SesionManager
import asyncio
import os
import json


def limpiar_archivos_usuario(id_usuario, nombre_usuario=None):
    """
    Limpia todos los archivos relacionados con un usuario específico.
    
    Args:
        id_usuario (str): ID de Firebase del usuario
        nombre_usuario (str): Nombre del usuario (opcional, para logs)
    
    Returns:
        dict: Diccionario con el resultado de la limpieza
    """
    archivos_eliminados = []
    errores = []
    
    # Lista de archivos que pueden existir para un usuario
    archivos_posibles = [
        f"data/config_usuario_{id_usuario}.json",  # Configuración personal del usuario
        f"data/pendientes_{id_usuario}.json",      # Pendientes personales del usuario
        # Agregar aquí otros archivos específicos del usuario si se crean en el futuro
    ]
    
    for archivo in archivos_posibles:
        try:
            if os.path.exists(archivo):
                os.remove(archivo)
                archivos_eliminados.append(archivo)
                print(f"✅ Archivo eliminado: {archivo}")
            else:
                print(f"ℹ️  Archivo no encontrado: {archivo}")
        except Exception as e:
            error_msg = f"Error al eliminar {archivo}: {str(e)}"
            errores.append(error_msg)
            print(f"❌ {error_msg}")
    
    # Intentar limpiar archivos con nombre de usuario como ID (para retrocompatibilidad)
    if nombre_usuario:
        archivos_nombre = [
            f"data/config_usuario_{nombre_usuario.lower()}.json",
            f"data/pendientes_{nombre_usuario.lower()}.json",
        ]
        
        for archivo in archivos_nombre:
            try:
                if os.path.exists(archivo):
                    os.remove(archivo)
                    archivos_eliminados.append(archivo)
                    print(f"✅ Archivo legacy eliminado: {archivo}")
            except Exception as e:
                error_msg = f"Error al eliminar archivo legacy {archivo}: {str(e)}"
                errores.append(error_msg)
                print(f"❌ {error_msg}")
    
    resultado = {
        "archivos_eliminados": archivos_eliminados,
        "errores": errores,
        "total_eliminados": len(archivos_eliminados),
        "total_errores": len(errores)
    }
    
    return resultado




async def eliminar_usuario_firebase(id_usuario): #Se manda a llamar en on_eliminar_click
    try:
        # Obtener datos del usuario antes de eliminarlo
        doc_ref = db.collection('usuarios').document(id_usuario)
        doc = doc_ref.get()
        usuario_nombre = "usuario"
        
        if doc.exists:
            usuario_data = doc.to_dict()
            usuario_nombre = usuario_data.get('nombre', 'usuario')
        else:
            print(f"❌ Usuario con ID {id_usuario} no encontrado en Firebase")
            return False
        
        # Limpiar archivos relacionados con el usuario ANTES de eliminarlo de Firebase
        print(f"🧹 Limpiando archivos del usuario '{usuario_nombre}' (ID: {id_usuario})...")
        resultado_limpieza = limpiar_archivos_usuario(id_usuario, usuario_nombre)
        
        # Eliminar el usuario de Firebase
        doc_ref.delete()
        print(f"✅ Usuario '{usuario_nombre}' eliminado de Firebase")
        
        # Registrar actividad en el historial con información de limpieza
        gestor_historial = GestorHistorial()
        usuario_actual = SesionManager.obtener_usuario_actual()
        
        descripcion_detallada = f"Eliminó usuario '{usuario_nombre}' (ID: {id_usuario})"
        if resultado_limpieza["total_eliminados"] > 0:
            descripcion_detallada += f" - Archivos limpiados: {resultado_limpieza['total_eliminados']}"
        if resultado_limpieza["total_errores"] > 0:
            descripcion_detallada += f" - Errores en limpieza: {resultado_limpieza['total_errores']}"
        
        await gestor_historial.agregar_actividad(
            tipo="eliminar_usuario",
            descripcion=descripcion_detallada,
            usuario=usuario_actual.get('username', 'Usuario') if usuario_actual else 'Sistema'
        )
        
        # Mostrar resumen de la limpieza
        print(f"📊 Resumen de eliminación:")
        print(f"   - Usuario eliminado de Firebase: ✅")
        print(f"   - Archivos eliminados: {resultado_limpieza['total_eliminados']}")
        print(f"   - Errores en limpieza: {resultado_limpieza['total_errores']}")
        
        if resultado_limpieza["archivos_eliminados"]:
            print(f"   - Archivos limpiados: {', '.join(resultado_limpieza['archivos_eliminados'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al eliminar usuario: {str(e)}")
        return False
    
    
async def on_eliminar_click(e, page, id_usuario, actualizar_tabla): #Se manda a llamar desde el botón de eliminar en la tabla de usuarios
    if await eliminar_usuario_firebase(id_usuario):
        print("✅ Usuario eliminado exitosamente.")
        
        # Invalidar cache para futuras consultas
        from app.utils.cache_firebase import cache_firebase
        cache_firebase._cache_usuarios = []
        cache_firebase._ultimo_update_usuarios = None
        print("🗑️ Cache de usuarios invalidado")
        
        # ACTUALIZACIÓN AUTOMÁTICA: Recargar tabla después de eliminar
        if actualizar_tabla:
            print("⚡ Ejecutando actualización automática después de eliminar usuario")
            try:
                await actualizar_tabla(forzar_refresh=True)  # Forzar refresh desde Firebase
            except Exception as e:
                print(f"Error en actualización automática: {e}")
        else:
            print("⚠️ No hay callback de actualización disponible")
            page.update()
        
        page.open(ft.SnackBar(ft.Text("Usuario eliminado exitosamente."), duration=2000))
    else:
        print("❌ Error al eliminar usuario.")
        page.open(ft.SnackBar(ft.Text("Error al eliminar usuario."), duration=2000))


def mensaje_confirmacion(page, id_usuario, actualizar_tabla): # Se manda a llamar desde el botón de eliminar en la tabla de usuarios
    tema = GestorTemas.obtener_tema()
    print(f"Se llamó a mensaje_confirmacion para ID: {id_usuario}")

    async def confirmar_async(e):
        page.close(dialog)
        await on_eliminar_click(e, page, id_usuario, actualizar_tabla)

    def confirmar(e):
        page.run_task(confirmar_async, e)

    def cerrar_dialogo(page):
        page.close(dialog)
        page.update()
        
    dialog = ft.AlertDialog(
        modal=True, 
        title=ft.Text("⚠️ Confirmación de eliminación", color=tema.ERROR_COLOR, weight=ft.FontWeight.BOLD),
        content=ft.Column([
            ft.Text("¿Estás seguro de eliminar este usuario?", color=tema.TEXT_COLOR, weight=ft.FontWeight.BOLD),
            ft.Text("Esta acción eliminará:", color=tema.TEXT_SECONDARY, size=14),
            ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.PERSON_REMOVE, color=tema.ERROR_COLOR, size=16),
                    ft.Text("Usuario de Firebase", color=tema.TEXT_SECONDARY, size=12)
                ], spacing=5),
                ft.Row([
                    ft.Icon(ft.Icons.SETTINGS, color=tema.WARNING_COLOR, size=16),
                    ft.Text("Configuraciones personales", color=tema.TEXT_SECONDARY, size=12)
                ], spacing=5),
                ft.Row([
                    ft.Icon(ft.Icons.TASK, color=tema.WARNING_COLOR, size=16),
                    ft.Text("Pendientes personales", color=tema.TEXT_SECONDARY, size=12)
                ], spacing=5),
            ], spacing=3),
            ft.Text("⚠️ Esta acción no se puede deshacer", color=tema.ERROR_COLOR, size=12, italic=True),
        ], 
        spacing=10,
        tight=True
        ),
        bgcolor=tema.CARD_COLOR,
        actions=[
            ft.TextButton("Cancelar", 
                         style=ft.ButtonStyle(color=tema.TEXT_SECONDARY),
                         on_click=lambda e: cerrar_dialogo(page)),
            ft.TextButton("Eliminar Usuario", 
                         style=ft.ButtonStyle(
                             color=ft.Colors.WHITE,
                             bgcolor=tema.ERROR_COLOR
                         ),
                         on_click=confirmar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.open(dialog)
    page.update()

