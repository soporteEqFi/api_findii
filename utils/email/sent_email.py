import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import time as std_time
import uuid
from datetime import datetime
from typing import Tuple, Optional
import requests
import pytz

from dotenv import load_dotenv
load_dotenv()  # Cargar .env del directorio del proyecto
from data.supabase_conn import supabase

def config_email():
    ENVIRONMENT = os.getenv('ENVIRONMENT')
    if ENVIRONMENT == 'development':
        smtp_server = "smtp.gmail.com"
        sender_email = "equitisoporte@gmail.com"
        sender_password = os.getenv('EMAIL_PASSWORD_BACK')
        EMAIL_DEFAULT = 'equitisoporte@gmail.com'
        EMAIL_DEFAULT_NAME = 'Equipo desarrollo Findii'
    else:
        smtp_server = "smtp.zoho.com"
        sender_email = "credito@findii.co"
        sender_password = os.getenv('EMAIL_PASSWORD')
        EMAIL_DEFAULT = 'comercial@findii.co'
        EMAIL_DEFAULT_NAME = 'Equipo Comercial Findii'

    email_settings = {
        "smtp_server": smtp_server,
        "smtp_port": 465,
        "sender_email": sender_email,
        "sender_password": sender_password,
        "email_default": EMAIL_DEFAULT,
        "email_default_name": EMAIL_DEFAULT_NAME
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

        # print("Probando conexion SMTP con Zoho...")
        # print(f"   Servidor: {email_settings['smtp_server']}")
        # print(f"   Puerto: {email_settings['smtp_port']}")
        # print(f"   Email: {email_settings['sender_email']}")
        # print(f"   Contrasena: {'*' * len(email_settings['sender_password'])}")

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

        print(f"   🔍 DATA: {data}")

        # Extraer datos del solicitante
        solicitante = data.get("solicitante", {})
        solicitudes = data.get("solicitudes", [])
        ubicaciones = data.get("ubicaciones", [])
        actividad_economica = data.get("actividad_economica", {})
        informacion_financiera = data.get("informacion_financiera", {})
        referencias = data.get("referencias", [])
        documentos = data.get("documentos", [])

        # Obtener primera solicitud si existe
        primera_solicitud = solicitudes[0] if solicitudes else {}
        primera_ubicacion = ubicaciones[0] if ubicaciones else {}

        # Generar ID de radicado único
        id_radicado = f"FD-{uuid.uuid4().hex[:8].upper()}"

        # Preparar datos básicos del solicitante
        nombre_completo = f"{solicitante.get('nombres', '')} {solicitante.get('primer_apellido', '')} {solicitante.get('segundo_apellido', '')}"
        correo_electronico = solicitante.get("correo", "")

        # Extraer campos dinámicos
        info_extra = solicitante.get("info_extra", {}) or {}
        detalle_credito = primera_solicitud.get("detalle_credito", {})

        # CORREGIDO: Incluir todos los campos de ubicación (campos fijos + detalle_direccion)
        detalle_direccion = primera_ubicacion.get("detalle_direccion", {}) if primera_ubicacion else {}
        ubicacion_completa = {}
        if primera_ubicacion:
            # Incluir campos fijos de ubicación
            ubicacion_completa["ciudad_residencia"] = primera_ubicacion.get("ciudad_residencia")
            ubicacion_completa["departamento_residencia"] = primera_ubicacion.get("departamento_residencia")
            # Incluir todos los campos de detalle_direccion
            if isinstance(detalle_direccion, dict):
                ubicacion_completa.update(detalle_direccion)

        detalle_actividad = actividad_economica.get("detalle_actividad", {}) if actividad_economica else {}
        detalle_financiera = informacion_financiera.get("detalle_financiera", {}) if informacion_financiera else {}

        # EXTRACCIÓN ROBUSTA DE CORREOS DESDE EL JSON ORIGINAL
        nombre_asesor = ""
        correo_asesor = ""
        nombre_banco_usuario = ""
        correo_banco_usuario = ""

        if original_json:
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

            # Verificar correo_asesor
            # if original_json.get("correo_asesor"):
            #     print(f"   📍 ✅ correo_asesor encontrado en RAÍZ: '{original_json.get('correo_asesor')}'")
            # elif solicitud_original.get("correo_asesor"):
            #     print(f"   📍 ✅ correo_asesor encontrado en SOLICITUDES[0]: '{solicitud_original.get('correo_asesor')}'")
            # else:
            #     print(f"   📍 ❌ correo_asesor NO encontrado en ninguna ubicación")

            # Verificar correo_banco_usuario
            # if original_json.get("correo_banco_usuario"):
            #     print(f"   📍 ✅ correo_banco_usuario encontrado en RAÍZ: '{original_json.get('correo_banco_usuario')}'")
            # elif solicitud_original.get("correo_banco_usuario"):
            #     print(f"   📍 ✅ correo_banco_usuario encontrado en SOLICITUDES[0]: '{solicitud_original.get('correo_banco_usuario')}'")
            # else:
            #     print(f"   📍 ❌ correo_banco_usuario NO encontrado en ninguna ubicación")

            # Mostrar estructura de solicitudes para debugging
            # print(f"   🔍 DEBUG ESTRUCTURA SOLICITUDES:")
            # if original_json.get("solicitudes"):
            #     print(f"      - Cantidad de solicitudes: {len(original_json.get('solicitudes', []))}")
            #     if solicitud_original:
            #         print(f"      - Claves en solicitudes[0]: {list(solicitud_original.keys())}")
            #         # Mostrar solo los campos relevantes
            #         campos_relevantes = ['nombre_asesor', 'correo_asesor', 'nombre_banco_usuario', 'correo_banco_usuario']
            #         for campo in campos_relevantes:
            #             valor = solicitud_original.get(campo, 'NO_ENCONTRADO')
            #             print(f"      - {campo}: '{valor}'")
            # else:
            #     print(f"      - No hay solicitudes en el JSON")
        else:
            # Fallback: usar datos del detalle_credito (método anterior)
            print(f"⚠️ WARNING - No se recibió JSON original, usando método fallback desde detalle_credito")
            nombre_asesor = detalle_credito.get("nombre_asesor", "").strip()
            correo_asesor = detalle_credito.get("correo_asesor", "").strip()
            nombre_banco_usuario = detalle_credito.get("nombre_banco_usuario", "").strip()
            correo_banco_usuario = detalle_credito.get("correo_banco_usuario", "").strip()
            # print(f"   👨‍💼 Asesor (fallback): '{nombre_asesor}' ('{correo_asesor}')")
            # print(f"   🏦 Usuario banco (fallback): '{nombre_banco_usuario}' ('{correo_banco_usuario}')")
            # print(f"   📋 Claves disponibles en detalle_credito: {list(detalle_credito.keys())}")

            # También intentar extraer desde la respuesta procesada
            if solicitudes and len(solicitudes) > 0:
                primera_solicitud_procesada = solicitudes[0]
                detalle_credito_procesado = primera_solicitud_procesada.get("detalle_credito", {})
                # print(f"   🔍 Intentando extraer desde solicitud procesada...")
                # print(f"   📋 Claves en detalle_credito procesado: {list(detalle_credito_procesado.keys())}")

                # Usar datos procesados si no se encontraron en detalle_credito original
                if not correo_asesor:
                    correo_asesor = detalle_credito_procesado.get("correo_asesor", "").strip()
                    nombre_asesor = detalle_credito_procesado.get("nombre_asesor", "").strip()
                if not correo_banco_usuario:
                    correo_banco_usuario = detalle_credito_procesado.get("correo_banco_usuario", "").strip()
                    nombre_banco_usuario = detalle_credito_procesado.get("nombre_banco_usuario", "").strip()

                # print(f"   👨‍💼 Asesor (procesado): '{nombre_asesor}' ('{correo_asesor}')")
                # print(f"   🏦 Usuario banco (procesado): '{nombre_banco_usuario}' ('{correo_banco_usuario}')")

        # Intentar usar usuario asignado directamente desde la BD para asegurar notificación correcta
        assigned_to_user_id = primera_solicitud.get("assigned_to_user_id")
        if assigned_to_user_id:
            try:
                usuario_asignado_resp = supabase.table("usuarios").select("nombre, correo").eq("id", assigned_to_user_id).execute()
                usuario_asignado_data = getattr(usuario_asignado_resp, "data", None)
                if isinstance(usuario_asignado_data, list) and usuario_asignado_data:
                    usuario_asignado = usuario_asignado_data[0]
                    correo_asignado = (usuario_asignado.get("correo") or "").strip()
                    nombre_asignado = (usuario_asignado.get("nombre") or "").strip()
                    if correo_asignado:
                        correo_asesor = correo_asignado
                    if nombre_asignado:
                        nombre_asesor = nombre_asignado
            except Exception as asignado_error:
                print(f"⚠️ No se pudo obtener datos del usuario asignado {assigned_to_user_id}: {asignado_error}")

        # CORREGIDO: Si el correo del banco está vacío, buscar en la BD por banco_nombre
        if not correo_banco_usuario or not correo_banco_usuario.strip():
            # Buscar banco_nombre en múltiples ubicaciones
            banco_nombre_buscar = (
                primera_solicitud.get("banco_nombre", "") or
                (original_json.get("banco_nombre", "") if original_json else "") or
                (original_json.get("solicitudes", [{}])[0].get("banco_nombre", "") if original_json and original_json.get("solicitudes") else "")
            )

            if banco_nombre_buscar and banco_nombre_buscar.strip():
                try:
                    empresa_id_email = solicitante.get("empresa_id")
                    if empresa_id_email:
                        # Buscar usuarios con rol "banco" cuyo info_extra.banco_nombre coincida
                        usuarios_banco_resp = supabase.table("usuarios").select("nombre, correo, info_extra").eq("rol", "banco").eq("empresa_id", empresa_id_email).execute()
                        usuarios_banco_data = getattr(usuarios_banco_resp, "data", None)

                        if isinstance(usuarios_banco_data, list) and usuarios_banco_data:
                            # Buscar usuario cuyo banco_nombre en info_extra coincida
                            for usuario_banco in usuarios_banco_data:
                                info_extra_banco = usuario_banco.get("info_extra", {})

                                # Parsear info_extra si es string
                                if isinstance(info_extra_banco, str):
                                    import json
                                    try:
                                        info_extra_banco = json.loads(info_extra_banco)
                                    except json.JSONDecodeError:
                                        info_extra_banco = {}

                                banco_nombre_usuario = info_extra_banco.get("banco_nombre", "") if isinstance(info_extra_banco, dict) else ""

                                # Comparar banco_nombre (case-insensitive y sin espacios)
                                if banco_nombre_usuario and banco_nombre_usuario.strip().lower() == banco_nombre_buscar.strip().lower():
                                    correo_banco_encontrado = (usuario_banco.get("correo") or "").strip()
                                    nombre_banco_encontrado = (usuario_banco.get("nombre") or "").strip()

                                    if correo_banco_encontrado:
                                        correo_banco_usuario = correo_banco_encontrado
                                        nombre_banco_usuario = nombre_banco_encontrado or nombre_banco_usuario
                                        print(f"   ✅ Correo del banco encontrado en BD: {correo_banco_usuario} (Banco: {banco_nombre_buscar})")
                                        break
                except Exception as error_busqueda_banco:
                    print(f"   ⚠️ No se pudo buscar correo del banco en BD: {error_busqueda_banco}")

        # Validar que los datos críticos no estén vacíos
        # print(f"\n🔍 VALIDACIÓN FINAL DE DATOS:")
        # print(f"   📧 Correo solicitante: '{correo_electronico}' - {'✅ Válido' if correo_electronico.strip() else '❌ Vacío'}")
        # print(f"   👨‍💼 Asesor: '{nombre_asesor}' / '{correo_asesor}' - {'✅ Válido' if correo_asesor.strip() else '❌ Vacío'}")
        # print(f"   🏦 Banco: '{nombre_banco_usuario}' / '{correo_banco_usuario}' - {'✅ Válido' if correo_banco_usuario.strip() else '❌ Vacío'}")

        # Resumen de dónde se encontraron los datos
        # if original_json:
        #     print(f"   📍 RESUMEN DE UBICACIONES:")
        #     if correo_asesor:
        #         ubicacion_asesor = "raíz" if original_json.get("correo_asesor") else "solicitudes[0]"
        #         print(f"      - Datos asesor: encontrados en {ubicacion_asesor}")
        #     if correo_banco_usuario:
        #         ubicacion_banco = "raíz" if original_json.get("correo_banco_usuario") else "solicitudes[0]"
        #         print(f"      - Datos banco: encontrados en {ubicacion_banco}")

        # Mapear datos al formato esperado por el email
        datos_mapeados = {
            "id_radicado": id_radicado,
            "solicitante": {
                "id": solicitante.get("id"),  # Incluir ID para poder obtener documentos después
                "nombre_completo": nombre_completo,
                "correo_electronico": correo_electronico,
                "datos_basicos": {
                    "tipo_identificacion": solicitante.get("tipo_identificacion", "N/A"),
                    "numero_documento": solicitante.get("numero_documento", "N/A"),
                    "fecha_nacimiento": solicitante.get("fecha_nacimiento", "N/A"),
                    "genero": solicitante.get("genero", "N/A")
                },
                "info_extra": info_extra,
                "ubicacion": ubicacion_completa,  # CORREGIDO: incluir todos los campos de ubicación
                "actividad_economica": detalle_actividad,
                "informacion_financiera": informacion_financiera,  # Incluir toda la información financiera, no solo el detalle
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
            },
            "documentos": documentos  # Incluir documentos para adjuntar
        }

        # print(f"\n✅ DATOS MAPEADOS CORRECTAMENTE PARA ENVIO DE EMAILS:")
        # print(f"   🆔 ID Radicado: {id_radicado}")
        # print(f"   👤 Solicitante: {nombre_completo} ({correo_electronico})")
        # print(f"   👨‍💼 Asesor: {nombre_asesor} ({correo_asesor})")
        # print(f"   🏦 Banco: {nombre_banco_usuario} ({correo_banco_usuario})")
        # print(f"   📊 Estado de emails: Solicitante={bool(correo_electronico.strip())}, Asesor={bool(correo_asesor.strip())}, Banco={bool(correo_banco_usuario.strip())}")
        # print(f"   📎 Documentos disponibles: {len(documentos)}")

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

        # Verificar documentos disponibles (ya deberían estar en response_data si se llamó desde el endpoint de envío)
        documentos_en_datos = datos_email.get('documentos', [])
        if documentos_en_datos:
            print(f"\n   ✅ Documentos disponibles en datos_email: {len(documentos_en_datos)}")
        else:
            print(f"\n   ℹ️ No hay documentos en datos_email (puede que no se hayan subido aún)")

        resultados = {
            "solicitante": False,
            "asesor": False,
            "banco": False
        }

        # 1. Enviar email al solicitante
        email_solicitante = datos_email['solicitante']['correo_electronico']
        if isinstance(email_solicitante, str) and email_solicitante.strip():
            resultados["solicitante"] = enviar_email_solicitante(email_settings, datos_email)
        else:
            print("⚠️ WARNING: No se encontró email del solicitante o está vacío")
            resultados["solicitante"] = False

        # Delay entre envíos para evitar rate limiting de Zoho
        if resultados["solicitante"]:
            print("⏳ Esperando 3 segundos antes del siguiente envío...")
            std_time.sleep(3)

        # 2. Enviar email al asesor
        email_asesor = datos_email['asesor']['correo']
        if isinstance(email_asesor, str) and email_asesor.strip():
            print("📧 Enviando email al asesor...")
            resultados["asesor"] = enviar_email_asesor(email_settings, datos_email)
        else:
            print("⚠️ WARNING: No se encontró email del asesor o está vacío")
            resultados["asesor"] = False

        # Delay entre envíos para evitar rate limiting de Zoho
        if resultados["asesor"]:
            print("⏳ Esperando 3 segundos antes del siguiente envío...")
            std_time.sleep(3)

        # 3. Enviar email al banco
        email_banco = datos_email.get('banco', {}).get('correo_usuario', '') or ''
        ciudad_raw = datos_email['solicitud'].get('ciudad_solicitud')
        banco_raw = datos_email['solicitud'].get('banco_nombre')

        ciudad_solicitud = ciudad_raw.strip() if isinstance(ciudad_raw, str) else ''
        banco_nombre = banco_raw.strip() if isinstance(banco_raw, str) else ''

        # Si no hay ciudad o banco, enviar a comercial@findii.co por defecto
        EMAIL_DEFAULT = email_settings.get("email_default", "comercial@findii.co")
        EMAIL_DEFAULT_NAME = email_settings.get("email_default_name", "Equipo Comercial Findii")

        # CORREGIDO: Validar y normalizar el email del banco
        email_banco = email_banco.strip() if isinstance(email_banco, str) else ''

        if not ciudad_solicitud or not banco_nombre or ciudad_solicitud == 'N/A' or banco_nombre == 'N/A':
            print("⚠️ WARNING: No se encontró ciudad o banco en la solicitud")
            print(f"   📍 Ciudad: '{ciudad_solicitud}' - Banco: '{banco_nombre}'")
            print(f"   📧 Enviando email al correo por defecto: {EMAIL_DEFAULT}")
            # Sobrescribir el email del banco con el correo por defecto
            datos_email['banco']['correo_usuario'] = EMAIL_DEFAULT
            datos_email['banco']['nombre_usuario'] = EMAIL_DEFAULT_NAME
            try:
                resultados["banco"] = enviar_email_banco(email_settings, datos_email)
            except Exception as e:
                print(f"❌ ERROR enviando email al banco (fallback por falta de ciudad/banco): {str(e)}")
                resultados["banco"] = False
        elif email_banco:
            print(f"📧 Enviando email al banco a: {email_banco}")
            try:
                resultados["banco"] = enviar_email_banco(email_settings, datos_email)
            except Exception as e:
                print(f"❌ ERROR enviando email al banco: {str(e)}")
                print(f"   📧 Intentando enviar al correo por defecto: {EMAIL_DEFAULT}")
                # Fallback: enviar a correo por defecto si falla el envío al banco
                datos_email['banco']['correo_usuario'] = EMAIL_DEFAULT
                datos_email['banco']['nombre_usuario'] = EMAIL_DEFAULT_NAME
                try:
                    resultados["banco"] = enviar_email_banco(email_settings, datos_email)
                except Exception as e2:
                    print(f"❌ ERROR enviando email al banco (fallback): {str(e2)}")
                    resultados["banco"] = False
        else:
            print("⚠️ WARNING: No se encontró email del banco o está vacío")
            print(f"   📧 Enviando email al correo por defecto: {EMAIL_DEFAULT}")
            # Enviar a comercial@findii.co como fallback
            datos_email['banco']['correo_usuario'] = EMAIL_DEFAULT
            datos_email['banco']['nombre_usuario'] = EMAIL_DEFAULT_NAME
            try:
                resultados["banco"] = enviar_email_banco(email_settings, datos_email)
            except Exception as e:
                print(f"❌ ERROR enviando email al banco (fallback por falta de email): {str(e)}")
                resultados["banco"] = False

        # Verificar si al menos uno se envió exitosamente
        exito_general = any(resultados.values())

        # Resumen mejorado con emojis
        # print(f"\n📊 RESUMEN DE ENVÍOS DE CORREOS:")
        # print(f"   👤 Solicitante: {'✅ Enviado' if resultados['solicitante'] else '❌ Fallido/Sin email'}")
        # print(f"   👨‍💼 Asesor: {'✅ Enviado' if resultados['asesor'] else '❌ Fallido/Sin email'}")
        # print(f"   🏦 Banco: {'✅ Enviado' if resultados['banco'] else '❌ Fallido/Sin email'}")
        # print(f"   📊 Total exitosos: {sum(resultados.values())}/3")

        return exito_general

    except Exception as e:
        print(f"❌ ERROR GENERAL enviando emails de registro completo: {str(e)}")
        print(f"📊 Resumen de envíos: Solicitante: ❌, Asesor: ❌, Banco: ❌")
        return False

def descargar_archivo_desde_url(url: str, timeout: int = 30) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Descarga un archivo desde una URL y retorna los bytes del archivo y el nombre.

    Args:
        url: URL del archivo a descargar
        timeout: Tiempo máximo de espera en segundos

    Returns:
        Tupla (bytes_del_archivo, nombre_archivo) o (None, None) si hay error
    """
    try:
        print(f"   📥 Descargando archivo desde: {url}")
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()

        # Intentar obtener el nombre del archivo desde el header Content-Disposition
        content_disposition = response.headers.get('Content-Disposition', '')
        nombre_archivo = None
        if 'filename=' in content_disposition:
            nombre_archivo = content_disposition.split('filename=')[1].strip('"\'')

        # Si no hay nombre en el header, extraer de la URL
        if not nombre_archivo:
            nombre_archivo = url.split('/')[-1].split('?')[0]
            if not nombre_archivo or nombre_archivo == '':
                nombre_archivo = 'documento'

        # Leer el contenido del archivo
        archivo_bytes = response.content
        print(f"   ✅ Archivo descargado: {nombre_archivo} ({len(archivo_bytes)} bytes)")

        return archivo_bytes, nombre_archivo

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error descargando archivo desde {url}: {str(e)}")
        return None, None
    except Exception as e:
        print(f"   ❌ Error inesperado descargando archivo: {str(e)}")
        return None, None

def adjuntar_documentos_a_email(msg: MIMEMultipart, documentos: list, descripcion: str = "documentos"):
    """
    Adjunta documentos a un mensaje de email.

    Args:
        msg: Objeto MIMEMultipart del email
        documentos: Lista de documentos con estructura:
            [
                {
                    "nombre": "nombre_archivo.pdf",
                    "documento_url": "https://...",
                    "_bytes": b"..." (opcional, bytes en memoria para adjuntar directamente),
                    "_content_type": "application/pdf" (opcional, tipo MIME)
                },
                ...
            ]
        descripcion: Descripción para mensajes de log

    Returns:
        Número de documentos adjuntados exitosamente
    """
    print(f"\n   🔍 DEBUG adjuntar_documentos_a_email:")
    print(f"      📊 documentos recibido: {documentos is not None}")
    print(f"      📊 es lista: {isinstance(documentos, list)}")
    print(f"      📊 cantidad: {len(documentos) if documentos and isinstance(documentos, list) else 0}")

    if not documentos or not isinstance(documentos, list):
        print(f"   ⚠️ No se pueden adjuntar documentos: documentos es None o no es lista")
        return 0

    documentos_adjuntados = 0

    print(f"\n   📎 Adjuntando {len(documentos)} {descripcion}...")

    for idx, doc in enumerate(documentos):
        print(f"\n   🔍 Procesando documento {idx+1}/{len(documentos)}...")
        try:
            nombre_archivo = doc.get("nombre") or doc.get("nombre_archivo") or "documento"

            # PRIORIDAD 1: Usar bytes directamente si están disponibles (más eficiente)
            if "_bytes" in doc and doc["_bytes"]:
                archivo_bytes = doc["_bytes"]
                tipo_mime = doc.get("_content_type", "application/octet-stream")
                print(f"   📎 Usando bytes en memoria para: {nombre_archivo}")
            else:
                # PRIORIDAD 2: Descargar desde URL si no hay bytes en memoria
                documento_url = doc.get("documento_url") or doc.get("url")

                if not documento_url:
                    print(f"   ⚠️ Documento sin URL ni bytes, saltando: {nombre_archivo}")
                    continue

                print(f"   📥 Descargando desde URL: {nombre_archivo}")
                archivo_bytes, nombre_descargado = descargar_archivo_desde_url(documento_url)

                if not archivo_bytes:
                    print(f"   ❌ No se pudo descargar el archivo: {nombre_archivo}")
                    continue

                # Usar el nombre del documento si está disponible, sino el descargado
                nombre_archivo = nombre_archivo if nombre_archivo != "documento" else nombre_descargado

                # Determinar el tipo MIME basado en la extensión
                extension = os.path.splitext(nombre_archivo)[1].lower()
                tipo_mime_map = {
                    '.pdf': 'application/pdf',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.doc': 'application/msword',
                    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    '.xls': 'application/vnd.ms-excel',
                    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                }
                tipo_mime = tipo_mime_map.get(extension, 'application/octet-stream')

            # Crear el adjunto
            tipo_principal, tipo_secundario = tipo_mime.split('/', 1) if '/' in tipo_mime else ('application', 'octet-stream')
            part = MIMEBase(tipo_principal, tipo_secundario)
            part.set_payload(archivo_bytes)
            encoders.encode_base64(part)

            # Configurar headers del adjunto
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{nombre_archivo}"'
            )

            # Adjuntar al mensaje
            print(f"   🔧 Adjuntando part al mensaje...")
            msg.attach(part)
            print(f"   ✅ Part adjuntado exitosamente")
            documentos_adjuntados += 1
            print(f"   ✅ Documento adjuntado: {nombre_archivo} ({len(archivo_bytes)} bytes)")

        except Exception as e:
            print(f"   ❌ Error adjuntando documento {doc.get('nombre', 'desconocido')}: {str(e)}")
            continue

    print(f"   📊 Total documentos adjuntados: {documentos_adjuntados}/{len(documentos)}")
    return documentos_adjuntados

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
    ⚠️ MODO DEBUG: El envío real está bloqueado temporalmente
    """
    # ========== MODO DEBUG: ENVÍO BLOQUEADO ==========
    # Extraer información del mensaje para logginghttp://localhost:5173/
    # destinatario = msg.get('To', 'Desconocido') if isinstance(msg, dict) else getattr(msg, 'get', lambda x: 'Desconocido')('To')
    # asunto = msg.get('Subject', 'Sin asunto') if isinstance(msg, dict) else getattr(msg, 'get', lambda x: 'Sin asunto')('Subject')

    # print("=" * 80)
    # print("🚫 MODO DEBUG: ENVÍO DE CORREO BLOQUEADO")
    # print("=" * 80)
    # print(f"📧 CORREO QUE SE ENVIARÍA:")
    # print(f"   ✉️  DE:      {email_settings.get('sender_email', 'N/A')}")
    # print(f"   📬 PARA:    {destinatario}")
    # print(f"   📝 ASUNTO:  {asunto}")
    # print(f"   🌐 SERVIDOR: {email_settings.get('smtp_server', 'N/A')}")
    # print(f"   🔌 PUERTO:   {email_settings.get('smtp_port', 'N/A')}")
    # print("=" * 80)
    # print("✅ Simulación exitosa - El correo NO fue enviado realmente")
    # print("=" * 80)

    # Retornar True para simular envío exitoso
    # return True

    # ========== CÓDIGO ORIGINAL COMENTADO ==========
    max_attempts = 3
    retry_delay = 2  # segundos entre intentos

    for attempt in range(max_attempts):
        try:
            # print(f"🔧 Configurando conexión SMTP para Zoho...")
            # print(f"   📧 Servidor: {email_settings['smtp_server']}")
            # print(f"   🔌 Puerto: {email_settings['smtp_port']}")
            # print(f"   👤 Usuario: {email_settings['sender_email']}")

            # Para Zoho con puerto 465, usar SMTP_SSL directamente
            if email_settings["smtp_port"] == 465:
                # print("   🔒 Usando SSL directo (puerto 465)")
                server = smtplib.SMTP_SSL(email_settings["smtp_server"], email_settings["smtp_port"])
            else:
                # print("   🔓 Usando STARTTLS")
                server = smtplib.SMTP(email_settings["smtp_server"], email_settings["smtp_port"])
                server.starttls()

            # Configurar timeout y debug
            server.set_debuglevel(0)  # Cambiar a 1 para debug detallado

            # print("   🔐 Iniciando autenticación...")
            server.login(email_settings["sender_email"], email_settings["sender_password"])
            # print("   ✅ Autenticación exitosa")

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
                # print("   📤 Enviando mensaje...")
                server.send_message(email_msg)
            else:
                # Si ya es un objeto de mensaje correctamente formateado
                # print("   📤 Enviando mensaje...")
                server.send_message(msg)

            server.quit()
            # print("   ✅ Correo enviado exitosamente")
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
        info_extra = solicitante.get('info_extra', {}) or {}
        ubicacion_solicitante = solicitante.get('ubicacion', {}) or {}
        # CORREGIDO: Buscar celular en múltiples ubicaciones (info_extra y ubicacion)
        celular = (info_extra.get('celular') or
                  info_extra.get('telefono') or
                  ubicacion_solicitante.get('celular') or
                  ubicacion_solicitante.get('telefono') or
                  'N/A')
        profesion = info_extra.get('profesion', 'N/A')

        # Obtener fecha y hora actual en formato 12 horas (zona horaria America/Bogota)
        fecha_hora_envio = datetime.now(pytz.timezone('America/Bogota')).strftime("%d/%m/%Y a las %I:%M:%S %p")

        # Cuerpo del mensaje para el solicitante
        body = f"""Hola {solicitante['nombre_completo']},

¡Gracias por confiar en Findii! 🚀 Hemos recibido tu solicitud de crédito y ya está en proceso de validación.

📅 Fecha y hora de envío: {fecha_hora_envio}

Aquí tienes un resumen de tu información registrada:

📌 DATOS DEL SOLICITANTE
Nombre: {solicitante['nombre_completo']}
Documento: {solicitante['datos_basicos']['tipo_identificacion']} {solicitante['datos_basicos']['numero_documento']}
Email: {solicitante['correo_electronico']}
Celular: {celular}
Profesión: {profesion}

📌 DETALLES DEL CRÉDITO
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
        EMAIL_DEFAULT = email_settings.get("email_default", "comercial@findii.co")
        ENVIRONMENT = os.getenv('ENVIRONMENT')

        msg = MIMEMultipart()
        msg['From'] = email_settings["sender_email"]

        destinatarios = []
        correo_asesor = (data.get('asesor', {}) or {}).get('correo')

        if correo_asesor:
            destinatarios.append(correo_asesor)

        # Mantener copia operativa solo fuera de development
        if EMAIL_DEFAULT and ENVIRONMENT != 'development':
            destinatarios.append(EMAIL_DEFAULT)

        print("DEBUG: destinatarios", destinatarios)

        msg['To'] = ', '.join(destinatarios) if destinatarios else EMAIL_DEFAULT or ''

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
        ubicacion_solicitante = solicitante.get('ubicacion', {}) or {}
        # CORREGIDO: Buscar celular en múltiples ubicaciones (info_extra y ubicacion)
        celular = (info_extra.get('celular') or
                  info_extra.get('telefono') or
                  ubicacion_solicitante.get('celular') or
                  ubicacion_solicitante.get('telefono') or
                  'N/A')
        profesion = info_extra.get('profesion', 'N/A')
        estado_civil = info_extra.get('estado_civil', 'N/A')

        # Obtener fecha y hora actual en formato 12 horas (zona horaria America/Bogota)
        fecha_hora_envio = datetime.now(pytz.timezone('America/Bogota')).strftime("%d/%m/%Y a las %I:%M:%S %p")

        # Cuerpo del mensaje para el asesor
        body = f"""Hola {data['asesor']['nombre']},

Se ha registrado una nueva solicitud de crédito en Findii y está asignada a tu gestión. 🎯

📅 Fecha y hora de envío: {fecha_hora_envio}

A continuación, encontrarás el resumen de la información para dar inicio al proceso:

📌 DATOS DEL CLIENTE
Nombre: {solicitante['nombre_completo']}
Documento: {solicitante['datos_basicos']['tipo_identificacion']} {solicitante['datos_basicos']['numero_documento']}
Teléfono: {celular}
Email: {solicitante['correo_electronico']}
Profesión: {profesion}
Estado civil: {estado_civil}

📌 DETALLES DE LA SOLICITUD
Banco destino: {solicitud['banco_nombre']}
Ciudad: {solicitud['ciudad_solicitud']}
Tipo de crédito: {tipo_credito}
Valor del vehículo: ${valor_vehiculo}
Monto solicitado: ${monto_solicitado}
Cuota inicial: ${cuota_inicial}
Plazo: {plazo} meses
Estado: {solicitud['estado']}

👉 Para continuar con la gestión, accede al portal de asesores aquí:
https://oneplatform.findii.co/

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
        EMAIL_DEFAULT = email_settings.get("email_default", "comercial@findii.co")
        ENVIRONMENT = os.getenv('ENVIRONMENT')

        msg = MIMEMultipart()
        msg['From'] = email_settings["sender_email"]

        # CORREGIDO: Validar y obtener el correo del banco de manera segura
        correo_banco = data.get('banco', {}).get('correo_usuario', '') or ''
        correo_banco = correo_banco.strip() if isinstance(correo_banco, str) else ''

        # En development, solo enviar a equitisoporte@gmail.com
        if ENVIRONMENT == 'development':
            msg['To'] = EMAIL_DEFAULT
            print(f"🔧 [DEV] Enviando email al banco a: {EMAIL_DEFAULT}")
        else:
            # En producción, enviar al correo del banco o usar el default si está vacío
            if correo_banco:
                msg['To'] = correo_banco
                print(f"📧 [PROD] Enviando email al banco a: {correo_banco}")
            else:
                print(f"⚠️ [PROD] Correo del banco vacío, usando default: {EMAIL_DEFAULT}")
                msg['To'] = EMAIL_DEFAULT

        msg['Subject'] = f"Nueva solicitud de crédito - {data['solicitante']['nombre_completo']}"

        # Extraer información para el email
        solicitante = data['solicitante']
        print(solicitante)
        solicitud = data['solicitud']
        # CORREGIDO: ubicación está dentro del solicitante, no en data['ubicacion']
        ubicacion_data = solicitante.get('ubicacion', {})
        detalle_credito = solicitud.get('detalle_credito', {})
        info_extra = solicitante.get('info_extra', {})
        actividad_economica = solicitante.get('actividad_economica', {})
        informacion_financiera = solicitante.get('informacion_financiera', {})
        documentos = data.get('documentos', [])  # Obtener documentos desde datos mapeados

        # Debug: verificar documentos
        print(f"\n   🔍 DEBUG - Documentos recibidos en enviar_email_banco:")
        print(f"      📊 Cantidad: {len(documentos) if documentos else 0}")
        if documentos:
            print(f"      📋 Primer documento: {documentos[0] if len(documentos) > 0 else 'N/A'}")
            for idx, doc in enumerate(documentos[:3]):  # Mostrar primeros 3
                print(f"      📄 Doc {idx+1}: nombre={doc.get('nombre', 'N/A')}, url={'✅' if doc.get('documento_url') else '❌'}, bytes={'✅' if doc.get('_bytes') else '❌'}")

        # EXTRAER DATOS DIRECTAMENTE COMO LO HACEN LOS OTROS EMAILS
        # Usar el mismo patrón que los emails del solicitante y asesor
        datos_basicos = solicitante.get('datos_basicos', {})

        fecha_nacimiento = datos_basicos.get('fecha_nacimiento', 'No especificado')
        genero_texto = "Masculino" if datos_basicos.get('genero', 'M') == 'M' else "Femenino"
        correo_electronico = solicitante.get('correo_electronico', solicitante.get('correo', 'No especificado'))

        # Información adicional del solicitante - acceso directo a info_extra
        # CORREGIDO: Buscar celular en múltiples ubicaciones (info_extra y ubicacion)
        celular = (info_extra.get('celular') or
                  info_extra.get('telefono') or
                  ubicacion_data.get('celular') or
                  ubicacion_data.get('telefono') or
                  'No especificado')
        profesion = info_extra.get('profesion', 'No especificado')
        nivel_estudios = info_extra.get('nivel_estudio', info_extra.get('nivel_estudios', 'No especificado'))
        estado_civil = info_extra.get('estado_civil', 'No especificado')
        nacionalidad = info_extra.get('nacionalidad', 'No especificado')
        lugar_nacimiento = info_extra.get('lugar_nacimiento', 'No especificado')
        fecha_expedicion = info_extra.get('fecha_expedicion', 'No especificado')
        personas_a_cargo = info_extra.get('personas_a_cargo', '0')

        # Información de ubicación - acceso directo
        # CORREGIDO: ahora ubicacion_data incluye todos los campos (ciudad_residencia, departamento_residencia + detalle_direccion)
        direccion_residencia = ubicacion_data.get('direccion_residencia', 'No especificado')
        tipo_vivienda = ubicacion_data.get('tipo_vivienda', 'No especificado')
        departamento_residencia = ubicacion_data.get('departamento_residencia', 'No especificado')
        ciudad_residencia = ubicacion_data.get('ciudad_residencia', 'No especificado')
        correspondencia = ubicacion_data.get('recibir_correspondencia', 'No especificado')

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

        # Información de actividad económica - formato dinámico
        # Extraer tipo de actividad para el título
        tipo_actividad = actividad_economica.get('tipo_actividad_economica', 'No especificado')
        # Crear copia sin el campo tipo_actividad_economica para formatear dinámicamente el resto
        actividad_economica_formatear = {k: v for k, v in actividad_economica.items() if k != 'tipo_actividad_economica'}
        # Formatear dinámicamente todos los campos de actividad económica
        actividad_economica_str_raw = formatear_campos_dinamicos(actividad_economica_formatear, "", nivel_indentacion=0)
        # Agregar salto de línea inicial si hay contenido formateado
        actividad_economica_str = f"\n{actividad_economica_str_raw}" if actividad_economica_str_raw else ""

        # Información financiera - formato dinámico
        # Extraer totales principales para mostrarlos primero
        totales_lineas = []
        total_ingresos = informacion_financiera.get('total_ingresos_mensuales', None)
        total_egresos = informacion_financiera.get('total_egresos_mensuales', None)
        total_activos = informacion_financiera.get('total_activos', None)
        total_pasivos = informacion_financiera.get('total_pasivos', None)

        if total_ingresos is not None:
            totales_lineas.append(f"Total ingresos mensuales: {formatear_dinero(total_ingresos)}")
        if total_egresos is not None:
            totales_lineas.append(f"Total egresos mensuales: {formatear_dinero(total_egresos)}")
        if total_activos is not None:
            totales_lineas.append(f"Total activos: {formatear_dinero(total_activos)}")
        if total_pasivos is not None:
            totales_lineas.append(f"Total pasivos: {formatear_dinero(total_pasivos)}")

        totales_str = "\n".join(totales_lineas) if totales_lineas else ""

        # Crear diccionario con solo los campos dinámicos (excluyendo campos del nivel superior ya mostrados)
        campos_fijos = ['total_ingresos_mensuales', 'total_egresos_mensuales', 'total_activos', 'total_pasivos',
                        'id', 'solicitante_id', 'empresa_id', 'created_at', 'updated_at']
        informacion_financiera_dinamica = {k: v for k, v in informacion_financiera.items()
                                          if k not in campos_fijos and v is not None and v != ''}
        # Formatear dinámicamente todos los campos restantes
        informacion_financiera_str_raw = formatear_campos_dinamicos(informacion_financiera_dinamica, "", nivel_indentacion=0)
        informacion_financiera_str = f"\n{informacion_financiera_str_raw}" if informacion_financiera_str_raw else ""

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

        # Obtener fecha y hora actual en formato 12 horas (zona horaria America/Bogota)
        fecha_hora_envio = datetime.now(pytz.timezone('America/Bogota')).strftime("%d/%m/%Y a las %I:%M:%S %p")

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
Tipo de actividad económica: {tipo_actividad}{actividad_economica_str if actividad_economica_str else ''}

📌 INFORMACIÓN FINANCIERA
{totales_str if totales_str else ''}{informacion_financiera_str}

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

👉 Para continuar con la gestión, accede al portal de bancos aquí:
https://oneplatform.findii.co/

{f'📎 NOTA: Se adjuntan {len(documentos)} documento(s) con la información y documentación del solicitante.' if documentos and isinstance(documentos, list) and len(documentos) > 0 else ''}

Quedamos atentos a su confirmación y a cualquier información adicional que requieran para agilizar el proceso.

Gracias por su apoyo y gestión. 😊

Este mensaje se ha enviado automáticamente a través de nuestro portal de asesores.

Responsable: {data['asesor']['nombre']}
Correo del responsable: {data['asesor']['correo']}"""

        msg.attach(MIMEText(body, 'plain'))

        # Verificar si hay documentos disponibles (ya deberían estar en datos_email)
        # Si no hay documentos, intentar obtener desde BD como fallback
        if not documentos or len(documentos) == 0:
            print(f"\n   🔍 No hay documentos en datos_email, intentando obtener desde BD...")
            from data.supabase_conn import supabase

            def _get_data_supabase_banco(resp):
                """Helper para obtener datos de respuesta de Supabase"""
                if hasattr(resp, "data"):
                    return resp.data
                if isinstance(resp, dict) and "data" in resp:
                    return resp["data"]
                return []

            # Obtener solicitante_id desde solicitante (dict del mapeo que ahora incluye id)
            solicitante_id_banco = None

            if isinstance(solicitante, dict):
                solicitante_id_banco = solicitante.get('id')

            if not solicitante_id_banco:
                solicitante_data = data.get('solicitante', {})
                if isinstance(solicitante_data, dict):
                    solicitante_id_banco = solicitante_data.get('id')

            if solicitante_id_banco:
                try:
                    documentos_bd_banco = supabase.table("documentos").select("*").eq("solicitante_id", solicitante_id_banco).execute()
                    documentos_data_banco = _get_data_supabase_banco(documentos_bd_banco)

                    if documentos_data_banco:
                        print(f"   ✅ Documentos encontrados en BD: {len(documentos_data_banco)}")
                        documentos = documentos_data_banco
                    else:
                        print(f"   ℹ️ No hay documentos en BD para solicitante_id: {solicitante_id_banco}")
                except Exception as e:
                    print(f"   ⚠️ Error obteniendo documentos desde BD: {e}")
        else:
            print(f"\n   ✅ Documentos ya disponibles en datos_email: {len(documentos)}")

        # Adjuntar documentos si existen
        print(f"\n   🔍 DEBUG - Antes de adjuntar documentos:")
        print(f"      📊 documentos es None: {documentos is None}")
        print(f"      📊 documentos es lista: {isinstance(documentos, list)}")
        print(f"      📊 len(documentos): {len(documentos) if documentos else 0}")

        if documentos and isinstance(documentos, list) and len(documentos) > 0:
            print(f"   ✅ Adjuntando {len(documentos)} documento(s)...")
            adjuntar_documentos_a_email(msg, documentos, "documentos del solicitante")
            print(f"   ✅ Función adjuntar_documentos_a_email completada")
        else:
            print("   ⚠️ No hay documentos para adjuntar al email del banco")
            print(f"      Razón: documentos={documentos}, tipo={type(documentos)}, len={len(documentos) if documentos else 'N/A'}")

        resultado = send_email(email_settings, msg)
        if resultado:
            print(f"✅ Email al banco enviado exitosamente a: {msg.get('To', 'desconocido')}")
        else:
            print(f"❌ Falló el envío del email al banco a: {msg.get('To', 'desconocido')}")
        return resultado

    except Exception as e:
        print(f"❌ ERROR CRÍTICO enviando email al banco: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        # CORREGIDO: Retornar False en lugar de relanzar para no interrumpir el flujo
        return False
