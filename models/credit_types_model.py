from models.generales.generales import *
from models.user_model import *
from datetime import datetime
import uuid


class credit_typesModel():
    mod_user = userModel()


    def get_all_credit_types(self):
        max_retries = 3
        retry_delay = 2  # segundos

        data = request.json 
        cedula = data['cedula']

        for attempt in range(max_retries):
            try:
                # Consultar la empresa del usuario logeado
                response_user_info = supabase.table("TABLA_USUARIOS")\
                    .select('*')\
                    .eq('cedula', cedula)\
                    .execute()

                if not response_user_info.data:
                    return jsonify({"mensaje": "Usuario no encontrado"}), 404

                id_empresa_usuario = response_user_info.data[0]['id_empresa']

                # Consultar los tipos de crédito de la empresa
                datos_empresa = supabase.table('EMPRESAS')\
                    .select('*')\
                    .eq('id_empresa', id_empresa_usuario)\
                    .execute()

                if not datos_empresa.data:
                    return jsonify({"mensaje": "Empresa no encontrada"}), 404

                id_empresa = datos_empresa.data[0]['id_empresa']

                # Consultar los tipos de crédito de la empresa
                res = supabase.table('TIPOS_CREDITOS_CONFIG')\
                    .select('*')\
                    .eq('id_empresa', id_empresa)\
                    .execute()

                return jsonify(res.data), 200

            except Exception as e:
                print(f"Intento {attempt + 1} fallido: {str(e)}")
                
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    print(f"Reintentando en {retry_delay} segundos...")
                    continue
                else:
                    print(f"Error después de {max_retries} intentos: {str(e)}")
                    return jsonify({
                        "mensaje": "Error al obtener los tipos de crédito",
                        "error": str(e)
                    }), 500

    def add_credit_type(self):
        try:
            data = request.json
            print("Datos de la solicitud")
            print(data)

            cedula = data['cedula']
            response_user_info = supabase.table("TABLA_USUARIOS").select('*').eq('cedula', cedula).execute()
            print("Datos del usuario")
            print(response_user_info.data)
            id_empresa_usuario = response_user_info.data[0]['id_empresa']
            print(id_empresa_usuario)

            # Obtener los datos del tipo de crédito
            credit_type = data['credit_type']
            name = credit_type['name']
            display_name = credit_type['display_name']
            description = credit_type['description']
            fields = credit_type['fields']
            is_active = credit_type['is_active']

            data_to_send = {
                "name": name,
                "display_name": display_name,
                "description": description,
                "fields": fields,
                "is_active": is_active,
                "id_empresa": id_empresa_usuario
            }

            print(data_to_send)

            # print(fields)
            # print(data)
            res = supabase.table('TIPOS_CREDITOS_CONFIG').insert(data_to_send).execute()
            print(res)
            return jsonify({"mensaje": "Tipo de crédito agregado exitosamente"}), 200
        except Exception as e:
            print(e)
            return jsonify({"mensaje": "Ocurrió un error al agregar el tipo de crédito."}), 500
        

    def edit_credit_type(self):
        try:
            data = request.get_json()

            print("Datos de la solicitud")
            print(data)
            
            if not data or 'id' not in data:
                return jsonify({'error': 'Se requiere el ID del tipo de crédito'}), 400

            credit_type_id = data.get('id')
            
            # Verificar primero si el tipo de crédito existe
            try:
                existing_credit = supabase.table('TIPOS_CREDITOS_CONFIG')\
                    .select('*')\
                    .eq('id', credit_type_id)\
                    .execute()
                    
                if not existing_credit.data:
                    return jsonify({'error': 'Tipo de crédito no encontrado'}), 404
                    
                current_data = existing_credit.data[0]

            except Exception as e:
                print(f"Error verificando existencia: {e}")
                return jsonify({'error': 'Error al verificar el tipo de crédito'}), 500

            # Preparar los datos para actualizar
            update_data = {}
            
            # Solo incluir los campos que vienen en la solicitud
            if 'name' in data:
                update_data['name'] = data['name']
            if 'display_name' in data:
                update_data['display_name'] = data['display_name']
            if 'description' in data:
                update_data['description'] = data['description']
            if 'is_active' in data:
                update_data['is_active'] = data['is_active']
            
            # Siempre actualizar updated_at
            update_data['updated_at'] = datetime.now().isoformat()
            
            # Si no hay campos para actualizar (excepto updated_at), verificar si hay campos
            if len(update_data) <= 1 and 'fields' not in data:
                return jsonify({'error': 'No se proporcionaron datos para actualizar'}), 400

            # Actualizar datos básicos del tipo de crédito
            try:
                response = supabase.table('TIPOS_CREDITOS_CONFIG')\
                    .update(update_data)\
                    .eq('id', credit_type_id)\
                    .execute()
                    
            except Exception as e:
                print(f"Error actualizando datos básicos: {e}")
                return jsonify({'error': f'Error actualizando datos básicos: {str(e)}'}), 500

            # Si se proporcionaron campos nuevos, actualizarlos
            if 'fields' in data:
                try:
                    # Mantener los campos existentes
                    current_fields = current_data.get('fields', [])
                    
                    # Crear un mapa de los campos actuales por ID
                    current_fields_map = {field['id']: field for field in current_fields}
                    
                    # Actualizar o agregar nuevos campos
                    for new_field in data['fields']:
                        field_id = new_field.get('id')
                        
                        if field_id and field_id in current_fields_map:
                            # Actualizar campo existente
                            current_field = current_fields_map[field_id]
                            current_field.update(new_field)
                        else:
                            # Agregar nuevo campo
                            if not field_id:
                                new_field['id'] = str(uuid.uuid4())
                            current_fields.append(new_field)
                    
                    # Actualizar los campos en la base de datos
                    response = supabase.table('TIPOS_CREDITOS_CONFIG')\
                        .update({'fields': current_fields})\
                        .eq('id', credit_type_id)\
                        .execute()
                        
                except Exception as e:
                    print(f"Error actualizando campos: {e}")
                    return jsonify({'error': f'Error actualizando campos: {str(e)}'}), 500

            # Obtener el registro actualizado
            try:
                updated_record = supabase.table('TIPOS_CREDITOS_CONFIG')\
                    .select('*')\
                    .eq('id', credit_type_id)\
                    .execute()
                    
                return jsonify({
                    'mensaje': 'Tipo de crédito actualizado exitosamente',
                    'tipo_credito': updated_record.data[0] if updated_record.data else None
                }), 200
                
            except Exception as e:
                print(f"Error obteniendo registro actualizado: {e}")
                return jsonify({'error': f'Error obteniendo registro actualizado: {str(e)}'}), 500

        except Exception as e:
            print(f"Error general: {e}")
            return jsonify({'error': f'Error general: {str(e)}'}), 500