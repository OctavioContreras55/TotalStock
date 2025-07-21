import sys
import os

# Subir dos niveles desde el archivo actual
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(BASE_DIR)
from conexiones.firebase_database import db  # Importar la conexión a Firestore

def crear_usuarios():
    referencia_usuarios = db.collection('usuarios')

    # Crear un nuevo usuario
    nuevo_usuario = {
        'nombre': 'Octavio',
        'contrasena': '123456',
        'es_admin': True
    }

    referencia_usuarios.add(nuevo_usuario)
    
    print("Usuario creado exitosamente.")

crear_usuarios()