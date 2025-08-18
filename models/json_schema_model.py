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
        resp = supabase.table(self.TABLE).select("id, empresa_id, entity, json_column, key, type, required, list_values, description, default_value, created_at").eq("empresa_id", empresa_id).eq("entity", entity).eq("json_column", json_column).execute()
        data = _get_resp_data(resp)
        return data or []

    def upsert_definitions(self, *, empresa_id: int, entity: str, json_column: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        print(f"🏗️ upsert_definitions llamado con:")
        print(f"   empresa_id: {empresa_id}")
        print(f"   entity: {entity}")
        print(f"   json_column: {json_column}")
        print(f"   items: {items}")

        # Normaliza items agregando claves fijas
        payload: List[Dict[str, Any]] = []
        for it in items:
            print(f"🔍 Procesando item: {it}")
            if not isinstance(it, dict) or "key" not in it:
                raise ValueError("Cada item debe incluir 'key'")

            normalized_item = {
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
            print(f"✅ Item normalizado: {normalized_item}")
            payload.append(normalized_item)

        print(f"📦 Payload final para Supabase: {payload}")
        print(f"🎯 Tabla destino: {self.TABLE}")

        try:
            # Primero intentar eliminar registros existentes para evitar duplicados
            for item in payload:
                print(f"🗑️ Eliminando definición existente: {item['key']}")
                supabase.table(self.TABLE).delete().eq("empresa_id", item["empresa_id"]).eq("entity", item["entity"]).eq("json_column", item["json_column"]).eq("key", item["key"]).execute()

            # Luego insertar los nuevos registros
            resp = supabase.table(self.TABLE).insert(payload).execute()
            print(f"📡 Respuesta de Supabase: {resp}")

            data = _get_resp_data(resp)
            print(f"📊 Datos extraídos: {data}")
            return data or []

        except Exception as e:
            print(f"💥 Error en Supabase insert: {e}")
            print(f"💥 Tipo de error: {type(e)}")
            import traceback
            traceback.print_exc()
            raise

    def delete_definition(self, *, empresa_id: int, entity: str, json_column: str, key: str | None = None) -> int:
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


