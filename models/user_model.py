from librerias import *
import time
from models.generales.generales import *
from models.utils.login.validate_info import *
from models.utils.login.fill_data import *
import os

class userModel():

    def create_user(self):
        datos = request.json
        email = datos.get('email', '').strip()
        password = datos.get('password', '').strip()
        name = datos.get('nombre', '').strip()
        rol = datos.get('rol', '').strip()
        identification = datos.get('cedula', '').strip()
        business = datos.get('empresa', '').strip()

        # 1. Validar email
        if not validar_email(email):
            return jsonify({"msg": "El formato del email es inválido"}), 400

        # 2. Verificar si el usuario ya existe en Supabase Auth
        if usuario_existe(email):
            return jsonify({"msg": "El usuario ya está registrado. Intenta iniciar sesión."}), 400

        # 3. Crear usuario en Supabase Auth (SIN verificación por correo)
        try:
            response = supabase.auth.sign_up({"email": email, "password": password, "email_confirmed_at": datetime.utcnow().isoformat()})

            # ✅ CORRECCIÓN: Verificar si hubo un error en la respuesta
            if response is None or response.user is None:
                return jsonify({"msg": "Error en Supabase Auth: No se pudo crear el usuario"}), 400
            
            # ✅ CORRECCIÓN: Obtener correctamente el ID del usuario
            user_id = response.user.id
            print(f"Usuario creado en Auth con ID: {user_id}")

            # 4. Insertar usuario en la tabla personalizada
            api_response = supabase.from_('TABLA_USUARIOS').insert({
                "email": email,
                "nombre": name,
                "rol": rol,
                "password": password,
                "cedula": identification,
                "empresa": business,
                "imagen_aliado": get_business_image()
            }).execute()

            # ✅ Verificar si la inserción falló
            if hasattr(api_response, "error") and api_response.error:
                print(f"Error al insertar en TABLA_USUARIOS: {api_response.error}")
                return jsonify({"msg": "Error al guardar usuario en la base de datos: " + str(api_response.error)}), 500

            print(f"Usuario insertado en TABLA_USUARIOS: {api_response.data}")

        except Exception as e:
            return jsonify({"msg": "Error inesperado al crear usuario: " + str(e)}), 500

        return jsonify({"msg": "Usuario creado exitosamente. VERIFICA TU CORREO PARA ACTIVAR TU CUENTA", "user_id": user_id}), 201
    

    # def get_agent_info(self, cedula):
    #     max_retries = 3
    #     retry_delay = 2  # seconds

    #     for attempt in range(max_retries):
    #         try:
    #             if cedula is None or cedula == "":
    #                 return jsonify({"error" : "campo cedula vacío"}), 401

    #             response = supabase.table("TABLA_USUARIOS").select('*').eq('cedula', cedula).execute()

    #             response_data = response.data

    #             return jsonify({
    #                 "id": response_data[0]['id'],
    #                 "nombre": response_data[0]['nombre'],
    #                 "correo": response_data[0]['email'],
    #                 "rol": response_data[0]['rol'],
    #                 "cedula": response_data[0]['cedula'],
    #                 "empresa": response_data[0]['empresa'],
    #                 "imagen_aliado": response_data[0]['imagen_aliado']
    #                 })

    #         except Exception as e:
    #             print(f"Attempt {attempt + 1} failed: {e}")
    #             if attempt < max_retries - 1:
    #                 time.sleep(retry_delay)
    #             else:
    #                 print("Ocurrió un error:", e)
    #                 return jsonify({"mensaje": "Ocurrió un error al procesar la solicitud."}), 500
                
        
    def get_user_info(self, cedula):
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                if cedula is None or cedula == "":
                    return jsonify({"error" : "campo cedula vacío"}), 401

                response = supabase.table("TABLA_USUARIOS").select('*').eq('cedula', cedula).execute()

                response_data = response.data
                print(response_data[0])
                
                # Convertir empresa a entero antes de hacer la consulta
                empresa_id = response_data[0]['id_empresa']
                datos_empresa = supabase.table('EMPRESAS').select('*').eq('id_empresa', empresa_id).execute()
                
                print(datos_empresa.data[0])
                return jsonify({
                    "id": response_data[0]['id'],
                    "nombre": response_data[0]['nombre'],
                    "correo": response_data[0]['email'],
                    "rol": response_data[0]['rol'],
                    "cedula": response_data[0]['cedula'],
                    "empresa": datos_empresa.data[0]['nombre'],
                    "imagen_aliado": datos_empresa.data[0]['imagen']
                    })

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    print("Ocurrió un error:", e)
                    return jsonify({"mensaje": "Ocurrió un error al procesar la solicitud."}), 500
                
    def get_solicitante_info(self, cedula):

        print(cedula)
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                if cedula is None or cedula == "":
                    return jsonify({"error" : "campo cedula vacío"}), 401

                response = supabase.table("SOLICITANTES").select('*').eq('numero_documento', cedula).execute()

                response_data = response.data # Changed from response.datas to response.data

                print(response_data[0]['solicitante_id'])

                return jsonify({
                    "numero_documento": response_data[0]['numero_documento'],
                    "solicitante_id": response_data[0]['solicitante_id']
                    })

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    print("Ocurrió un error:", e)
                    return jsonify({"mensaje": "Ocurrió un error al procesar la solicitud."}), 500
    def update_user(self):
        try:
            data_dict ={
                "nombre": request.json.get('nombre'),
                "cedula": request.json.get('cedula'),
                "rol": request.json.get('rol'),
                "empresa": request.json.get('empresa'),
                "email": request.json.get('email'),
                "password": request.json.get('password'),
            }

            id = request.json.get('id')

            campos_vacios = diccionario_vacio(data_dict)

            if campos_vacios:
                return jsonify({"registrar_agente_status": "existen campos vacios", "campos_vacios": campos_vacios}), 400      

            # Primero, eliminar las solicitudes asociadas al usuario
            try:
                supabase.table('SOLICITUDES').delete().eq('asesor_id', id).execute()
            except Exception as e:
                print(f"Error al eliminar solicitudes asociadas: {e}")
                # Continuamos con la actualización incluso si hay error al eliminar solicitudes

            # Luego actualizamos el usuario
            supabase.table('TABLA_USUARIOS').update(data_dict).eq('id', id).execute()

            return jsonify({"actualizar_agente": "OK"}), 200
        
        except Exception as e:
            print("Ocurrió un error:", e)
            return jsonify({"mensaje": "Ocurrió un error al procesar la solicitud."}), 500
                      
    def get_all_users(self):

        try:
            response = supabase.table("TABLA_USUARIOS").select("*").execute()

            if (len(response.data) == 0):
                return jsonify({"res" : "No hay registros en esta tabla"}), 200

            else:

                return jsonify({
                    "users": response.data
                }), 200

        except Exception as e:
            print("Ocurrió un error:", e)
            return jsonify({"mensaje": "Ocurrió un error al procesar la solicitud."}), 500
        
    def delete_user(self, id):
        try:
            # Primero obtener el email del usuario
            user = supabase.table('TABLA_USUARIOS').select('email').eq('id', id).execute()
            
            if not user.data or len(user.data) == 0:
                return jsonify({"mensaje": "Usuario no encontrado"}), 404
            
            email = user.data[0]['email']
            
            # Eliminar de la tabla personalizada
            supabase.table('TABLA_USUARIOS').delete().eq('id', id).execute()
            
            # Eliminar usuario de Authentication usando service_role
            try:
                # # Crear una nueva instancia de Supabase con service_role
                # admin_supabase = create_client(
                #     supabase_url=os.getenv('SUPABASE_URL'),
                #     supabase_key=os.getenv('SERVICE_ROLE_KEY')
                # )
                
                # Obtener todos los usuarios y filtrar por email
                users = supabase.auth.admin.list_users()
                user_to_delete = None
                
                for user in users:
                    if user.email == email:
                        user_to_delete = user
                        break
                
                if user_to_delete:
                    # Eliminar usuario de Authentication
                    admin_supabase.auth.admin.delete_user(user_to_delete.id)
                    return jsonify({"mensaje": "Usuario eliminado correctamente de la base de datos y Authentication"}), 200
                else:
                    print(f"No se encontró el usuario con email {email} en Authentication")
                    return jsonify({"mensaje": "Usuario eliminado de la base de datos pero no se encontró en Authentication"}), 200
            except Exception as auth_error:
                print("Error al eliminar usuario de Authentication:", auth_error)
                return jsonify({"mensaje": "Usuario eliminado de la base de datos pero no de Authentication. Por favor, verifica los permisos de administrador."}), 500
            
        except Exception as e:
            print("Ocurrió un error:", e)
            return jsonify({"mensaje": "Ocurrió un error al procesar la solicitud."}), 500
