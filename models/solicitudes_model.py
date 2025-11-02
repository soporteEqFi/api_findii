from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid
from data.supabase_conn import supabase

def _get_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp
def _deep_merge_dicts(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dicts without losing nested content.

    Values in 'updates' override or extend values in 'base'. If both values are dicts,
    they are merged recursively. Lists and scalars are replaced by the 'updates' value.
    """
    if not isinstance(base, dict):
        base = {}
    if not isinstance(updates, dict):
        return updates

    merged: Dict[str, Any] = dict(base)
    for k, v in updates.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = _deep_merge_dicts(merged[k], v)
        else:
            merged[k] = v
    return merged
class SolicitudesModel:
    """Operaciones CRUD para la entidad solicitud usando Supabase."""

    TABLE = "solicitudes"

    def create(self, *, empresa_id: int, solicitante_id: int, created_by_user_id: int, assigned_to_user_id: Optional[int] = None, banco_nombre: Optional[str] = None, ciudad_solicitud: Optional[str] = None, estado: Optional[str] = None, detalle_credito: Optional[Dict[str, Any]] = None, observacion_inicial: Optional[str] = None, usuario_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Crear observaciones inicial si se proporciona
        observaciones_data = {}
        if observacion_inicial and usuario_info:
            observaciones_data = self._crear_observacion_inicial(observacion_inicial, usuario_info)

        payload: Dict[str, Any] = {
            "empresa_id": empresa_id,
            "solicitante_id": solicitante_id,
            "created_by_user_id": created_by_user_id,
            "estado": estado or "Pendiente",
            "detalle_credito": detalle_credito or {},
            "observaciones": observaciones_data,
        }
        if assigned_to_user_id is not None:
            payload["assigned_to_user_id"] = assigned_to_user_id
        if banco_nombre is not None:
            payload["banco_nombre"] = banco_nombre
        if ciudad_solicitud is not None:
            payload["ciudad_solicitud"] = ciudad_solicitud

        resp = supabase.table(self.TABLE).insert(payload).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else data

    def get_by_id(self, *, id: int, empresa_id: int) -> Optional[Dict[str, Any]]:
        # Hacer JOIN con usuarios para obtener el nombre del creador
        resp = supabase.table(self.TABLE).select("*, usuarios!created_by_user_id(nombre)").eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)

        if not data or not isinstance(data, list) or len(data) == 0:
            return None

        item = data[0]

        # Extraer nombre del usuario creador
        usuario_creador = item.get("usuarios", {})
        created_by_user_name = usuario_creador.get("nombre") if usuario_creador else None

        # Crear nuevo objeto con el campo agregado
        processed_item = {**item}
        processed_item["created_by_user_name"] = created_by_user_name

        # Remover el objeto usuarios anidado para limpiar la respuesta
        if "usuarios" in processed_item:
            del processed_item["usuarios"]

        return processed_item

    def list(self, *, empresa_id: int, estado: Optional[str] = None, solicitante_id: Optional[int] = None, banco_nombre: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        # Hacer JOIN con usuarios para obtener el nombre del creador
        q = supabase.table(self.TABLE).select("*, usuarios!created_by_user_id(nombre)").eq("empresa_id", empresa_id)
        if estado:
            q = q.eq("estado", estado)
        if solicitante_id:
            q = q.eq("solicitante_id", solicitante_id)
        if banco_nombre:
            q = q.eq("banco_nombre", banco_nombre)
        q = q.range(offset, offset + max(limit - 1, 0))
        resp = q.execute()
        data = _get_data(resp)

        # Procesar datos para agregar created_by_user_name
        processed_data = []
        for item in data:
            # Extraer nombre del usuario creador
            usuario_creador = item.get("usuarios", {})
            created_by_user_name = usuario_creador.get("nombre") if usuario_creador else None

            # Crear nuevo objeto con el campo agregado
            processed_item = {**item}
            processed_item["created_by_user_name"] = created_by_user_name

            # Remover el objeto usuarios anidado para limpiar la respuesta
            if "usuarios" in processed_item:
                del processed_item["usuarios"]

            processed_data.append(processed_item)

        return processed_data or []

    def update(
        self,
        *,
        id: int,
        empresa_id: int,
        base_updates: Optional[Dict[str, Any]] = None,
        detalle_credito_merge: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        # Leer actual para merge del JSON
        current_resp = (
            supabase.table(self.TABLE)
            .select("detalle_credito")
            .eq("id", id)
            .eq("empresa_id", empresa_id)
            .execute()
        )
        current_data = _get_data(current_resp) or []
        current = current_data[0] if isinstance(current_data, list) and current_data else {}
        current_json = current.get("detalle_credito") if isinstance(current, dict) else {}

        update_payload: Dict[str, Any] = {}
        if base_updates:
            update_payload.update(base_updates)
        if detalle_credito_merge:
            # Deep merge para no perder campos anidados (e.g., credito_vehicular)
            merged = _deep_merge_dicts(current_json or {}, detalle_credito_merge)
            update_payload["detalle_credito"] = merged

        if not update_payload:
            return self.get_by_id(id=id, empresa_id=empresa_id)

        resp = supabase.table(self.TABLE).update(update_payload).eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def delete(self, *, id: int, empresa_id: int) -> int:
        # Primero verificar que el registro existe
        existing_record = self.get_by_id(id=id, empresa_id=empresa_id)
        if not existing_record:
            print(f"❌ Solicitud no encontrada para eliminar: id={id}, empresa_id={empresa_id}")
            return 0

        # Intentar eliminar
        resp = supabase.table(self.TABLE).delete().eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)

        deleted_count = len(data) if isinstance(data, list) else 0
        # Verificar que realmente se eliminó
        if deleted_count > 0:
            # Verificar que ya no existe
            still_exists = self.get_by_id(id=id, empresa_id=empresa_id)
            if still_exists:
                print(f"⚠️ Solicitud aún existe después de eliminar: {still_exists}")
            else:
                print(f"✅ Solicitud eliminada exitosamente")

        return deleted_count

    def list_con_filtros_rol(self, *, empresa_id: int, usuario_info: dict = None, estado: Optional[str] = None, solicitante_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Listar solicitudes aplicando filtros de permisos por rol"""
        # Consulta simple sin JOIN por ahora
        q = supabase.table(self.TABLE).select("*").eq("empresa_id", empresa_id)

        # Aplicar filtros básicos
        if estado:
            q = q.eq("estado", estado)
        if solicitante_id:
            q = q.eq("solicitante_id", solicitante_id)

        # Aplicar filtros de permisos por rol
        if usuario_info:
            rol = usuario_info.get("rol")

            if rol == "admin":
                # Admin ve todas las solicitudes de la empresa
                print(f"   ✅ Admin - sin filtros aplicados")
                pass
            elif rol == "banco":
                # Usuario banco solo ve solicitudes de su banco y ciudad
                banco_nombre = usuario_info.get("banco_nombre")
                ciudad_solicitud = usuario_info.get("ciudad_solicitud")

                if banco_nombre:
                    q = q.eq("banco_nombre", banco_nombre)
                else:
                    # Si no tiene banco asignado, no ve nada
                    print(f"   ❌ Usuario sin banco asignado - retornando lista vacía")
                    return []

                # Aplicar filtro de ciudad_solicitud si está disponible
                if ciudad_solicitud:
                    q = q.eq("ciudad_solicitud", ciudad_solicitud)
                    print(f"   ✅ Filtro ciudad aplicado: {ciudad_solicitud}")
                else:
                    print(f"   ⚠️ Usuario sin ciudad asignada - solo filtro por banco")

            elif rol == "empresa":
                # Usuario empresa ve todas las solicitudes de su empresa
                print(f"   ✅ Empresa - sin filtros aplicados")
                pass
            elif rol == "supervisor":
                # Usuario supervisor ve las solicitudes de su equipo + las suyas propias
                user_id = usuario_info.get("id")
                if user_id:
                    # Obtener IDs de usuarios de su equipo
                    from models.usuarios_model import UsuariosModel
                    usuarios_model = UsuariosModel()
                    team_members = usuarios_model.get_team_members(user_id, empresa_id)

                    # Incluir su propio ID + IDs de su equipo
                    user_ids = [user_id]  # Su propio ID
                    if team_members:
                        team_ids = [member["id"] for member in team_members]
                        user_ids.extend(team_ids)
                        print(f"   ✅ Supervisor - viendo solicitudes de su equipo + las suyas: {user_ids}")
                    else:
                        print(f"   ✅ Supervisor sin equipo - viendo solo sus solicitudes: {user_ids}")

                    # Filtrar por created_by_user_id o assigned_to_user_id
                    q = q.or_(f"created_by_user_id.in.({','.join(map(str, user_ids))}),assigned_to_user_id.in.({','.join(map(str, user_ids))})")
                else:
                    print(f"   ❌ Supervisor sin ID de usuario")
                    return []
            elif rol == "asesor":
                # Usuario asesor ve solo sus propias solicitudes
                user_id = usuario_info.get("id")
                if user_id:
                    q = q.or_(f"created_by_user_id.eq.{user_id},assigned_to_user_id.eq.{user_id}")
                    print(f"   ✅ Asesor - filtros aplicados para su ID: {user_id}")
                else:
                    print(f"   ❌ Asesor sin ID de usuario")
                    return []
            else:
                # Rol desconocido, no ve nada
                print(f"   ❌ Rol desconocido '{rol}' - retornando lista vacía")
                return []

        # Aplicar paginación
        q = q.range(offset, offset + max(limit - 1, 0))

        resp = q.execute()
        data = _get_data(resp)

        # print(f"🔍 DEBUG JOIN - Datos recibidos: {len(data) if data else 0} registros")
        # if data and len(data) > 0:
        #     print(f"🔍 DEBUG JOIN - Primer registro: {data[0]}")

        # Obtener todos los IDs de usuarios únicos
        user_ids = set()
        for item in data:
            if item.get("created_by_user_id"):
                user_ids.add(item["created_by_user_id"])
            if item.get("assigned_to_user_id"):
                user_ids.add(item["assigned_to_user_id"])

        # print(f"🔍 DEBUG JOIN - IDs de usuarios encontrados: {user_ids}")

        # Consultar usuarios para obtener nombres y supervisores
        usuarios_map = {}
        supervisores_map = {}
        if user_ids:
            # Obtener información completa de usuarios (incluyendo reports_to_id)
            usuarios_resp = supabase.table("usuarios").select("id, nombre, reports_to_id").in_("id", list(user_ids)).execute()
            usuarios_data = _get_data(usuarios_resp) or []
            usuarios_map = {usuario["id"]: usuario["nombre"] for usuario in usuarios_data}

            # Obtener IDs de supervisores únicos
            supervisor_ids = set()
            for usuario in usuarios_data:
                if usuario.get("reports_to_id"):
                    supervisor_ids.add(usuario["reports_to_id"])

            # Consultar nombres de supervisores
            if supervisor_ids:
                supervisores_resp = supabase.table("usuarios").select("id, nombre").in_("id", list(supervisor_ids)).execute()
                supervisores_data = _get_data(supervisores_resp) or []
                supervisores_map = {supervisor["id"]: supervisor["nombre"] for supervisor in supervisores_data}

                # print(f"🔍 DEBUG JOIN - Mapa de usuarios: {usuarios_map}")
                # print(f"🔍 DEBUG JOIN - Mapa de supervisores: {supervisores_map}")

        # Procesar datos para agregar created_by_user_name y created_by_supervisor_name
        processed_data = []
        for item in data:
            # Obtener nombre del usuario creador
            created_by_user_id = item.get("created_by_user_id")
            created_by_user_name = usuarios_map.get(created_by_user_id) if created_by_user_id else None

            # Obtener nombre del supervisor del usuario creador
            created_by_supervisor_name = None
            if created_by_user_id:
                # Buscar el reports_to_id del usuario creador
                for usuario in usuarios_data:
                    if usuario["id"] == created_by_user_id and usuario.get("reports_to_id"):
                        supervisor_id = usuario["reports_to_id"]
                        created_by_supervisor_name = supervisores_map.get(supervisor_id)
                        break

            # print(f"🔍 DEBUG JOIN - ID: {created_by_user_id}, Nombre: {created_by_user_name}, Supervisor: {created_by_supervisor_name}")

            # Crear nuevo objeto con los campos agregados
            processed_item = {**item}
            processed_item["created_by_user_name"] = created_by_user_name
            processed_item["created_by_supervisor_name"] = created_by_supervisor_name

            processed_data.append(processed_item)

        return processed_data or []

    def get_by_id_con_filtros_rol(self, *, id: int, empresa_id: int, usuario_info: dict = None) -> Optional[Dict[str, Any]]:
        """Obtener una solicitud específica aplicando filtros de permisos por rol"""
        # Hacer JOIN con usuarios para obtener el nombre del creador
        q = supabase.table(self.TABLE).select("*, usuarios!created_by_user_id(nombre)").eq("id", id).eq("empresa_id", empresa_id)

        # Aplicar filtros de permisos por rol
        if usuario_info:
            rol = usuario_info.get("rol")

            if rol == "admin":
                # Admin ve todas las solicitudes de la empresa
                pass
            elif rol == "banco":
                # Usuario banco solo ve solicitudes de su banco y ciudad
                banco_nombre = usuario_info.get("banco_nombre")
                ciudad_solicitud = usuario_info.get("ciudad_solicitud")

                if banco_nombre:
                    q = q.eq("banco_nombre", banco_nombre)
                else:
                    # Si no tiene banco asignado, no ve nada
                    return None

                # Aplicar filtro de ciudad_solicitud si está disponible
                if ciudad_solicitud:
                    q = q.eq("ciudad_solicitud", ciudad_solicitud)
            elif rol == "empresa":
                # Usuario empresa ve todas las solicitudes de su empresa
                pass
            elif rol == "supervisor":
                # Usuario supervisor ve las solicitudes de su equipo + las suyas propias
                user_id = usuario_info.get("id")
                if user_id:
                    # Obtener IDs de usuarios de su equipo
                    from models.usuarios_model import UsuariosModel
                    usuarios_model = UsuariosModel()
                    team_members = usuarios_model.get_team_members(user_id, empresa_id)

                    # Incluir su propio ID + IDs de su equipo
                    user_ids = [user_id]  # Su propio ID
                    if team_members:
                        team_ids = [member["id"] for member in team_members]
                        user_ids.extend(team_ids)

                    # Filtrar por created_by_user_id o assigned_to_user_id
                    q = q.or_(f"created_by_user_id.in.({','.join(map(str, user_ids))}),assigned_to_user_id.in.({','.join(map(str, user_ids))})")
                else:
                    return None
            elif rol == "asesor":
                # Usuario asesor ve solo sus propias solicitudes
                user_id = usuario_info.get("id")
                if user_id:
                    q = q.or_(f"created_by_user_id.eq.{user_id},assigned_to_user_id.eq.{user_id}")
                else:
                    return None
            else:
                # Rol desconocido, no ve nada
                return None

        resp = q.execute()
        data = _get_data(resp)

        if not data or not isinstance(data, list) or len(data) == 0:
            return None

        item = data[0]

        # Extraer nombre del usuario creador
        usuario_creador = item.get("usuarios", {})
        created_by_user_name = usuario_creador.get("nombre") if usuario_creador else None

        # Obtener nombre del supervisor del usuario creador
        created_by_supervisor_name = None
        created_by_user_id = item.get("created_by_user_id")
        if created_by_user_id:
            # Consultar el reports_to_id del usuario creador
            usuario_resp = supabase.table("usuarios").select("reports_to_id").eq("id", created_by_user_id).execute()
            usuario_data = _get_data(usuario_resp)
            if usuario_data and len(usuario_data) > 0:
                reports_to_id = usuario_data[0].get("reports_to_id")
                if reports_to_id:
                    # Consultar el nombre del supervisor
                    supervisor_resp = supabase.table("usuarios").select("nombre").eq("id", reports_to_id).execute()
                    supervisor_data = _get_data(supervisor_resp)
                    if supervisor_data and len(supervisor_data) > 0:
                        created_by_supervisor_name = supervisor_data[0].get("nombre")

        # Crear nuevo objeto con los campos agregados
        processed_item = {**item}
        processed_item["created_by_user_name"] = created_by_user_name
        processed_item["created_by_supervisor_name"] = created_by_supervisor_name

        # Remover el objeto usuarios anidado para limpiar la respuesta
        if "usuarios" in processed_item:
            del processed_item["usuarios"]

        return processed_item

    def _crear_observacion_inicial(self, observacion: str, usuario_info: Dict[str, Any]) -> Dict[str, Any]:
        """Crear la estructura inicial de observaciones"""
        return {
            "historial": [{
                "id": str(uuid.uuid4()),
                "fecha": datetime.utcnow().isoformat() + "Z",
                "usuario_id": usuario_info.get("id"),
                "usuario_nombre": usuario_info.get("nombre", "Usuario"),
                "tipo": "creacion",
                "estado_anterior": None,
                "estado_nuevo": "Pendiente",
                "observacion": observacion,
                "metadata": {
                    "sistema": "api",
                    "rol": usuario_info.get("rol")
                }
            }]
        }

    def agregar_observacion_simple(self, id: int, observacion: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega una observación simple a una solicitud existente.

        Args:
            id: ID de la solicitud
            observacion: Diccionario con la estructura {
                'observacion': 'texto',
                'fecha_creacion': 'fecha_iso',
                'tipo': 'comentario' (opcional),
                'usuario_id': 123,
                'usuario_nombre': 'Juan Pérez'
            }

        Returns:
            La solicitud actualizada con la nueva observación
        """
        # Obtener la solicitud actual
        current = supabase.table(self.TABLE).select('observaciones').eq('id', id).execute()
        current_data = _get_data(current)

        if not current_data:
            raise ValueError("Solicitud no encontrada")

        # Inicializar observaciones si no existen
        observaciones = current_data[0].get('observaciones', {})
        if not observaciones or 'historial' not in observaciones:
            observaciones = {'historial': []}

        # Agregar la nueva observación al historial
        nueva_observacion = {
            'id': str(uuid.uuid4()),
            'fecha': observacion.get('fecha_creacion', datetime.utcnow().isoformat() + "Z"),
            'tipo': observacion.get('tipo', 'comentario'),
            'observacion': observacion['observacion']
        }

        # Agregar usuario_id y usuario_nombre si están presentes
        if 'usuario_id' in observacion:
            nueva_observacion['usuario_id'] = observacion['usuario_id']
        if 'usuario_nombre' in observacion:
            nueva_observacion['usuario_nombre'] = observacion['usuario_nombre']

        observaciones['historial'].append(nueva_observacion)

        # Actualizar la solicitud
        resp = (
            supabase.table(self.TABLE)
            .update({'observaciones': observaciones})
            .eq('id', id)
            .execute()
        )

        updated_data = _get_data(resp)
        return updated_data[0] if isinstance(updated_data, list) and updated_data else updated_data

    def _agregar_observacion(self, observaciones_actuales: Dict[str, Any], nueva_observacion: str, usuario_info: Dict[str, Any], tipo: str = "comentario", estado_anterior: Optional[str] = None, estado_nuevo: Optional[str] = None) -> Dict[str, Any]:
        """Agregar una nueva observación al historial existente"""
        if not observaciones_actuales:
            observaciones_actuales = {"historial": []}

        if "historial" not in observaciones_actuales:
            observaciones_actuales["historial"] = []

        nueva_entrada = {
            "id": str(uuid.uuid4()),
            "fecha": datetime.utcnow().isoformat() + "Z",
            "usuario_id": usuario_info.get("id"),
            "usuario_nombre": usuario_info.get("nombre", "Usuario"),
            "tipo": tipo,
            "estado_anterior": estado_anterior,
            "estado_nuevo": estado_nuevo,
            "observacion": nueva_observacion,
            "metadata": {
                "sistema": "api",
                "rol": usuario_info.get("rol")
            }
        }

        observaciones_actuales["historial"].append(nueva_entrada)
        return observaciones_actuales

    def agregar_observacion(self, *, id: int, empresa_id: int, observacion: str, usuario_info: Dict[str, Any], tipo: str = "comentario") -> Optional[Dict[str, Any]]:
        """Agregar una nueva observación a una solicitud existente"""
        # Obtener la solicitud actual
        solicitud_actual = self.get_by_id(id=id, empresa_id=empresa_id)
        if not solicitud_actual:
            return None

        # Obtener observaciones actuales
        observaciones_actuales = solicitud_actual.get("observaciones", {})

        # Agregar nueva observación
        observaciones_actualizadas = self._agregar_observacion(
            observaciones_actuales=observaciones_actuales,
            nueva_observacion=observacion,
            usuario_info=usuario_info,
            tipo=tipo
        )

        # Actualizar en la base de datos
        update_payload = {"observaciones": observaciones_actualizadas}
        resp = supabase.table(self.TABLE).update(update_payload).eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def actualizar_con_observacion(self, *, id: int, empresa_id: int, base_updates: Optional[Dict[str, Any]] = None, detalle_credito_merge: Optional[Dict[str, Any]] = None, observacion: Optional[str] = None, usuario_info: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Actualizar solicitud y agregar observación automáticamente si hay cambios de estado"""
        # Obtener solicitud actual
        solicitud_actual = self.get_by_id(id=id, empresa_id=empresa_id)
        if not solicitud_actual:
            return None

        # Detectar cambio de estado
        estado_anterior = solicitud_actual.get("estado")
        estado_nuevo = base_updates.get("estado") if base_updates else None

        # Realizar actualización normal
        solicitud_actualizada = self.update(
            id=id,
            empresa_id=empresa_id,
            base_updates=base_updates,
            detalle_credito_merge=detalle_credito_merge
        )

        # Agregar observación si se proporciona o hay cambio de estado
        if (observacion or estado_nuevo) and usuario_info:
            observaciones_actuales = solicitud_actualizada.get("observaciones", {})

            # Determinar tipo y mensaje de observación
            if estado_nuevo and estado_nuevo != estado_anterior:
                tipo_obs = "cambio_estado"
                mensaje_obs = observacion or f"Estado cambiado de '{estado_anterior}' a '{estado_nuevo}'"
            else:
                tipo_obs = "comentario"
                mensaje_obs = observacion

            if mensaje_obs:
                observaciones_actualizadas = self._agregar_observacion(
                    observaciones_actuales=observaciones_actuales,
                    nueva_observacion=mensaje_obs,
                    usuario_info=usuario_info,
                    tipo=tipo_obs,
                    estado_anterior=estado_anterior,
                    estado_nuevo=estado_nuevo
                )

                # Actualizar observaciones en BD
                update_payload = {"observaciones": observaciones_actualizadas}
                resp = supabase.table(self.TABLE).update(update_payload).eq("id", id).eq("empresa_id", empresa_id).execute()
                data = _get_data(resp)
                solicitud_actualizada = data[0] if isinstance(data, list) and data else solicitud_actualizada

        return solicitud_actualizada


