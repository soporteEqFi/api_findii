from __future__ import annotations

from typing import Any, Dict, List, Optional

from data.supabase_conn import supabase


def _get_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp


class ReferenciasModel:
    """CRUD para entidad referencia."""

    TABLE = "referencias"

    def create(
        self,
        *,
        empresa_id: int,
        solicitante_id: int,
        tipo_referencia: str,
        detalle_referencia: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "empresa_id": empresa_id,
            "solicitante_id": solicitante_id,
            "tipo_referencia": tipo_referencia,
            "detalle_referencia": detalle_referencia or {},
        }
        resp = supabase.table(self.TABLE).insert(payload).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else data

    def get_by_id(self, *, id: int, empresa_id: int) -> Optional[Dict[str, Any]]:
        resp = (
            supabase.table(self.TABLE)
            .select("*")
            .eq("id", id)
            .eq("empresa_id", empresa_id)
            .execute()
        )
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def list(
        self,
        *,
        empresa_id: int,
        solicitante_id: Optional[int] = None,
        tipo_referencia: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        q = supabase.table(self.TABLE).select("*").eq("empresa_id", empresa_id)
        if solicitante_id:
            q = q.eq("solicitante_id", solicitante_id)
        if tipo_referencia:
            q = q.eq("tipo_referencia", tipo_referencia)
        resp = q.range(offset, offset + max(limit - 1, 0)).execute()
        return _get_data(resp) or []

    def update(
        self,
        *,
        id: int,
        empresa_id: int,
        updates: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        resp = (
            supabase.table(self.TABLE)
            .update(updates)
            .eq("id", id)
            .eq("empresa_id", empresa_id)
            .execute()
        )
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def delete(self, *, id: int, empresa_id: int) -> int:
        resp = (
            supabase.table(self.TABLE)
            .delete()
            .eq("id", id)
            .eq("empresa_id", empresa_id)
            .execute()
        )
        data = _get_data(resp)
        return len(data) if isinstance(data, list) else 0
