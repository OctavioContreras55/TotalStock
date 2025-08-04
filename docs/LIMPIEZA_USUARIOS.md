# 🧹 Sistema de Limpieza de Datos de Usuario

## Descripción General

El sistema de TotalStock ahora incluye una funcionalidad completa de limpieza de datos cuando se eliminan usuarios, asegurando que no se acumulen archivos innecesarios y manteniendo la privacidad de los datos.

## 📁 Archivos de Usuario que se Gestionan

### Por Usuario Específico:
- `data/config_usuario_{firebase_id}.json` - Configuraciones personales (tema, preferencias)
- `data/pendientes_{firebase_id}.json` - Lista de pendientes personales
- Archivos legacy con nombre de usuario (para retrocompatibilidad)

## 🔧 Funcionalidades Implementadas

### 1. Eliminación Automática al Borrar Usuario
**Archivo**: `app/crud_usuarios/delete_usuarios.py`

**Función**: `limpiar_archivos_usuario(id_usuario, nombre_usuario=None)`
- ✅ Elimina automáticamente todos los archivos relacionados con el usuario
- ✅ Maneja errores graciosamente
- ✅ Reporta archivos eliminados y errores
- ✅ Compatibilidad con archivos legacy

**Proceso de Eliminación**:
1. Se obtienen los datos del usuario de Firebase
2. Se limpian todos sus archivos relacionados
3. Se elimina el usuario de Firebase
4. Se registra la actividad en el historial con detalles de limpieza

### 2. Diálogo de Confirmación Mejorado
- ⚠️ Muestra claramente qué se va a eliminar
- 📋 Lista los tipos de datos que se borrarán
- 🚨 Advertencia de que la acción es irreversible

### 3. Utilidad de Limpieza de Archivos Huérfanos
**Archivo**: `utils_limpieza_usuarios.py`

**Propósito**: Limpiar archivos de usuarios que ya no existen en Firebase

#### Modos de Operación:
```bash
# Modo prueba (por defecto) - Solo muestra qué se eliminaría
python utils_limpieza_usuarios.py

# Modo ejecución - Elimina archivos realmente
python utils_limpieza_usuarios.py --ejecutar
```

**Características**:
- 🔍 Escanea todos los archivos de usuario en `data/`
- 📊 Compara con usuarios existentes en Firebase
- 🗑️ Identifica archivos huérfanos
- ⚠️ Modo prueba seguro por defecto
- 📈 Reportes detallados de la operación

## 📊 Ventajas del Sistema

### Privacidad y Seguridad:
- ✅ Elimina completamente los datos personales del usuario
- ✅ No deja rastros de configuraciones privadas
- ✅ Cumple con buenas prácticas de manejo de datos

### Mantenimiento del Sistema:
- ✅ Evita acumulación de archivos innecesarios
- ✅ Mantiene el directorio `data/` organizado
- ✅ Mejora el rendimiento al reducir archivos huérfanos

### Trazabilidad:
- ✅ Registra todas las eliminaciones en el historial
- ✅ Reporta archivos eliminados y posibles errores
- ✅ Logs detallados para administradores

## 🔄 Flujo de Eliminación de Usuario

```
1. Admin selecciona "Eliminar Usuario"
     ↓
2. Aparece diálogo de confirmación detallado
     ↓
3. Admin confirma eliminación
     ↓
4. Sistema obtiene datos del usuario de Firebase
     ↓
5. Sistema limpia archivos relacionados:
   - config_usuario_{id}.json
   - pendientes_{id}.json
   - Archivos legacy si existen
     ↓
6. Sistema elimina usuario de Firebase
     ↓
7. Sistema registra actividad en historial
     ↓
8. Se muestra confirmación al admin
```

## 📋 Mantenimiento Recomendado

### Limpieza Periódica:
Ejecutar mensualmente o cuando sea necesario:
```bash
python utils_limpieza_usuarios.py
```

### En Caso de Migración:
Si se cambia el sistema de IDs de usuarios, la utilidad puede identificar y limpiar archivos con el formato anterior.

## 🚨 Consideraciones Importantes

1. **Irreversibilidad**: Una vez eliminado un usuario, sus datos no se pueden recuperar
2. **Respaldo**: Considerar hacer respaldos antes de eliminaciones masivas
3. **Permisos**: Solo administradores pueden eliminar usuarios
4. **Logs**: Todas las operaciones se registran para auditoría

## 🔧 Personalización

El sistema es fácilmente extensible. Para agregar nuevos tipos de archivos de usuario:

1. Modificar la lista `archivos_posibles` en `limpiar_archivos_usuario()`
2. Actualizar los patrones de búsqueda en `utils_limpieza_usuarios.py`
3. Documentar el nuevo tipo de archivo aquí

---

✨ **El sistema garantiza que la eliminación de usuarios sea limpia, segura y trazable.**
