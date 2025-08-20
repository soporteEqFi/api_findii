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

    def create(self, *, empresa_id: int, solicitante_id: int, created_by_user_id: int, assigned_to_user_id: Optional[int] = None, banco_nombre: Optional[str] = None, estado: Optional[str] = None, detalle_credito: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
        resp = supabase.table(self.TABLE).delete().eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        if isinstance(data, list):
            return len(data)
        return 0


