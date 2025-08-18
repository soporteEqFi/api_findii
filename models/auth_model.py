from __future__ import annotations
from typing import Dict, Optional
import bcrypt
from data.supabase_conn import supabase

def _get_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp
class AuthModel:
    """Modelo para autenticación de usuarios."""

    def __init__(self):
        self.usuarios_table = "usuarios"
        self.roles_table = "rol"

    def authenticate_user(self, correo: str, contraseña: str) -> Optional[Dict]:
        """Autentica usuario por correo y contraseña."""

        resp = (
            supabase.table(self.usuarios_table)
            .select("id, nombre, cedula, correo, contraseña, rol, created_at")
            .eq("correo", correo)
            .execute()
        )

        data = _get_data(resp)

        if not data or len(data) == 0:
            return None

        usuario = data[0]

        password_hash = usuario.get("contraseña", "")

        password_valid = self._verify_password(contraseña, password_hash)

        if not password_valid:
            return None

        rol_info = self._get_rol_info(usuario.get("rol"))

        return {
            "id": usuario["id"],
            "nombre": usuario["nombre"],
            "email": usuario["correo"],
            "cedula": usuario["cedula"],
            "rol": rol_info.get("nombre", usuario.get("rol")),
            "rol_id": usuario.get("rol"),
            "created_at": usuario.get("created_at")
        }

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica contraseña usando bcrypt."""
        try:
            if not hashed_password.startswith('$2b$'):
                result = plain_password == hashed_password
                return result

            result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
            return result
        except Exception as e:
            result = plain_password == hashed_password
            return result

    def _get_rol_info(self, rol_id) -> Dict:
        """Obtiene información del rol."""
        if not rol_id:
            return {"id": None, "nombre": "usuario"}

        try:
            resp = supabase.table(self.roles_table).select("id, nombre, descripcion").eq("id", rol_id).execute()

            data = _get_data(resp)
            if data and len(data) > 0:
                return data[0]
        except Exception:
            pass

        return {"id": rol_id, "nombre": str(rol_id)}

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Obtiene usuario por ID (para validar tokens)."""
        resp = supabase.table(self.usuarios_table).select("id, nombre, cedula, correo, rol, created_at").eq("id", user_id).execute()

        data = _get_data(resp)
        if not data or len(data) == 0:
            return None

        usuario = data[0]
        rol_info = self._get_rol_info(usuario.get("rol"))

        return {
            "id": usuario["id"],
            "nombre": usuario["nombre"],
            "email": usuario["correo"],
            "cedula": usuario["cedula"],
            "rol": rol_info.get("nombre", usuario.get("rol")),
            "rol_id": usuario.get("rol"),
            "created_at": usuario.get("created_at")
        }

    def hash_password(self, password: str) -> str:
        """Hashea una contraseña (para crear usuarios)."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
