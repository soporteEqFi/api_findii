from librerias import *
from model.generales.generales import *
import re

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
    
        return jsonify({"acceso": "AUTORIZADO", "usuario": data_usuario, "access_token": access_token}), 200
    
    def crear_usuario(self):
        datos = request.json
        email = datos.get('email', '').strip()
        password = datos.get('password', '').strip()
        nombre = datos.get('nombre', '').strip()
        rol = datos.get('rol', '').strip()

        # 1. Validar email
        if not self.validar_email(email):
            return jsonify({"msg": "El formato del email es inválido"}), 400

        # 2. Verificar si el usuario ya existe en Supabase Auth
        if self.usuario_existe(email):
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
                "nombre": nombre,
                "rol": rol,
                "password": password
            }).execute()

            # ✅ Verificar si la inserción falló
            if hasattr(api_response, "error") and api_response.error:
                print(f"Error al insertar en TABLA_USUARIOS: {api_response.error}")
                return jsonify({"msg": "Error al guardar usuario en la base de datos: " + str(api_response.error)}), 500

            print(f"Usuario insertado en TABLA_USUARIOS: {api_response.data}")

        except Exception as e:
            return jsonify({"msg": "Error inesperado: " + str(e)}), 500

        return jsonify({"msg": "Usuario creado exitosamente", "user_id": user_id}), 201

    def validar_email(self, email):
        """Valida el formato del email usando una expresión regular"""
        patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(patron, email) is not None

    def usuario_existe(self, email):
        """Verifica si un usuario ya existe en Supabase Auth"""
        try:
            response = supabase.auth.admin.list_users()
            usuarios = response.data.users
            return any(user.email == email for user in usuarios)
        except Exception:
            return False