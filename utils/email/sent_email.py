import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time as std_time
import uuid
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()  # Cargar .env del directorio del proyecto

def config_email():
    smtp_server = "smtp.zoho.com"
    smtp_port = 465
    sender_email = "credito@findii.co"
    sender_password = os.getenv('EMAIL_PASSWORD')

    email_settings = {
        "smtp_server": smtp_server,
        "smtp_port": smtp_port,
        "sender_email": sender_email,
        "sender_password": sender_password
    }

    return email_settings

def test_email_connection():
    """
    Funcion para probar la conexion SMTP con Zoho
    """
    try:
        email_settings = config_email()

        if not email_settings["sender_password"]:
            print("ERROR: No se encontro EMAIL_PASSWORD en las variables de entorno")
            return False

        print("Probando conexion SMTP con Zoho...")
        print(f"   Servidor: {email_settings['smtp_server']}")
        print(f"   Puerto: {email_settings['smtp_port']}")
        print(f"   Email: {email_settings['sender_email']}")
        print(f"   Contrasena: {'*' * len(email_settings['sender_password'])}")

        # Probar conexion SSL
        server = smtplib.SMTP_SSL(email_settings["smtp_server"], email_settings["smtp_port"])
        server.set_debuglevel(1)  # Debug detallado

        print("   Probando autenticacion...")
        server.login(email_settings["sender_email"], email_settings["sender_password"])

        server.quit()
        print("   CONEXION EXITOSA!")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"   ERROR de autenticacion: {str(e)}")
        print("   Soluciones:")
        print("      1. Verifica que tengas 2FA habilitado en Zoho")
        print("      2. Genera una contrasena de aplicacion especifica")
        print("      3. Usa la contrasena de aplicacion, NO tu contrasena normal")
        return False

    except smtplib.SMTPConnectError as e:
        print(f"   ERROR de conexion: {str(e)}")
        print("   Verifica tu conexion a internet")
        return False

    except Exception as e:
        print(f"   ERROR inesperado: {str(e)}")
        return False

def formatear_campos_dinamicos(campos_dict, titulo="", nivel_indentacion=1):
    """
    Formatea campos dinámicos de manera recursiva para mostrar en el email
    """
    if not campos_dict or not isinstance(campos_dict, dict):
        return ""

    resultado = []
    indentacion = "    " * nivel_indentacion

    if titulo:
        resultado.append(f"\n{indentacion}{titulo.upper()}")
        resultado.append(f"{indentacion}{'=' * len(titulo)}")

    for clave, valor in campos_dict.items():
        # Formatear clave para mostrar
        clave_formateada = clave.replace('_', ' ').title()

        if isinstance(valor, dict):
            # Si es un diccionario, formatear recursivamente
            resultado.append(f"{indentacion}• {clave_formateada}:")
            sub_contenido = formatear_campos_dinamicos(valor, "", nivel_indentacion + 1)
            if sub_contenido:
                resultado.append(sub_contenido)
        elif isinstance(valor, list):
            # Si es una lista, mostrar cada elemento
            resultado.append(f"{indentacion}• {clave_formateada}:")
            for i, item in enumerate(valor):
                if isinstance(item, dict):
                    resultado.append(f"{indentacion}    {i+1}:")
                    sub_contenido = formatear_campos_dinamicos(item, "", nivel_indentacion + 2)
                    if sub_contenido:
                        resultado.append(sub_contenido)
                else:
                    resultado.append(f"{indentacion}    • {item}")
        else:
            # Valor simple
            resultado.append(f"{indentacion}• {clave_formateada}: {valor}")

    return "\n".join(resultado)

