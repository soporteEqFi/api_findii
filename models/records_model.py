
from models.generales.generales import *
from datetime import datetime
from models.utils.pdf.generate_pdf import *
import time as std_time
from datetime import datetime, time
import errno
from io import BytesIO
import uuid  # Para generar nombres únicos
from models.utils.email.sent_email import config_email, email_body_and_send
from models.utils.others.date_utils import format_date
from models.seguimiento_solicitud import trackingModel
from models.utils.files.files import upload_files

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
                "banco", "informacion_producto" 
            }

            # Obtener datos del form-data
            if not request.form:
                return jsonify({"error": "No se recibieron datos"}), 400
            
            print("Form data:", request.form)
            # print("Llenando el solicitante")
            # Crear registro del solicitante
            applicant = {
                "nombre_completo": request.form.get('nombre_completo'),
                "tipo_documento": request.form.get('tipo_documento'),
                "numero_documento": request.form.get('numero_documento'),
                "fecha_nacimiento": request.form.get('fecha_nacimiento'),
                "numero_celular": request.form.get('numero_celular'),
                "correo_electronico": request.form.get('correo_electronico'),
                "nivel_estudio": request.form.get('nivel_estudio'),
                "profesion": request.form.get('profesion'),  # Campo opcional
                "estado_civil": request.form.get('estado_civil'),
                "personas_a_cargo": request.form.get('personas_a_cargo')
            }

            res = supabase.table('SOLICITANTES').insert(applicant).execute()

            applicant_id = res.data[0]['solicitante_id']

            files = request.files.getlist('archivos')

            for file in files:
                print("Procesando archivo:", file.filename)

                try:
                    # Crear nombre único para el archivo
                    extension = file.filename.split('.')[-1]
                    unique_filename = f"{uuid.uuid4().hex}_{int(datetime.timestamp(datetime.now()))}.{extension}"
                    file_path = f"images/{unique_filename}"

                    print("Nombre archivo")
                    print(unique_filename)

                    # Leer archivo y convertir a bytes
                    file_data = file.read()

                    # Subir archivo a Supabase Storage
                    res = supabase.storage.from_("findii").upload(
                        file_path,
                        file_data,
                        file_options={"content-type": file.mimetype}
                    )

                    print("Subir archivo")
                    print(res)

                    if isinstance(res, dict) and "error" in res:
                        print(f"Error al subir archivo {file.filename}: {res['error']}")
                        continue

                    # Hacer que el archivo sea público (importante para PDFs)
                    # supabase.storage.from_("findii").update(file_path, {'public': True})

                    # Obtener URL pública e insertar en BD
                    image_url = supabase.storage.from_("findii").get_public_url(file_path)

                    # Insertar registro para esta imagen
                    datos_insertar = {
                        "id_solicitante": applicant_id,
                        "imagen": image_url
                    }

                    print("Datos insertar")
                    print(datos_insertar)
                    res_db = supabase.table("PRUEBA_IMAGEN").insert(datos_insertar).execute()
                    print("Respuesta db")
                    print(res_db)

                except Exception as e:
                    print(f"Error procesando archivo {file.filename}: {str(e)}")
                    continue

            # Verificar campos faltantes
            missing_fields = required_fields - set(request.form.keys())
            if missing_fields:
                print("Faltan campos requeridos")
                print(missing_fields)
                return jsonify({
                    "error": "Faltan campos requeridos",
                    "campos_faltantes": list(missing_fields)
                }), 400

            print(request.form.get('asesor_usuario'))

            # Obtener el asesor de la tabla de asesores
            agents_info = supabase.table("TABLA_USUARIOS").select('*').eq('cedula', request.form.get('asesor_usuario')).execute()
            print("Asesores info")
            print(agents_info.data)
            agent_id = agents_info.data[0]['id']

            # print(agent_id)
            print("Llenando la ubicación")
            # Crear registro de ubicación
            location = {
                "solicitante_id": applicant_id,
                "direccion_residencia": request.form.get('direccion_residencia'),
                "tipo_vivienda": request.form.get('tipo_vivienda'),
                "barrio": request.form.get('barrio'),
                "departamento": request.form.get('departamento'),
                "estrato": request.form.get('estrato'),
                "ciudad_gestion": request.form.get('ciudad_gestion')
            }

            res = supabase.table('UBICACION').insert(location).execute()

            print("Ubicaciones")
            # print(res.data)
            
            # Crear registro de actividad económica
            economic_activity = {
                "solicitante_id": applicant_id,
                "actividad_economica": request.form.get('actividad_economica'),
                "empresa_labora": request.form.get('empresa_labora'),
                "fecha_vinculacion": datetime.strptime(request.form.get('fecha_vinculacion'), '%Y-%m-%d').strftime('%Y,%m,%d'),
                "direccion_empresa": request.form.get('direccion_empresa'),
                "telefono_empresa": request.form.get('telefono_empresa'),
                "tipo_contrato": request.form.get('tipo_contrato'),
                "cargo_actual": request.form.get('cargo_actual')
            }

            res = supabase.table('ACTIVIDAD_ECONOMICA').insert(economic_activity).execute()

            print("Actividad economica")
            # print(res.data)
            
            # Crear registro de información financiera
            financial_info = {
                "solicitante_id": applicant_id,
                "ingresos": request.form.get('ingresos'),
                "valor_inmueble": request.form.get('valor_inmueble'),
                "cuota_inicial": request.form.get('cuota_inicial'),
                "porcentaje_financiar": request.form.get('porcentaje_financiar'),
                "total_egresos": request.form.get('total_egresos'),
                "total_activos": request.form.get('total_activos'),
                "total_pasivos": request.form.get('total_pasivos')
            }

            res = supabase.table('INFORMACION_FINANCIERA').insert(financial_info).execute()

            print("Informacion financiera")
            # print(res.data)
            # Crear registro de producto solicitado
            try:
                informacion_producto = json.loads(request.form.get('informacion_producto', '{}'))
            except json.JSONDecodeError:
                return jsonify({"error": "El campo informacion_producto debe ser un JSON válido"}), 400
            # Crear registro de producto solicitado
            product = {
                "solicitante_id": applicant_id,
                "tipo_credito": request.form.get('tipo_credito'),
                "plazo_meses": request.form.get('plazo_meses'),
                "informacion_producto": informacion_producto,
                "segundo_titular": True if request.form.get('segundo_titular') == 'si' else False,
                "observacion": request.form.get('observacion'),
                "estado": "Radicado",
            }

            res = supabase.table('PRODUCTO_SOLICITADO').insert(product).execute()
            print("Producto solicitado")
            # print(res.data)
            
            # Crear registro de solicitud
            solicitud = {
                "solicitante_id": applicant_id,
                "asesor_id": agent_id,
                "banco": request.form.get('banco'),
            }

            res = supabase.table('SOLICITUDES').insert(solicitud).execute()

            # Recopilar toda la información en un diccionario data
            data = {
                "solicitante": {
                    "id": applicant_id,
                    "nombre": request.form.get('nombre_completo', '').split()[0] if request.form.get('nombre_completo') else '',
                    "apellido": ' '.join(request.form.get('nombre_completo', '').split()[1:]) if request.form.get('nombre_completo') and len(request.form.get('nombre_completo', '').split()) > 1 else '',
                    "tipo_documento": request.form.get('tipo_documento'),
                    "numero_documento": request.form.get('numero_documento'),
                    "fecha_nacimiento": request.form.get('fecha_nacimiento'),
                    "estado_civil": request.form.get('estado_civil'),
                    "email": request.form.get('correo_electronico'),
                    "numero_celular": request.form.get('numero_celular'),
                    "nivel_estudio": request.form.get('nivel_estudio'),
                    "profesion": request.form.get('profesion'),
                    "personas_a_cargo": request.form.get('personas_a_cargo')
                },
                "ubicacion": {
                    "solicitante_id": applicant_id,
                    "direccion": request.form.get('direccion_residencia'),
                    "ciudad": request.form.get('ciudad_gestion'),
                    "departamento": request.form.get('departamento'),
                    "estrato": request.form.get('estrato'),
                    "tipo_vivienda": request.form.get('tipo_vivienda'),
                    "tiempo_residencia": request.form.get('barrio')  # Usando barrio como tiempo_residencia por compatibilidad con PDF
                },
                "actividad_economica": {
                    "solicitante_id": applicant_id,
                    "actividad": request.form.get('actividad_economica'),
                    "empresa": request.form.get('empresa_labora'),
                    "cargo": request.form.get('cargo_actual'),
                    "tipo_contrato": request.form.get('tipo_contrato'),
                    "fecha_vinculacion": request.form.get('fecha_vinculacion'),
                    "direccion_empresa": request.form.get('direccion_empresa'),
                    "telefono_empresa": request.form.get('telefono_empresa')
                },
                "informacion_financiera": {
                    "solicitante_id": applicant_id,
                    "ingresos": request.form.get('ingresos'),
                    "valor_inmueble": request.form.get('valor_inmueble'),
                    "cuota_inicial": request.form.get('cuota_inicial'),
                    "porcentaje_financiar": request.form.get('porcentaje_financiar'),
                    "total_egresos": request.form.get('total_egresos'),
                    "total_activos": request.form.get('total_activos'),
                    "total_pasivos": request.form.get('total_pasivos')
                },
                "producto": {
                    "solicitante_id": applicant_id,
                    "tipo_credito": request.form.get('tipo_credito'),
                    "plazo_meses": request.form.get('plazo_meses'),
                    "segundo_titular": True if request.form.get('segundo_titular') == 's' else False,
                    "observacion": request.form.get('observacion'),
                    "estado": "Radicado"
                },
                "solicitud": {
                    "solicitante_id": applicant_id,
                    "asesor_id": agent_id,
                    "banco": request.form.get('banco')
                },
                "banco": request.form.get('banco'),
                "asesor_id": agent_id
            }

            # En tu función principal
            pdf_data = generar_pdf_desde_html(data)
            if pdf_data:
                # Crear nombre único para el PDF
                unique_filename = f"registro_{uuid.uuid4().hex}.pdf"
                file_path = f"documentos/{unique_filename}"
                
                # Subir a Supabase Storage
                res = supabase.storage.from_("findii").upload(
                    file_path,
                    pdf_data,
                    file_options={"content-type": "application/pdf"}
                )
                
                if isinstance(res, dict) and "error" in res:
                    print(f"Error al subir PDF: {res['error']}")
                else:
                    # Obtener URL pública
                    pdf_url = supabase.storage.from_("findii").get_public_url(file_path)
                    print("PDF guardado:", pdf_url)

                return jsonify({
                    "mensaje": "Registro creado exitosamente",
                }), 200

        except Exception as e:
            error_msg = str(e)
            print("Ocurrió un error al crear un registro:", error_msg)
            return jsonify({"mensaje": f"Ocurrió un error al crear un registro: {error_msg}"}), 500
    
    def get_all_data(self):
        max_retries = 3
        retry_delay = 4  # seconds

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
                    "solicitud": "SOLICITUDES",
                    "documentos": "PRUEBA_IMAGEN"
                }

                # Consultas a las tablas de Supabase en un solo paso con ordenamiento descendente
                registros = {}
                
                # Para cada tabla, aplicar ordenamiento descendente según su clave primaria
                for clave, tabla in tablas.items():
                    if tabla == "SOLICITANTES":
                        # Ordenar por solicitante_id descendente
                        registros[clave] = supabase.table(tabla).select("*").order("solicitante_id", desc=True).execute().data
                    elif tabla == "SOLICITUDES":
                        # Ordenar por id descendente
                        registros[clave] = supabase.table(tabla).select("*").order("id", desc=True).execute().data
                    elif tabla == "PRUEBA_IMAGEN":
                        # Ordenar por id descendente
                        registros[clave] = supabase.table(tabla).select("*").order("id", desc=True).execute().data
                    else:
                        # Para las demás tablas, ordenar por id descendente
                        registros[clave] = supabase.table(tabla).select("*").order("id", desc=True).execute().data

                if all(len(value) == 0 for value in registros.values()):
                    return jsonify({"mensaje": "No hay registros en estas tablas"}), 200

                # Combinar datos por cada solicitante
                solicitantes = registros.get("solicitantes", [])
                activity = registros.get("economic_activity", [])
                financial = registros.get("financial_info", [])
                location = registros.get("location", [])
                product = registros.get("product", [])
                solicitud = registros.get("solicitud", [])
                documentos = registros.get("documentos", [])
                
                datos_combinados = []
                
                for solicitante in solicitantes:
                    actividad = next((a for a in activity if a.get("solicitante_id") == solicitante.get("solicitante_id")), {})
                    finanzas = next((f for f in financial if f.get("solicitante_id") == solicitante.get("solicitante_id")), {})
                    ubicacion = next((l for l in location if l.get("solicitante_id") == solicitante.get("solicitante_id")), {})
                    producto = next((p for p in product if p.get("solicitante_id") == solicitante.get("solicitante_id")), {})
                    solicitud_info = next((s for s in solicitud if s.get("solicitante_id") == solicitante.get("solicitante_id")), {})
                    documento = next((d for d in documentos if d.get("id_solicitante") == solicitante.get("solicitante_id")), {})
                    
                    datos_combinados.append({
                        # Info solicitante
                        "id_solicitante": solicitante.get("solicitante_id", "N/A"),
                        "nombre": solicitante.get("nombre_completo", "N/A"),
                        "tipo_documento": solicitante.get("tipo_documento", "N/A"),
                        "fecha_nacimiento": solicitante.get("fecha_nacimiento", "N/A"),
                        "numero_documento": solicitante.get("numero_documento", "N/A"),
                        "correo": solicitante.get("correo_electronico", "N/A"),
                        "profesion": solicitante.get("profesion", "N/A"),
                        "personas_a_cargo": solicitante.get("personas_a_cargo", "N/A"),
                        "numero_celular": solicitante.get("numero_celular", "N/A"),
                        "nivel_estudio": solicitante.get("nivel_estudio", "N/A"),
                        
                        # Actividad económica
                        "actividad_economica": actividad.get("actividad_economica", "N/A"),
                        "cargo_actual": actividad.get("cargo_actual", "N/A"),
                        "empresa_labora": actividad.get("empresa_labora", "N/A"),
                        "direccion_empresa": actividad.get("direccion_empresa", "N/A"),
                        "telefono_empresa": actividad.get("telefono_empresa", "N/A"),
                        "tipo_de_contrato": actividad.get("tipo_contrato", "N/A"),
                        "fecha_vinculacion": actividad.get("fecha_vinculacion", "N/A"),
                        
                        # Finanzas
                        "ingresos": finanzas.get("ingresos", "N/A"),
                        "egresos": finanzas.get("total_egresos", "N/A"),
                        "cuota_inicial": finanzas.get("cuota_inicial", "N/A"),
                        "porcentaje_financiar": finanzas.get("porcentaje_financiar", "N/A"),
                        "total_activos": finanzas.get("total_activos", "N/A"),
                        "total_pasivos": finanzas.get("total_pasivos", "N/A"),
                        "valor_inmueble": finanzas.get("valor_inmueble", "N/A"),
                        
                        # Ubicación
                        "ciudad_gestion": ubicacion.get("ciudad_gestion", "N/A"),
                        "departamento": ubicacion.get("departamento", "N/A"),
                        "direccion": ubicacion.get("direccion_residencia", "N/A"),
                        "barrio": ubicacion.get("barrio", "N/A"),
                        "estrato": ubicacion.get("estrato", "N/A"),
                        
                        # Producto
                        "producto_solicitado": producto.get("tipo_credito", "N/A"),
                        "observacion": producto.get("observacion", "N/A"),
                        "plazo_meses": producto.get("plazo_meses", "N/A"),
                        "segundo_titular": producto.get("segundo_titular", "N/A"),
                        "estado": producto.get("estado", "N/A"),
                        
                        # Documentos
                        "archivos": documento.get("imagen", "N/A"),
                        
                        # Solicitud
                        "banco": solicitud_info.get("banco", "N/A"),
                        "created_at": solicitud_info.get("created_at", "N/A"),
                    })
                
                # Ordenar datos_combinados por id_solicitante de forma descendente
                datos_combinados_ordenados = sorted(datos_combinados, key=lambda x: x.get("id_solicitante", 0), reverse=True)
                
                # Mantener los registros originales y agregar los datos combinados
                return jsonify({
                    "registros": registros,
                    "datos_combinados": datos_combinados_ordenados
                }), 200

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
            # csv_filename= '/home/equitisoporte/api_findii/ventas_realizadas.csv'
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

            print(f"Estado: {estado}")
            print(f"Solicitante ID: {solicitante_id}")
            print(f"Numero Documento: {numero_documento}")

            # Validar que se reciban todos los datos necesarios
            if not estado or not solicitante_id or not numero_documento:
                return jsonify({"error": "Faltan datos para actualizar el estado"}), 400

            # 2. Validar que el solicitante tenga el número de documento indicado
            respuesta_solicitantes = supabase.table("SOLICITANTES") \
                                            .select("numero_documento") \
                                            .eq("solicitante_id", solicitante_id) \
                                            .execute()
            
            print(respuesta_solicitantes)

            # Si no se encontró información en SOLICITANTES, se retorna error
            if not respuesta_solicitantes.data:
                return jsonify({"error": "No se encontró el solicitante"}), 404

            # Se asume que solo hay un registro por solicitante_id
            solicitante = respuesta_solicitantes.data[0]
            print(solicitante)
            print(solicitante.get("numero_documento"))

            print(numero_documento)
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
        
    def edit_record(self):
        try:
            data = request.get_json()
            print(data)
            if not data:
                return jsonify({"error": "No se recibieron datos"}), 400

            solicitante_id = data.get('solicitante_id')
            print(solicitante_id)
            if not solicitante_id:
                return jsonify({"error": "Se requiere el ID del solicitante"}), 400

            # Definir los campos por tabla
            actualizaciones = {
                "SOLICITANTES": {
                    "campos_permitidos": {
                        "nombre_completo", "tipo_documento", "numero_documento",
                        "fecha_nacimiento", "numero_celular", "correo_electronico",
                        "nivel_estudio", "profesion", "estado_civil", "personas_a_cargo"
                    }
                },
                "UBICACION": {
                    "campos_permitidos": {
                        "direccion_residencia", "tipo_vivienda", "barrio",
                        "departamento", "estrato", "ciudad_gestion"
                    }
                },
                "ACTIVIDAD_ECONOMICA": {
                    "campos_permitidos": {
                        "actividad_economica", "empresa_labora", "fecha_vinculacion",
                        "direccion_empresa", "telefono_empresa", "tipo_contrato",
                        "cargo_actual"
                    }
                },
                "INFORMACION_FINANCIERA": {
                    "campos_permitidos": {
                        "ingresos", "valor_inmueble", "cuota_inicial",
                        "porcentaje_financiar", "total_egresos", "total_activos",
                        "total_pasivos"
                    }
                },
                "PRODUCTO_SOLICITADO": {
                    "campos_permitidos": {
                        "tipo_credito", "plazo_meses", "segundo_titular",
                        "observacion", "estado", "informacion_producto"
                    }
                },
                "SOLICITUDES": {
                    "campos_permitidos": {
                        "banco"
                    }
                }
            }

            resultados = {}

            # Procesar cada tabla
            for tabla, config in actualizaciones.items():
                # Obtener los datos de la tabla específica
                datos_tabla = data.get(tabla, {})
                datos_actualizacion = {}

                for campo in config["campos_permitidos"]:
                    if campo in datos_tabla and datos_tabla[campo] is not None and datos_tabla[campo] != "" and datos_tabla[campo] != "undefined":
                        # Procesamiento especial para algunos campos
                        if campo == "segundo_titular":
                            datos_actualizacion[campo] = datos_tabla[campo].lower() == "si"
                        elif campo in ["fecha_nacimiento", "fecha_vinculacion"]:
                            try:
                                fecha = datetime.strptime(datos_tabla[campo], '%Y-%m-%d')
                                datos_actualizacion[campo] = fecha.strftime('%Y-%m-%d')
                            except ValueError as e:
                                print(f"Error en formato de fecha para {campo}: {e}")
                                continue
                        else:
                            datos_actualizacion[campo] = datos_tabla[campo]

                # print(f"Datos a actualizar en {tabla}:")
                # print(datos_actualizacion)

                if datos_actualizacion:
                    try:
                        res = supabase.table(tabla)\
                            .update(datos_actualizacion)\
                            .eq('solicitante_id', solicitante_id)\
                            .execute()

                        resultados[tabla] = {
                            "estado": "exitoso",
                            "datos_actualizados": datos_actualizacion
                        }
                    except Exception as e:
                        resultados[tabla] = {
                            "estado": "error",
                            "error": str(e)
                        }

            if not resultados:
                return jsonify({"error": "No se realizaron actualizaciones"}), 400

            return jsonify({
                "mensaje": "Registro actualizado exitosamente",
                "resultados": resultados
            }), 200

        except Exception as e:
            print("Error:", e)
            return jsonify({"error": str(e)}), 500
    
    def delete_record(self):
        try:
            data = request.get_json()

            print(data)

            if not data or "solicitante_id" not in data:
                return jsonify({"error": "Falta el ID del solicitante"}), 400
                
            solicitante_id = data["solicitante_id"]
            
            # Definir las tablas relacionadas en orden de eliminación (de hijas a padres)
            # Primero las tablas dependientes, luego las principales
            tablas_relacionadas = [
                "PRUEBA_IMAGEN",      # Primero eliminamos las imágenes
                "UBICACION",          # Luego las tablas que tienen restricciones de clave foránea
                "PRODUCTO_SOLICITADO",
                "INFORMACION_FINANCIERA",
                "ACTIVIDAD_ECONOMICA",
                "SOLICITUDES",
                "SOLICITANTES"        # Finalmente la tabla principal
            ]
            
            resultados = {}
            
            # Eliminar registros de cada tabla relacionada
            for tabla in tablas_relacionadas:
                try:
                    # Manejo especial para PRUEBA_IMAGEN que usa id_solicitante en lugar de solicitante_id
                    if tabla == "PRUEBA_IMAGEN":
                        res = supabase.table(tabla)\
                            .delete()\
                            .eq('id_solicitante', solicitante_id)\
                            .execute()
                    else:
                        res = supabase.table(tabla)\
                            .delete()\
                            .eq('solicitante_id', solicitante_id)\
                            .execute()
                    
                    resultados[tabla] = {
                        "estado": "exitoso",
                        "registros_eliminados": len(res.data) if hasattr(res, 'data') else 0
                    }
                except Exception as e:
                    resultados[tabla] = {
                        "estado": "error",
                        "error": str(e)
                    }
            
            # Verificar si se eliminó el solicitante principal
            if resultados.get("SOLICITANTES", {}).get("estado") == "exitoso":
                print(resultados)
                return jsonify({
                    "mensaje": "Registro eliminado exitosamente",
                    "resultados": resultados
                }), 200
            else:
                return jsonify({
                    "mensaje": "Eliminación parcial",
                    "resultados": resultados,
                    "error": "No se pudo eliminar el registro principal del solicitante"
                }), 207
                
        except Exception as e:
            print("Error al eliminar registro:", e)
            return jsonify({"error": f"Error al eliminar registro: {str(e)}"}), 500

    def update_files(self):
        try:
            # Verificar si hay un ID de solicitante
            if 'solicitante_id' not in request.form:
                return jsonify({"error": "Falta el ID del solicitante"}), 400
            
            solicitante_id = request.form['solicitante_id']

            print(solicitante_id)
            
            resultados = {
                "archivos_eliminados": [],
                "archivos_subidos": []
            }

            # 1. Manejar eliminación de archivos
            files_to_delete = request.form.getlist('files_to_delete')
            if files_to_delete:
                for file_url in files_to_delete:
                    try:
                        # Extraer el nombre del archivo de la URL
                        file_path = file_url.split('findii/')[-1] if 'findii/' in file_url else file_url
                        
                        # Eliminar el archivo del storage
                        supabase.storage.from_("findii").remove([file_path])
                        
                        # Eliminar el registro de la base de datos
                        res = supabase.table('PRUEBA_IMAGEN')\
                            .delete()\
                            .eq('imagen', file_url)\
                            .eq('id_solicitante', solicitante_id)\
                            .execute()
                            
                        resultados["archivos_eliminados"].append({
                            "url": file_url,
                            "estado": "eliminado"
                        })
                        
                    except Exception as e:
                        print(f"Error eliminando archivo {file_url}: {e}")
                        resultados["archivos_eliminados"].append({
                            "url": file_url,
                            "estado": "error",
                            "error": str(e)
                        })

            # 2. Manejar nuevos archivos
            if 'archivos' in request.files:
                files = request.files.getlist('archivos')

                print("Archivos")
                print(files)
                
                for file in files:
                    try:
                        # Crear nombre único para el archivo
                        extension = file.filename.split('.')[-1]
                        unique_filename = f"{uuid.uuid4().hex}_{int(datetime.timestamp(datetime.now()))}.{extension}"
                        file_path = f"images/{unique_filename}"

                        # Leer archivo y convertir a bytes
                        file_data = file.read()

                        # Subir archivo a Supabase Storage
                        res = supabase.storage.from_("findii").upload(
                            file_path,
                            file_data,
                            file_options={"content-type": file.mimetype}
                        )

                        if isinstance(res, dict) and "error" in res:
                            raise Exception(res["error"])

                        # Obtener URL pública
                        image_url = supabase.storage.from_("findii").get_public_url(file_path)

                        # Insertar registro en la base de datos
                        datos_insertar = {
                            "id_solicitante": solicitante_id,
                            "imagen": image_url,
                        }

                        res_db = supabase.table("PRUEBA_IMAGEN").insert(datos_insertar).execute()
                        print("Respuesta db AHORA")
                        print(res_db)

                        resultados["archivos_subidos"].append({
                            "nombre_original": file.filename,
                            "url": image_url,
                            "estado": "subido"
                        })

                    except Exception as e:
                        print(f"Error procesando archivo {file.filename}: {e}")
                        resultados["archivos_subidos"].append({
                            "nombre_original": file.filename,
                            "estado": "error",
                            "error": str(e)
                        })

            # 3. Devolver resultados
            return jsonify({
                "mensaje": "Archivos actualizados exitosamente",
                "resultados": resultados
            }), 200

        except Exception as e:
            print(f"Error general actualizando archivos: {e}")
            return jsonify({
                "error": "Error actualizando archivos",
                "detalle": str(e)
            }), 500