# from modelo.supabase.keys import *
from librerias import *
from dotenv import load_dotenv
import os
load_dotenv()   

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

tabla_usuarios = 'TABLA_USUARIOS'