def mapear_datos_para_email(response_data, original_json=None):
    """
    Mapea los datos de la respuesta del controlador crear_registro_completo
    al formato esperado por las funciones de email (solicitante, asesor y banco)

    Args:
        response_data: Respuesta del controlador con los datos creados
        original_json: JSON original enviado desde el frontend (para extraer correos)
    """
    try:
        data = response_data.get("data", {})

        # Extraer datos del solicitante
        solicitante = data.get("solicitante", {})
        solicitudes = data.get("solicitudes", [])
        ubicaciones = data.get("ubicaciones", [])
        actividad_economica = data.get("actividad_economica", {})
        informacion_financiera = data.get("informacion_financiera", {})
        referencias = data.get("referencias", [])

        # Obtener primera solicitud si existe
        primera_solicitud = solicitudes[0] if solicitudes else {}
        primera_ubicacion = ubicaciones[0] if ubicaciones else {}

        # Generar ID de radicado único
        id_radicado = f"FD-{uuid.uuid4().hex[:8].upper()}"

        # Preparar datos básicos del solicitante
        nombre_completo = f"{solicitante.get('nombres', '')} {solicitante.get('primer_apellido', '')} {solicitante.get('segundo_apellido', '')}"
        correo_electronico = solicitante.get("correo", "")

        # Extraer campos dinámicos
        info_extra = solicitante.get("info_extra", {})
        detalle_credito = primera_solicitud.get("detalle_credito", {})
        detalle_direccion = primera_ubicacion.get("detalle_direccion", {}) if primera_ubicacion else {}
        detalle_actividad = actividad_economica.get("detalle_actividad", {}) if actividad_economica else {}
        detalle_financiera = informacion_financiera.get("detalle_financiera", {}) if informacion_financiera else {}

        # EXTRACCIÓN ROBUSTA DE CORREOS DESDE EL JSON ORIGINAL
        nombre_asesor = ""
        correo_asesor = ""
        nombre_banco_usuario = ""
        correo_banco_usuario = ""

        if original_json:
            print(f"🔍 DEBUG - Extrayendo correos desde JSON original:")
            print(f"   📋 Claves en JSON original: {list(original_json.keys())}")

            # Extraer correo del solicitante (siempre en la raíz)
            correo_solicitante_original = original_json.get("correo", "")
            if correo_solicitante_original:
                correo_electronico = correo_solicitante_original
                print(f"   ✅ Correo solicitante encontrado en raíz: {correo_electronico}")

            # EXTRACCIÓN ROBUSTA: BUSCAR EN RAÍZ Y EN SOLICITUDES[0]
            # Obtener primera solicitud del JSON original si existe
            solicitud_original = (original_json.get("solicitudes") or [{}])[0]

            # Buscar en raíz primero, luego en solicitudes[0]
            correo_asesor = (original_json.get("correo_asesor") or solicitud_original.get("correo_asesor", "")).strip()
            nombre_asesor = (original_json.get("nombre_asesor") or solicitud_original.get("nombre_asesor", "")).strip()
            correo_banco_usuario = (original_json.get("correo_banco_usuario") or solicitud_original.get("correo_banco_usuario", "")).strip()
            nombre_banco_usuario = (original_json.get("nombre_banco_usuario") or solicitud_original.get("nombre_banco_usuario", "")).strip()

            print(f"   👨‍💼 Asesor extraído: '{nombre_asesor}' ('{correo_asesor}')")
            print(f"   🏦 Usuario banco extraído: '{nombre_banco_usuario}' ('{correo_banco_usuario}')")

            # Debug adicional: mostrar dónde se encontraron exactamente los datos
            print(f"   🔍 DEBUG UBICACIÓN DE DATOS:")

            # Verificar correo_asesor
            if original_json.get("correo_asesor"):
                print(f"   📍 ✅ correo_asesor encontrado en RAÍZ: '{original_json.get('correo_asesor')}'")
            elif solicitud_original.get("correo_asesor"):
                print(f"   📍 ✅ correo_asesor encontrado en SOLICITUDES[0]: '{solicitud_original.get('correo_asesor')}'")
            else:
                print(f"   📍 ❌ correo_asesor NO encontrado en ninguna ubicación")

            # Verificar correo_banco_usuario
            if original_json.get("correo_banco_usuario"):
                print(f"   📍 ✅ correo_banco_usuario encontrado en RAÍZ: '{original_json.get('correo_banco_usuario')}'")
            elif solicitud_original.get("correo_banco_usuario"):
                print(f"   📍 ✅ correo_banco_usuario encontrado en SOLICITUDES[0]: '{solicitud_original.get('correo_banco_usuario')}'")
            else:
                print(f"   📍 ❌ correo_banco_usuario NO encontrado en ninguna ubicación")

            # Mostrar estructura de solicitudes para debugging
            print(f"   🔍 DEBUG ESTRUCTURA SOLICITUDES:")
            if original_json.get("solicitudes"):
                print(f"      - Cantidad de solicitudes: {len(original_json.get('solicitudes', []))}")
                if solicitud_original:
                    print(f"      - Claves en solicitudes[0]: {list(solicitud_original.keys())}")
                    # Mostrar solo los campos relevantes
                    campos_relevantes = ['nombre_asesor', 'correo_asesor', 'nombre_banco_usuario', 'correo_banco_usuario']
                    for campo in campos_relevantes:
                        valor = solicitud_original.get(campo, 'NO_ENCONTRADO')
                        print(f"      - {campo}: '{valor}'")
            else:
                print(f"      - No hay solicitudes en el JSON")
        else:
            # Fallback: usar datos del detalle_credito (método anterior)
            print(f"⚠️ WARNING - No se recibió JSON original, usando método fallback desde detalle_credito")
            nombre_asesor = detalle_credito.get("nombre_asesor", "").strip()
            correo_asesor = detalle_credito.get("correo_asesor", "").strip()
            nombre_banco_usuario = detalle_credito.get("nombre_banco_usuario", "").strip()
            correo_banco_usuario = detalle_credito.get("correo_banco_usuario", "").strip()
            print(f"   👨‍💼 Asesor (fallback): '{nombre_asesor}' ('{correo_asesor}')")
            print(f"   🏦 Usuario banco (fallback): '{nombre_banco_usuario}' ('{correo_banco_usuario}')")
            print(f"   📋 Claves disponibles en detalle_credito: {list(detalle_credito.keys())}")

            # También intentar extraer desde la respuesta procesada
            if solicitudes and len(solicitudes) > 0:
                primera_solicitud_procesada = solicitudes[0]
                detalle_credito_procesado = primera_solicitud_procesada.get("detalle_credito", {})
                print(f"   🔍 Intentando extraer desde solicitud procesada...")
                print(f"   📋 Claves en detalle_credito procesado: {list(detalle_credito_procesado.keys())}")

                # Usar datos procesados si no se encontraron en detalle_credito original
                if not correo_asesor:
                    correo_asesor = detalle_credito_procesado.get("correo_asesor", "").strip()
                    nombre_asesor = detalle_credito_procesado.get("nombre_asesor", "").strip()
                if not correo_banco_usuario:
                    correo_banco_usuario = detalle_credito_procesado.get("correo_banco_usuario", "").strip()
                    nombre_banco_usuario = detalle_credito_procesado.get("nombre_banco_usuario", "").strip()

                print(f"   👨‍💼 Asesor (procesado): '{nombre_asesor}' ('{correo_asesor}')")
                print(f"   🏦 Usuario banco (procesado): '{nombre_banco_usuario}' ('{correo_banco_usuario}')")

        # Validar que los datos críticos no estén vacíos
        print(f"\n🔍 VALIDACIÓN FINAL DE DATOS:")
        print(f"   📧 Correo solicitante: '{correo_electronico}' - {'✅ Válido' if correo_electronico.strip() else '❌ Vacío'}")
        print(f"   👨‍💼 Asesor: '{nombre_asesor}' / '{correo_asesor}' - {'✅ Válido' if correo_asesor.strip() else '❌ Vacío'}")
        print(f"   🏦 Banco: '{nombre_banco_usuario}' / '{correo_banco_usuario}' - {'✅ Válido' if correo_banco_usuario.strip() else '❌ Vacío'}")

        # Resumen de dónde se encontraron los datos
        if original_json:
            print(f"   📍 RESUMEN DE UBICACIONES:")
            if correo_asesor:
                ubicacion_asesor = "raíz" if original_json.get("correo_asesor") else "solicitudes[0]"
                print(f"      - Datos asesor: encontrados en {ubicacion_asesor}")
            if correo_banco_usuario:
                ubicacion_banco = "raíz" if original_json.get("correo_banco_usuario") else "solicitudes[0]"
                print(f"      - Datos banco: encontrados en {ubicacion_banco}")

        # Mapear datos al formato esperado por el email
        datos_mapeados = {
            "id_radicado": id_radicado,
            "solicitante": {
                "nombre_completo": nombre_completo,
                "correo_electronico": correo_electronico,
                "datos_basicos": {
                    "tipo_identificacion": solicitante.get("tipo_identificacion", "N/A"),
                    "numero_documento": solicitante.get("numero_documento", "N/A"),
                    "fecha_nacimiento": solicitante.get("fecha_nacimiento", "N/A"),
                    "genero": solicitante.get("genero", "N/A")
                },
                "info_extra": info_extra,
                "ubicacion": detalle_direccion,
                "actividad_economica": detalle_actividad,
                "informacion_financiera": detalle_financiera,
                "referencias": referencias
            },
            "solicitud": {
                "banco_nombre": primera_solicitud.get("banco_nombre", "N/A"),
                "ciudad_solicitud": primera_solicitud.get("ciudad_solicitud", "N/A"),
                "estado": primera_solicitud.get("estado", "Pendiente"),
                "detalle_credito": detalle_credito
            },
            "asesor": {
                "nombre": nombre_asesor,
                "correo": correo_asesor
            },
            "banco": {
                "nombre_usuario": nombre_banco_usuario,
                "correo_usuario": correo_banco_usuario
            }
        }

        print(f"\n✅ DATOS MAPEADOS CORRECTAMENTE PARA ENVIO DE EMAILS:")
        print(f"   🆔 ID Radicado: {id_radicado}")
        print(f"   👤 Solicitante: {nombre_completo} ({correo_electronico})")
        print(f"   👨‍💼 Asesor: {nombre_asesor} ({correo_asesor})")
        print(f"   🏦 Banco: {nombre_banco_usuario} ({correo_banco_usuario})")
        print(f"   📊 Estado de emails: Solicitante={bool(correo_electronico.strip())}, Asesor={bool(correo_asesor.strip())}, Banco={bool(correo_banco_usuario.strip())}")

        return datos_mapeados

    except Exception as e:
        print(f"❌ ERROR CRITICO mapeando datos para email: {str(e)}")
        import traceback
        print(f"📋 Traceback completo: {traceback.format_exc()}")
        # Mostrar información de debugging adicional
        if 'original_json' in locals() and original_json:
            print(f"🔍 JSON original keys: {list(original_json.keys())}")
            if 'solicitudes' in original_json:
                print(f"🔍 Solicitudes disponibles: {len(original_json['solicitudes'])}")
        return None

