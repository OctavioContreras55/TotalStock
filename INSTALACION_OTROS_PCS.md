# 🖥️ Guía de Instalación para Otras PCs

## 📋 **Requisitos Previos**

### **Software Necesario**
- **Python 3.8+** (recomendado Python 3.11 o superior)
- **Git** (para clonar el repositorio)
- **Conexión a Internet** (para descargar dependencias)

### **Verificar Python**
```bash
python --version
# o
python3 --version
```

## 🚀 **Instalación Paso a Paso**

### **1. Clonar el Repositorio**
```bash
git clone https://github.com/OctavioContreras55/TotalStock.git
cd TotalStock
```

### **2. Crear Entorno Virtual (Recomendado)**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### **3. Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### **4. Configurar Firebase** 🔑
**¡CRÍTICO!** El archivo de credenciales NO está en el repositorio por seguridad.

#### Opción A: Conseguir credenciales del propietario
1. Solicitar el archivo `credenciales_firebase.json` 
2. Colocarlo en: `conexiones/credenciales_firebase.json`

#### Opción B: Crear tu propio proyecto Firebase
1. Ir a [Firebase Console](https://console.firebase.google.com)
2. Crear nuevo proyecto
3. Habilitar Firestore Database
4. Generar clave privada de cuenta de servicio
5. Descargar como `credenciales_firebase.json`
6. Colocar en carpeta `conexiones/`

### **5. Ejecutar la Aplicación**
```bash
python run.py
```

---

## 🔧 **Compilar Ejecutable (Opcional)**

### **Para crear ejecutable independiente:**
```bash
python build.py
```

### **Opciones de compilación:**
- **Básica**: Compilación rápida
- **Optimizada**: Recomendada para distribución
- **Debug**: Para desarrollo
- **Completa**: Para producción

---

## 🛠️ **Resolución de Problemas Comunes**

### **Error: No module named 'flet'**
```bash
pip install flet>=0.21.0
```

### **Error: Credenciales Firebase no encontradas**
- Verificar que `credenciales_firebase.json` esté en `conexiones/`
- Verificar permisos de lectura del archivo

### **Error: ModuleNotFoundError**
```bash
pip install -r requirements.txt --force-reinstall
```

### **Problemas con Polars/Pandas**
```bash
pip uninstall polars pandas
pip install polars>=0.20.0 pandas>=2.0.0
```

---

## 📁 **Estructura de Archivos Necesarios**

```
TotalStock/
├── conexiones/
│   └── credenciales_firebase.json  ⚠️ NECESARIO
├── assets/
│   ├── logo.png
│   └── logo.ico
├── app/ (todo el código)
├── requirements.txt
└── run.py
```

---

## 🌐 **Consideraciones de Red**

### **Puertos necesarios:**
- **443** (HTTPS para Firebase)
- **80** (HTTP para actualizaciones)

### **Dominios a permitir:**
- `*.googleapis.com`
- `*.firebase.google.com`
- `firestore.googleapis.com`

---

## 💡 **Recomendaciones**

1. **Usar entorno virtual** para evitar conflictos
2. **Verificar versión de Python** (3.8+ mínimo)
3. **Tener credenciales Firebase** antes de ejecutar
4. **Probar primero en modo desarrollo** antes de compilar
5. **Mantener backup de credenciales** en lugar seguro

---

## 🆘 **Soporte**

Si encuentras problemas:
1. Verificar que Python esté actualizado
2. Revisar que todas las dependencias estén instaladas
3. Confirmar que las credenciales Firebase estén configuradas
4. Consultar logs de error en la consola

---

## 🔒 **Seguridad**

- **NUNCA** compartir `credenciales_firebase.json` públicamente
- Mantener credenciales en ubicación segura
- Usar diferentes proyectos Firebase para desarrollo/producción
