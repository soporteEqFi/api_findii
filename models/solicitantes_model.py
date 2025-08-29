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

    def create(self, *, empresa_id: int, nombres: str, primer_apellido: str, segundo_apellido: str, tipo_identificacion: str, numero_documento: str, fecha_nacimiento: str, genero: str, correo: str, info_extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
        resp = supabase.table(self.TABLE).select("*").eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def list(self, *, empresa_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        # Hacer JOIN con tablas relacionadas para obtener información completa
        query = """
            *,
            ubicacion(ciudad_residencia, departamento_residencia),
            solicitudes(detalle_credito, banco_nombre, estado)
        """
        
        resp = supabase.table(self.TABLE).select(query).eq("empresa_id", empresa_id).range(offset, offset + max(limit - 1, 0)).execute()
        data = _get_data(resp) or []
        
        # Procesar los datos para aplanar la estructura
        processed_data = []
        for item in data:
            # Datos base del solicitante
            solicitante = {
                "id": item.get("id"),
                "nombres": item.get("nombres"),
                "primer_apellido": item.get("primer_apellido"),
                "segundo_apellido": item.get("segundo_apellido"),
                "tipo_identificacion": item.get("tipo_identificacion"),
                "numero_documento": item.get("numero_documento"),
                "fecha_nacimiento": item.get("fecha_nacimiento"),
                "genero": item.get("genero"),
                "correo": item.get("correo"),
                "created_at": item.get("created_at"),
                "empresa_id": item.get("empresa_id")
            }
            
            # Agregar información de ubicación
            ubicaciones = item.get("ubicacion", [])
            if ubicaciones and len(ubicaciones) > 0:
                ubicacion = ubicaciones[0]  # Tomar la primera ubicación
                solicitante["ciudad_residencia"] = ubicacion.get("ciudad_residencia")
                solicitante["departamento_residencia"] = ubicacion.get("departamento_residencia")
            else:
                solicitante["ciudad_residencia"] = None
                solicitante["departamento_residencia"] = None
            
            # Agregar información de solicitudes (tipo de crédito)
            solicitudes = item.get("solicitudes", [])
            if solicitudes and len(solicitudes) > 0:
                solicitud = solicitudes[0]  # Tomar la primera solicitud
                detalle_credito = solicitud.get("detalle_credito", {})
                solicitante["tipo_credito"] = detalle_credito.get("tipo_credito")
                solicitante["banco_nombre"] = solicitud.get("banco_nombre")
                solicitante["estado_solicitud"] = solicitud.get("estado")
            else:
                solicitante["tipo_credito"] = None
                solicitante["banco_nombre"] = None
                solicitante["estado_solicitud"] = None
            
            # Agregar información extra (celular)
            info_extra = item.get("info_extra", {})
            solicitante["celular"] = info_extra.get("celular") or info_extra.get("telefono")
            
            processed_data.append(solicitante)
        
        return processed_data

    def update(self, *, id: int, empresa_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        resp = supabase.table(self.TABLE).update(updates).eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def delete(self, *, id: int, empresa_id: int) -> int:
        resp = supabase.table(self.TABLE).delete().eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return len(data) if isinstance(data, list) else 0
