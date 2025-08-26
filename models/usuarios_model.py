from __future__ import annotations
from typing import Dict, List, Optional
from data.supabase_conn import supabase

def _get_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp

class UsuariosModel:
    """Modelo para gestión de usuarios."""

    def __init__(self):
        self.usuarios_table = "usuarios"

    def list_by_empresa(self, empresa_id: int) -> List[Dict]:
        """Lista todos los usuarios de una empresa."""
        try:
            # Obtener usuarios que pertenecen a la empresa usando el campo empresa_id
            resp = supabase.table(self.usuarios_table).select(
                "id, nombre, cedula, correo, rol, info_extra, empresa_id, created_at"
            ).eq("empresa_id", empresa_id).execute()

            data = _get_data(resp)
            if not data:
                return []

            # Procesar usuarios
            usuarios_empresa = []
            for usuario in data:
                info_extra = usuario.get("info_extra", {})
                if isinstance(info_extra, str):
                    import json
                    try:
                        info_extra = json.loads(info_extra)
                    except json.JSONDecodeError:
                        info_extra = {}

                usuarios_empresa.append({
                    "id": usuario["id"],
                    "nombre": usuario["nombre"],
                    "cedula": usuario["cedula"],
                    "correo": usuario["correo"],
                    "rol": usuario["rol"],
                    "empresa_id": usuario["empresa_id"],
                    "info_extra": info_extra,
                    "created_at": usuario["created_at"]
                })

            return usuarios_empresa

        except Exception as e:
            print(f"Error al listar usuarios por empresa: {e}")
            return []

    def get_by_id(self, user_id: int, empresa_id: int) -> Optional[Dict]:
        """Obtiene un usuario específico por ID, verificando que pertenezca a la empresa."""
        try:
            resp = supabase.table(self.usuarios_table).select(
                "id, nombre, cedula, correo, rol, info_extra, empresa_id, created_at"
            ).eq("id", user_id).eq("empresa_id", empresa_id).execute()

            data = _get_data(resp)
            if not data or len(data) == 0:
                return None

            usuario = data[0]
            info_extra = usuario.get("info_extra", {})

            if isinstance(info_extra, str):
                import json
                try:
                    info_extra = json.loads(info_extra)
                except json.JSONDecodeError:
                    info_extra = {}

            return {
                "id": usuario["id"],
                "nombre": usuario["nombre"],
                "cedula": usuario["cedula"],
                "correo": usuario["correo"],
                "rol": usuario["rol"],
                "empresa_id": usuario["empresa_id"],
                "info_extra": info_extra,
                "created_at": usuario["created_at"]
            }

        except Exception as e:
            print(f"Error al obtener usuario por ID: {e}")
            return None

    def update(self, user_id: int, empresa_id: int, **kwargs) -> Optional[Dict]:
        """Actualiza un usuario específico, verificando que pertenezca a la empresa."""
        try:
            # Primero verificar que el usuario existe y pertenece a la empresa
            usuario_actual = self.get_by_id(user_id, empresa_id)
            if not usuario_actual:
                return None

            # Preparar datos para actualizar (excluir campos sensibles)
            datos_actualizar = {}
            campos_permitidos = ["nombre", "cedula", "correo", "rol", "info_extra"]

            for campo in campos_permitidos:
                if campo in kwargs:
                    datos_actualizar[campo] = kwargs[campo]

            if not datos_actualizar:
                return usuario_actual  # No hay cambios

            # Actualizar en la base de datos
            resp = supabase.table(self.usuarios_table).update(datos_actualizar).eq("id", user_id).execute()

            data = _get_data(resp)
            if not data or len(data) == 0:
                return None

            usuario_actualizado = data[0]
            info_extra = usuario_actualizado.get("info_extra", {})

            if isinstance(info_extra, str):
                import json
                try:
                    info_extra = json.loads(info_extra)
                except json.JSONDecodeError:
                    info_extra = {}

            return {
                "id": usuario_actualizado["id"],
                "nombre": usuario_actualizado["nombre"],
                "cedula": usuario_actualizado["cedula"],
                "correo": usuario_actualizado["correo"],
                "rol": usuario_actualizado["rol"],
                "empresa_id": usuario_actualizado["empresa_id"],
                "info_extra": info_extra,
                "created_at": usuario_actualizado["created_at"]
            }

        except Exception as e:
            print(f"Error al actualizar usuario: {e}")
            return None

    def create(self, empresa_id: int, **kwargs) -> Optional[Dict]:
        """Crea un nuevo usuario para una empresa."""
        try:
            # Validar campos requeridos
            campos_requeridos = ["nombre", "cedula", "correo", "contraseña", "rol"]
            for campo in campos_requeridos:
                if campo not in kwargs:
                    print(f"Campo requerido faltante: {campo}")
                    return None

            # Preparar datos para crear
            datos_usuario = {
                "nombre": kwargs["nombre"],
                "cedula": kwargs["cedula"],
                "correo": kwargs["correo"],
                "contraseña": kwargs["contraseña"],
                "rol": kwargs["rol"],
                "empresa_id": empresa_id,
                "info_extra": kwargs.get("info_extra", {})
            }

            # Crear en la base de datos
            resp = supabase.table(self.usuarios_table).insert(datos_usuario).execute()

            data = _get_data(resp)
            if not data or len(data) == 0:
                return None

            usuario_creado = data[0]
            info_extra = usuario_creado.get("info_extra", {})

            if isinstance(info_extra, str):
                import json
                try:
                    info_extra = json.loads(info_extra)
                except json.JSONDecodeError:
                    info_extra = {}

            return {
                "id": usuario_creado["id"],
                "nombre": usuario_creado["nombre"],
                "cedula": usuario_creado["cedula"],
                "correo": usuario_creado["correo"],
                "rol": usuario_creado["rol"],
                "empresa_id": usuario_creado["empresa_id"],
                "info_extra": info_extra,
                "created_at": usuario_creado["created_at"]
            }

        except Exception as e:
            print(f"Error al crear usuario: {e}")
            return None

    def delete(self, user_id: int, empresa_id: int) -> bool:
        """Elimina un usuario específico, verificando que pertenezca a la empresa."""
        try:
            # Primero verificar que el usuario existe y pertenece a la empresa
            usuario_actual = self.get_by_id(user_id, empresa_id)
            if not usuario_actual:
                return False

            # Eliminar de la base de datos
            resp = supabase.table(self.usuarios_table).delete().eq("id", user_id).execute()

            # Verificar que se eliminó correctamente
            data = _get_data(resp)
            return data is not None and len(data) > 0

        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            return False
