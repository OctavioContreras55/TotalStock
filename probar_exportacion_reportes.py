#!/usr/bin/env python3
"""
Script de prueba para la nueva funcionalidad de exportación de reportes
Verifica que se puedan exportar reportes en PDF, Excel y JSON
"""

import sys
import os
import asyncio
from datetime import datetime

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar funciones necesarias
try:
    from app.funciones.exportar_reportes import (
        exportar_reporte_json, 
        exportar_reporte_excel, 
        exportar_reporte_pdf,
        PDF_AVAILABLE
    )
    print("✅ Módulos importados correctamente")
except ImportError as e:
    print(f"❌ Error al importar módulos: {e}")
    sys.exit(1)

async def probar_exportacion():
    """Prueba la exportación en todos los formatos"""
    
    # Datos de prueba para el reporte
    datos_reporte = [
        {
            "id": 1,
            "nombre": "Producto A",
            "categoria": "Electrónicos",
            "stock": 50,
            "precio": 299.99,
            "fecha": "2025-01-15"
        },
        {
            "id": 2,
            "nombre": "Producto B",
            "categoria": "Hogar",
            "stock": 25,
            "precio": 149.50,
            "fecha": "2025-01-16"
        },
        {
            "id": 3,
            "nombre": "Producto C",
            "categoria": "Deportes",
            "stock": 75,
            "precio": 89.99,
            "fecha": "2025-01-17"
        }
    ]
    
    # Metadatos del reporte
    metadata_reporte = {
        "tipo_reporte": "inventario",
        "nombre_reporte": "Reporte de Inventario - Prueba",
        "fecha_generacion": datetime.now().isoformat(),
        "fecha_inicio": "2025-01-01",
        "fecha_fin": "2025-01-31",
        "usuario_filtro": "todos",
        "total_registros": len(datos_reporte)
    }
    
    # Crear directorio de pruebas
    directorio_prueba = "test_exports"
    os.makedirs(directorio_prueba, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"📁 Directorio de prueba: {directorio_prueba}")
    print(f"🕒 Timestamp: {timestamp}")
    print(f"📊 Datos de prueba: {len(datos_reporte)} registros")
    
    # Simulador de página (mock)
    class MockPage:
        def open(self, snackbar):
            print(f"📱 SnackBar: {snackbar.content.value}")
    
    page = MockPage()
    
    # Probar exportación JSON
    print("\n🔄 Probando exportación JSON...")
    try:
        await exportar_reporte_json(
            datos_reporte, 
            metadata_reporte, 
            directorio_prueba, 
            timestamp, 
            "inventario", 
            page
        )
        print("✅ Exportación JSON exitosa")
    except Exception as e:
        print(f"❌ Error en exportación JSON: {e}")
    
    # Probar exportación Excel
    print("\n🔄 Probando exportación Excel...")
    try:
        await exportar_reporte_excel(
            datos_reporte, 
            metadata_reporte, 
            directorio_prueba, 
            timestamp, 
            "inventario", 
            page
        )
        print("✅ Exportación Excel exitosa")
    except Exception as e:
        print(f"❌ Error en exportación Excel: {e}")
    
    # Probar exportación PDF
    print(f"\n🔄 Probando exportación PDF... (PDF disponible: {PDF_AVAILABLE})")
    if PDF_AVAILABLE:
        try:
            await exportar_reporte_pdf(
                datos_reporte, 
                metadata_reporte, 
                directorio_prueba, 
                timestamp, 
                "inventario", 
                page
            )
            print("✅ Exportación PDF exitosa")
        except Exception as e:
            print(f"❌ Error en exportación PDF: {e}")
    else:
        print("⚠️ ReportLab no disponible - PDF omitido")
    
    # Mostrar archivos generados
    print("\n📄 Archivos generados:")
    archivos_generados = os.listdir(directorio_prueba)
    for archivo in archivos_generados:
        ruta_completa = os.path.join(directorio_prueba, archivo)
        tamaño = os.path.getsize(ruta_completa)
        print(f"  📎 {archivo} ({tamaño} bytes)")
    
    print(f"\n🎉 Prueba completada - {len(archivos_generados)} archivos generados")

def main():
    """Función principal"""
    print("🧪 === PRUEBA DE EXPORTACIÓN DE REPORTES ===")
    print(f"🐍 Python: {sys.version}")
    print(f"📂 Directorio: {os.getcwd()}")
    
    # Ejecutar prueba
    try:
        asyncio.run(probar_exportacion())
    except KeyboardInterrupt:
        print("\n⏹️ Prueba cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