def enviar_email_registro_completo(response_data, original_json=None):
    """
    Función principal para enviar los tres emails después de crear/editar un registro completo:
    1. Email al solicitante
    2. Email al asesor
    3. Email al banco

    Args:
        response_data: Respuesta del controlador con los datos creados
        original_json: JSON original enviado desde el frontend (para extraer correos)
    """
    try:
        # Mapear datos al formato esperado
        datos_email = mapear_datos_para_email(response_data, original_json)
        if not datos_email:
            print("❌ No se pudieron mapear los datos para el email")
            return False

        # Configurar email
        email_settings = config_email()
        if not email_settings["sender_password"]:
            print("❌ No se encontró la contraseña del email en las variables de entorno")
            return False

        resultados = {
            "solicitante": False,
            "asesor": False,
            "banco": False
        }

        # 1. Enviar email al solicitante
        email_solicitante = datos_email['solicitante']['correo_electronico']
        if email_solicitante and email_solicitante.strip():
            print("📧 Enviando email al solicitante...")
            resultados["solicitante"] = enviar_email_solicitante(email_settings, datos_email)
        else:
            print("⚠️ WARNING: No se encontró email del solicitante o está vacío")
            resultados["solicitante"] = False

        # Delay entre envíos para evitar rate limiting de Zoho
        if resultados["solicitante"]:
            print("⏳ Esperando 5 segundos antes del siguiente envío...")
            std_time.sleep(5)

        # 2. Enviar email al asesor
        email_asesor = datos_email['asesor']['correo']
        if email_asesor and email_asesor.strip():
            print("📧 Enviando email al asesor...")
            resultados["asesor"] = enviar_email_asesor(email_settings, datos_email)
        else:
            print("⚠️ WARNING: No se encontró email del asesor o está vacío")
            resultados["asesor"] = False

        # Delay entre envíos para evitar rate limiting de Zoho
        if resultados["asesor"]:
            print("⏳ Esperando 5 segundos antes del siguiente envío...")
            std_time.sleep(5)

        # 3. Enviar email al banco
        email_banco = datos_email['banco']['correo_usuario']
        ciudad_solicitud = datos_email['solicitud'].get('ciudad_solicitud', '').strip()
        banco_nombre = datos_email['solicitud'].get('banco_nombre', '').strip()

        # Si no hay ciudad o banco, enviar a comercial@findii.co por defecto
        if not ciudad_solicitud or not banco_nombre or ciudad_solicitud == 'N/A' or banco_nombre == 'N/A':
            print("⚠️ WARNING: No se encontró ciudad o banco en la solicitud")
            print(f"   📍 Ciudad: '{ciudad_solicitud}' - Banco: '{banco_nombre}'")
            print("   📧 Enviando email al correo por defecto: comercial@findii.co")
            # Sobrescribir el email del banco con el correo por defecto
            datos_email['banco']['correo_usuario'] = 'comercial@findii.co'
            datos_email['banco']['nombre_usuario'] = 'Equipo Comercial Findii'
            resultados["banco"] = enviar_email_banco(email_settings, datos_email)
        elif email_banco and email_banco.strip():
            print("📧 Enviando email al banco...")
            resultados["banco"] = enviar_email_banco(email_settings, datos_email)
        else:
            print("⚠️ WARNING: No se encontró email del banco o está vacío")
            print("   📧 Enviando email al correo por defecto: comercial@findii.co")
            # Enviar a comercial@findii.co como fallback
            datos_email['banco']['correo_usuario'] = 'comercial@findii.co'
            datos_email['banco']['nombre_usuario'] = 'Equipo Comercial Findii'
            resultados["banco"] = enviar_email_banco(email_settings, datos_email)

        # Verificar si al menos uno se envió exitosamente
        exito_general = any(resultados.values())

        # Resumen mejorado con emojis
        print(f"\n📊 RESUMEN DE ENVÍOS DE CORREOS:")
        print(f"   👤 Solicitante: {'✅ Enviado' if resultados['solicitante'] else '❌ Fallido/Sin email'}")
        print(f"   👨‍💼 Asesor: {'✅ Enviado' if resultados['asesor'] else '❌ Fallido/Sin email'}")
        print(f"   🏦 Banco: {'✅ Enviado' if resultados['banco'] else '❌ Fallido/Sin email'}")
        print(f"   📊 Total exitosos: {sum(resultados.values())}/3")

        return exito_general

    except Exception as e:
        print(f"❌ ERROR GENERAL enviando emails de registro completo: {str(e)}")
        print(f"📊 Resumen de envíos: Solicitante: ❌, Asesor: ❌, Banco: ❌")
        return False

