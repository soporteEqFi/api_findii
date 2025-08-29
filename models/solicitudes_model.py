from __future__ import annotations
from typing import Any, Dict, List, Optional
from data.supabase_conn import supabase

def _get_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp
class SolicitudesModel:
    """Operaciones CRUD para la entidad solicitud usando Supabase."""

    TABLE = "solicitudes"

    def create(self, *, empresa_id: int, solicitante_id: int, created_by_user_id: int, assigned_to_user_id: Optional[int] = None, banco_nombre: Optional[str] = None, ciudad_solicitud: Optional[str] = None, estado: Optional[str] = None, detalle_credito: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "empresa_id": empresa_id,
            "solicitante_id": solicitante_id,
            "created_by_user_id": created_by_user_id,
            "estado": estado or "Pendiente",
            "detalle_credito": detalle_credito or {},
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
        resp = supabase.table(self.TABLE).select("*").eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def list(self, *, empresa_id: int, estado: Optional[str] = None, solicitante_id: Optional[int] = None, banco_nombre: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        q = supabase.table(self.TABLE).select("*").eq("empresa_id", empresa_id)
        if estado:
            q = q.eq("estado", estado)
        if solicitante_id:
            q = q.eq("solicitante_id", solicitante_id)
        if banco_nombre:
            q = q.eq("banco_nombre", banco_nombre)
        q = q.range(offset, offset + max(limit - 1, 0))
        resp = q.execute()
        data = _get_data(resp)
        return data or []

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
            merged = {**(current_json or {}), **detalle_credito_merge}
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

        print(f"🗑️ Intentando eliminar solicitud: id={id}, empresa_id={empresa_id}")
        print(f"   📋 Datos de la solicitud: estado={existing_record.get('estado')}, banco={existing_record.get('banco_nombre')}")

        # Intentar eliminar
        resp = supabase.table(self.TABLE).delete().eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)

        deleted_count = len(data) if isinstance(data, list) else 0
        print(f"📊 Respuesta de eliminación de solicitud: {resp}")
        print(f"📊 Datos eliminados: {data}")
        print(f"📊 Cantidad eliminada: {deleted_count}")

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
        q = supabase.table(self.TABLE).select("*").eq("empresa_id", empresa_id)

        # Aplicar filtros básicos
        if estado:
            q = q.eq("estado", estado)
        if solicitante_id:
            q = q.eq("solicitante_id", solicitante_id)

        # Aplicar filtros de permisos por rol
        if usuario_info:
            rol = usuario_info.get("rol")
            print(f"🔍 APLICANDO FILTROS POR ROL:")
            print(f"   🏷️ Rol del usuario: {rol}")
            print(f"   👤 Info completa del usuario: {usuario_info}")

            if rol == "admin":
                # Admin ve todas las solicitudes de la empresa
                print(f"   ✅ Admin - sin filtros aplicados")
                pass
            elif rol == "banco":
                # Usuario banco solo ve solicitudes de su banco y ciudad
                banco_nombre = usuario_info.get("banco_nombre")
                ciudad_solicitud = usuario_info.get("ciudad_solicitud")

                print(f"   🏦 Banco del usuario: {banco_nombre}")
                print(f"   🏙️ Ciudad del usuario: {ciudad_solicitud}")

                if banco_nombre:
                    q = q.eq("banco_nombre", banco_nombre)
                    print(f"   ✅ Filtro banco aplicado: {banco_nombre}")
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

                print(f"   🔍 FILTROS APLICADOS:")
                print(f"      🏦 banco_nombre = {banco_nombre}")
                print(f"      🏙️ ciudad_solicitud = {ciudad_solicitud}")
                print(f"      📋 Query final: banco_nombre='{banco_nombre}' AND ciudad_solicitud='{ciudad_solicitud}'")
            elif rol == "empresa":
                # Usuario empresa ve todas las solicitudes de su empresa
                print(f"   ✅ Empresa - sin filtros aplicados")
                pass
            elif rol == "supervisor":
                # Usuario supervisor ve todas las solicitudes de la empresa (similar a admin)
                print(f"   ✅ Supervisor - sin filtros aplicados")
                pass
            else:
                # Rol desconocido, no ve nada
                print(f"   ❌ Rol desconocido '{rol}' - retornando lista vacía")
                return []

        # Aplicar paginación
        q = q.range(offset, offset + max(limit - 1, 0))

        resp = q.execute()
        data = _get_data(resp)
        return data or []

    def get_by_id_con_filtros_rol(self, *, id: int, empresa_id: int, usuario_info: dict = None) -> Optional[Dict[str, Any]]:
        """Obtener una solicitud específica aplicando filtros de permisos por rol"""
        q = supabase.table(self.TABLE).select("*").eq("id", id).eq("empresa_id", empresa_id)

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
                # Usuario supervisor ve todas las solicitudes de la empresa (similar a admin)
                pass
            else:
                # Rol desconocido, no ve nada
                return None

        resp = q.execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None


