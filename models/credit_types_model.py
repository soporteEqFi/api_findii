from models.generales.generales import *
from models.user_model import *
from datetime import datetime
import uuid
import errno


class credit_typesModel():
    mod_user = userModel()


    def get_all_credit_types(self):
        max_retries = 3
        retry_delay = 4  # seconds

        for attempt in range(max_retries):
            try:
                data = request.json 
                cedula = data['cedula']

                # Consultas a las tablas en un solo paso, similar a get_all_data
                tablas = {
                    "user_info": supabase.table("TABLA_USUARIOS").select('*').eq('cedula', cedula).execute().data,
                    "credit_types": None  # Lo llenaremos después de obtener id_empresa
                }

                if not tablas["user_info"]:
                    return jsonify({
                        "mensaje": "Usuario no encontrado",
                        "data": []
                    }), 404

                id_empresa = tablas["user_info"][0]['id_empresa']

                # Ahora obtenemos los tipos de crédito
                tablas["credit_types"] = supabase.table('TIPOS_CREDITOS_CONFIG')\
                    .select('*')\
                    .eq('id_empresa', id_empresa)\
                    .execute().data

                return jsonify({
                    "mensaje": "Tipos de crédito obtenidos exitosamente",
                    "data": tablas["credit_types"] if tablas["credit_types"] else []
                }), 200

            except Exception as e:
                if isinstance(e, OSError) and e.errno == errno.WSAEWOULDBLOCK:
                    print(f"Intento {attempt + 1} fallido debido a operación de socket no bloqueante: {e}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(retry_delay)
                        continue
                else:
                    print(f"Intento {attempt + 1} fallido: {e}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(retry_delay)
                        continue

        # Si llegamos aquí, significa que todos los intentos fallaron
        return jsonify({
            "mensaje": "No se pudieron obtener los tipos de crédito después de varios intentos. Por favor, intenta nuevamente.",
            "data": []
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