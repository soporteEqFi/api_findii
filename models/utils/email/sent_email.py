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

def email_body_and_send(email_settings, data):
    try:
        print("Datos a usar para el correo")
        print(data)
        print()
        
        msg = MIMEMultipart()
        msg['From'] = email_settings["sender_email"]
        msg['To'] = data['solicitante']['email']
        msg['Subject'] = "Confirmación de registro de solicitud"

        # Cuerpo del mensaje
        body = f"""
        Estimado/a {data['solicitante']['nombre']} {data['solicitante']['apellido']},

        Su solicitud ha sido registrada exitosamente con los siguientes detalles:

        Nombre completo: {data['solicitante']['nombre']} {data['solicitante']['apellido']}
        Tipo de documento: {data['solicitante']['tipo_documento']}
        Número de documento: {data['solicitante']['numero_documento']}
        Fecha de nacimiento: {data['solicitante']['fecha_nacimiento']}
        Número celular: {data['solicitante']['numero_celular']}
        Correo electrónico: {data['solicitante']['email']}
        Nivel de estudio: {data['solicitante']['nivel_estudio']}
        Profesión: {data['solicitante']['profesion']}
        Estado civil: {data['solicitante']['estado_civil']}
        Personas a cargo: {data['solicitante']['personas_a_cargo']}
        Dirección residencia: {data['ubicacion']['direccion']}
        Tipo de vivienda: {data['ubicacion']['tipo_vivienda']}
        Barrio: {data['ubicacion']['tiempo_residencia']}
        Departamento: {data['ubicacion']['departamento']}
        Estrato: {data['ubicacion']['estrato']}
        Ciudad gestión: {data['ubicacion']['ciudad']}
        Actividad económica: {data['actividad_economica']['actividad']}
        Empresa donde labora: {data['actividad_economica']['empresa']}
        Fecha vinculación: {data['actividad_economica']['fecha_vinculacion']}
        Dirección empresa: {data['actividad_economica']['direccion_empresa']}
        Teléfono empresa: {data['actividad_economica']['telefono_empresa']}
        Tipo de contrato: {data['actividad_economica']['tipo_contrato']}
        Cargo actual: {data['actividad_economica']['cargo']}
        Ingresos: {data['informacion_financiera']['ingresos']}
        Tipo de crédito: {data['producto']['tipo_credito']}
        Banco: {data['banco']}
        Valor del inmueble: {data['informacion_financiera']['valor_inmueble']}
        Plazo en meses: {data['producto']['plazo_meses']}
        Cuota inicial: {data['informacion_financiera']['cuota_inicial']}
        Porcentaje a financiar: {data['informacion_financiera']['porcentaje_financiar']}
        Total de egresos: {data['informacion_financiera']['total_egresos']}
        Total de activos: {data['informacion_financiera']['total_activos']}
        Total de pasivos: {data['informacion_financiera']['total_pasivos']}
        Segundo titular: {'Sí' if data['producto']['segundo_titular'] else 'No'}
        Observaciones: {data['producto']['observacion']}
        

        Nos pondremos en contacto con usted pronto para dar seguimiento a su solicitud.

        Saludos cordiales,
        Equipo de Findii
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