def format_second_holder_info(info):
    """Formatea la información del segundo titular para mostrarla de manera legible"""
    if not info or info == 'N/A' or info == '':
        return ""

    try:
        # Si es un JSON, formatearlo de manera legible
        if isinstance(info, dict):
            formatted_info = []
            for key, value in info.items():
                if value and value != 'N/A' and value != '':
                    # Convertir la clave a un formato más legible
                    key_formatted = key.replace('_', ' ').title()
                    formatted_info.append(f"{key_formatted}: {value}")

            if formatted_info:
                return "\n        " + "\n        ".join([f"• {item}" for item in formatted_info])
            else:
                return ""
        else:
            # Si es un string, mostrarlo tal como está
            return f"\n        • {info}"
    except:
        # Si hay algún error, mostrar la información tal como está
        return f"\n        • {info}"

def email_body_and_send(email_settings, data):
    try:
        print("Datos a usar para el correo")
        print(data)
        print()

        msg = MIMEMultipart()
        msg['From'] = email_settings["sender_email"]
        msg['To'] = data['solicitante']['correo_electronico']
        msg['Subject'] = "Confirmación de registro de solicitud"

        # Formatear datos básicos del solicitante
        datos_basicos_str = formatear_campos_dinamicos(data['solicitante']['datos_basicos'])

        # Formatear información extra del solicitante
        info_extra_str = formatear_campos_dinamicos(data['solicitante']['info_extra'], "Información Adicional")

        # Formatear detalles del crédito
        detalle_credito_str = formatear_campos_dinamicos(data['solicitud']['detalle_credito'], "Detalles del Crédito")

        # Cuerpo del mensaje
        body = f"""
        Estimado/a {data['solicitante']['nombre_completo']},

        ¡Gracias por confiar en Findii! Su solicitud ha sido registrada exitosamente.

        A continuación encontrará el resumen de la información registrada:

        DATOS DEL SOLICITANTE
        ====================
        • Nombre: {data['solicitante']['nombre_completo']}
        • Email: {data['solicitante']['correo_electronico']}

        DATOS BÁSICOS
        =============
{datos_basicos_str}
{info_extra_str}

        INFORMACIÓN DE LA SOLICITUD
        ==========================
        • Banco: {data['solicitud']['banco_nombre']}
        • Ciudad de solicitud: {data['solicitud']['ciudad_solicitud']}
        • Estado: {data['solicitud']['estado']}
{detalle_credito_str}

        Uno de nuestros asesores se pondrá en contacto con usted muy pronto para dar seguimiento a su solicitud.

        Si tiene alguna duda, puede responder directamente a este correo.

        ¡Gracias por elegirnos!

        Cordialmente,
        Equipo Findii
        """

        msg.attach(MIMEText(body, 'plain'))

        # Enviar el correo directamente
        resultado = send_email(email_settings, msg)
        return resultado

    except Exception as e:
        print(f"Error al preparar el correo: {str(e)}")
        return False

