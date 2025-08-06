from flask import request, jsonify
from models.generales.generales import supabase
from functools import wraps

def get_user_empresa_id(cedula):
    """
    Obtiene el ID de la empresa del usuario por su cédula
    """
    try:
        response = supabase.table("TABLA_USUARIOS").select('id_empresa').eq('cedula', cedula).execute()
        if response.data:
            return response.data[0]['id_empresa']
        return None
    except Exception as e:
        print(f"Error al obtener empresa del usuario: {e}")
        return None

def require_empresa_auth(f):
    """
    Decorador para validar que el usuario solo acceda a datos de su empresa
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Obtener cédula del usuario desde el token o request
            # Por ahora asumimos que viene en el request
            cedula = request.json.get('cedula') if request.json else None
            
            if not cedula:
                return jsonify({"error": "Se requiere identificación del usuario"}), 401
            
            # Obtener empresa del usuario
            empresa_id = get_user_empresa_id(cedula)
            if not empresa_id:
                return jsonify({"error": "Usuario no encontrado o sin empresa asignada"}), 404
            
            # Agregar empresa_id al request para uso posterior
            request.empresa_id = empresa_id
            request.cedula_usuario = cedula
            
            return f(*args, **kwargs)
            
        except Exception as e:
            print(f"Error en middleware de empresa: {e}")
            return jsonify({"error": "Error de autenticación por empresa"}), 500
    
    return decorated_function

def filter_by_empresa(query, empresa_id):
    """
    Filtra una query por empresa_id
    """
    return query.eq('id_empresa', empresa_id)

def get_empresa_filtered_data(table_name, empresa_id, additional_filters=None):
    """
    Obtiene datos de una tabla filtrados por empresa
    """
    try:
        query = supabase.table(table_name).select('*')
        
        # Aplicar filtro por empresa si la tabla tiene ese campo
        if hasattr(query, 'eq'):
            query = query.eq('id_empresa', empresa_id)
        
        # Aplicar filtros adicionales si se proporcionan
        if additional_filters:
            for field, value in additional_filters.items():
                query = query.eq(field, value)
        
        result = query.execute()
        return result.data
        
    except Exception as e:
        print(f"Error al obtener datos filtrados por empresa: {e}")
        return [] 