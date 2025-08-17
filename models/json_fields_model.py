from __future__ import annotations

from typing import Any, Dict, Optional

from data.supabase_conn import supabase


def _get_resp_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp


class JSONFieldsModel:
    """Modelo muy simple usando Supabase.

    Soporta operaciones de PRIMER NIVEL únicamente:
    - Leer todo el JSON o una clave top-level
    - Merge top-level
    - Set/Delete de una clave top-level
    """

    def __init__(self, db=None):
        self._db = db

    def _read_current(self, table: str, column: str, record_id: int, empresa_id: int) -> Dict[str, Any]:
        resp = (
            supabase.table(table)
            .select(column)
            .eq("id", record_id)
            .eq("empresa_id", empresa_id)
            .execute()
        )
        data = _get_resp_data(resp)
        if isinstance(data, list) and data:
            record = data[0]
            return record.get(column) if isinstance(record, dict) else {}
        return {}

    # Lectura
    def read_json_field(
        self,
        *,
        table_name: str,
        json_column: str,
        record_id: int,
        empresa_id: int,
        path_segments: Optional[list[str]],
    ) -> Any:
        current = self._read_current(table_name, json_column, record_id, empresa_id)
        if not path_segments:
            return current
        if len(path_segments) != 1:
            raise ValueError("Solo se soportan claves de primer nivel (sin puntos)")
        return current.get(path_segments[0])

    # Update / Merge
    def update_json_field(
        self,
        *,
        table_name: str,
        json_column: str,
        record_id: int,
        empresa_id: int,
        path_segments: Optional[list[str]],
        value: Any,
    ) -> Any:
        current = self._read_current(table_name, json_column, record_id, empresa_id)

        if not path_segments:
            if not isinstance(value, dict):
                raise ValueError("Cuando no hay 'path', 'value' debe ser objeto para merge")
            new_json = {**current, **value}
        else:
            if len(path_segments) != 1:
                raise ValueError("Solo se soportan claves de primer nivel (sin puntos)")
            key = path_segments[0]
            new_json = dict(current)
            new_json[key] = value

        upd_resp = (
            supabase.table(table_name)
            .update({json_column: new_json})
            .eq("id", record_id)
            .eq("empresa_id", empresa_id)
            .execute()
        )
        _get_resp_data(upd_resp)
        return new_json if not path_segments else new_json.get(path_segments[0])

    # Delete clave
    def delete_json_field(
        self,
        *,
        table_name: str,
        json_column: str,
        record_id: int,
        empresa_id: int,
        path_segments: list[str],
    ) -> Any:
        if not path_segments or len(path_segments) != 1:
            raise ValueError("'path' requerido y debe ser una sola clave de primer nivel")

        current = self._read_current(table_name, json_column, record_id, empresa_id)
        key = path_segments[0]
        if key in current:
            del current[key]
        upd_resp = (
            supabase.table(table_name)
            .update({json_column: current})
            .eq("id", record_id)
            .eq("empresa_id", empresa_id)
            .execute()
        )
        _get_resp_data(upd_resp)
        return current


