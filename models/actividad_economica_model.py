from __future__ import annotations
from typing import Any, Dict, List, Optional
from data.supabase_conn import supabase

def _get_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp
class ActividadEconomicaModel:
    """CRUD para entidad actividad_economica."""

    TABLE = "actividad_economica"

    def create(self, *, empresa_id: int, solicitante_id: int, detalle_actividad: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {
            "empresa_id": empresa_id,
            "solicitante_id": solicitante_id,
            "detalle_actividad": detalle_actividad or {},
        }
        resp = supabase.table(self.TABLE).insert(payload).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else data

    def get_by_id(self, *, id: int, empresa_id: int) -> Optional[Dict[str, Any]]:
        resp = supabase.table(self.TABLE).select("*").eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def list(self, *, empresa_id: int, solicitante_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        q = supabase.table(self.TABLE).select("*").eq("empresa_id", empresa_id)
        if solicitante_id:
            q = q.eq("solicitante_id", solicitante_id)
        resp = q.range(offset, offset + max(limit - 1, 0)).execute()
        return _get_data(resp) or []

    def update(self, *, id: int, empresa_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        resp = supabase.table(self.TABLE).update(updates).eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def delete(self, *, id: int, empresa_id: int) -> int:
        # Primero verificar que el registro existe
        existing_record = self.get_by_id(id=id, empresa_id=empresa_id)
        if not existing_record:
            print(f"❌ Registro no encontrado para eliminar: id={id}, empresa_id={empresa_id}")
            return 0

        print(f"🗑️ Intentando eliminar registro: id={id}, empresa_id={empresa_id}")

        # Intentar eliminar
        resp = supabase.table(self.TABLE).delete().eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)

        deleted_count = len(data) if isinstance(data, list) else 0
        print(f"📊 Respuesta de eliminación: {resp}")
        print(f"📊 Datos eliminados: {data}")
        print(f"📊 Cantidad eliminada: {deleted_count}")

        # Verificar que realmente se eliminó
        if deleted_count > 0:
            # Verificar que ya no existe
            still_exists = self.get_by_id(id=id, empresa_id=empresa_id)
            if still_exists:
                print(f"⚠️ Registro aún existe después de eliminar: {still_exists}")
            else:
                print(f"✅ Registro eliminado exitosamente")

        return deleted_count

    def delete_by_solicitante(self, *, solicitante_id: int, empresa_id: int) -> int:
        """Eliminar toda la actividad económica de un solicitante"""
        resp = supabase.table(self.TABLE).delete().eq("solicitante_id", solicitante_id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return len(data) if isinstance(data, list) else 0
