import firebase_admin
from firebase_admin import credentials, firestore

credenciales = credentials.Certificate("conexiones/credenciales_firebase.json") # Credenciales de Firebase

if not firebase_admin._apps: # Verifica si ya se ha inicializado la app
    firebase_admin.initialize_app(credenciales) # Inicializar Firebase Admin SDK

db = firestore.client() # Inicializar Firestore