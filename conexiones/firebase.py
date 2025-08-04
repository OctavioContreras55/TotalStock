import firebase_admin
from firebase_admin import credentials, firestore
import os
import sys

def obtener_ruta_recurso(ruta_relativa):
    """Obtiene la ruta correcta para recursos, tanto en desarrollo como en ejecutable"""
    try:
        # PyInstaller crea una carpeta temporal _MEIPASS cuando ejecuta
        ruta_base = sys._MEIPASS
    except AttributeError:
        # En desarrollo, usar la ruta actual
        ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(ruta_base, ruta_relativa)

# Obtener ruta correcta para las credenciales
ruta_credenciales = obtener_ruta_recurso("conexiones/credenciales_firebase.json")

try:
    credenciales = credentials.Certificate(ruta_credenciales) # Credenciales de Firebase
    print(f"✅ Credenciales Firebase cargadas desde: {ruta_credenciales}")
except FileNotFoundError:
    print(f"❌ Error: No se encontraron las credenciales en: {ruta_credenciales}")
    print("💡 Asegúrate de que el archivo credenciales_firebase.json esté en la carpeta conexiones/")
    raise

if not firebase_admin._apps: # Verifica si ya se ha inicializado la app
    firebase_admin.initialize_app(credenciales) # Inicializar Firebase Admin SDK

db = firestore.client() # Inicializar Firestore