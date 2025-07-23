from models.generales.generales import *
from models.user_model import *
from datetime import datetime
import uuid
import errno


class credit_typesModel():
    mod_user = userModel()


    def get_all_credit_types(self):
        max_retries = 3
        retry_delay = 1  # Reducir a 1 segundo para ser más responsivo

        # PASO 1: Obtener información del usuario (con reintentos)
        user_info = None
        for attempt in range(max_retries):
            try:
                data = request.json 
                cedula = data['cedula']
                
                print("Antes de consultar la tabla de usuarios")
                user_info = supabase.table("TABLA_USUARIOS").select('*').eq('cedula', cedula).execute().data

                print("info usuario ejecutado")
                
                if not user_info:
                    return jsonify({
                        "mensaje": "Usuario no encontrado",
                        "data": []
                    }), 404
                    
                break  # ✅ Si llegamos aquí, la consulta del usuario fue exitosa
                
            except Exception as e:
                error_msg = str(e)
                if "10035" in error_msg or "WSAEWOULDBLOCK" in error_msg:
                    print(f"Error de conectividad en consulta de usuario (intento {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(retry_delay)
                        continue
                else:
                    print(f"Error no relacionado con conectividad: {e}")
                    return jsonify({
                        "mensaje": "Error al obtener información del usuario",
                        "error": str(e),
                        "data": []
                    }), 500
        else:
            return jsonify({
                "mensaje": "No se pudo obtener información del usuario después de varios intentos",
                "data": []
            }), 500

        # PASO 2: Obtener tipos de crédito (con reintentos independientes)
        id_empresa = user_info[0]['id_empresa']
        
        for attempt in range(max_retries):
            try:
                print("Antes de consultar la tabla de TIPOS DE CRÉDITOS")
                credit_types = supabase.table('TIPOS_CREDITOS_CONFIG')\
                    .select('*')\
                    .eq('id_empresa', id_empresa)\
                    .execute().data
                
                print("tipos de créditos ejecutado")

                return jsonify({
                    "mensaje": "Tipos de crédito obtenidos exitosamente",
                    "data": credit_types if credit_types else []
                }), 200

            except Exception as e:
                error_msg = str(e)
                if "10035" in error_msg or "WSAEWOULDBLOCK" in error_msg:
                    print(f"Error de conectividad en consulta de tipos de crédito (intento {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(retry_delay)
                        continue
                else:
                    print(f"Error no relacionado con conectividad en tipos de crédito: {e}")
                    return jsonify({
                        "mensaje": "Error al obtener tipos de crédito",
                        "error": str(e),
                        "data": []
                    }), 500

        # Si llegamos aquí, significa que todos los intentos de la segunda consulta fallaron
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
            
            # Solo incluir los campos que vienen en la solicitud (en snake_case)
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

            # Si se proporcionaron campos nuevos, reemplazar la lista completa
            if 'fields' in data:
                try:
                    print("Campos recibidos del frontend:")
                    print(data['fields'])
                    
                    # Asegurarse de que cada campo tenga un id
                    new_fields = []
                    for field in data['fields']:
                        if not field.get('id'):
                            field['id'] = str(uuid.uuid4())
                        new_fields.append(field)

                    print("Campos procesados para guardar:")
                    print(new_fields)

                    # Reemplazar la lista completa de campos
                    response = supabase.table('TIPOS_CREDITOS_CONFIG')\
                        .update({'fields': new_fields})\
                        .eq('id', credit_type_id)\
                        .execute()
                        
                    print("Respuesta de la actualización de campos:")
                    print(response)
                        
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

    def delete_credit_type(self):
        try:
            data = request.get_json()
            print("=== ELIMINANDO TIPO DE CRÉDITO ===")
            print("Datos de la solicitud:", data)
            
            if not data or 'id' not in data:
                return jsonify({'error': 'Se requiere el ID del tipo de crédito'}), 400

            credit_type_id = data.get('id')
            print(f"ID del tipo de crédito a eliminar: {credit_type_id}")
            
            # Verificar primero si el tipo de crédito existe
            try:
                existing_credit = supabase.table('TIPOS_CREDITOS_CONFIG')\
                    .select('*')\
                    .eq('id', credit_type_id)\
                    .execute()
                    
                if not existing_credit.data:
                    return jsonify({'error': 'Tipo de crédito no encontrado'}), 404
                    
                credit_type_to_delete = existing_credit.data[0]
                print(f"Tipo de crédito encontrado: {credit_type_to_delete['name']}")

            except Exception as e:
                print(f"Error verificando existencia: {e}")
                return jsonify({'error': 'Error al verificar el tipo de crédito'}), 500

            # Eliminar el tipo de crédito
            try:
                response = supabase.table('TIPOS_CREDITOS_CONFIG')\
                    .delete()\
                    .eq('id', credit_type_id)\
                    .execute()
                    
                print("Respuesta de la eliminación:")
                print(response)
                
                if response.data:
                    print(f"Tipo de crédito '{credit_type_to_delete['name']}' eliminado exitosamente")
                    return jsonify({
                        'mensaje': f"Tipo de crédito '{credit_type_to_delete['name']}' eliminado exitosamente"
                    }), 200
                else:
                    return jsonify({'error': 'No se pudo eliminar el tipo de crédito'}), 500
                    
            except Exception as e:
                print(f"Error eliminando tipo de crédito: {e}")
                return jsonify({'error': f'Error eliminando tipo de crédito: {str(e)}'}), 500

        except Exception as e:
            print(f"Error general en delete_credit_type: {e}")
            return jsonify({'error': f'Error general: {str(e)}'}), 500