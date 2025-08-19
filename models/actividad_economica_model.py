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

    def create(self, *, empresa_id: int, solicitante_id: int, tipo_actividad: str, sector_economico: str, codigo_ciiu: Optional[str] = None, departamento_empresa: Optional[str] = None, ciudad_empresa: Optional[str] = None, telefono_empresa: Optional[str] = None, correo_oficina: Optional[str] = None, nit: Optional[str] = None, nit_empresa: Optional[str] = None, detalle_actividad: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {
            "empresa_id": empresa_id,
            "solicitante_id": solicitante_id,
            "tipo_actividad": tipo_actividad,
            "sector_economico": sector_economico,
            "codigo_ciiu": codigo_ciiu,
            "departamento_empresa": departamento_empresa,
            "ciudad_empresa": ciudad_empresa,
            "telefono_empresa": telefono_empresa,
            "correo_oficina": correo_oficina,
            "nit": nit or nit_empresa,
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
        resp = supabase.table(self.TABLE).delete().eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return len(data) if isinstance(data, list) else 0
