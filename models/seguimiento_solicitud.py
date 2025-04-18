from models.generales.generales import *
from datetime import datetime
import random
import string
import uuid

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
    
    def crear_seguimiento(self):
        try:
            data = request.json
            id_solicitante = data.get('id_solicitante')
            id_producto = data.get('id_producto')
            id_asesor = data.get('id_asesor')
            producto_solicitado = data.get('producto_solicitado')
            banco = data.get('banco')
            
            # Validar datos requeridos
            if not id_solicitante or not id_producto or not id_asesor:
                return jsonify({"error": "Faltan datos requeridos"}), 400
                
            # Generar ID único para seguimiento
            id_radicado = self.generar_id_radicado()
            
            # Obtener documentos ya subidos
            docs = supabase.table("PRUEBA_IMAGEN").select('*').eq('id_solicitante', id_solicitante).execute()
            archivos_existentes = []
            
            if docs.data:
                for doc in docs.data:
                    archivos_existentes.append({
                        "archivo_id": str(uuid.uuid4()),
                        "nombre": doc.get('imagen', '').split('/')[-1] if '/' in doc.get('imagen', '') else 'documento.pdf',
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
                    "requisitos_pendientes": ["Subir cédula", "Subir desprendibles de pago"],
                    "fecha_actualizacion": datetime.now().isoformat(),
                    "comentarios": "Por favor sube los documentos requeridos",
                    "estado": "Pendiente",
                    "historial": [
                        {"fecha": datetime.now().isoformat(), "estado": "Pendiente", "usuario_id": id_asesor, "comentario": "Creación de solicitud"}
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
                "estado_global": "Iniciado",
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
            
            if id_radicado:
                query = query.eq('id_radicado', id_radicado)
            elif id_solicitante:
                query = query.eq('id_solicitante', id_solicitante)
                
            resultado = query.execute()
            
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
        try:
            # Verificar si hay un ID de seguimiento
            if 'id_radicado' not in request.form and 'id_seguimiento' not in request.form:
                return jsonify({"error": "Falta el ID de seguimiento o radicado"}), 400
            
            id_radicado = request.form.get('id_radicado')
            id_seguimiento = request.form.get('id_seguimiento')
            
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
            
            # Buscar la etapa de documentos
            etapa_documentos = None
            for etapa in etapas:
                if etapa['etapa'] == 'documentos':
                    etapa_documentos = etapa
                    break
                    
            if not etapa_documentos:
                return jsonify({"error": "Etapa de documentos no encontrada"}), 404
                
            # Procesar archivos nuevos
            if 'archivos' in request.files:
                files = request.files.getlist('archivos')
                
                if 'archivos' not in etapa_documentos:
                    etapa_documentos['archivos'] = []
                    
                for file in files:
                    try:
                        # Crear nombre único para el archivo
                        extension = file.filename.split('.')[-1]
                        unique_filename = f"{uuid.uuid4().hex}_{int(datetime.timestamp(datetime.now()))}.{extension}"
                        file_path = f"creditos/{unique_filename}"

                        # Leer archivo y convertir a bytes
                        file_data = file.read()

                        # Subir archivo a Supabase Storage
                        res = supabase.storage.from_("findii").upload(
                            file_path,
                            file_data,
                            file_options={"content-type": file.mimetype}
                        )

                        # Obtener URL pública
                        archivo_url = supabase.storage.from_("findii").get_public_url(file_path)

                        # Añadir a la lista de archivos
                        etapa_documentos['archivos'].append({
                            "archivo_id": str(uuid.uuid4()),
                            "nombre": file.filename,
                            "url": archivo_url,
                            "estado": "pendiente",
                            "comentario": "",
                            "modificado": False,
                            "fecha_modificacion": datetime.now().isoformat(),
                            "ultima_fecha_modificacion": datetime.now().isoformat()
                        })

                    except Exception as e:
                        print(f"Error procesando archivo {file.filename}: {e}")
                        continue
                
                # Actualizar la fecha de la etapa
                etapa_documentos['fecha_actualizacion'] = datetime.now().isoformat()
                
                # Añadir al historial
                if 'historial' not in etapa_documentos:
                    etapa_documentos['historial'] = []
                    
                etapa_documentos['historial'].append({
                    "fecha": datetime.now().isoformat(),
                    "estado": "Documentos actualizados",
                    "usuario_id": request.form.get('usuario_id', ''),
                    "comentario": "Se subieron nuevos documentos"
                })
                
                # Guardar cambios
                resultado = supabase.table('SEGUIMIENTO_SOLICITUDES')\
                    .update({
                        "etapas": etapas,
                        "fecha_ultima_actualizacion": datetime.now().isoformat()
                    })\
                    .eq('id', seguimiento_data['id'])\
                    .execute()
                    
                return jsonify({
                    "mensaje": "Documentos actualizados exitosamente",
                    "archivos": etapa_documentos['archivos']
                }), 200
                
            return jsonify({"error": "No se enviaron archivos"}), 400
            
        except Exception as e:
            print(f"Error al actualizar documentos: {e}")
            return jsonify({"error": f"Error al actualizar documentos: {str(e)}"}), 500

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
                        "nombre": doc.get('imagen', '').split('/')[-1] if '/' in doc.get('imagen', '') else 'documento.pdf',
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