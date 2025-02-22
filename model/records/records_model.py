from librerias import *
from model.generales.generales import *
from datetime import datetime
import time

# TODO: Separar lógica de agregar datos a cada tabla de la BD
# TODO: Agregar validaciones de datos a cada tabla
# TODO: Validar si el asesor existe en la tabla de asesores

class recordsModel():
    def add_record(self):
        try:
            agents_info = supabase.table("ASESORES").select('*').eq('usuario', request.json.get('asesor_usuario')).execute()
            print("Asesores info")
            print(agents_info.data)
            agent_id = agents_info.data[0]['id']

            # Crear registro del solicitante
            applicant = {
                "nombre_completo":  request.json.get('nombre_completo'),
                "tipo_documento": request.json.get('tipo_documento'),
                "numero_documento": request.json.get('numero_documento'),
                "fecha_nacimiento": request.json.get('fecha_nacimiento'),
                "numero_celular": request.json.get('numero_celular'),
                "correo_electronico": request.json.get('correo_electronico'),
                "nivel_estudio":  request.json.get('nivel_estudio'),
                "profesion": request.json.get('profesion'),  # Campo opcional
                "estado_civil": request.json.get('estado_civil'),
                "personas_a_cargo": request.json.get('personas_a_cargo')
            }

            res = supabase.table('SOLICITANTES').insert(applicant).execute()
            print("Solicitante")
            print(res.data)

            applicant_id = res.data[0]['id']

            # Crear registro de ubicación
            location = {
                "solicitante_id": applicant_id,
                "direccion_residencia": request.json.get('direccion_residencia'),
                "tipo_vivienda": request.json.get('tipo_vivienda'),
                "barrio": request.json.get('barrio'),
                "departamento": request.json.get('departamento'),
                "estrato": request.json.get('estrato'),
                "ciudad_gestion": request.json.get('ciudad_gestion')
            }

            res = supabase.table('UBICACION').insert(location).execute()

            print("Ubicaciones")
            print(res.data)
            
            # Crear registro de actividad económica
            economic_activity = {
                "solicitante_id": applicant_id,
                "actividad_economica": request.json.get('actividad_economica'),
                "empresa_labora": request.json.get('empresa_labora'),
                "fecha_vinculacion": datetime.strptime(request.json.get('fecha_vinculacion'), '%Y-%m-%d').strftime('%Y,%m,%d'),  # Comentado debido al error
                "direccion_empresa": request.json.get('direccion_empresa'),
                "telefono_empresa": request.json.get('telefono_empresa'),
                "tipo_contrato": request.json.get('tipo_contrato'),
                "cargo_actual": request.json.get('cargo_actual')
            }

            res = supabase.table('ACTIVIDAD_ECONOMICA').insert(economic_activity).execute()

            print("Actividad economica")
            print(res.data)
            
            # Crear registro de información financiera
            financial_info = {
                "solicitante_id": applicant_id,
                "ingresos": request.json.get('ingresos'),
                "valor_inmueble": request.json.get('valor_inmueble'),
                "cuota_inicial": request.json.get('cuota_inicial'),
                "porcentaje_financiar": request.json.get('porcentaje_financiar'),
                "total_egresos": request.json.get('total_egresos'),
                "total_activos": request.json.get('total_activos'),
                "total_pasivos": request.json.get('total_pasivos')
            }

            res = supabase.table('INFORMACION_FINANCIERA').insert(financial_info).execute()

            print("Informacion financiera")
            print(res.data)
            
            # Crear registro de producto solicitado
            product = {
                "solicitante_id": applicant_id,
                "tipo_credito": request.json.get('tipo_credito'),
                "plazo_meses": request.json.get('plazo_meses'),
                "segundo_titular": request.json.get('segundo_titular'),
                "observacion": request.json.get('observacion')
            }

            res = supabase.table('PRODUCTO_SOLICITADO').insert(product).execute()
            print("Producto solicitado")
            print(res.data)
            
            # Crear registro de solicitud
            solicitud = {
                "solicitante_id": applicant_id,
                "asesor_id": agent_id,
                "banco": request.json.get('banco'),
                # "fecha_solicitud": datetime.now().strftime('%d/%m/%Y %H %M %S')
            }

            res = supabase.table('SOLICITUDES').insert(solicitud).execute()
            print("Solicitud")
            print(res.data)

            print(applicant)
            print(location)
            print(economic_activity)
            print(financial_info)
            print(product)
            print(solicitud)
            
            return jsonify({
                "mensaje": "Registro creado exitosamente",
            }), 200
            
        except Exception as e:
            print("Ocurrió un error:", e)
            return jsonify({"mensaje": "Ocurrió un error al procesar la solicitud."}), 500
    
    def select_data(self):
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                # Consultas a las tablas
                tablas = {
                    "agents_info": "ASESORES",
                    "solicitantes": tabla_solicitantes,
                    "location": "UBICACION",
                    "economic_activity": "ACTIVIDAD_ECONOMICA",
                    "financial_info": "INFORMACION_FINANCIERA",
                    "product": "PRODUCTO_SOLICITADO",
                    "solicitud": "SOLICITUDES"
                }

                # Consultas a las tablas de Supabase en un solo paso
                registros = {
                    clave: supabase.table(tabla).select("*").execute().data
                    for clave, tabla in tablas.items()
                }
                # print(registros)

                if all(len(value) == 0 for value in registros.values()):
                    return jsonify({"mensaje": "No hay registros en estas tablas"}), 200

                return jsonify({"registros": registros}), 200

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    return jsonify({"mensaje": "Error en la lectura"}), 500
        
    def get_user_info(self, cedula):
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                if cedula is None or cedula == "":
                    return jsonify({"error" : "campo cedula vacío"}), 401

                response = supabase.table("TABLA_USUARIOS").select('*').eq('cedula', cedula).execute()

                response_data = response.data

                return jsonify({
                    "id": response_data[0]['id'],
                    "cedula": response_data[0]['cedula'],
                    "nombre": response_data[0]['nombre'],
                    "rol": response_data[0]['rol'],
                    "empresa": response_data[0]['empresa'],
                    "imagen_aliado": response_data[0]['imagen_aliado']
                    })

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    print("Ocurrió un error:", e)
                    return jsonify({"mensaje": "Ocurrió un error al procesar la solicitud."}), 500
        
    def filtrar_tabla(self):
        try:
            data = request.get_json()

            print("Datos recibidos:", data)

            if not data or "columna_buscar" not in data or "texto_buscar" not in data:
                print("Error: Faltan parámetros requeridos en la solicitud")
                return jsonify({"error": "Faltan parámetros en la solicitud"}), 400

            columna_buscar = data["columna_buscar"]
            texto_buscar = data["texto_buscar"]

            print(f"Buscando columna: {columna_buscar}, texto: {texto_buscar}")

            # Diccionario con las columnas de cada tabla (definido manualmente)
            columnas_tablas = {
                "SOLICITANTES": ["solicitante_id","nombre_completo","tipo_documento","numero_documento","fecha_nacimiento","numero_celular","correo_electronico","nivel_estudios","profesion","estado_civil","personas_a_cargo"],

                "UBICACION": ["id", "solicitante_id", "barrio", "ciudad_gestion", "direccion_residencia","estrato","tipo_vivienda"],

                "ACTIVIDAD_ECONOMICA": ["id", "solicitante_id", "actividad_economica", "empresa_labora", "fecha_vinculacion","direccion_empresa","telefono_empresa", "tipo_contrato", "cargo_actual"],

                "INFORMACION_FINANCIERA": ["id", "solicitante_id", "ingresos", "total_egresos", "valor_inmueble","cuota_inicial", "porcentaje_financiar","total_activos", "total_pasivos"],

                "PRODUCTO_SOLICITADO": ["id", "solicitante_id", "tipo_credito", "plazo_meses", "segundo_titular", "observacion"],
                
                "SOLICITUDES": ["id", "solicitante_id", "banco", "fecha_solicitud"]
            }

            print("Estructura de columnas_tablas:", columnas_tablas)

            solicitante_ids = set()

            # Buscar en cada tabla si la columna existe y tiene coincidencias
            for tabla, columnas in columnas_tablas.items():
                print(f"\nRevisando tabla: {tabla}")
                if columna_buscar in columnas:
                    print(f"Columna {columna_buscar} encontrada en tabla {tabla}")
                    try:
                        res = supabase.table(tabla).select("solicitante_id").eq(columna_buscar, texto_buscar).execute()
                        print(f"Resultado de búsqueda en {tabla}:", res.data)
                        if res.data:
                            solicitante_ids.update(row["solicitante_id"] for row in res.data)
                    except Exception as e:
                        print(f"Error al consultar {tabla}: {e}")

            print("IDs de solicitantes encontrados:", solicitante_ids)

            if not solicitante_ids:
                print("No se encontraron registros que coincidan con el criterio de búsqueda")
                return jsonify({"error": "No se encontraron registros con ese criterio"}), 204

            # Obtener datos de todas las tablas filtrando por solicitante_id
            registros = {
                tabla: supabase.table(tabla).select("*").in_("solicitante_id", list(solicitante_ids)).execute().data
                for tabla in columnas_tablas.keys()
            }

            print("Registros recuperados:", registros)
            return jsonify({"registros": registros}), 200

        except requests.exceptions.HTTPError as err:
            print("Error en la solicitud a Supabase:", err)
            return jsonify({"error": "Error al consultar la base de datos"}), 500