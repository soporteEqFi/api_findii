from librerias import *
import time
from model.generales.generales import *
from model.utils.login.validate_info import *
from model.utils.login.fill_data import *

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
            response = supabase.auth.sign_up({"email": email, "password": password})

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
    

    def get_agent_info(self, cedula):
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                if cedula is None or cedula == "":
                    return jsonify({"error" : "campo cedula vacío"}), 401

                response = supabase.table("ASESORES").select('*').eq('cedula', cedula).execute()

                response_data = response.data

                return jsonify({
                    "id": response_data[0]['id'],
                    "cedula": response_data[0]['cedula'],
                    "nombre": response_data[0]['nombre'],
                    "rol": response_data[0]['rol'],
                    "correo": response_data[0]['correo'],
                    "apellido": response_data[0]['apellido']
                    })

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    print("Ocurrió un error:", e)
                    return jsonify({"mensaje": "Ocurrió un error al procesar la solicitud."}), 500
                
        
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
                      


