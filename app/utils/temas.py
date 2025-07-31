class TemaOscuro:
    # Colores principales - versión ligeramente más suave
    BG_COLOR = "#1A1D21"  # Fondo ligeramente más claro
    CARD_COLOR = "#25282C"  # Tarjetas un poco más claras
    SIDEBAR_COLOR = "#1E2124"
    
    # Tabla
    TABLE_BG = "#25282C"
    TABLE_HEADER_BG = "#36393F"
    TABLE_BORDER = "#36393F"
    TABLE_HOVER = "#2C2F33"
    
    # Colores de acento - ligeramente más suaves
    PRIMARY_COLOR = "#7B8FDB"  # Azul un poco más suave
    SUCCESS_COLOR = "#4CBB17"  # Verde un poco más vibrante pero suave
    ERROR_COLOR = "#F55757"  # Rojo un poco más suave
    WARNING_COLOR = "#FFA726"  # Naranja más suave
    ICON_BTN_COLOR = "#7B8FDB" # Azul para iconos de botones
    
    # Texto
    TEXT_COLOR = "#F5F5F5"  # Blanco ligeramente más suave
    TEXT_SECONDARY = "#B9BBBE"
    SECONDARY_TEXT_COLOR = "#B9BBBE"  # Alias para compatibilidad
    TEXT_MUTED = "#72767D"
    
    # Texto específico para sidebar
    SIDEBAR_TEXT_COLOR = "#FFFFFF"  # Blanco para texto en sidebar
    SIDEBAR_TEXT_SECONDARY = "#B9BBBE"  # Gris claro para texto secundario en sidebar
    SIDEBAR_ICON_COLOR = "#B9BBBE"  # Gris claro para iconos en sidebar
    
    # Botones
    BUTTON_BG = "#25282C"  # Un poco más claro
    BUTTON_HOVER = "#2C2F33"
    BUTTON_TEXT = "#FFFFFF"
    BUTTON_PRIMARY_BG = "#7B8FDB"
    BUTTON_SUCCESS_BG = "#4CBB17"
    BUTTON_ERROR_BG = "#F55757"
    
    # Inputs
    INPUT_BG = "#2C2F33"
    INPUT_BORDER = "#36393F"
    INPUT_FOCUS = "#7B8FDB"
    
    # Efectos
    BORDER_RADIUS = 10
    SHADOW = "0px 2px 8px #00000040"
    DIVIDER_COLOR = "#36393F"
    
    # Estados
    DISABLED_COLOR = "#72767D"
    SELECTED_COLOR = "#7B8FDB20"


class TemaAzul:
    # Colores principales basados en el diseño exacto de la imagen
    BG_COLOR = "#BBE1D9"  # Fondo azul muy claro como en la imagen
    CARD_COLOR = "#FFFFFF"  # Tarjetas blancas
    SIDEBAR_COLOR = "#1B4B5A"  # Azul oscuro exacto del sidebar de la imagen
    
    # Tabla
    TABLE_BG = "#FFFFFF"
    TABLE_HEADER_BG = "#2E86AB"  # Azul de los headers como en la imagen
    TABLE_BORDER = "#B8E0F0"  # Azul claro para bordes
    TABLE_HOVER = "#F0F9FC"  # Hover muy sutil
    
    # Colores de acento
    PRIMARY_COLOR = "#2E86AB"  # Azul principal exacto de la imagen
    SUCCESS_COLOR = "#27AE60"  # Verde equilibrado
    ERROR_COLOR = "#E74C3C"  # Rojo estándar
    WARNING_COLOR = "#F39C12"  # Naranja equilibrado
    ICON_BTN_COLOR = "#010D12"  # Azul para iconos de botones
    
    # Texto - Mejorado para legibilidad
    TEXT_COLOR = "#1B365D"  # Azul oscuro para texto principal
    TEXT_SECONDARY = "#34495E"  # Gris azulado para texto secundario
    SECONDARY_TEXT_COLOR = "#34495E"  # Alias para compatibilidad
    TEXT_MUTED = "#7F8C8D"  # Gris para texto deshabilitado
    
    # Texto específico para sidebar (contraste con fondo oscuro)
    SIDEBAR_TEXT_COLOR = "#FFFFFF"  # Blanco para texto en sidebar oscuro
    SIDEBAR_TEXT_SECONDARY = "#B8E0F0"  # Azul claro para texto secundario en sidebar
    SIDEBAR_ICON_COLOR = "#B8E0F0"  # Azul claro para iconos en sidebar
    
    # Botones
    BUTTON_BG = "#2E86AB"  # Azul principal para botones
    BUTTON_HOVER = "#2471A3"  # Azul más oscuro para hover
    BUTTON_TEXT = "#FFFFFF"
    BUTTON_PRIMARY_BG = "#2E86AB"
    BUTTON_SUCCESS_BG = "#27AE60"
    BUTTON_ERROR_BG = "#E74C3C"
    
    # Inputs
    INPUT_BG = "#FFFFFF"
    INPUT_BORDER = "#B8E0F0"  # Azul claro para bordes de inputs
    INPUT_FOCUS = "#2E86AB"  # Azul principal para focus
    
    # Efectos
    BORDER_RADIUS = 8  # Radio más moderado
    SHADOW = "0px 2px 8px #00000008"  # Sombra muy sutil
    DIVIDER_COLOR = "#D6EAF8"  # Divisor azul muy claro
    
    # Estados
    DISABLED_COLOR = "#BDC3C7"
    SELECTED_COLOR = "#2E86AB15"  # Selección azul muy sutil


# Clase para manejar el tema actual
class GestorTemas:
    _tema_actual = None  # Se cargará desde configuración
    
    @classmethod
    def _cargar_tema_inicial(cls):
        """Carga el tema desde la configuración persistente"""
        if cls._tema_actual is None:
            from app.utils.configuracion import GestorConfiguracion
            cls._tema_actual = GestorConfiguracion.obtener_tema()
    
    @classmethod
    def obtener_tema(cls):
        cls._cargar_tema_inicial()
        if cls._tema_actual == "azul":
            return TemaAzul()
        else:
            return TemaOscuro()
    
    @classmethod
    def cambiar_tema(cls, nuevo_tema):
        """Cambia el tema y lo guarda en la configuración persistente"""
        from app.utils.configuracion import GestorConfiguracion
        cls._tema_actual = nuevo_tema
        GestorConfiguracion.cambiar_tema(nuevo_tema)
    
    @classmethod
    def obtener_tema_actual(cls):
        cls._cargar_tema_inicial()
        return cls._tema_actual