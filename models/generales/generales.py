# from modelo.supabase.keys import *
from librerias import *
from dotenv import load_dotenv
import os

load_dotenv(os.path.expanduser("~/api_findii/.env"))


supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

tabla_usuarios = 'TABLA_USUARIOS'
tabla_solicitantes = 'SOLICITANTES'
def diccionario_vacio(data_dict):
    campos_vacios = [key for key, value in data_dict.items() if value is None or value == ""]
    if campos_vacios:
        return campos_vacios
    else:
        return False
