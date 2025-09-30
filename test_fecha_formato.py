"""
Script para probar el formato de fecha y hora
"""
from datetime import datetime

print("=" * 60)
print("PRUEBA DE FORMATOS DE FECHA Y HORA")
print("=" * 60)

# Formato anterior (24 horas)
formato_24h = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
print(f"\nFormato 24 horas (ANTERIOR):")
print(f"  {formato_24h}")

# Formato nuevo (12 horas con AM/PM)
formato_12h = datetime.now().strftime("%d/%m/%Y a las %I:%M:%S %p")
print(f"\nFormato 12 horas (NUEVO):")
print(f"  {formato_12h}")

print("\n" + "=" * 60)
print("Explicacion del formato:")
print("  %I = Hora en formato 12 horas (01-12)")
print("  %p = AM o PM")
print("=" * 60)
