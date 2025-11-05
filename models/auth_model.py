from __future__ import annotations
from typing import Dict, Optional
from datetime import datetime
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
        """Autentica usuario por correo y contraseña.

        También valida si el usuario es temporal y si su fecha de expiración ha pasado.
        Si es usuario temporal y está expirado, marca usuario_activo como False y rechaza el login.

        Returns:
            Dict con datos del usuario si autenticación exitosa
            None si credenciales inválidas o usuario temporal expirado/inactivo
        """
        try:
            print(f"\n[authenticate_user] 🔍 Iniciando autenticación para correo: {correo}")

            resp = (
                supabase.table(self.usuarios_table)
                .select("id, nombre, cedula, correo, contraseña, rol, info_extra, empresa_id, created_at")
                .eq("correo", correo)
                .execute()
            )

            print(f"[authenticate_user] ✅ Consulta a BD ejecutada")

            data = _get_data(resp)
            print(f"[authenticate_user] 📊 Datos obtenidos: {len(data) if data else 0} registro(s)")

            if not data or len(data) == 0:
                print(f"[authenticate_user] ❌ Usuario no encontrado en BD")
                return None

            usuario = data[0]
            print(f"[authenticate_user] 👤 Usuario encontrado - ID: {usuario.get('id')}, Nombre: {usuario.get('nombre')}")

            password_hash = usuario.get("contraseña", "")
            print(f"[authenticate_user] 🔐 Hash de contraseña obtenido: {'Sí' if password_hash else 'No'}")

            password_valid = self._verify_password(contraseña, password_hash)
            print(f"[authenticate_user] 🔐 Validación de contraseña: {'✅ Válida' if password_valid else '❌ Inválida'}")

            if not password_valid:
                print(f"[authenticate_user] ❌ Contraseña inválida, rechazando login")
                return None

            # Validar si es usuario temporal
            info_extra = usuario.get("info_extra", {})
            print(f"[authenticate_user] 📋 Info_extra tipo: {type(info_extra)}, valor: {info_extra}")

            # Manejar caso cuando info_extra es None
            if info_extra is None:
                print(f"[authenticate_user] 📋 Info_extra es None, convirtiendo a dict vacío")
                info_extra = {}
            elif isinstance(info_extra, str):
                import json
                try:
                    info_extra = json.loads(info_extra)
                    print(f"[authenticate_user] 📋 Info_extra parseado de JSON a dict")
                except json.JSONDecodeError as e:
                    print(f"[authenticate_user] ⚠️ Error parseando JSON de info_extra: {e}")
                    info_extra = {}

            print(f"[authenticate_user] 📋 Info_extra final: {info_extra}")

            # Verificar si es usuario temporal
            if "usuario_activo" in info_extra or "tiempo_conexion" in info_extra:
                print(f"[authenticate_user] ⏰ Usuario TEMPORAL detectado")
                # Es usuario temporal
                usuario_activo = info_extra.get("usuario_activo", True)
                tiempo_conexion_str = info_extra.get("tiempo_conexion", "")

                print(f"[authenticate_user] ⏰ usuario_activo: {usuario_activo}, tiempo_conexion: {tiempo_conexion_str}")

                # Si está inactivo, rechazar login
                if usuario_activo is False:
                    print(f"[authenticate_user] ❌ Usuario temporal INACTIVO, rechazando login")
                    return None

                # Validar fecha de expiración
                if tiempo_conexion_str:
                    print(f"[authenticate_user] ⏰ Validando fecha de expiración: {tiempo_conexion_str}")
                    if self._validar_fecha_expiracion(tiempo_conexion_str, usuario["id"]):
                        print(f"[authenticate_user] ❌ Fecha de expiración PASADA, marcando como inactivo")
                        # La fecha expiró, marcar como inactivo y rechazar
                        self._marcar_usuario_inactivo(usuario["id"])
                        return None
                    else:
                        print(f"[authenticate_user] ✅ Fecha de expiración VÁLIDA")
                # Fecha aún válida, continuar con login
            else:
                print(f"[authenticate_user] ✅ Usuario PERMANENTE (no temporal)")

            print(f"[authenticate_user] 🔍 Obteniendo información del rol...")
            rol_info = self._get_rol_info(usuario.get("rol"))
            print(f"[authenticate_user] 📋 Rol info: {rol_info}")

            resultado = {
                "id": usuario["id"],
                "nombre": usuario["nombre"],
                "email": usuario["correo"],
                "cedula": usuario["cedula"],
                "rol": rol_info.get("nombre", usuario.get("rol")),
                "rol_id": usuario.get("rol"),
                "empresa_id": usuario.get("empresa_id"),
                "created_at": usuario.get("created_at"),
                "info_extra": usuario.get("info_extra")
            }

            print(f"[authenticate_user] ✅ Autenticación exitosa - Retornando datos del usuario")
            return resultado

        except Exception as e:
            print(f"[authenticate_user] ❌ ERROR EXCEPCIÓN: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"[authenticate_user] 📋 Traceback completo:")
            traceback.print_exc()
            return None

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
        resp = supabase.table(self.usuarios_table).select("id, nombre, cedula, correo, rol, info_extra, empresa_id, created_at").eq("id", user_id).execute()

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
            "empresa_id": usuario.get("empresa_id"),
            "created_at": usuario.get("created_at"),
            "info_extra": usuario.get("info_extra")
        }

    def get_empresa_info(self, empresa_id: int) -> Optional[Dict]:
        """Obtiene información de la empresa."""
        try:
            resp = supabase.table("empresas").select("id, nombre, imagen, created_at").eq("id", empresa_id).execute()

            data = _get_data(resp)
            if not data or len(data) == 0:
                return None

            return data[0]
        except Exception as e:
            print(f"Error al obtener información de empresa: {e}")
            return None

    def _validar_fecha_expiracion(self, tiempo_conexion_str: str, usuario_id: int) -> bool:
        """
        Valida si la fecha y hora de tiempo_conexion ya pasó.

        Args:
            tiempo_conexion_str: Fecha y hora en formato "DD/MM/YYYY HH:MM" o "DD/MM/YYYY HH:MM:SS"
                                También acepta solo fecha "DD/MM/YYYY" (se asume hora 23:59:59)
            usuario_id: ID del usuario (para logging)

        Returns:
            True si la fecha y hora ya expiró, False si aún es válida
        """
        try:
            # Intentar parsear con diferentes formatos
            fecha_expira = None

            # Formato 1: DD/MM/YYYY HH:MM:SS
            try:
                fecha_expira = datetime.strptime(tiempo_conexion_str, "%d/%m/%Y %H:%M:%S")
                print(f"[_validar_fecha_expiracion] ✅ Fecha parseada con formato 'DD/MM/YYYY HH:MM:SS': {fecha_expira}")
            except ValueError:
                pass

            # Formato 2: DD/MM/YYYY HH:MM
            if fecha_expira is None:
                try:
                    fecha_expira = datetime.strptime(tiempo_conexion_str, "%d/%m/%Y %H:%M")
                    print(f"[_validar_fecha_expiracion] ✅ Fecha parseada con formato 'DD/MM/YYYY HH:MM': {fecha_expira}")
                except ValueError:
                    pass

            # Formato 3: DD/MM/YYYY (solo fecha, asumir fin del día 23:59:59)
            if fecha_expira is None:
                try:
                    fecha_base = datetime.strptime(tiempo_conexion_str, "%d/%m/%Y")
                    fecha_expira = fecha_base.replace(hour=23, minute=59, second=59, microsecond=0)
                    print(f"[_validar_fecha_expiracion] ✅ Fecha parseada con formato 'DD/MM/YYYY' (asumiendo 23:59:59): {fecha_expira}")
                except ValueError:
                    pass

            # Si no se pudo parsear con ningún formato, error
            if fecha_expira is None:
                raise ValueError(f"No se pudo parsear la fecha con formato reconocido: {tiempo_conexion_str}")

            # Obtener fecha y hora actual
            fecha_actual = datetime.now()
            print(f"[_validar_fecha_expiracion] 📅 Fecha actual: {fecha_actual}")
            print(f"[_validar_fecha_expiracion] 📅 Fecha expiración: {fecha_expira}")
            print(f"[_validar_fecha_expiracion] ⏰ Diferencia: {fecha_expira - fecha_actual}")

            # Comparar: si fecha_expira < fecha_actual, significa que expiró
            expirado = fecha_expira < fecha_actual
            print(f"[_validar_fecha_expiracion] {'❌ EXPIRADO' if expirado else '✅ VÁLIDO'}")

            return expirado

        except ValueError as e:
            # Si hay error parseando la fecha, loguear pero permitir login
            print(f"[_validar_fecha_expiracion] ⚠️ Error parseando fecha de expiración para usuario {usuario_id}: {e}")
            return False
        except Exception as e:
            print(f"[_validar_fecha_expiracion] ⚠️ Error validando fecha de expiración para usuario {usuario_id}: {e}")
            return False

    def _marcar_usuario_inactivo(self, usuario_id: int):
        """
        Marca un usuario temporal como inactivo en la base de datos.

        Args:
            usuario_id: ID del usuario a marcar como inactivo
        """
        try:
            # Obtener info_extra actual
            resp = supabase.table(self.usuarios_table).select("info_extra").eq("id", usuario_id).execute()
            data = _get_data(resp)

            if not data or len(data) == 0:
                return

            info_extra = data[0].get("info_extra", {})
            if isinstance(info_extra, str):
                import json
                try:
                    info_extra = json.loads(info_extra)
                except json.JSONDecodeError:
                    info_extra = {}

            # Actualizar usuario_activo a False
            info_extra["usuario_activo"] = False

            # Guardar en BD
            supabase.table(self.usuarios_table).update({"info_extra": info_extra}).eq("id", usuario_id).execute()

        except Exception as e:
            print(f"Error marcando usuario {usuario_id} como inactivo: {e}")

    def _verificar_usuario_temporal(self, correo: str) -> Optional[Dict]:
        """
        Verifica si un usuario existe y es temporal, y si está inactivo o expirado.
        Este método se usa para dar mensajes de error más específicos.

        Args:
            correo: Correo del usuario a verificar

        Returns:
            Dict con información del estado del usuario temporal, o None si no es temporal o no existe
        """
        try:
            resp = (
                supabase.table(self.usuarios_table)
                .select("id, info_extra")
                .eq("correo", correo)
                .execute()
            )

            data = _get_data(resp)
            if not data or len(data) == 0:
                return None

            usuario = data[0]
            info_extra = usuario.get("info_extra", {})

            # Manejar caso cuando info_extra es None
            if info_extra is None:
                info_extra = {}
            elif isinstance(info_extra, str):
                import json
                try:
                    info_extra = json.loads(info_extra)
                except json.JSONDecodeError:
                    info_extra = {}

            # Verificar si es usuario temporal
            if "usuario_activo" not in info_extra and "tiempo_conexion" not in info_extra:
                return None  # No es usuario temporal

            # Es usuario temporal
            usuario_activo = info_extra.get("usuario_activo", True)
            tiempo_conexion_str = info_extra.get("tiempo_conexion", "")

            resultado = {}

            # Verificar si está inactivo
            if usuario_activo is False:
                resultado["inactivo"] = True
                resultado["fecha_expiracion"] = tiempo_conexion_str
                return resultado

            # Verificar si está expirado
            if tiempo_conexion_str:
                if self._validar_fecha_expiracion(tiempo_conexion_str, usuario["id"]):
                    resultado["expirado"] = True
                    resultado["fecha_expiracion"] = tiempo_conexion_str
                    return resultado

            return None  # Usuario temporal pero activo y no expirado

        except Exception as e:
            print(f"Error verificando usuario temporal: {e}")
            return None

    def hash_password(self, password: str) -> str:
        """Hashea una contraseña (para crear usuarios)."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
