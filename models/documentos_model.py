from __future__ import annotations
from typing import Any, Dict, List, Optional

from data.supabase_conn import supabase


def _get_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp


class DocumentosModel:
    """CRUD para entidad documentos."""

    TABLE = "documentos"

    def create(self, *, nombre: str, documento_url: str, solicitante_id: int) -> Dict[str, Any]:
        payload = {
            "nombre": nombre,
            "documento_url": documento_url,
            "solicitante_id": solicitante_id,
        }
        resp = supabase.table(self.TABLE).insert(payload).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else data

    def list(self, *, solicitante_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        q = supabase.table(self.TABLE).select("*")
        if solicitante_id is not None:
            q = q.eq("solicitante_id", solicitante_id)
        resp = q.range(offset, offset + max(limit - 1, 0)).execute()
        return _get_data(resp) or []

    def delete(self, *, id: int) -> int:
        resp = supabase.table(self.TABLE).delete().eq("id", id).execute()
        data = _get_data(resp)
        return len(data) if isinstance(data, list) else 0

    def get_by_id(self, *, id: int) -> Optional[Dict[str, Any]]:
        resp = supabase.table(self.TABLE).select("*").eq("id", id).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def update(self, *, id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        resp = supabase.table(self.TABLE).update(updates).eq("id", id).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def delete_by_solicitante(self, *, solicitante_id: int, empresa_id: int) -> int:
        """Eliminar todos los documentos de un solicitante"""
        resp = supabase.table(self.TABLE).delete().eq("solicitante_id", solicitante_id).execute()
        data = _get_data(resp)
        return len(data) if isinstance(data, list) else 0
