from __future__ import annotations
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from data.supabase_conn import supabase

def _get_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp

class NotificacionesModel:
    """Modelo para gestión de notificaciones."""

    def __init__(self):
        self.notificaciones_table = "notificaciones"
        self.configuraciones_table = "configuraciones"

    def get_configuracion_notificaciones(self, empresa_id: int) -> Optional[Dict]:
        """Obtiene la configuración de notificaciones para una empresa."""
        try:
            resp = supabase.table(self.configuraciones_table).select("*").eq("empresa_id", empresa_id).eq("categoria", "notificaciones_recordatorio").eq("activo", True).execute()

            data = _get_data(resp)
            if not data or len(data) == 0:
                return None

            return data[0]
        except Exception as e:
            print(f"Error al obtener configuración de notificaciones: {e}")
            return None

    def validar_notificacion(self, empresa_id: int, datos: Dict) -> tuple[bool, str]:
        """Valida una notificación contra la configuración de la empresa."""
        try:
            config = self.get_configuracion_notificaciones(empresa_id)
            if not config:
                return False, "No se encontró configuración de notificaciones para la empresa"

            config_data = config.get("configuracion", {})

            # Validar tipo
            tipo = datos.get("tipo")
            tipos_disponibles = config_data.get("tipos_disponibles", [])
            if tipo not in tipos_disponibles:
                return False, f"Tipo de notificación '{tipo}' no está configurado. Opciones: {tipos_disponibles}"

            # Validar estado
            estado = datos.get("estado", "pendiente")
            estados_disponibles = config_data.get("estados_disponibles", [])
            if estado not in estados_disponibles:
                return False, f"Estado '{estado}' no es válido. Opciones: {estados_disponibles}"

            # Validar prioridad
            prioridad = datos.get("prioridad", "normal")
            prioridades_disponibles = config_data.get("prioridades_disponibles", [])
            if prioridad not in prioridades_disponibles:
                return False, f"Prioridad '{prioridad}' no es válida. Opciones: {prioridades_disponibles}"

            # Validar fechas
            fecha_recordatorio = datos.get("fecha_recordatorio")
            fecha_vencimiento = datos.get("fecha_vencimiento")

            if fecha_recordatorio and fecha_vencimiento:
                try:
                    fecha_rec = datetime.fromisoformat(fecha_recordatorio.replace('Z', '+00:00'))
                    fecha_ven = datetime.fromisoformat(fecha_vencimiento.replace('Z', '+00:00'))

                    if fecha_ven <= fecha_rec:
                        return False, "fecha_vencimiento debe ser posterior a fecha_recordatorio"
                except ValueError:
                    return False, "Formato de fecha inválido"

            # Validar metadata (campos opcionales)
            metadata = datos.get("metadata", {})
            if metadata:
                # Validar estado_actual si existe
                estado_actual = metadata.get("estado_actual")
                if estado_actual:
                    estados_actuales = config_data.get("estados_actuales_disponibles", [])
                    if estados_actuales and estado_actual not in estados_actuales:
                        return False, f"Estado actual '{estado_actual}' no es válido. Opciones: {estados_actuales}"

                # Validar accion_requerida si existe
                accion_requerida = metadata.get("accion_requerida")
                if accion_requerida:
                    acciones_disponibles = config_data.get("acciones_requeridas_disponibles", [])
                    if acciones_disponibles and accion_requerida not in acciones_disponibles:
                        return False, f"Acción requerida '{accion_requerida}' no es válida. Opciones: {acciones_disponibles}"

            return True, "Validación exitosa"

        except Exception as e:
            return False, f"Error en validación: {str(e)}"

    def create(self, empresa_id: int, **kwargs) -> Optional[Dict]:
        """Crea una nueva notificación."""
        try:
            # Validar datos
            es_valida, mensaje = self.validar_notificacion(empresa_id, kwargs)
            if not es_valida:
                print(f"Error de validación: {mensaje}")
                return None

            # Preparar datos
            datos_notificacion = {
                "empresa_id": empresa_id,
                "tipo": kwargs["tipo"],
                "titulo": kwargs["titulo"],
                "mensaje": kwargs["mensaje"],
                "fecha_recordatorio": kwargs["fecha_recordatorio"],
                "fecha_vencimiento": kwargs.get("fecha_vencimiento"),
                "estado": kwargs.get("estado", "pendiente"),
                "prioridad": kwargs.get("prioridad", "normal"),
                "solicitud_id": kwargs.get("solicitud_id"),
                "usuario_id": kwargs.get("usuario_id"),
                "metadata": kwargs.get("metadata", {})
            }

            # Crear en BD
            resp = supabase.table(self.notificaciones_table).insert(datos_notificacion).execute()

            data = _get_data(resp)
            if not data or len(data) == 0:
                return None

            return data[0]

        except Exception as e:
            print(f"Error al crear notificación: {e}")
            return None

    def list(self, empresa_id: int, usuario_info: dict = None, **filtros) -> List[Dict]:
        """Lista notificaciones con filtros opcionales y permisos por rol."""
        try:
            print(f"\n🔍 [NotificacionesModel.list] empresa_id: {empresa_id}")
            print(f"👤 [NotificacionesModel.list] usuario_info: {usuario_info}")

            query = supabase.table(self.notificaciones_table).select("*").eq("empresa_id", empresa_id)

            # Aplicar filtros de rol
            query = self._aplicar_filtros_rol(query, usuario_info, empresa_id)

            # Aplicar filtros adicionales
            if filtros.get("tipo"):
                query = query.eq("tipo", filtros["tipo"])
            if filtros.get("estado"):
                query = query.eq("estado", filtros["estado"])
            if filtros.get("solicitud_id"):
                query = query.eq("solicitud_id", filtros["solicitud_id"])
            if filtros.get("usuario_id"):
                query = query.eq("usuario_id", filtros["usuario_id"])
            if filtros.get("prioridad"):
                query = query.eq("prioridad", filtros["prioridad"])

            # Ordenar por fecha de recordatorio
            query = query.order("fecha_recordatorio", desc=False)

            resp = query.execute()
            notificaciones = _get_data(resp) or []
            return notificaciones

        except Exception as e:
            print(f"Error al listar notificaciones: {e}")
            return []

    def get_by_id(self, notificacion_id: int, empresa_id: int) -> Optional[Dict]:
        """Obtiene una notificación específica."""
        try:
            resp = supabase.table(self.notificaciones_table).select("*").eq("id", notificacion_id).eq("empresa_id", empresa_id).execute()

            data = _get_data(resp)
            if not data or len(data) == 0:
                return None

            return data[0]

        except Exception as e:
            print(f"Error al obtener notificación: {e}")
            return None

    def update(self, notificacion_id: int, empresa_id: int, **kwargs) -> Optional[Dict]:
        """Actualiza una notificación."""
        try:
            # Verificar que existe
            notificacion_actual = self.get_by_id(notificacion_id, empresa_id)
            if not notificacion_actual:
                return None

            # Validar datos si se están actualizando campos críticos
            if "tipo" in kwargs or "metadata" in kwargs:
                datos_completos = {**notificacion_actual, **kwargs}
                es_valida, mensaje = self.validar_notificacion(empresa_id, datos_completos)
                if not es_valida:
                    print(f"Error de validación en actualización: {mensaje}")
                    return None

            # Actualizar
            resp = supabase.table(self.notificaciones_table).update(kwargs).eq("id", notificacion_id).execute()

            data = _get_data(resp)
            if not data or len(data) == 0:
                return None

            return data[0]

        except Exception as e:
            print(f"Error al actualizar notificación: {e}")
            return None

    def delete(self, notificacion_id: int, empresa_id: int) -> bool:
        """Elimina una notificación."""
        try:
            resp = supabase.table(self.notificaciones_table).delete().eq("id", notificacion_id).eq("empresa_id", empresa_id).execute()

            data = _get_data(resp)
            return data is not None and len(data) > 0

        except Exception as e:
            print(f"Error al eliminar notificación: {e}")
            return False

    def marcar_como_leida(self, notificacion_id: int, empresa_id: int) -> Optional[Dict]:
        """Marca una notificación como leída."""
        return self.update(notificacion_id, empresa_id, estado="leida")

    def obtener_pendientes(self, empresa_id: int, usuario_info: dict = None, usuario_id: Optional[int] = None) -> List[Dict]:
        """Obtiene notificaciones pendientes con filtros por rol."""
        filtros = {"estado": "pendiente"}
        if usuario_id:
            filtros["usuario_id"] = usuario_id

        # Manejar compatibilidad con llamadas sin usuario_info
        if usuario_info is not None:
            return self.list(empresa_id, usuario_info, **filtros)
        else:
            # Llamada sin filtros de rol (comportamiento anterior)
            return self.list(empresa_id, **filtros)

    def _aplicar_filtros_rol(self, query, usuario_info: dict = None, empresa_id: int = None):
        """Aplica filtros de rol a una query de notificaciones"""
        if not usuario_info:
            return query

        rol = usuario_info.get("rol")
        user_id = usuario_info.get("id")

        if rol == "banco":
            # Usuario banco: solo ve notificaciones de su banco y ciudad
            banco_nombre = usuario_info.get("banco_nombre")
            ciudad = usuario_info.get("ciudad")

            # Filtrar por metadata que contenga banco_nombre y ciudad
            if banco_nombre or ciudad:
                # Crear filtros para metadata JSONB
                metadata_filtros = []
                if banco_nombre:
                    metadata_filtros.append(f"metadata->>'banco_nombre'.eq.{banco_nombre}")
                if ciudad:
                    metadata_filtros.append(f"metadata->>'ciudad'.eq.{ciudad}")

                if metadata_filtros:
                    # Aplicar filtros OR para metadata
                    query = query.or_(",".join(metadata_filtros))

        elif rol == "supervisor":
            # Usuario supervisor: ve notificaciones creadas por su equipo + las suyas propias
            if user_id and empresa_id:
                # Obtener IDs de usuarios de su equipo
                from models.usuarios_model import UsuariosModel
                usuarios_model = UsuariosModel()
                team_members = usuarios_model.get_team_members(user_id, empresa_id)

                # Incluir su propio ID + IDs de su equipo
                user_ids = [user_id]  # Su propio ID
                if team_members:
                    team_ids = [member["id"] for member in team_members]
                    user_ids.extend(team_ids)
                    print(f"   ✅ Supervisor {user_id} - viendo notificaciones creadas por su equipo: {user_ids}")

                # Filtrar por usuario_id (quien creó la notificación)
                query = query.in_("usuario_id", user_ids)

        elif rol == "asesor":
            # Usuario asesor: ve notificaciones creadas por él + las creadas por su supervisor
            if user_id and empresa_id:
                # Obtener el supervisor del asesor
                from models.usuarios_model import UsuariosModel
                usuarios_model = UsuariosModel()
                asesor_info = usuarios_model.get_by_id(user_id, empresa_id)

                user_ids = [user_id]  # Sus propias notificaciones

                if asesor_info and asesor_info.get("reports_to_id"):
                    supervisor_id = asesor_info["reports_to_id"]
                    user_ids.append(supervisor_id)
                    print(f"   ✅ Asesor {user_id} - viendo notificaciones creadas por él + por su supervisor {supervisor_id}: {user_ids}")
                else:
                    print(f"   ✅ Asesor {user_id} - sin supervisor, viendo solo sus notificaciones: {user_ids}")

                # Filtrar por usuario_id (quien creó la notificación)
                query = query.in_("usuario_id", user_ids)

        # admin, empresa: ven todas las notificaciones (sin filtros adicionales)

        return query
