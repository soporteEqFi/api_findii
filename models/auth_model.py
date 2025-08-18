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
        print(f"=== AUTH MODEL DEBUG ===")
        print(f"Buscando usuario con correo: {correo}")

        # Buscar usuario por correo
        resp = (
            supabase.table(self.usuarios_table)
            .select("id, nombre, cedula, correo, contraseña, rol, created_at")
            .eq("correo", correo)
            .execute()
        )

        data = _get_data(resp)
        print(f"Respuesta de Supabase: {data}")

        if not data or len(data) == 0:
            print("ERROR: Usuario no encontrado en BD")
            return None

        usuario = data[0]
        print(f"Usuario encontrado: {usuario.get('nombre')} - {usuario.get('correo')}")

        # Verificar contraseña
        password_hash = usuario.get("contraseña", "")
        print(f"Hash en BD: {password_hash[:20]}..." if password_hash else "Sin contraseña en BD")

        password_valid = self._verify_password(contraseña, password_hash)
        print(f"Contraseña válida: {password_valid}")

        if not password_valid:
            print("ERROR: Contraseña incorrecta")
            return None

        # Obtener información del rol
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
        print(f"=== VERIFY PASSWORD ===")
        print(f"Password ingresada: {'***' if plain_password else 'VACÍA'}")
        print(f"Hash en BD: {hashed_password[:20]}..." if hashed_password else "Hash VACÍO")

        try:
            # Si la contraseña en BD no está hasheada (texto plano), comparar directamente
            if not hashed_password.startswith('$2b$'):
                print("Comparando contraseñas en texto plano")
                result = plain_password == hashed_password
                print(f"Resultado comparación plana: {result}")
                return result

            # Si está hasheada, usar bcrypt
            print("Usando bcrypt para verificar")
            result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
            print(f"Resultado bcrypt: {result}")
            return result
        except Exception as e:
            print(f"Error en verificación: {e}")
            # Fallback a comparación directa si bcrypt falla
            result = plain_password == hashed_password
            print(f"Resultado fallback: {result}")
            return result

    def _get_rol_info(self, rol_id) -> Dict:
        """Obtiene información del rol."""
        if not rol_id:
            return {"id": None, "nombre": "usuario"}

        try:
            resp = (
                supabase.table(self.roles_table)
                .select("id, nombre, descripcion")
                .eq("id", rol_id)
                .execute()
            )

            data = _get_data(resp)
            if data and len(data) > 0:
                return data[0]
        except Exception:
            pass

        return {"id": rol_id, "nombre": str(rol_id)}

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Obtiene usuario por ID (para validar tokens)."""
        resp = (
            supabase.table(self.usuarios_table)
            .select("id, nombre, cedula, correo, rol, created_at")
            .eq("id", user_id)
            .execute()
        )

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
