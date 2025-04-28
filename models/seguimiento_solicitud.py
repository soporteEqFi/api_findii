from models.generales.generales import *
from datetime import datetime
from models.utils.tracking.validate_tracking_type import validate_etapa_type
from models.utils.tracking.validate_tracking_data import validate_etapa_data
from models.utils.tracking.etapas import get_etapa_by_radicado
from models.utils.others.date_utils import iso_date

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
    
    # def crear_seguimiento(self):
    #     try:
    #         data = request.json
    #         id_solicitante = data.get('id_solicitante')
    #         id_producto = data.get('id_producto')
    #         id_asesor = data.get('id_asesor')
    #         producto_solicitado = data.get('producto_solicitado')
    #         banco = data.get('banco')
            
    #         # Validar datos requeridos
    #         if not id_solicitante or not id_producto or not id_asesor:
    #             return jsonify({"error": "Faltan datos requeridos"}), 400
                
    #         # Generar ID único para seguimiento
    #         id_radicado = self.generar_id_radicado()
            
    #         # Obtener documentos ya subidos
    #         docs = supabase.table("PRUEBA_IMAGEN").select('*').eq('id_solicitante', id_solicitante).execute()
    #         archivos_existentes = []
            
    #         if docs.data:
    #             for doc in docs.data:
    #                 archivos_existentes.append({
    #                     "archivo_id": str(uuid.uuid4()),
    #                     "nombre": doc.get('imagen', '').split('/')[-1] if '/' in doc.get('imagen', '') else 'documento.pdf',
    #                     "url": doc.get('imagen'),
    #                     "estado": "pendiente",
    #                     "comentario": "",
    #                     "modificado": False,
    #                     "fecha_modificacion": datetime.now().isoformat(),
    #                     "ultima_fecha_modificacion": datetime.now().isoformat()
    #                 })
            
    #         # Crear estructura inicial de etapas
    #         etapas_iniciales = [
    #             {
    #                 "etapa": "documentos",
    #                 "archivos": archivos_existentes,
    #                 "requisitos_pendientes": ["Subir cédula", "Subir desprendibles de pago"],
    #                 "fecha_actualizacion": datetime.now().isoformat(),
    #                 "comentarios": "Por favor sube los documentos requeridos",
    #                 "estado": "Pendiente",
    #                 "historial": [
    #                     {"fecha": datetime.now().isoformat(), "estado": "Pendiente", "usuario_id": id_asesor, "comentario": "Creación de solicitud"}
    #                 ]
    #             },
    #             {
    #                 "etapa": "banco",
    #                 "archivos": [],
    #                 "viabilidad": "Pendiente",
    #                 "fecha_actualizacion": datetime.now().isoformat(),
    #                 "comentarios": "",
    #                 "estado": "Pendiente",
    #                 "historial": []
    #             },
    #             {
    #                 "etapa": "desembolso",
    #                 "desembolsado": False,
    #                 "estado": "Pendiente",
    #                 "fecha_estimada": None,
    #                 "fecha_actualizacion": datetime.now().isoformat(),
    #                 "comentarios": "",
    #                 "historial": []
    #             }
    #         ]
            
    #         # Insertar registro de seguimiento
    #         resultado = supabase.table('SEGUIMIENTO_SOLICITUDES').insert({
    #             "id_radicado": id_radicado,
    #             "id_solicitante": id_solicitante,
    #             "id_producto": id_producto,
    #             "id_asesor": id_asesor,
    #             "producto_solicitado": producto_solicitado,
    #             "banco": banco,
    #             "estado_global": "Iniciado",
    #             "etapas": etapas_iniciales
    #         }).execute()
            
    #         return jsonify({
    #             "mensaje": "Seguimiento creado exitosamente",
    #             "id_radicado": id_radicado,
    #             "id": resultado.data[0]['id'] if resultado.data else None
    #         }), 201
            
    #     except Exception as e:
    #         print(f"Error al crear seguimiento: {e}")
    #         return jsonify({"error": f"Error al crear seguimiento: {str(e)}"}), 500

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
                print("Docs")
                print(docs.data)
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
        
    def consultar_seguimiento(self, id_radicado=None, id_solicitante=None):
        try:
            if not id_radicado and not id_solicitante:
                return jsonify({"error": "Se requiere id_radicado o id_solicitante"}), 400
                
            query = supabase.table('SEGUIMIENTO_SOLICITUDES').select('*')
            print(query)
            if id_radicado:
                query = query.eq('id_radicado', id_radicado)
                print(query)
            elif id_solicitante:
                query = query.eq('id_solicitante', id_solicitante)
                
            resultado = query.execute()
            print(resultado)
            
            if not resultado.data:
                return jsonify({"error": "Seguimiento no encontrado"}), 404
                
            return jsonify(resultado.data[0]), 200
            
        except Exception as e:
            print(f"Error al consultar seguimiento: {e}")
            return jsonify({"error": f"Error al consultar seguimiento: {str(e)}"}), 500
    
    def actualizar_etapa(self):
        try:
            data = request.json
            id_seguimiento = data.get('id_seguimiento')
            id_radicado = data.get('id_radicado')
            etapa_nombre = data.get('etapa')
            nuevo_estado = data.get('estado')
            comentarios = data.get('comentarios', '')
            usuario_id = data.get('usuario_id')
            
            if not (id_seguimiento or id_radicado) or not etapa_nombre or not nuevo_estado:
                return jsonify({"error": "Faltan datos requeridos"}), 400
                
            # Obtener el registro actual
            query = supabase.table('SEGUIMIENTO_SOLICITUDES').select('*')
            
            if id_seguimiento:
                query = query.eq('id', id_seguimiento)
            else:
                query = query.eq('id_radicado', id_radicado)
                
            seguimiento = query.execute()
            
            if not seguimiento.data:
                return jsonify({"error": "Seguimiento no encontrado"}), 404
                
            seguimiento_data = seguimiento.data[0]
            etapas = seguimiento_data['etapas']
            
            # Buscar la etapa a actualizar
            etapa_actualizada = False
            for etapa in etapas:
                if etapa['etapa'] == etapa_nombre:
                    estado_anterior = etapa['estado']
                    etapa['estado'] = nuevo_estado
                    etapa['comentarios'] = comentarios
                    etapa['fecha_actualizacion'] = datetime.now().isoformat()
                    
                    # Añadir al historial
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
                    break
            
            if not etapa_actualizada:
                return jsonify({"error": f"Etapa '{etapa_nombre}' no encontrada"}), 404
                
            # Actualizar estado global si todas las etapas están completas o si alguna está rechazada
            estados = [e['estado'] for e in etapas]
            if all(e == 'Completado' for e in estados):
                estado_global = 'Completado'
            elif any(e == 'Rechazado' for e in estados):
                estado_global = 'Rechazado'
            else:
                estado_global = 'En proceso'
                
            # Guardar cambios
            resultado = supabase.table('SEGUIMIENTO_SOLICITUDES')\
                .update({
                    "etapas": etapas,
                    "estado_global": estado_global,
                    "fecha_ultima_actualizacion": datetime.now().isoformat()
                })\
                .eq('id', seguimiento_data['id'])\
                .execute()
                
            return jsonify({
                "mensaje": "Etapa actualizada exitosamente",
                "estado_anterior": estado_anterior,
                "estado_nuevo": nuevo_estado,
                "estado_global": estado_global
            }), 200
            
        except Exception as e:
            print(f"Error al actualizar etapa: {e}")
            return jsonify({"error": f"Error al actualizar etapa: {str(e)}"}), 500
            
    def actualizar_documentos(self):
        from models.utils.seguimiento_solicitud.utils import handle_new_files, handle_history_update, handle_update_files

        try:
            # Valida que vengan todos los datos necesarios
            id_radicado, solicitante_id, etapa_nombre = validate_etapa_data(request)

            seguimiento_data = get_etapa_by_radicado(id_radicado, supabase)
            # print(seguimiento_data)
            etapas = seguimiento_data[0]['etapas']
            seguimiento_id = seguimiento_data[0]['id']

            # Traer qué tipo de etapa es, puede ser documentos, banco o desembolso.
            etapa_name = validate_etapa_type(etapa_nombre)
            if not etapa_name:
                return jsonify({"error": f"La etapa {etapa_nombre} no es válida"}), 400
            
            for etapa in etapas:
                if etapa['etapa'] == etapa_name:
                    etapa_selected = etapa        
                    break

            # etapa_selected = None
            # etapa_index = None
            # for i, etapa in enumerate(etapas):
            #     if etapa['etapa'] == 'documentos':
            #         etapa_selected = etapa
            #         etapa_index = i
            #         break

            # Manejar actualizaciones específicas por tipo de etapa
            if etapa_nombre == 'documentos':

                user_data = {
                    "id_solicitante": solicitante_id,
                    "id_radicado": id_radicado,
                    "etapa": etapa_name
                }

                # Manejar archivos para reemplazar
                replace_files = request.form.get('hay_archivos_para_reemplazar', '').lower() in ['true', 'True']
                new_files = request.form.get('hay_archivos_nuevos', '').lower() in ['true', 'True'] 

                print(type(new_files))
                
                print("Replace files")
                print(replace_files)
                print("New files")
                print(new_files)

                if replace_files:
                    print("Hay archivos para reemplazar")
                    datos_actualizados = handle_update_files(request, supabase)
                    history_new_data = handle_history_update(request, etapa_selected)

                    print("Datos actualizados")
                    print(datos_actualizados)

                    # Encontrar y actualizar el archivo en la etapa
                    for i, archivo in enumerate(etapa_selected['archivos']):
                        if archivo['url'] == request.form.get('ruta_archivo_reemplazar'):
                            # Reemplazar los datos del archivo
                            etapa_selected['archivos'][i] = datos_actualizados
                            break

                    # Actualizar el historial
                    etapa_selected['historial'].append(history_new_data)
                    
                    # Actualizar estado y comentarios
                    etapa_selected['estado'] = request.form.get('estado') if request.form.get('estado') else etapa_selected['estado']
                    etapa_selected['comentarios'] = request.form.get('comentarios') if request.form.get('comentarios') else etapa_selected['comentarios']
                    etapa_selected['fecha_actualizacion'] = iso_date()

                    print("Etapa a actualizar")
                    print(json.dumps(etapas, indent=4, ensure_ascii=False))

                    try:
                        resultado = supabase.table('SEGUIMIENTO_SOLICITUDES')\
                            .update({
                                "etapas": etapas,
                            })\
                            .eq('id', seguimiento_id)\
                            .execute()
                    except Exception as e:
                        print(f"Error al actualizar el seguimiento: {str(e)}")
                        return jsonify({"error": "Error al actualizar el seguimiento"}), 500

                    print("Seguimiento actualizado")
                    print(resultado)

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
        