def send_email(email_settings, msg):
    """
    Envía correo usando SSL para Zoho (puerto 465)
    """
    max_attempts = 3
    retry_delay = 2  # segundos entre intentos

    for attempt in range(max_attempts):
        try:
            print(f"🔧 Configurando conexión SMTP para Zoho...")
            print(f"   📧 Servidor: {email_settings['smtp_server']}")
            print(f"   🔌 Puerto: {email_settings['smtp_port']}")
            print(f"   👤 Usuario: {email_settings['sender_email']}")

            # Para Zoho con puerto 465, usar SMTP_SSL directamente
            if email_settings["smtp_port"] == 465:
                print("   🔒 Usando SSL directo (puerto 465)")
                server = smtplib.SMTP_SSL(email_settings["smtp_server"], email_settings["smtp_port"])
            else:
                print("   🔓 Usando STARTTLS")
                server = smtplib.SMTP(email_settings["smtp_server"], email_settings["smtp_port"])
                server.starttls()

            # Configurar timeout y debug
            server.set_debuglevel(0)  # Cambiar a 1 para debug detallado

            print("   🔐 Iniciando autenticación...")
            server.login(email_settings["sender_email"], email_settings["sender_password"])
            print("   ✅ Autenticación exitosa")

            # Verifica que msg sea un objeto EmailMessage o MIMEMultipart
            if isinstance(msg, dict):
                # Si es un diccionario, construye un mensaje adecuado
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText

                email_msg = MIMEMultipart()
                email_msg['From'] = email_settings["sender_email"]
                email_msg['To'] = msg.get('to', '')
                email_msg['Subject'] = msg.get('subject', 'Sin asunto')

                # El cuerpo del mensaje
                body = msg.get('body', '')
                if isinstance(body, dict):
                    body = str(body)  # Convertir diccionario a string si es necesario

                email_msg.attach(MIMEText(body, 'html' if msg.get('html', False) else 'plain'))

                # Enviar el mensaje correctamente formateado
                print("   📤 Enviando mensaje...")
                server.send_message(email_msg)
            else:
                # Si ya es un objeto de mensaje correctamente formateado
                print("   📤 Enviando mensaje...")
                server.send_message(msg)

            server.quit()
            print("   ✅ Correo enviado exitosamente")
            return True

        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Error de autenticación (intento {attempt+1}/{max_attempts}): {str(e)}")
            print("   💡 Verifica:")
            print("      - Email: credito@findii.co")
            print("      - Contraseña de aplicación (no la contraseña normal)")
            print("      - 2FA habilitado en Zoho")
            if attempt < max_attempts - 1:
                print(f"   ⏳ Reintentando en {retry_delay} segundos...")
                std_time.sleep(retry_delay)
            else:
                return False

        except smtplib.SMTPConnectError as e:
            print(f"❌ Error de conexión (intento {attempt+1}/{max_attempts}): {str(e)}")
            print("   💡 Verifica:")
            print("      - Conexión a internet")
            print("      - Servidor SMTP: smtp.zoho.com")
            print("      - Puerto: 465")
            if attempt < max_attempts - 1:
                print(f"   ⏳ Reintentando en {retry_delay} segundos...")
                std_time.sleep(retry_delay)
            else:
                return False

        except smtplib.SMTPDataError as e:
            error_msg = str(e)
            print(f"❌ Error de datos SMTP (intento {attempt+1}/{max_attempts}): {error_msg}")
            print(f"   🔍 Tipo de error: {type(e).__name__}")
            print(f"   📧 Tipo de msg: {type(msg)}")

            # Detectar rate limiting específico de Zoho
            if "5.4.6" in error_msg and "Unusual sending activity" in error_msg:
                rate_limit_delay = 10 + (attempt * 5)  # Incrementar delay progresivamente
                print(f"   🚫 Rate limiting detectado de Zoho")
                print(f"   💡 Sugerencia: Reducir frecuencia de envíos")
                if attempt < max_attempts - 1:
                    print(f"   ⏳ Esperando {rate_limit_delay} segundos por rate limiting...")
                    std_time.sleep(rate_limit_delay)
                else:
                    print("   ❌ Se agotaron los intentos - Rate limiting persistente")
                    return False
            else:
                if attempt < max_attempts - 1:
                    print(f"   ⏳ Reintentando en {retry_delay} segundos...")
                    std_time.sleep(retry_delay)
                else:
                    print("   ❌ Se agotaron los intentos para enviar el correo")
                    return False

        except Exception as e:
            print(f"❌ Error general (intento {attempt+1}/{max_attempts}): {str(e)}")
            print(f"   🔍 Tipo de error: {type(e).__name__}")
            print(f"   📧 Tipo de msg: {type(msg)}")

            if attempt < max_attempts - 1:
                print(f"   ⏳ Reintentando en {retry_delay} segundos...")
                std_time.sleep(retry_delay)
            else:
                print("   ❌ Se agotaron los intentos para enviar el correo")
                return False

