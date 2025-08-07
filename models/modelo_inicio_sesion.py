from librerias import *
from models.generales.generales import *
from models.utils.login.validate_info import *
from models.utils.login.fill_data import *

class modeloIniciarSesion():
    
    def iniciar_sesion(self):
        datos = request.json
        email = datos.get('email')
        password = datos.get('password')
        
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        if 'error' in response:
            return jsonify({"msg": "Credenciales inválidas"}), 401
        
        access_token = response.session.access_token if response.session else None
    
        tabla_usuario = supabase.table('TABLA_USUARIOS')
        try:
            api_response = tabla_usuario.select('*').eq('email', email).execute()
            data_usuario = api_response.data
            print(api_response.data)# Extract data from APIResponse object
        except Exception as e:
            return jsonify({"msg": "Error al obtener los datos del usuario: " + str(e)}), 500
    
        return jsonify({"acceso": "AUTORIZADO", "usuario": data_usuario, "rol": data_usuario[0]['rol'], "access_token": access_token}), 200
    
    def iniciar_sesion_sin_auth(self):
        """
        Inicia sesión validando directamente contra la tabla de usuarios
        sin usar Supabase Auth
        """
        try:
            datos = request.json
            email = datos.get('email')
            password = datos.get('password')

            print(datos)
            
            # Validar que se proporcionen los datos requeridos
            if not email or not password:
                return jsonify({"msg": "Email y password son requeridos"}), 400
            
            # Buscar usuario en la tabla TABLA_USUARIOS
            tabla_usuario = supabase.table('TABLA_USUARIOS')
            api_response = tabla_usuario.select('*').eq('email', email).execute()
            
            if not api_response.data or len(api_response.data) == 0:
                return jsonify({"msg": "Usuario no encontrado"}), 401
            
            data_usuario = api_response.data[0]
            
            # Validar password (comparación directa - en producción debería usar hash)
            if data_usuario['password'] != password:
                return jsonify({"msg": "Credenciales inválidas ALGO MAL NIÑO"}), 401
            
            # Obtener información de la empresa
            empresa_id = data_usuario.get('id_empresa')
            empresa_info = {}
            
            if empresa_id:
                try:
                    empresa_response = supabase.table('EMPRESAS').select('*').eq('id_empresa', empresa_id).execute()
                    if empresa_response.data:
                        empresa_info = empresa_response.data[0]
                except Exception as e:
                    print(f"Error al obtener información de empresa: {e}")

            # Generar access token
            import jwt
            import datetime
            
            token_payload = {
                'user_id': data_usuario['id'],
                'email': email,
                'rol': data_usuario['rol'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }
            
            secret_key = os.getenv('JWT_SECRET_KEY', 'mi_clave_secreta_temporal')

            print(secret_key)
            access_token = jwt.encode(token_payload, secret_key, algorithm='HS256')
            
            # Preparar respuesta con datos del usuario y empresa
            response_data = {
                "acceso": "AUTORIZADO", 
                "access_token": access_token,
                "usuario": [data_usuario],
                "rol": data_usuario['rol']
            }
            
            return jsonify(response_data), 200
            
        except Exception as e:
            print(f"Error en iniciar_sesion_sin_auth: {e}")
            return jsonify({"msg": "Error interno del servidor"}), 500
    