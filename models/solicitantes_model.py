from __future__ import annotations

from typing import Any, Dict, List, Optional

from data.supabase_conn import supabase


def _get_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp


class SolicitantesModel:
    """CRUD para entidad solicitante."""

    TABLE = "solicitantes"

    def create(
        self,
        *,
        empresa_id: int,
        nombres: str,
        primer_apellido: str,
        segundo_apellido: str,
        tipo_identificacion: str,
        numero_documento: str,
        fecha_nacimiento: str,
        genero: str,
        correo: str,
        info_extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "empresa_id": empresa_id,
            "nombres": nombres,
            "primer_apellido": primer_apellido,
            "segundo_apellido": segundo_apellido,
            "tipo_identificacion": tipo_identificacion,
            "numero_documento": numero_documento,
            "fecha_nacimiento": fecha_nacimiento,
            "genero": genero,
            "correo": correo,
            "info_extra": info_extra or {},
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
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        resp = (
            supabase.table(self.TABLE)
            .select("*")
            .eq("empresa_id", empresa_id)
            .range(offset, offset + max(limit - 1, 0))
            .execute()
        )
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
