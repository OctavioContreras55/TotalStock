"""
Sistema para garantizar que solo una instancia de la aplicación esté ejecutándose
"""
import os
import sys
import socket
import atexit
import tempfile
from pathlib import Path

class InstanceLock:
    def __init__(self, app_name="TotalStock"):
        self.app_name = app_name
        self.lock_file = None
        self.socket = None
        self.port = 65432  # Puerto para comunicación entre instancias
        
    def is_already_running(self):
        """Verificar si ya hay una instancia ejecutándose"""
        try:
            # Intentar crear un socket servidor en el puerto específico
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('localhost', self.port))
            self.socket.listen(1)
            
            # Si llegamos aquí, no hay otra instancia ejecutándose
            self._create_lock_file()
            atexit.register(self._cleanup)
            return False
            
        except socket.error:
            # El puerto está ocupado, otra instancia está ejecutándose
            self._notify_existing_instance()
            return True
            
    def _create_lock_file(self):
        """Crear archivo de bloqueo"""
        try:
            temp_dir = tempfile.gettempdir()
            self.lock_file = os.path.join(temp_dir, f"{self.app_name}.lock")
            
            with open(self.lock_file, 'w') as f:
                f.write(str(os.getpid()))
                
        except Exception as e:
            print(f"Error creando archivo de bloqueo: {e}")
            
    def _notify_existing_instance(self):
        """Notificar a la instancia existente que se enfoque"""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', self.port))
            client_socket.send(b"FOCUS_WINDOW")
            client_socket.close()
        except Exception as e:
            print(f"No se pudo notificar a la instancia existente: {e}")
            
    def _cleanup(self):
        """Limpiar recursos al cerrar"""
        if self.socket:
            self.socket.close()
            
        if self.lock_file and os.path.exists(self.lock_file):
            try:
                os.remove(self.lock_file)
            except Exception as e:
                print(f"Error eliminando archivo de bloqueo: {e}")
                
    def start_listener(self, focus_callback=None):
        """Iniciar listener para peticiones de enfoque"""
        if self.socket and focus_callback:
            import threading
            
            def listen_for_focus():
                try:
                    while True:
                        conn, addr = self.socket.accept()
                        data = conn.recv(1024)
                        if data == b"FOCUS_WINDOW":
                            focus_callback()
                        conn.close()
                except Exception as e:
                    print(f"Error en listener: {e}")
                    
            listener_thread = threading.Thread(target=listen_for_focus, daemon=True)
            listener_thread.start()

# Instancia global
instance_lock = InstanceLock()
