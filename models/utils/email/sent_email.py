import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import time as std_time

load_dotenv(os.path.expanduser("~/api_findii/.env"))


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

        
        # Cuerpo del mensaje
        body = f"""
        Estimado/a {data['solicitante']['nombre_completo']},

        ¡Gracias por confiar en Findii! Su solicitud ha sido registrada exitosamente.

        Para hacer seguimiento a su solicitud, puede ingresar al siguiente enlace:
        https://findii.co/seguimiento/{data['id_radicado']}

        A continuación encontrará el resumen de la información registrada:

        DATOS PERSONALES
        ================
        • Nombre: {data['solicitante']['nombre_completo']}
        • Documento: {data['solicitante']['tipo_documento']} {data['solicitante']['numero_documento']}
        • Fecha nacimiento: {data['solicitante']['fecha_nacimiento']}
        • Celular: {data['solicitante']['numero_celular']}
        • Email: {data['solicitante']['correo_electronico']}
        • Nivel educativo: {data['solicitante']['nivel_estudio']}
        • Profesión: {data['solicitante']['profesion']}
        • Estado civil: {data['solicitante']['estado_civil']}
        • Personas a cargo: {data['solicitante']['personas_a_cargo']}

        UBICACIÓN
        =========
        • Dirección: {data['ubicacion']['direccion_residencia']}
        • Tipo vivienda: {data['ubicacion']['tipo_vivienda']}
        • Barrio: {data['ubicacion']['barrio']}
        • Ciudad: {data['ubicacion']['ciudad_gestion']}
        • Departamento: {data['ubicacion']['departamento']}
        • Estrato: {data['ubicacion']['estrato']}

        INFORMACIÓN LABORAL
        ==================
        • Actividad: {data['actividad_economica']['actividad_economica']}
        • Empresa: {data['actividad_economica']['empresa_labora']}
        • Fecha vinculación: {data['actividad_economica']['fecha_vinculacion']}
        • Dirección empresa: {data['actividad_economica']['direccion_empresa']}
        • Teléfono empresa: {data['actividad_economica']['telefono_empresa']}
        • Tipo contrato: {data['actividad_economica']['tipo_contrato']}
        • Cargo: {data['actividad_economica']['cargo_actual']}

        INFORMACIÓN FINANCIERA
        =====================
        • Ingresos mensuales: ${data['informacion_financiera']['ingresos']}
        • Total egresos: ${data['informacion_financiera']['total_egresos']}
        • Total activos: ${data['informacion_financiera']['total_activos']}
        • Total pasivos: ${data['informacion_financiera']['total_pasivos']}

        PRODUCTO SOLICITADO
        ==================
        • Tipo de crédito: {data['producto']['tipo_credito']}
        • Banco: {data['banco']}
        • Valor inmueble: ${data['informacion_financiera']['valor_inmueble']}
        • Cuota inicial: ${data['informacion_financiera']['cuota_inicial']}
        • Porcentaje a financiar: {data['informacion_financiera']['porcentaje_financiar']}%
        • Plazo: {data['producto']['plazo_meses']} meses
        • Segundo titular: {'Sí' if data['producto']['segundo_titular'] == 'si' else 'No'}{format_second_holder_info(data['producto'].get('info_segundo_titular')) if data['producto']['segundo_titular'] == 'si' else ""}
        • Observaciones: {data['producto']['observacion']}

        Uno de nuestros asesores se pondrá en contacto con usted muy pronto para dar seguimiento a su solicitud.

        Si tiene alguna duda, puede responder directamente a este correo.

        ¡Gracias por elegirnos!

        Cordialmente,
        Equipo Findii
        """

        msg.attach(MIMEText(body, 'plain'))
        
        # Enviar el correo directamente
        send_email(email_settings, msg)
        
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


