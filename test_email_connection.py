"""
Script de prueba para verificar la conexion SMTP y envio de correos
"""
from utils.email.sent_email import test_email_connection, config_email
import os

def get_email_default():
    """Obtiene el correo por defecto según el entorno"""
    ENVIRONMENT = os.getenv('ENVIRONMENT')
    if ENVIRONMENT == 'production':
        return 'comercial@findii.co'
    else:
        return 'equitisoporte@gmail.com'

def mostrar_destinatarios_ejemplo():
    """
    Muestra los destinatarios a los que se enviarían correos en un escenario real
    con datos de ejemplo
    """
    EMAIL_DEFAULT = get_email_default()

    # Datos de ejemplo (ficticios para prueba)
    datos_ejemplo = {
        'solicitante': {
            'correo_electronico': 'juan.perez@ejemplo.com',
            'nombre_completo': 'Juan Pérez González'
        },
        'asesor': {
            'correo': 'asesor.maria@findii.co',
            'nombre': 'María Rodríguez'
        },
        'banco': {
            'correo_usuario': 'creditos.bancopopular@bancopopular.com.co',
            'nombre_usuario': 'Oficial de Créditos - Banco Popular'
        },
        'solicitud': {
            'ciudad_solicitud': 'Bogotá',
            'banco_nombre': 'Banco Popular'
        }
    }

    print("\n" + "=" * 60)
    print("📧 DESTINATARIOS DE CORREOS ELECTRÓNICOS (EJEMPLO)")
    print("=" * 60)

    # 1. Correo al solicitante
    email_solicitante = datos_ejemplo['solicitante']['correo_electronico']
    print(f"\n1. 👤 SOLICITANTE:")
    print(f"   📧 {email_solicitante} ✅")
    print(f"   📝 Nombre: {datos_ejemplo['solicitante']['nombre_completo']}")
    print(f"   📨 Tipo: Correo de confirmación de registro")

    # 2. Correo al asesor (siempre incluye EMAIL_DEFAULT)
    email_asesor = datos_ejemplo['asesor']['correo']
    print(f"\n2. 👨‍💼 ASESOR:")
    print(f"   📧 {email_asesor} ✅")
    print(f"   📧 {EMAIL_DEFAULT} (correo fijo - siempre incluido) ✅")
    print(f"   📝 Nombre: {datos_ejemplo['asesor']['nombre']}")
    print(f"   📨 Tipo: Notificación de nueva solicitud asignada")
    print(f"   ℹ️  Nota: Se envía a AMBOS correos (asesor + correo por defecto)")

    # 3. Correo al banco
    email_banco = datos_ejemplo['banco']['correo_usuario']
    ciudad_solicitud = datos_ejemplo['solicitud']['ciudad_solicitud']
    banco_nombre = datos_ejemplo['solicitud']['banco_nombre']

    print(f"\n3. 🏦 BANCO:")
    print(f"   📧 {email_banco} ✅")
    print(f"   📝 Nombre: {datos_ejemplo['banco']['nombre_usuario']}")
    print(f"   🏦 Banco: {banco_nombre}")
    print(f"   📍 Ciudad: {ciudad_solicitud}")
    print(f"   📨 Tipo: Notificación de nueva solicitud de crédito")

    # Calcular destinatarios únicos
    destinatarios_unicos = set()
    destinatarios_unicos.add(email_solicitante)
    destinatarios_unicos.add(email_asesor)
    destinatarios_unicos.add(EMAIL_DEFAULT)
    destinatarios_unicos.add(email_banco)

    print("\n" + "=" * 60)
    print(f"📊 RESUMEN: Se enviarían correos a {len(destinatarios_unicos)} destinatario(s) único(s)")
    print(f"   Destinatarios:")
    for i, email in enumerate(sorted(destinatarios_unicos), 1):
        tipo = ""
        if email == email_solicitante:
            tipo = " (Solicitante)"
        elif email == email_asesor:
            tipo = " (Asesor)"
        elif email == email_banco:
            tipo = " (Banco)"
        elif email == EMAIL_DEFAULT:
            tipo = " (Correo fijo/Default)"
        print(f"      {i}. {email}{tipo}")

    print("\n📋 INFORMACIÓN ADICIONAL:")
    print(f"   • Correo por defecto (EMAIL_DEFAULT): {EMAIL_DEFAULT}")
    print(f"   • Este correo SIEMPRE se incluye en el email al asesor")
    print(f"   • Si no hay correo del banco, se usa como fallback")
    print("=" * 60 + "\n")

print("=" * 60)
print("PRUEBA DE CONFIGURACION DE EMAIL")
print("=" * 60)

# 0. Mostrar destinatarios de ejemplo
mostrar_destinatarios_ejemplo()

# 1. Verificar que exista EMAIL_PASSWORD en variables de entorno
email_settings = config_email()
print("=" * 60)
print("VERIFICACION DE CONFIGURACION")
print("=" * 60)
print(f"\n1. VERIFICANDO VARIABLES DE ENTORNO:")
print(f"   SMTP Server: {email_settings['smtp_server']}")
print(f"   SMTP Port: {email_settings['smtp_port']}")
print(f"   Sender Email: {email_settings['sender_email']}")
print(f"   PASSWORD configurado: {'SI' if email_settings['sender_password'] else 'NO'}")
print(f"   Correo por defecto (EMAIL_DEFAULT): {get_email_default()}")

if not email_settings['sender_password']:
    print("\nERROR CRITICO: EMAIL_PASSWORD no esta configurado en el archivo .env")
    print("   Solucion: Agregar EMAIL_PASSWORD=tu_contrasena en el archivo .env")
    exit(1)

print(f"   Password (primeros 5 chars): {email_settings['sender_password'][:5]}...")

# 2. Probar conexion SMTP
print(f"\n2. PROBANDO CONEXION SMTP:")
print("-" * 60)
resultado = test_email_connection()
print("-" * 60)

if resultado:
    print("\n✅ EXITO! La conexion SMTP esta funcionando correctamente")
    print("   Los correos deberian enviarse sin problemas")
else:
    print("\n❌ FALLO: La conexion SMTP no esta funcionando")
    print("   Posibles soluciones:")
    print("   1. Verificar que la contrasena en .env sea una 'App Password' de Zoho/Gmail")
    print("   2. Asegurarse de tener 2FA habilitado en la cuenta")
    print("   3. Verificar la conexion a internet")

print("\n" + "=" * 60)
