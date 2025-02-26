import re
from models.generales.generales import *

def validar_email(email):
    """Valida el formato del email usando una expresión regular"""
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, email) is not None

def usuario_existe(email):
    """Verifica si un usuario ya existe en Supabase Auth"""
    try:
        response = supabase.auth.admin.list_users()
        usuarios = response.data.users
        return any(user.email == email for user in usuarios)
    except Exception:
        return False