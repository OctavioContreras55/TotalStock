import json
import os
from pathlib import Path

class GestorConfiguracion:
    """
    Clase para manejar la configuración persistente de la aplicación.
    Guarda las preferencias del usuario en un archivo JSON.
    """
    
    _config_file = "data/configuracion.json"
    _config_default = {
        "tema": "oscuro",
        "idioma": "es",
        "notificaciones": True,
        "auto_backup": False,
        "ultima_actualizacion": None
    }
    
    @classmethod
    def _asegurar_directorio(cls):
        """Crea el directorio data/ si no existe"""
        directorio = Path(cls._config_file).parent
        directorio.mkdir(exist_ok=True)
    
    @classmethod
    def cargar_configuracion(cls):
        """
        Carga la configuración desde el archivo JSON.
        Si no existe, crea uno con valores por defecto.
        """
        try:
            cls._asegurar_directorio()
            
            if os.path.exists(cls._config_file):
                with open(cls._config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Asegurar que todas las claves necesarias existen
                    for clave, valor_default in cls._config_default.items():
                        if clave not in config:
                            config[clave] = valor_default
                    return config
            else:
                # Archivo no existe, crear con valores por defecto
                cls.guardar_configuracion(cls._config_default)
                return cls._config_default.copy()
                
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
            return cls._config_default.copy()
    
    @classmethod
    def guardar_configuracion(cls, config):
        """
        Guarda la configuración en el archivo JSON.
        """
        try:
            cls._asegurar_directorio()
            
            with open(cls._config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
            
        except Exception as e:
            print(f"Error al guardar configuración: {e}")
            return False
    
    @classmethod
    def obtener_tema(cls):
        """Obtiene el tema guardado"""
        config = cls.cargar_configuracion()
        return config.get("tema", "oscuro")
    
    @classmethod
    def cambiar_tema(cls, nuevo_tema):
        """Cambia y guarda el tema"""
        config = cls.cargar_configuracion()
        config["tema"] = nuevo_tema
        return cls.guardar_configuracion(config)
    
    @classmethod
    def obtener_configuracion_completa(cls):
        """Obtiene toda la configuración"""
        return cls.cargar_configuracion()
    
    @classmethod
    def actualizar_configuracion(cls, **kwargs):
        """
        Actualiza múltiples valores de configuración.
        Ejemplo: actualizar_configuracion(tema="azul", notificaciones=False)
        """
        config = cls.cargar_configuracion()
        config.update(kwargs)
        return cls.guardar_configuracion(config)
