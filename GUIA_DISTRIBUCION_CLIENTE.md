# 📦 GUÍA DE DISTRIBUCIÓN - TotalStock

## ✅ **QUÉ PASAR AL CLIENTE**

### **RESPUESTA SIMPLE: SOLO EL ARCHIVO EXE**

```
📁 Para el cliente:
└── TotalStock.exe  (142.9 MB)
```

**Eso es todo. No necesitas nada más.**

---

## 🎯 **CONFIRMACIÓN TÉCNICA**

### **✅ El ejecutable YA INCLUYE:**

1. **Python completo** (3.13) embebido
2. **Todas las librerías** necesarias:
   - Firebase Admin SDK
   - Flet UI Framework
   - Polars (datos)
   - ReportLab (PDFs)
   - OpenPyXL (Excel)
3. **Todas las DLLs** de sistema (incluye `python313.dll`)
4. **Archivos de configuración** por defecto
5. **Assets** (iconos, etc.)

### **❌ NO necesitas incluir:**
- ❌ Carpeta `assets/`
- ❌ Carpeta `conexiones/`
- ❌ Carpeta `data/`
- ❌ Archivos `.py`
- ❌ `requirements.txt`
- ❌ Otras carpetas del proyecto

---

## 📋 **INSTRUCCIONES PARA EL CLIENTE**

### **Para instalar:**
```
1. Recibir: TotalStock.exe
2. Guardar en cualquier carpeta (ej: C:\TotalStock\)
3. Doble clic en TotalStock.exe
4. ¡Listo!
```

### **Requisitos del PC del cliente:**
- ✅ Windows 10 o 11 (64 bits)
- ✅ 4 GB RAM mínimo
- ✅ 200 MB espacio libre
- ✅ Conexión a Internet (para Firebase)
- ❌ NO requiere Python
- ❌ NO requiere instalar nada más

---

## 🚀 **MÉTODOS DE ENTREGA**

### **Opción 1: Transferencia en línea**
```
📊 Tamaño: 142.9 MB
✅ Google Drive / OneDrive
✅ WeTransfer (gratis hasta 2 GB)
✅ SendAnywhere
✅ Dropbox
```

### **Opción 2: Transferencia física**
```
✅ USB (cualquier tamaño > 150 MB)
✅ CD/DVD
✅ Transferencia directa por red local
```

### **Opción 3: Email (NO recomendado)**
```
❌ El archivo es muy grande para email (142 MB)
❌ La mayoría de servidores tienen límite de 25 MB
```

---

## ⚠️ **ADVERTENCIAS IMPORTANTES**

### **1. Antivirus / Windows Defender:**
```
PROBLEMA: Puede marcar el ejecutable como "sospechoso"
RAZÓN: Es un ejecutable nuevo, no firmado digitalmente

SOLUCIÓN PARA EL CLIENTE:
1. Si aparece advertencia de Windows:
   - Clic en "Más información"
   - Clic en "Ejecutar de todas formas"

2. Si el antivirus lo bloquea:
   - Agregar excepción para TotalStock.exe
   - Temporalmente deshabilitar análisis en tiempo real
```

### **2. Permisos de Windows:**
```
Si aparece error de permisos:
1. Clic derecho en TotalStock.exe
2. "Ejecutar como administrador"
3. Aceptar permisos UAC
```

### **3. Verificación de integridad:**
```
Para verificar que el archivo se transfirió correctamente:

Tamaño exacto: 142,886,868 bytes
Si el tamaño es diferente = archivo corrupto en transferencia
```

---

## 💼 **INSTALACIÓN EMPRESARIAL**

### **Para múltiples PCs:**
```
1. Copiar TotalStock.exe a carpeta compartida de red
2. Cada usuario copia a su PC local
3. Ejecutar desde carpeta local (mejor rendimiento)
```

### **Para administradores IT:**
```
- El ejecutable NO modifica el registro
- NO instala servicios de Windows
- NO requiere permisos de administrador (recomendado pero no obligatorio)
- Se puede ejecutar desde cualquier ubicación
- Fácil de desinstalar (solo eliminar el archivo)
```

---

## 🔍 **VERIFICACIÓN POST-INSTALACIÓN**

### **Prueba rápida en el PC del cliente:**
```
1. Abrir TotalStock.exe
2. Debería aparecer pantalla de login
3. Si aparece = ✅ Instalación exitosa
4. Si hay error = revisar sección de problemas
```

### **Conectividad Firebase:**
```
- Al hacer login, verificará conexión automáticamente
- Si no hay internet = mensaje de error claro
- Si Firebase está mal configurado = mensaje específico
```

---

## 📞 **SOPORTE AL CLIENTE**

### **Si el cliente reporta problemas:**

1. **Verificar archivo:**
   ```
   ¿El tamaño es exactamente 142,886,868 bytes?
   Si no = reenviar archivo
   ```

2. **Verificar Windows:**
   ```
   ¿Qué versión de Windows tiene?
   ¿Es 64 bits?
   ¿Tiene permisos de administrador?
   ```

3. **Verificar antivirus:**
   ```
   ¿Qué antivirus usa?
   ¿Bloqueó el archivo?
   ¿Necesita agregar excepción?
   ```

4. **Log de errores:**
   ```
   Si persisten problemas, pedir que ejecute:
   TotalStock.exe > log.txt 2>&1
   
   Enviar el archivo log.txt para diagnóstico
   ```

---

## 🎉 **RESUMEN EJECUTIVO**

### **✅ LO QUE SÍ:**
- Enviar solo `TotalStock.exe`
- 142.9 MB de tamaño
- Funciona inmediatamente
- No requiere instalación adicional

### **❌ LO QUE NO:**
- No enviar carpetas del proyecto
- No requerir Python en el cliente
- No complicar con dependencias
- No necesitar permisos especiales

**El método de ejecutable único (--onefile) hace que la distribución sea súper simple: un archivo, una transferencia, listo para usar. 🚀**

---

**Fecha:** 10 de agosto de 2025  
**Archivo:** TotalStock.exe  
**Tamaño:** 142,886,868 bytes  
**Estado:** ✅ Listo para distribución