def enviar_email_solicitante(email_settings, data):
    """
    Envía email de confirmación al solicitante
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = email_settings["sender_email"]
        msg['To'] = data['solicitante']['correo_electronico']
        msg['Subject'] = "✅ Tu solicitud de crédito ha sido registrada con éxito"

        # Extraer información para el email
        solicitante = data['solicitante']
        solicitud = data['solicitud']
        detalle_credito = solicitud.get('detalle_credito', {})

        # Obtener datos específicos del crédito
        tipo_credito = detalle_credito.get('tipo_credito', 'N/A')
        valor_vehiculo = detalle_credito.get('credito_vehicular', {}).get('valor_vehiculo', 'N/A') if 'credito_vehicular' in detalle_credito else 'N/A'
        monto_solicitado = detalle_credito.get('credito_vehicular', {}).get('monto_solicitado', 'N/A') if 'credito_vehicular' in detalle_credito else 'N/A'
        plazo = detalle_credito.get('credito_vehicular', {}).get('plazo_meses', 'N/A') if 'credito_vehicular' in detalle_credito else 'N/A'
        cuota_inicial = detalle_credito.get('credito_vehicular', {}).get('cuota_inicial', 'N/A') if 'credito_vehicular' in detalle_credito else 'N/A'

        # Obtener información adicional del solicitante
        info_extra = solicitante.get('info_extra', {})
        celular = info_extra.get('celular', 'N/A')
        profesion = info_extra.get('profesion', 'N/A')

        # Obtener fecha y hora actual en formato 12 horas
        fecha_hora_envio = datetime.now().strftime("%d/%m/%Y a las %I:%M:%S %p")

        # Cuerpo del mensaje para el solicitante
        body = f"""Hola {solicitante['nombre_completo']},

¡Gracias por confiar en Findii! 🚀 Hemos recibido tu solicitud de crédito y ya está en proceso de validación.

📅 Fecha y hora de envío: {fecha_hora_envio}

Aquí tienes un resumen de tu información registrada:

📌 Datos del solicitante

Nombre: {solicitante['nombre_completo']}

Documento: {solicitante['datos_basicos']['tipo_identificacion']} {solicitante['datos_basicos']['numero_documento']}

Email: {solicitante['correo_electronico']}

Celular: {celular}

Profesión: {profesion}

📌 Detalles del crédito

Banco seleccionado: {solicitud['banco_nombre']}

Tipo de crédito: {tipo_credito}

Valor del vehículo: ${valor_vehiculo}

Monto solicitado: ${monto_solicitado}

Plazo: {plazo} meses

Cuota inicial: ${cuota_inicial}

Estado actual: {solicitud['estado']}

👉 Muy pronto uno de nuestros asesores se pondrá en contacto contigo para guiarte en el proceso y resolver cualquier inquietud.

Si tienes dudas, puedes responder directamente a este correo o escribirnos en nuestra página web findii.co
Gracias por elegirnos,
El equipo Findii ✨"""

        msg.attach(MIMEText(body, 'plain'))
        return send_email(email_settings, msg)

    except Exception as e:
        print(f"Error enviando email al solicitante: {str(e)}")
        return False

def enviar_email_asesor(email_settings, data):
    """
    Envía email de notificación al asesor
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = email_settings["sender_email"]
        # Enviar tanto al asesor como a comercial@findii.co
        destinatarios = [data['asesor']['correo'], 'comercial@findii.co']
        msg['To'] = ', '.join(destinatarios)
        msg['Subject'] = f"Nueva solicitud asignada a tu gestión – Cliente: {data['solicitante']['nombre_completo']}"

        # Extraer información para el email
        solicitante = data['solicitante']
        solicitud = data['solicitud']
        detalle_credito = solicitud.get('detalle_credito', {})
        info_extra = solicitante.get('info_extra', {})

        # Obtener datos específicos del crédito
        tipo_credito = detalle_credito.get('tipo_credito', 'N/A')
        valor_vehiculo = detalle_credito.get('credito_vehicular', {}).get('valor_vehiculo', 'N/A') if 'credito_vehicular' in detalle_credito else 'N/A'
        monto_solicitado = detalle_credito.get('credito_vehicular', {}).get('monto_solicitado', 'N/A') if 'credito_vehicular' in detalle_credito else 'N/A'
        cuota_inicial = detalle_credito.get('credito_vehicular', {}).get('cuota_inicial', 'N/A') if 'credito_vehicular' in detalle_credito else 'N/A'
        plazo = detalle_credito.get('credito_vehicular', {}).get('plazo_meses', 'N/A') if 'credito_vehicular' in detalle_credito else 'N/A'

        # Información adicional del solicitante
        celular = info_extra.get('celular', 'N/A')
        profesion = info_extra.get('profesion', 'N/A')
        estado_civil = info_extra.get('estado_civil', 'N/A')

        # Obtener fecha y hora actual en formato 12 horas
        fecha_hora_envio = datetime.now().strftime("%d/%m/%Y a las %I:%M:%S %p")

        # Cuerpo del mensaje para el asesor
        body = f"""Hola {data['asesor']['nombre']},

Se ha registrado una nueva solicitud de crédito en Findii y está asignada a tu gestión. 🎯

📅 Fecha y hora de envío: {fecha_hora_envio}

A continuación, encontrarás el resumen de la información para dar inicio al proceso:

📌 Datos del cliente

Nombre: {solicitante['nombre_completo']}

Documento: {solicitante['datos_basicos']['tipo_identificacion']} {solicitante['datos_basicos']['numero_documento']}

Teléfono: {celular}

Email: {solicitante['correo_electronico']}

Profesión: {profesion}

Estado civil: {estado_civil}

📌 Detalles de la solicitud

Banco destino: {solicitud['banco_nombre']}

Ciudad: {solicitud['ciudad_solicitud']}

Tipo de crédito: {tipo_credito}

Valor del vehículo: ${valor_vehiculo}

Monto solicitado: ${monto_solicitado}

Cuota inicial: ${cuota_inicial}

Plazo: {plazo} meses

Estado: {solicitud['estado']}

👉 Para continuar con la gestión, accede al portal de asesores aquí:
https://updated-crm.netlify.app/

Recuerda que tu acompañamiento es clave para agilizar la aprobación del crédito y garantizar una excelente experiencia al cliente.

¡Éxitos en este proceso! 🚀

Equipo Findii"""

        msg.attach(MIMEText(body, 'plain'))
        return send_email(email_settings, msg)

    except Exception as e:
        print(f"Error enviando email al asesor: {str(e)}")
        return False

