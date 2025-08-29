import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time as std_time
import uuid

from dotenv import load_dotenv
# load_dotenv(os.path.expanduser("~/api_findii/.env"))
load_dotenv()

def config_email():
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "equitisoporte@gmail.com"  # Reemplaza con tu correo
    sender_password = os.getenv('EMAIL_PASSWORD')  # Reemplaza con tu contraseña de aplicación

    email_settings = {
        "smtp_server": smtp_server,
        "smtp_port": smtp_port,
        "sender_email": sender_email,
        "sender_password": sender_password
    }

    return email_settings

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

def mapear_datos_para_email(response_data):
    """
    Mapea los datos de la respuesta del controlador crear_registro_completo
    al formato esperado por la función de email (solo solicitante y solicitud)
    """
    try:
        data = response_data.get("data", {})
        
        # Extraer datos del solicitante
        solicitante = data.get("solicitante", {})
        solicitudes = data.get("solicitudes", [])
        
        # Obtener primera solicitud si existe
        primera_solicitud = solicitudes[0] if solicitudes else {}
        
        # Generar ID de radicado único
        id_radicado = f"FD-{uuid.uuid4().hex[:8].upper()}"
        
        # Preparar datos básicos del solicitante
        nombre_completo = f"{solicitante.get('nombres', '')} {solicitante.get('primer_apellido', '')} {solicitante.get('segundo_apellido', '')}".strip()
        correo_electronico = solicitante.get("correo", "")
        
        # Extraer campos dinámicos
        info_extra = solicitante.get("info_extra", {})
        detalle_credito = primera_solicitud.get("detalle_credito", {})
        
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
                "info_extra": info_extra
            },
            "solicitud": {
                "banco_nombre": primera_solicitud.get("banco_nombre", "N/A"),
                "ciudad_solicitud": primera_solicitud.get("ciudad_solicitud", "N/A"),
                "estado": primera_solicitud.get("estado", "Pendiente"),
                "detalle_credito": detalle_credito
            }
        }
        
        return datos_mapeados
        
    except Exception as e:
        print(f"Error mapeando datos para email: {str(e)}")
        return None

def enviar_email_registro_completo(response_data):
    """
    Función principal para enviar email después de crear un registro completo
    """
    try:
        # Mapear datos al formato esperado
        datos_email = mapear_datos_para_email(response_data)
        if not datos_email:
            print("❌ No se pudieron mapear los datos para el email")
            return False

        # Verificar que hay email del solicitante
        email_solicitante = datos_email['solicitante']['correo_electronico']
        if not email_solicitante:
            print("❌ No se encontró email del solicitante")
            return False

        # Configurar email
        email_settings = config_email()
        if not email_settings["sender_password"]:
            print("❌ No se encontró la contraseña del email en las variables de entorno")
            return False

        # Enviar email
        resultado = email_body_and_send(email_settings, datos_email)
        return resultado

    except Exception as e:
        print(f"❌ Error enviando email de registro completo: {str(e)}")
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

        Para hacer seguimiento a su solicitud, puede ingresar al siguiente enlace:
        https://findii.co/seguimiento/{data['id_radicado']}

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

    # Enviar correo
    max_attempts = 3
    retry_delay = 2  # segundos entre intentos

    for attempt in range(max_attempts):
        try:
            server = smtplib.SMTP(email_settings["smtp_server"], email_settings["smtp_port"])
            server.starttls()
            server.login(email_settings["sender_email"], email_settings["sender_password"])

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
                server.send_message(email_msg)
            else:
                # Si ya es un objeto de mensaje correctamente formateado
                server.send_message(msg)

            server.quit()
            print("Correo enviado exitosamente")
            return True
        except Exception as e:
            print(f"Intento {attempt+1}/{max_attempts} - Error al enviar correo: {str(e)}")
            # Imprimir información adicional para depuración
            print(f"Tipo de msg: {type(msg)}")
            if hasattr(msg, 'items'):
                print(f"Contenido de msg: {dict(msg)}")

            if attempt < max_attempts - 1:
                print(f"Reintentando en {retry_delay} segundos...")
                std_time.sleep(retry_delay)
            else:
                print("Se agotaron los intentos para enviar el correo")
                return False


