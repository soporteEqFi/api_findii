from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


def check_supabase_health():
    """
    Verifica conectividad con Supabase.
    Returns:
        (ok: bool, error: str | None) - True si está disponible, False + mensaje si falla.
    """
    try:
        # Query mínima para validar conexión
        supabase.table("empresas").select("id").limit(1).execute()
        return True, None
    except Exception as e:
        return False, str(e)