def enviar_email_banco(email_settings, data):
    """
    Envía email de notificación al banco con toda la información completa del solicitante
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = email_settings["sender_email"]
        msg['To'] = data['banco']['correo_usuario']
        msg['Subject'] = f"Nueva solicitud de crédito - {data['solicitante']['nombre_completo']}"

        # Extraer información para el email
        solicitante = data['solicitante']
        print(solicitante)
        solicitud = data['solicitud']
        # CORREGIDO: ubicacion está dentro del solicitante, no en data['ubicacion']
        ubicacion_data = solicitante.get('ubicacion', {})
        detalle_credito = solicitud.get('detalle_credito', {})
        info_extra = solicitante.get('info_extra', {})
        actividad_economica = solicitante.get('actividad_economica', {})
        informacion_financiera = solicitante.get('informacion_financiera', {})


        # EXTRAER DATOS DIRECTAMENTE COMO LO HACEN LOS OTROS EMAILS
        # Usar el mismo patrón que los emails del solicitante y asesor
        datos_basicos = solicitante.get('datos_basicos', {})

        fecha_nacimiento = datos_basicos.get('fecha_nacimiento', 'No especificado')
        genero_texto = "Masculino" if datos_basicos.get('genero', 'M') == 'M' else "Femenino"
        correo_electronico = solicitante.get('correo_electronico', solicitante.get('correo', 'No especificado'))

        # Información adicional del solicitante - acceso directo a info_extra
        celular = info_extra.get('celular', 'No especificado')
        profesion = info_extra.get('profesion', 'No especificado')
        nivel_estudios = info_extra.get('nivel_estudio', info_extra.get('nivel_estudios', 'No especificado'))
        estado_civil = info_extra.get('estado_civil', 'No especificado')
        nacionalidad = info_extra.get('nacionalidad', 'No especificado')
        lugar_nacimiento = info_extra.get('lugar_nacimiento', 'No especificado')
        fecha_expedicion = info_extra.get('fecha_expedicion', 'No especificado')
        personas_a_cargo = info_extra.get('personas_a_cargo', '0')

        # Información de ubicación - acceso directo
        # CORREGIDO: usar ubicacion_data y acceder directamente a los campos disponibles
        direccion_residencia = ubicacion_data.get('direccion_residencia', 'No especificado')
        tipo_vivienda = ubicacion_data.get('tipo_vivienda', 'No especificado')
        # Estos campos no están disponibles en la estructura actual, usar valores por defecto
        departamento_residencia = 'No especificado'
        ciudad_residencia = 'No especificado'
        correspondencia = ubicacion_data.get('recibir_correspondencia', 'No especificado')

        # Información de actividad económica - acceso directo
        # CORREGIDO: acceder directamente a actividad_economica sin detalle_actividad
        tipo_actividad = actividad_economica.get('tipo_actividad_economica', 'No especificado')
        # Para empleados, buscar en datos_empleado
        datos_empleado = actividad_economica.get('datos_empleado', {})
        empresa = datos_empleado.get('nombre_empresa', 'No especificado')
        cargo = datos_empleado.get('cargo', 'No especificado')
        salario_base = datos_empleado.get('salario_base', '0')

        # Información financiera - acceso directo
        # CORREGIDO: acceder directamente a informacion_financiera sin detalle_financiera
        ingreso_basico = informacion_financiera.get('ingreso_basico_mensual', '0')
        ingreso_variable = informacion_financiera.get('ingreso_variable_mensual', '0')
        otros_ingresos = informacion_financiera.get('otros_ingresos_mensuales', '0')
        gastos_financieros = informacion_financiera.get('gastos_financieros_mensuales', '0')
        gastos_personales = informacion_financiera.get('gastos_personales_mensuales', '0')
        declara_renta = informacion_financiera.get('declara_renta', 'No especificado')

        # Información del crédito - acceso directo
        tipo_credito = detalle_credito.get('tipo_credito', 'N/A')
        credito_vehicular = detalle_credito.get('credito_vehicular', {})
        if credito_vehicular:
            valor_vehiculo = credito_vehicular.get('valor_vehiculo', 'N/A')
            cuota_inicial = credito_vehicular.get('cuota_inicial', 'N/A')
            plazo_meses = credito_vehicular.get('plazo_meses', 'N/A')
            monto_solicitado = credito_vehicular.get('monto_solicitado', 'N/A')
            estado_vehiculo = credito_vehicular.get('estado_vehiculo', 'N/A')
            tipo_credito_especifico = credito_vehicular.get('tipo_credito', tipo_credito)
        else:
            valor_vehiculo = cuota_inicial = plazo_meses = monto_solicitado = estado_vehiculo = tipo_credito_especifico = 'N/A'



        # Formatear valores monetarios con separadores de miles
        def formatear_dinero(valor):
            if not valor or valor in ['N/A', 'No especificado', '', 'None', '0']:
                return 'No reportado'
            try:
                # Convertir a entero si es string numérico
                if isinstance(valor, str):
                    # Limpiar el valor de caracteres no numéricos excepto puntos y comas
                    valor_limpio = valor.replace('$', '').replace('.', '').replace(',', '').strip()
                    if valor_limpio.isdigit():
                        valor = int(valor_limpio)
                    else:
                        return 'No reportado'
                elif isinstance(valor, (int, float)):
                    valor = int(valor)
                else:
                    return 'No reportado'

                # Si el valor es 0, mostrar como no reportado
                if valor == 0:
                    return 'No reportado'

                # Formatear con separadores de miles
                return f"${valor:,}".replace(',', '.')
            except:
                return 'No reportado'



        # Obtener fecha y hora actual en formato 12 horas
        fecha_hora_envio = datetime.now().strftime("%d/%m/%Y a las %I:%M:%S %p")

        # Cuerpo del mensaje mejorado para el banco
        body = f"""Buenos días,

