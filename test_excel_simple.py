import polars as pl
import os

# Test simple de Polars Excel
datos = [
    {"Nombre": "Producto A", "Precio": 100},
    {"Nombre": "Producto B", "Precio": 200}
]

df = pl.DataFrame(datos)
ruta = "test_exports/test_simple.xlsx"

try:
    df.write_excel(ruta)
    print(f"✅ Excel creado exitosamente: {ruta}")
    print(f"Tamaño: {os.path.getsize(ruta)} bytes")
except Exception as e:
    print(f"❌ Error: {e}")
