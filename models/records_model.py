from librerias import *
from models.generales.generales import *
from datetime import datetime
import time as std_time
from datetime import datetime, time
import errno


# TODO: Separar lógica de agregar datos a cada tabla de la BD
# TODO: Agregar validaciones de datos a cada tabla
# TODO: Validar si el asesor existe en la tabla de asesores

class recordsModel():
    def add_record(self):
        try:
            # Lista de campos requeridos
            required_fields = {
                "nombre_completo", "tipo_documento", "numero_documento", "fecha_nacimiento",
                "numero_celular", "correo_electronico", "nivel_estudio", "profesion",
                "estado_civil", "personas_a_cargo", "direccion_residencia", "tipo_vivienda",
                "barrio", "departamento", "estrato", "ciudad_gestion", "actividad_economica",
                "empresa_labora", "fecha_vinculacion", "direccion_empresa", "telefono_empresa",
                "tipo_contrato", "cargo_actual", "ingresos", "valor_inmueble", "cuota_inicial",
                "porcentaje_financiar", "total_egresos", "total_activos", "total_pasivos",
                "tipo_credito", "plazo_meses", "segundo_titular", "observacion", "asesor_usuario",
                "banco"
            }

            # Obtener datos del request
            data = request.get_json()
            if not data:
                return jsonify({"error": "No se recibieron datos"}), 400
            
            print(request.get_json())

            # Verificar campos faltantes
            missing_fields = required_fields - set(data.keys())
            if missing_fields:
                return jsonify({
                    "error": "Faltan campos requeridos",
                    "campos_faltantes": list(missing_fields)
                }), 400

            # # Verificar que ningún campo requerido esté vacío
            # empty_fields = [field for field in required_fields if not data.get(field) and data.get(field) != 0]
            # if empty_fields:
            #     return jsonify({
            #         "error": "Los siguientes campos están vacíos",
            #         "campos_vacios": empty_fields
            #     }), 400

            # Obtener el asesor de la tabla de asesores
            agents_info = supabase.table("ASESORES").select('*').eq('cedula', request.json.get('asesor_usuario')).execute()
            print("Asesores info")
            print(agents_info.data)
            agent_id = agents_info.data[0]['id']

            # agent_id = request.json.get('asesor_usuario')

            print(agent_id)

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

            applicant_id = res.data[0]['solicitante_id']

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
                "segundo_titular": True if request.json.get('segundo_titular') == 'si' else False,
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
    
    def get_all_data(self):
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                # Consultas a las tablas
                tablas = {
                    "agents_info": "ASESORES",
                    "solicitantes": "SOLICITANTES",
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
                if isinstance(e, OSError) and e.errno == errno.WSAEWOULDBLOCK:
                    print(f"Attempt {attempt + 1} failed due to non-blocking socket operation: {e}")
                    if attempt < max_retries - 1:
                        std_time.sleep(retry_delay)
                    else:
                        return jsonify({"mensaje": "Error en la lectura debido a operación de socket no bloqueante"}), 500
                else:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        std_time.sleep(retry_delay)
                    else:
                        return jsonify({"mensaje": "Error en la lectura"}), 500
                
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
                
                "SOLICITUDES": ["id", "solicitante_id", "banco", "fecha_solicitud", "estado"]
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
    
    # Descarga todas las ventas con id's mayor a 1000
    # /descargar-ventas/
    def descargar_ventas_realizadas(self):
        try:
            csv_filename = 'ventas_realizadas.csv'
            
            # 1. Descarga de la tabla principal (por ejemplo, "SOLICITANTES")
            solicitantes_resp = supabase.table("SOLICITANTES").select("*").execute()
            if not solicitantes_resp.data:
                return jsonify({"res": "No existen datos en SOLICITANTES"}), 200
            
            # Creamos el DataFrame principal
            df_solicitantes = pd.DataFrame(solicitantes_resp.data)

            # 2. Definir las demás tablas a unir
            tablas_relacionadas = {
                "location": "UBICACION",
                "economic_activity": "ACTIVIDAD_ECONOMICA",
                "financial_info": "INFORMACION_FINANCIERA",
                "product": "PRODUCTO_SOLICITADO",
                "solicitud": "SOLICITUDES"
            }
            
            # 3. Para cada tabla relacionada, la descargamos y unimos con df_solicitantes
            for clave, nombre_tabla in tablas_relacionadas.items():
                resp = supabase.table(nombre_tabla).select("*").execute()
                if resp.data:
                    df_rel = pd.DataFrame(resp.data)
                    
                    # Asegúrate de que 'solicitante_id' exista en ambas tablas
                    df_solicitantes = df_solicitantes.merge(
                        df_rel,
                        on="solicitante_id",               # <-- tu clave de unión
                        how="left",                        # 'left' para mantener todos los de la tabla principal
                        suffixes=("", f"_{clave}")         # Para evitar choques de nombres de columnas
                    )
                else:
                    print(f"No se encontraron datos en la tabla {nombre_tabla}")
            
            # 4. Exportar el DataFrame unificado a CSV
            df_solicitantes.to_csv(csv_filename, index=False)
            
            # 5. Retornar el CSV para su descarga
            return send_file(csv_filename, as_attachment=True), 200
        
        except Exception as e:
            print("Ocurrió un error:", e)
            return jsonify({"mensaje": "Ocurrió un error al procesar la solicitud."}), 500
    
    def editar_estado(self):
        try:
            # 1. Extraer los datos del request
            estado = request.json.get('estado')
            solicitante_id = request.json.get('solicitante_id')
            numero_documento = request.json.get('numero_documento')

            # Validar que se reciban todos los datos necesarios
            if not estado or not solicitante_id or not numero_documento:
                return jsonify({"error": "Faltan datos para actualizar el estado"}), 400

            # 2. Validar que el solicitante tenga el número de documento indicado
            respuesta_solicitantes = supabase.table("SOLICITANTES") \
                                            .select("numero_documento") \
                                            .eq("solicitante_id", solicitante_id) \
                                            .execute()

            # Si no se encontró información en SOLICITANTES, se retorna error
            if not respuesta_solicitantes.data:
                return jsonify({"error": "No se encontró el solicitante"}), 404

            # Se asume que solo hay un registro por solicitante_id
            solicitante = respuesta_solicitantes.data[0]
            if solicitante.get("numero_documento") != numero_documento:
                return jsonify({"error": "El número de documento no coincide"}), 400

            # 3. Preparar el diccionario con el nuevo valor a actualizar
            data_dict = {"estado": estado}

            # 4. Actualizar la tabla PRODUCTO_SOLICITADO usando solicitante_id como filtro
            respuesta_update = supabase.table("PRODUCTO_SOLICITADO") \
                                        .update(data_dict) \
                                        .eq("solicitante_id", solicitante_id) \
                                        .execute()
            
            print(respuesta_update)

            # Si la actualización no retorna datos, asumimos que falló
            if not respuesta_update.data:
                return jsonify({"error": "No se pudo actualizar el estado"}), 500

            # (Opcional) Aquí podrías registrar un historial de cambios

            return jsonify({"actualizar_estado_venta": "OK"}), 200

        except Exception as e:
            print("Ocurrió un error:", e)
            return jsonify({"mensaje": e}), 500
   
    def mostrar_por_fecha(self):
        try:
            # 1. Extraer la fecha enviada en formato dd/mm/yyyy
            fecha_str = request.json.get("fecha_venta")
            if not fecha_str:
                return jsonify({"error": "El campo fecha_venta está vacío"}), 400

            import datetime
            # 2. Convertir el string a un objeto date usando strptime
            fecha_obj = datetime.datetime.strptime(fecha_str, "%d/%m/%Y").date()

            # 3. Definir el rango de búsqueda: desde el inicio hasta el final del día
            inicio_dia = datetime.datetime.combine(fecha_obj, datetime.time.min)
            fin_dia = datetime.datetime.combine(fecha_obj, datetime.time.max)

            # Convertir a cadena ISO 8601 (asegúrate de que coincida con la zona horaria de tus datos)
            inicio_iso = inicio_dia.isoformat()
            fin_iso = fin_dia.isoformat()

            # 4. Definir las tablas a consultar
            tablas = {
                "solicitantes": "SOLICITANTES",
                "location": "UBICACION",
                "economic_activity": "ACTIVIDAD_ECONOMICA",
                "financial_info": "INFORMACION_FINANCIERA",
                "product": "PRODUCTO_SOLICITADO",
                "solicitud": "SOLICITUDES"  # Únicamente esta tabla tiene la columna created_at
            }

            resultados = {}
            for key, tabla in tablas.items():
                # Si la tabla es SOLICITUDES (clave "solicitud"), aplicamos el filtro de fecha
                if key == "solicitud":
                    resp = supabase.table(tabla)\
                                .select("*")\
                                .gte("created_at", inicio_iso)\
                                .lte("created_at", fin_iso)\
                                .order("id", desc=True)\
                                .execute()
                else:
                    # Para las demás tablas, se listan todos los registros (o puedes aplicar otro filtro si lo requieres)
                    resp = supabase.table(tabla)\
                                .select("*")\
                                .order("solicitante_id", desc=True)\
                                .execute()

                resultados[key] = resp.data if resp.data is not None else []

            return jsonify({"registros": resultados}), 200

        except Exception as e:
            print("Ocurrió un error:", e)
            return jsonify({"mensaje": "Ocurrió un error al procesar la solicitud."}), 500
    
    def mostrar_por_intervalo(self):
        try:
            # 1. Extraer las fechas enviadas (en formato dd/mm/yyyy)
            fecha_inicial_str = request.json.get("fecha_inicial")
            fecha_final_str = request.json.get("fecha_final")

            if not fecha_inicial_str or not fecha_final_str:
                return jsonify({"error": "Las fechas de inicio y fin son requeridas"}), 400

            # 2. Convertir las cadenas a objetos datetime
            fecha_inicial = datetime.strptime(fecha_inicial_str, '%d/%m/%Y')
            fecha_final = datetime.strptime(fecha_final_str, '%d/%m/%Y')

            # 3. Definir el rango de búsqueda para SOLICITUDES usando created_at
            inicio_iso = datetime.combine(fecha_inicial.date(), time.min).isoformat()
            fin_iso = datetime.combine(fecha_final.date(), time.max).isoformat()

            # 4. Consultar la tabla SOLICITUDES con el filtro de fecha
            resp_solicitud = supabase.table("SOLICITUDES")\
                            .select("*")\
                            .gte("created_at", inicio_iso)\
                            .lte("created_at", fin_iso)\
                            .order("id", desc=True)\
                            .execute()
            ventas_solicitud = resp_solicitud.data if resp_solicitud.data is not None else []

            # 5. (Opcional) Filtrar adicionalmente para ventas que pertenezcan a un mismo mes y año.
            #    Si el intervalo es amplio, este paso podría eliminar registros de meses intermedios.
            ventas_en_intervalo = []
            for venta in ventas_solicitud:
                try:
                    # Convertir created_at (ISO 8601) a objeto datetime
                    # Se reemplaza 'Z' si existe, para que fromisoformat lo procese correctamente.
                    venta_date = datetime.fromisoformat(venta['created_at'].replace('Z', '+00:00'))
                except Exception as parse_err:
                    print("Error al parsear la fecha de la venta:", parse_err)
                    continue

                # Ejemplo de filtrado: conservar solo ventas del mismo mes y año que la fecha inicial
                if venta_date.month == fecha_inicial.month and venta_date.year == fecha_inicial.year:
                    ventas_en_intervalo.append(venta)

            # 6. Consultar las demás tablas sin filtro de fecha
            otras_tablas = {
                "solicitantes": "SOLICITANTES",
                "location": "UBICACION",
                "economic_activity": "ACTIVIDAD_ECONOMICA",
                "financial_info": "INFORMACION_FINANCIERA",
                "product": "PRODUCTO_SOLICITADO"
            }
            resultado_tablas = {
                "solicitud": ventas_en_intervalo,

            }
            for key, tabla in otras_tablas.items():
                resp = supabase.table(tabla)\
                            .select("*")\
                            .order("solicitante_id", desc=True)\
                            .execute()
                resultado_tablas[key] = resp.data if resp.data is not None else []

            return jsonify({"registros": resultado_tablas}), 200

        except Exception as e:
            print("Ocurrió un error:", e)
            return jsonify({"error": "Ocurrió un error al procesar la solicitud"}), 500