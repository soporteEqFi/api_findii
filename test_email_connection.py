"""
Script de prueba para verificar la conexion SMTP y envio de correos
"""
from utils.email.sent_email import test_email_connection, config_email
import os

print("=" * 60)
print("PRUEBA DE CONFIGURACION DE EMAIL")
print("=" * 60)

# 1. Verificar que exista EMAIL_PASSWORD en variables de entorno
email_settings = config_email()
print(f"\n1. VERIFICANDO VARIABLES DE ENTORNO:")
print(f"   SMTP Server: {email_settings['smtp_server']}")
print(f"   SMTP Port: {email_settings['smtp_port']}")
print(f"   Sender Email: {email_settings['sender_email']}")
print(f"   PASSWORD configurado: {'SI' if email_settings['sender_password'] else 'NO'}")

if not email_settings['sender_password']:
    print("\nERROR CRITICO: EMAIL_PASSWORD no esta configurado en el archivo .env")
    print("   Solucion: Agregar EMAIL_PASSWORD=tu_contrasena en el archivo .env")
    exit(1)

print(f"   Password (primeros 5 chars): {email_settings['sender_password'][:5]}...")

# 2. Probar conexion SMTP
print(f"\n2. PROBANDO CONEXION SMTP CON ZOHO:")
print("-" * 60)
resultado = test_email_connection()
print("-" * 60)

if resultado:
    print("\nEXITO! La conexion SMTP esta funcionando correctamente")
    print("   Los correos deberian enviarse sin problemas")
else:
    print("\nFALLO: La conexion SMTP no esta funcionando")
    print("   Posibles soluciones:")
    print("   1. Verificar que la contrasena en .env sea una 'App Password' de Zoho")
    print("   2. Asegurarse de tener 2FA habilitado en la cuenta de Zoho")
    print("   3. Verificar la conexion a internet")

print("\n" + "=" * 60)
