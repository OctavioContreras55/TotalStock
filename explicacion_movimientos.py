#!/usr/bin/env python3
"""
Explicación de los tipos de movimientos en TotalStock
"""

print("📋 DIFERENCIAS ENTRE TIPOS DE MOVIMIENTOS EN TOTALSTOCK")
print("=" * 60)
print()

print("🔄 NUEVO MOVIMIENTO (General):")
print("   📦 Propósito: Control de inventario tradicional")
print("   📋 Tipos disponibles:")
print("      • Entrada: Recepción de productos del proveedor")
print("      • Salida: Ventas o envíos de productos")
print("      • Ajuste: Correcciones de inventario (pérdidas, daños)")
print("      • Transferencia: Entre diferentes almacenes/sucursales")
print("   🎯 Afecta: Cantidad total en inventario")
print("   📊 Ejemplo: 'Recibí 100 laptops nuevas del proveedor'")
print()

print("📍 MOVIMIENTO DE UBICACIONES (Específico):")
print("   🏢 Propósito: Reorganización física dentro del mismo almacén")
print("   📋 Tipo único:")
print("      • Traslado: Entre ubicaciones físicas (almacén/estantería)")
print("   🎯 NO afecta: Cantidad total (solo reubica)")
print("   📊 Ejemplo: 'Mover 5 Cadenas de Almacén 1/Estante A → Almacén 2/Estante B'")
print()

print("🔍 CASOS DE USO PRÁCTICOS:")
print()
print("   🔄 Usar 'Nuevo Movimiento' cuando:")
print("      • Llegan productos nuevos")
print("      • Se venden productos")
print("      • Hay productos dañados/perdidos")
print("      • Se transfiere entre sucursales")
print()
print("   📍 Usar 'Movimiento de Ubicaciones' cuando:")
print("      • Necesitas reorganizar el almacén")
print("      • Cambiar productos de estantería")
print("      • Optimizar el espacio físico")
print("      • Separar productos por categorías")
print()

print("✨ RESUMEN:")
print("   • Nuevo Movimiento = Cambios en cantidad total")
print("   • Movimiento de Ubicaciones = Solo cambios de posición física")
print("   • Ambos se registran en el historial para auditoría")
print()
