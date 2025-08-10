"""
Sistema para garantizar que solo una instancia de la aplicación esté ejecutándose
VERSIÓN CORREGIDA - Evita problemas de múltiples ventanas
"""
import os
import sys
import socket
import atexit
import tempfile
import threading
import time
from pathlib import Path

class InstanceLock:
    def __init__(self, app_name="TotalStock"):
        self.app_name = app_name
        self.lock_file = None
        self.socket = None
        self.port = 65432  # Puerto para comunicación entre instancias
        self.listener_thread = None
        self.listener_running = False
        
    def is_already_running(self):
        """Verificar si ya hay una instancia ejecutándose"""
        try:
            # Intentar crear un socket servidor en el puerto específico
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permitir reutilizar
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
            client_socket.settimeout(2)  # Timeout de 2 segundos
            client_socket.connect(('localhost', self.port))
            client_socket.send(b"FOCUS_WINDOW")
            client_socket.close()
        except Exception as e:
            print(f"No se pudo notificar a la instancia existente: {e}")
            
    def _cleanup(self):
        """Limpiar recursos al cerrar"""
        # Detener listener
        self.listener_running = False
        
        # Cerrar socket
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            
        # Eliminar archivo de bloqueo
        if self.lock_file and os.path.exists(self.lock_file):
            try:
                os.remove(self.lock_file)
            except Exception as e:
                print(f"Error eliminando archivo de bloqueo: {e}")
                
        # Esperar a que termine el listener
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=1)
                
    def start_listener(self, focus_callback=None):
        """Iniciar listener para peticiones de enfoque"""
        if self.socket and focus_callback and not self.listener_running:
            self.listener_running = True
            
            def listen_for_focus():
                try:
                    while self.listener_running:
                        try:
                            self.socket.settimeout(1)  # Timeout para poder verificar listener_running
                            conn, addr = self.socket.accept()
                            
                            if not self.listener_running:
                                conn.close()
                                break
                                
                            data = conn.recv(1024)
                            if data == b"FOCUS_WINDOW":
                                try:
                                    focus_callback()
                                except Exception as e:
                                    print(f"Error en focus callback: {e}")
                            conn.close()
                            
                        except socket.timeout:
                            continue  # Continuar el loop para verificar listener_running
                        except socket.error:
                            if self.listener_running:
                                print("Error en socket listener")
                            break
                            
                except Exception as e:
                    print(f"Error en listener: {e}")
                finally:
                    self.listener_running = False
                    
            self.listener_thread = threading.Thread(target=listen_for_focus, daemon=True)
            self.listener_thread.start()

# Instancia global
instance_lock = InstanceLock()