En Findii valoramos nuestra alianza y seguimos trabajando para que más clientes accedan a soluciones de financiamiento rápidas y efectivas. 🚀

📅 Fecha y hora de envío: {fecha_hora_envio}

Agradecemos su colaboración con la siguiente consulta para {solicitud['banco_nombre']}, relacionada con la radicación de un {tipo_credito_especifico.lower()}. Adjuntamos la documentación correspondiente para su revisión.

📋 DATOS DEL SOLICITANTE
Nombres: {solicitante['nombre_completo']}
Tipo de identificación: {solicitante['datos_basicos']['tipo_identificacion']}
Número de documento: {solicitante['datos_basicos']['numero_documento']}
Fecha de expedición: {fecha_expedicion}
Fecha de nacimiento: {fecha_nacimiento}
Lugar de nacimiento: {lugar_nacimiento}
Nacionalidad: {nacionalidad}
Género: {genero_texto}
Correo: {correo_electronico}
Teléfono / Celular: {celular}
Estado civil: {estado_civil}
Personas a cargo: {personas_a_cargo}
Nivel de estudios: {nivel_estudios}
Profesión: {profesion}

📌 UBICACIÓN
Departamento de residencia: {departamento_residencia}
Ciudad de residencia: {ciudad_residencia}
Dirección: {direccion_residencia}
Tipo de vivienda: {tipo_vivienda}
Correspondencia: {correspondencia}

📌 ACTIVIDAD ECONÓMICA
Tipo de actividad económica: {tipo_actividad}
Empresa: {empresa}
Cargo: {cargo}
Salario base: {formatear_dinero(salario_base)}

📌 INFORMACIÓN FINANCIERA
Total ingresos mensuales: {formatear_dinero(informacion_financiera.get('total_ingresos_mensuales', '0'))}
Total egresos mensuales: {formatear_dinero(informacion_financiera.get('total_egresos_mensuales', '0'))}
Detalle:
  Ingreso básico: {formatear_dinero(ingreso_basico)}
  Ingreso variable: {formatear_dinero(ingreso_variable)}
  Otros ingresos: {formatear_dinero(otros_ingresos)}
  Gastos financieros: {formatear_dinero(gastos_financieros)}
  Gastos personales: {formatear_dinero(gastos_personales)}
  Declara renta: {declara_renta}

📌 DETALLES DEL CRÉDITO
Banco: {solicitud['banco_nombre']}
Ciudad de solicitud: {solicitud['ciudad_solicitud']}
Estado de la solicitud: {solicitud['estado']}
Tipo de crédito: {tipo_credito}
Modalidad: {tipo_credito_especifico}
Estado del vehículo: {estado_vehiculo}
Valor del vehículo: {formatear_dinero(valor_vehiculo)}
Monto solicitado: {formatear_dinero(monto_solicitado)}
Cuota inicial: {formatear_dinero(cuota_inicial)}
Plazo: {plazo_meses} meses


Quedamos atentos a su confirmación y a cualquier información adicional que requieran para agilizar el proceso.

Gracias por su apoyo y gestión. 😊

Este mensaje se ha enviado automáticamente a través de nuestro portal de asesores.

Responsable: {data['asesor']['nombre']}
Correo del responsable: {data['asesor']['correo']}"""

        msg.attach(MIMEText(body, 'plain'))
        return send_email(email_settings, msg)

    except Exception as e:
        print(f"Error enviando email al banco: {str(e)}")
        return False
