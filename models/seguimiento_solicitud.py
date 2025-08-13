from models.generales.generales import *
from datetime import datetime
from models.utils.tracking.validate_tracking_type import validate_etapa_type
from models.utils.tracking.validate_tracking_data import validate_etapa_data
from models.utils.tracking.etapas import get_etapa_by_radicado
from models.utils.others.date_utils import iso_date
from flask import request, jsonify

import uuid
import json

class trackingModel():

    def generar_id_radicado(self):
        # Formato: SOL-AÑO-MES-SECUENCIAL (ej: SOL-2023-05-0001)
        ahora = datetime.now()
        prefijo = "SOL"
        año = ahora.strftime("%Y")
        mes = ahora.strftime("%m")

        # Consultar el último secuencial para este mes
        ultimo = supabase.table('SEGUIMIENTO_SOLICITUDES')\
            .select('id_radicado')\
            .like('id_radicado', f'{prefijo}-{año}-{mes}-%')\
            .order('id_radicado', desc=True)\
            .limit(1)\
            .execute()

        if ultimo.data:
            ultimo_num = int(ultimo.data[0]['id_radicado'].split('-')[-1])
            secuencial = str(ultimo_num + 1).zfill(4)
        else:
            secuencial = "0001"

        return f"{prefijo}-{año}-{mes}-{secuencial}"

    def crear_seguimiento_interno(self, datos):
        try:
            id_solicitante = datos.get('id_solicitante')
            id_producto = datos.get('id_producto')
            id_asesor = datos.get('id_asesor')
            producto_solicitado = datos.get('producto_solicitado')
            banco = datos.get('banco')

            id_radicado = datos.get('id_radicado')
            if not id_radicado:
                id_radicado = self.generar_id_radicado()

            # Validar datos requeridos
            if not id_solicitante or not id_producto or not id_asesor:
                return jsonify({"error": "Faltan datos requeridos"}), 400

            # Obtener documentos ya subidos
            docs = supabase.table("PRUEBA_IMAGEN").select('*').eq('id_solicitante', id_solicitante).execute()
            archivos_existentes = []

            if docs.data:
                for doc in docs.data:
                    archivos_existentes.append({
                        "archivo_id": str(uuid.uuid4()),
                        "nombre": doc.get('nombre'),
                        "url": doc.get('imagen'),
                        "estado": "pendiente",
                        "comentario": "",
                        "modificado": False,
                        "fecha_modificacion": datetime.now().isoformat(),
                        "ultima_fecha_modificacion": datetime.now().isoformat()
                    })

            # Crear estructura inicial de etapas
            etapas_iniciales = [
                {
                    "etapa": "documentos",
                    "archivos": archivos_existentes,
                    "requisitos_pendientes": ["Documentos en revisión"],
                    "fecha_actualizacion": datetime.now().isoformat(),
                    "comentarios": "Sus documentos han sido recibidos y están en proceso de revisión",
                    "estado": "En revisión",
                    "historial": [
                        {"fecha": datetime.now().isoformat(), "estado": "En revisión", "usuario_id": id_asesor, "comentario": "Solicitud creada"}
                    ]
                },
                {
                    "etapa": "banco",
                    "archivos": [],
                    "viabilidad": "Pendiente",
                    "fecha_actualizacion": datetime.now().isoformat(),
                    "comentarios": "",
                    "estado": "Pendiente",
                    "historial": []
                },
                {
                    "etapa": "desembolso",
                    "desembolsado": False,
                    "estado": "Pendiente",
                    "fecha_estimada": None,
                    "fecha_actualizacion": datetime.now().isoformat(),
                    "comentarios": "",
                    "historial": []
                }
            ]

            # Insertar registro de seguimiento
            resultado = supabase.table('SEGUIMIENTO_SOLICITUDES').insert({
                "id_radicado": id_radicado,
                "id_solicitante": id_solicitante,
                "id_producto": id_producto,
                "id_asesor": id_asesor,
                "producto_solicitado": producto_solicitado,
                "banco": banco,
                "estado_global": "En proceso",
                "fecha_creacion": datetime.now().isoformat(),
                "fecha_ultima_actualizacion": datetime.now().isoformat(),
                "etapas": etapas_iniciales
            }).execute()

            return jsonify({
                "mensaje": "Seguimiento creado exitosamente",
                "id_radicado": id_radicado,
                "id": resultado.data[0]['id'] if resultado.data else None
            }), 201

        except Exception as e:
            print(f"Error al crear seguimiento: {e}")
            return jsonify({"error": f"Error al crear seguimiento: {str(e)}"}), 500

    def actualizar_etapa(self):
        try:
            data = request.json
            id_seguimiento = data.get('id_seguimiento')
            id_radicado = data.get('id_radicado')
            etapa_nombre = data.get('etapa')
            nuevo_estado = data.get('estado')
            comentarios = data.get('comentarios', '')
            usuario_id = data.get('usuario_id')


            # Validar que se proporcione al menos un identificador (id_seguimiento o id_radicado)
            if not (id_seguimiento or id_radicado) or not etapa_nombre or not nuevo_estado:
                return jsonify({"error": "Faltan datos requeridos: se necesita id_seguimiento o id_radicado, etapa y estado"}), 400

            # Parte de la query para consultar, pero teniendo en cuenta si se da un id o id_radicado
            query = supabase.table('SEGUIMIENTO_SOLICITUDES').select('*')

            if id_seguimiento:
                query = query.eq('id', id_seguimiento)
            else:
                query = query.eq('id_radicado', id_radicado)

            # Se ejecuta la query
            seguimiento = query.execute()

            # Si no se encuentra datos, se retorna un error
            if not seguimiento.data:
                return jsonify({"error": "Seguimiento no encontrado"}), 404

            # Se obtiene el seguimiento
            seguimiento_data = seguimiento.data[0]
            etapas = seguimiento_data['etapas']

            # Buscar y actualizar la etapa específica
            etapa_actualizada = False
            # En el input, se indica la etapa a actualizar, por lo que se busca en las etapas del seguimiento
            for i, etapa in enumerate(etapas):
                print(f"Etapa {i}: {etapa.get('etapa', 'sin nombre')} - Estado actual: {etapa.get('estado', 'sin estado')}")
                if etapa['etapa'] == etapa_nombre:
                    print(f"Etapa encontrada: {etapa}")
                    estado_anterior = etapa['estado']
                    etapa['estado'] = nuevo_estado
                    etapa['comentarios'] = comentarios
                    etapa['fecha_actualizacion'] = datetime.now().isoformat()

                    # Si no existe el historial, se crea uno incluyendo la fecha, estado, usuario_id y comentarios
                    if 'historial' not in etapa:
                        etapa['historial'] = []

                    etapa['historial'].append({
                        "fecha": datetime.now().isoformat(),
                        "estado": nuevo_estado,
                        "usuario_id": usuario_id,
                        "comentario": comentarios
                    })

                    # Actualizar requisitos pendientes si se proporcionan
                    if 'requisitos_pendientes' in data:
                        etapa['requisitos_pendientes'] = data['requisitos_pendientes']

                    etapa_actualizada = True
                    print(f"Etapa actualizada: {etapa}")
                    break

            if not etapa_actualizada:
                return jsonify({"error": f"Etapa '{etapa_nombre}' no encontrada"}), 404

            # Actualizar estado global si todas las etapas están completas o si alguna está rechazada
            estados = [e['estado'] for e in etapas]
            if all(e == 'Pagado' for e in estados):
                estado_global = 'Pagado'
            elif any(e == 'Negado' for e in estados):
                estado_global = 'Negado'
            elif any(e == 'Desistido' for e in estados):
                estado_global = 'Desistido'
            elif any(e == 'Aprobado' for e in estados):
                estado_global = 'Aprobado'
            elif any(e == 'Desembolsado' for e in estados):
                estado_global = 'Desembolsado'
            elif any(e == 'En estudio' for e in estados):
                estado_global = 'En estudio'
            elif any(e == 'Pendiente información adicional' for e in estados):
                estado_global = 'Pendiente información adicional'
            else:
                estado_global = 'Pendiente'

            # Guardar cambios en la base de datos
            resultado = supabase.table('SEGUIMIENTO_SOLICITUDES')\
                .update({
                    "etapas": etapas,
                    "estado_global": estado_global,
                    "fecha_cambio": datetime.now().isoformat()
                })\
                .eq('id', seguimiento_data['id'])\
                .execute()

            # Verificar que la actualización fue exitosa
            if not resultado.data:
                return jsonify({"error": "Error al guardar los cambios en la base de datos"}), 500

            print(f"Etapa '{etapa_nombre}' actualizada exitosamente. Estado anterior: {estado_anterior}, Nuevo estado: {nuevo_estado}")

            return jsonify({
                "mensaje": "Etapa actualizada exitosamente",
                "estado_anterior": estado_anterior,
                "estado_nuevo": nuevo_estado,
                "estado_global": estado_global,
                "etapa_actualizada": etapa_nombre
            }), 200

        except Exception as e:
            print(f"Error al actualizar etapa: {e}")
            return jsonify({"error": f"Error al actualizar etapa: {str(e)}"}), 500

    # TODO: Separar esta etapa en un archivo distinto para que sea mas flexible y fácil de entender.
    # *: Probada en etapa de documentos.
    # *: Se comprobó la subida de nuevos archivos (teniendo alguno existen)
    # *: Se comprobó el reemplazo de un archivo (teniendo alguno existente)
    # TODO: Validar cuando no existe ningún archivo en la etapa (etapa sin documentos). Debería agregar uno nuevo.
            #     etapa_selected['historial'].append({
            #         "fecha": datetime.now().isoformat(),
            #         "estado": request.form.get('estado'),
            #         "usuario_id": usuario_id,
            #         "comentario": request.form.get('comentario', '')
            #     })

            # # Actualizar comentarios si se proporcionan
            # if 'comentarios' in request.form:
            #     etapa_a_modificar['comentarios'] = request.form.get('comentarios')

            # # Actualizar la fecha de la etapa
            # etapa_a_modificar['fecha_actualizacion'] = iso_date()

            # # Guardar cambios
            # resultado = supabase.table('SEGUIMIENTO_SOLICITUDES')\
            #     .update({
            #         "etapas": etapas,
            #         "fecha_ultima_actualizacion": datetime.now().isoformat()
            #     })\
            #     .eq('id', seguimiento_data['id'])\
            #     .execute()

            return jsonify({
                "mensaje": f"Etapa {etapa_nombre} actualizada exitosamente",
            }), 200

        except Exception as e:
            print(f"Error al actualizar etapa: {e}")
            return jsonify({"error": f"Error al actualizar etapa: {str(e)}"}), 500

    def actualizar_documentos(self):
            """
            Esta función se encarga de actualizar los documentos de la etapa de documentos. Puede ser que se suban nuevos archivos
            o que se reemplacen los archivos existentes.
            """
            from models.utils.seguimiento_solicitud.handle_updates import handle_new_files, handle_history_update, handle_update_files

            try:
                # Valida que los datos necesarios estén presentes en el input, de lo contrario, retorna un error
                id_radicado, solicitante_id, etapa_nombre = validate_etapa_data(request)

                print(request.form)

                # Se obtiene la información del seguimiento
                seguimiento_data = get_etapa_by_radicado(id_radicado, supabase)
                etapas = seguimiento_data[0]['etapas']
                seguimiento_id = seguimiento_data[0]['id']

                # Validar cual es el nombre de la etapa, puede ser documentos, banco o desembolso.
                # TODO: Si se puede validar que existe la etapa, se puede retornar los datos de esta y se evita el for de mas abajo.
                etapa_name = validate_etapa_type(etapa_nombre)
                if not etapa_name:
                    return jsonify({"error": f"La etapa {etapa_nombre} no es válida"}), 400

                for etapa in etapas:
                    # print(etapa)
                    if etapa['etapa'] == etapa_name:
                        etapa_selected = etapa
                        break
                # TODO: Hasta acá

                # Manejar actualizaciones específicas por tipo de etapa
                if etapa_nombre == 'documentos':

                    print(f"La etapa es{etapa_nombre}")

                    # En un diccionario para evitar enviar tantos parámetros
                    user_data = {
                        "id_solicitante": solicitante_id,
                        "id_radicado": id_radicado,
                        "etapa": etapa_name
                    }

                    # Booleanos para verificar si hay archivos para reemplazar o hay nuevos.
                    replace_files = request.form.get('hay_archivos_para_reemplazar', '').lower() in ['true', 'True']
                    new_files = request.form.get('hay_archivos_nuevos', '').lower() in ['true', 'True']

                    # Si ocurre que se sube archivos nuevos y se modifican otros, acá se almacenan los datos de cada uno
                    # Si por ejemplo, llegaron 2 archivos nuevos, toda la info de cada uno se almacenará en un diccionario
                    # y se añadirán a la etapa.
                    dict_files_info = {}
                    dict_history_info = {}

                    # Si existen archivos nuevos, se suben y se actualiza el historial con un nuevo registro.
                    if new_files:
                        print("Hay archivos nuevos")
                        # Si existe un archivo nuevo, se sube y se crea un registro de tipo diccionario
                        # para tener la información relacionada.
                        dict_files_info = handle_new_files(request, etapa_selected, user_data, supabase)
                        dict_history_info = handle_history_update(request, etapa_selected)

                        # En caso de que no existan archivos en la etapa, se crea una lista vacía.
                        # (puede ser una etapa que no contenía archivos)
                        if 'archivos' not in etapa_selected:
                            etapa_selected['archivos'] = []

                        # Se agrega el nuevo registro del archivo a la etapa
                        etapa_selected['archivos'].extend(dict_files_info)

                        print("Datos actualizados")
                        # print(dict_files_info)

                    # Si existen archivos para reemplazar, se actualizan y se actualiza el historial con un nuevo registro.
                    if replace_files:
                        print("Hay archivos para reemplazar")
                        dict_files_info = handle_update_files(request, supabase)
                        dict_history_info = handle_history_update(request, etapa_selected)

                        # Encontrar y actualizar el archivo en la etapa
                        for i, archivo in enumerate(etapa_selected['archivos']):
                            if archivo['url'] == request.form.get('ruta_archivo_reemplazar'):
                                # Reemplazar los datos del archivo
                                etapa_selected['archivos'][i] = dict_files_info
                                break

                    # Si existen archivos nuevos o reemplazados, se actualiza el historial
                    if dict_files_info and dict_history_info:

                        # Se valida que exista el historial, de lo contrario, se crea una lista vacía.
                        if 'historial' not in etapa_selected:
                            etapa_selected['historial'] = []

                        # Se añade el nuevo registro del historial (si ya existe, se añade al final como un nuevo registro)
                        etapa_selected['historial'].append(dict_history_info)

                        # En caso de que se haya modificado el estado o comentarios, se actualiza el estado y comentarios de la etapa
                        etapa_selected['estado'] = request.form.get('estado') if request.form.get('estado') else etapa_selected['estado']
                        etapa_selected['comentarios'] = request.form.get('comentarios') if request.form.get('comentarios') else etapa_selected['comentarios']

                        # Se actualiza la fecha de la etapa con la fecha actual formato ISO
                        etapa_selected['fecha_actualizacion'] = iso_date()


                        # Informativo para ver los datos de la etapa
                        # print("Las etapas son:")
                        # print(etapas)
                        # print("Etapa a actualizar")
                        # print(json.dumps(etapas, indent=4, ensure_ascii=False))

                        try:
                            resultado = supabase.table('SEGUIMIENTO_SOLICITUDES').update({"etapas": etapas}).eq('id', seguimiento_id).execute()
                            print("Seguimiento actualizado")
                            print(resultado)
                        except Exception as e:
                            print(f"Error al actualizar el seguimiento: {str(e)}")
                            return jsonify({"error": "Error al actualizar el seguimiento"}), 500

                elif etapa_nombre == 'banco':
                    print("La etapa es banco")
                    # # Actualizar viabilidad si se proporciona
                    # if 'viabilidad' in request.form:
                    #     etapa_selected['viabilidad'] = request.form.get('viabilidad')

                    # # Manejar archivos si se envían
                    # files = exist_files_in_request(request)
                    # if files:
                    #     if 'archivos' not in etapa_selected:
                    #         etapa_selected['archivos'] = []
                    #     uploaded_files_data = upload_files(request.files, supabase)
                    #     etapa_file = add_files_to_etapa(uploaded_files_data, usuario_id)
                    #     etapa_selected['archivos'].append(etapa_file)

                elif etapa_nombre == 'desembolso':
                    print("La etapa es desembolso")
                    # # Actualizar estado de desembolso
                    # if 'desembolsado' in request.form:
                    #     etapa_selected['desembolsado'] = request.form.get('desembolsado') == 'true'

                    # # Actualizar fecha estimada si se proporciona
                    # if 'fecha_estimada' in request.form:
                    #     etapa_selected['fecha_estimada'] = request.form.get('fecha_estimada')

                # Actualizar estado si se proporciona
                # if 'estado' in request.form:
                #     estado_anterior = etapa_selected.get('estado')
                #     etapa_selected['estado'] = request.form.get('estado')

                #     # Añadir al historial
                #     if 'historial' not in etapa_selected:
                #         etapa_selected['historial'] = []

                #     etapa_selected['historial'].append({
                #         "fecha": datetime.now().isoformat(),
                #         "estado": request.form.get('estado'),
                #         "usuario_id": usuario_id,
                #         "comentario": request.form.get('comentario', '')
                #     })

                # # Actualizar comentarios si se proporcionan
                # if 'comentarios' in request.form:
                #     etapa_a_modificar['comentarios'] = request.form.get('comentarios')

                # # Actualizar la fecha de la etapa
                # etapa_a_modificar['fecha_actualizacion'] = iso_date()

                # # Guardar cambios
                # resultado = supabase.table('SEGUIMIENTO_SOLICITUDES')\
                #     .update({
                #         "etapas": etapas,
                #         "fecha_ultima_actualizacion": datetime.now().isoformat()
                #     })\
                #     .eq('id', seguimiento_data['id'])\
                #     .execute()

                return jsonify({
                    "mensaje": f"Etapa {etapa_nombre} actualizada exitosamente",
                }), 200

            except Exception as e:
                print(f"Error al actualizar etapa: {e}")
                return jsonify({"error": f"Error al actualizar etapa: {str(e)}"}), 500

    def consultar_seguimiento_por_radicado_publico(self, id_radicado):
        try:
            if not id_radicado:
                return jsonify({"error": "Se requiere el ID de radicado"}), 400

            seguimiento = supabase.table('SEGUIMIENTO_SOLICITUDES')\
                .select('*')\
                .eq('id_radicado', id_radicado)\
                .execute()
            if not seguimiento.data:
                return jsonify({"error": "No se encontró el seguimiento solicitado"}), 404

            # Obtener datos del solicitante
            solicitud = seguimiento.data[0]
            solicitante_id = solicitud.get('solicitante_id')

            # Obtener datos básicos del solicitante para mostrar
            solicitante = supabase.table('SOLICITANTES')\
                .select('nombre_completo,numero_documento')\
                .eq('solicitante_id', solicitante_id)\
                .execute()

            # Formateamos la respuesta para presentarla de manera amigable al usuario
            resultado = {
                "id_radicado": id_radicado,
                "producto_solicitado": solicitud.get('producto_solicitado'),
                "estado_global": solicitud.get('estado_global'),
                "banco": solicitud.get('banco'),
                "fecha_creacion": solicitud.get('fecha_creacion'),
                "fecha_ultima_actualizacion": solicitud.get('fecha_cambio'),
                "solicitante": {
                    "nombre": solicitante.data[0].get('nombre_completo') if solicitante.data else "No disponible",
                    "documento": solicitante.data[0].get('numero_documento') if solicitante.data else "No disponible"
                },
                "etapas": solicitud.get('etapas', [])
            }

            return jsonify(resultado), 200

        except Exception as e:
            print(f"Error al consultar seguimiento público: {e}")
            return jsonify({"error": f"Error al consultar seguimiento: {str(e)}"}), 500
