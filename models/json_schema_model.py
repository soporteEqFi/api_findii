from __future__ import annotations

from typing import Any, Dict, List

from data.supabase_conn import supabase


def _get_resp_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp


class JSONSchemaModel:
    """Acceso al catálogo json_field_definition en Supabase."""

    TABLE = "json_field_definition"

    def get_schema(self, *, empresa_id: int, entity: str, json_column: str) -> List[Dict[str, Any]]:
        resp = (
            supabase.table(self.TABLE)
            .select("id, empresa_id, entity, json_column, key, type, required, list_values, description, default_value, created_at")
            .eq("empresa_id", empresa_id)
            .eq("entity", entity)
            .eq("json_column", json_column)
            .execute()
        )
        data = _get_resp_data(resp)
        return data or []

    def upsert_definitions(
        self,
        *,
        empresa_id: int,
        entity: str,
        json_column: str,
        items: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        # Normaliza items agregando claves fijas
        payload: List[Dict[str, Any]] = []
        for it in items:
            if not isinstance(it, dict) or "key" not in it:
                raise ValueError("Cada item debe incluir 'key'")
            payload.append(
                {
                    "empresa_id": empresa_id,
                    "entity": entity,
                    "json_column": json_column,
                    "key": it.get("key"),
                    "type": it.get("type", "string"),
                    "required": bool(it.get("required", False)),
                    "list_values": it.get("list_values"),
                    "description": it.get("description"),
                    "default_value": it.get("default_value"),
                }
            )

        # Requiere un índice único en (empresa_id, entity, json_column, key) para on_conflict
        resp = supabase.table(self.TABLE).upsert(
            payload,
            on_conflict="empresa_id,entity,json_column,key",
            ignore_duplicates=False,
        ).execute()
        data = _get_resp_data(resp)
        return data or []

    def delete_definition(
        self,
        *,
        empresa_id: int,
        entity: str,
        json_column: str,
        key: str | None = None,
    ) -> int:
        q = (
            supabase.table(self.TABLE)
            .delete()
            .eq("empresa_id", empresa_id)
            .eq("entity", entity)
            .eq("json_column", json_column)
        )
        if key:
            q = q.eq("key", key)
        resp = q.execute()
        data = _get_resp_data(resp)
        # supabase devuelve deleted rows en data; retornamos cantidad
        if isinstance(data, list):
            return len(data)
        return 0


