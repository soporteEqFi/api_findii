from __future__ import annotations
from typing import Any, Dict, List, Optional
from data.supabase_conn import supabase

def _get_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp

class ConfiguracionesModel:
    """Operaciones para la tabla configuraciones usando Supabase."""

    TABLE = "configuraciones"

    def obtener_por_categoria(self, *, empresa_id: int, categoria: str) -> List[str]:
        """Obtener configuración por categoría (ej: ciudades, bancos)"""
        try:
            resp = supabase.table(self.TABLE).select("configuracion").eq("empresa_id", empresa_id).eq("categoria", categoria).eq("activo", True).execute()
            data = _get_data(resp)

            if data and len(data) > 0:
                # configuracion es un JSONB que contiene una lista
                return data[0].get("configuracion", [])
            return []

        except Exception as e:
            print(f"❌ Error obteniendo configuración {categoria}: {e}")
            return []

    def obtener_todas_categorias(self, *, empresa_id: int) -> Dict[str, List[str]]:
        """Obtener todas las configuraciones de una empresa"""
        try:
            resp = supabase.table(self.TABLE).select("categoria, configuracion").eq("empresa_id", empresa_id).eq("activo", True).execute()
            data = _get_data(resp)

            configuraciones = {}
            for item in data:
                categoria = item.get("categoria")
                configuracion = item.get("configuracion", [])
                if categoria:
                    configuraciones[categoria] = configuracion

            return configuraciones

        except Exception as e:
            print(f"❌ Error obteniendo configuraciones: {e}")
            return {}
