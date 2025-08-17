from __future__ import annotations

from flask import request, jsonify
from models.json_fields_model import JSONFieldsModel
from models.json_schema_model import JSONSchemaModel


class JSONFieldsController:
    """Controlador para operaciones sobre campos JSONB por entidad."""

    def __init__(self, db=None):
        # db es opcional; si no se provee, el modelo lanzará error al ejecutar
        self.model = JSONFieldsModel(db=db)
        self.schema_model = JSONSchemaModel()

        # Mapeo entidad -> tabla y columnas JSON válidas
        # Nota: mantener sincronizado con el contrato de datos
        self._entity_map = {
            "solicitante": {
                "table": "solicitantes",
                "json_columns": {"info_extra"},
            },
            "ubicacion": {
                "table": "ubicacion",
                "json_columns": {"detalle_direccion"},
            },
            "actividad_economica": {
                "table": "actividad_economica",
                "json_columns": {"detalle_actividad"},
            },
            "informacion_financiera": {
                "table": "informacion_financiera",
                "json_columns": {"detalle_financiera"},
            },
            "referencia": {
                "table": "referencias",
                "json_columns": {"detalle_referencia"},
            },
            "documento": {
                "table": "documento",
                "json_columns": set(),
            },
            "solicitud": {
                "table": "solicitudes",
                "json_columns": {"detalle_credito"},
            },
            "tipo_credito": {
                "table": "tipo_credito",
                "json_columns": {"fields"},
            },
        }

    def _parse_path(self, path_str: str | None) -> list[str] | None:
        # Convierte 'a.b.c' -> ['a','b','c'] o None si vacío
        if path_str is None or str(path_str).strip() == "":
            return None
        return [seg for seg in str(path_str).split(".") if seg]

    def _require_empresa_id(self) -> int:
        # Obtiene empresa_id de header o querystring
        empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
        if empresa_id is None:
            raise ValueError("empresa_id es requerido (header X-Empresa-Id o query param)")
        try:
            return int(empresa_id)
        except Exception as exc:  # noqa: B902
            raise ValueError("empresa_id debe ser entero") from exc

    def _validate_entity_and_field(self, entity: str, json_field: str) -> tuple[str, str]:
        # Valida entidad y nombre de columna JSON; retorna (table, json_column)
        entity_info = self._entity_map.get(entity)
        if entity_info is None:
            raise ValueError(f"Entidad no soportada: {entity}")
        if json_field not in entity_info["json_columns"]:
            raise ValueError(
                f"Campo JSON no soportado para {entity}: {json_field}"
            )
        return entity_info["table"], json_field

    def get_json(self, entity: str, record_id: int, json_field: str):
        # Lee un campo JSON o una ruta específica
        try:
            empresa_id = self._require_empresa_id()
            table, json_column = self._validate_entity_and_field(entity, json_field)
            path = self._parse_path(request.args.get("path"))

            value = self.model.read_json_field(
                table_name=table,
                json_column=json_column,
                record_id=record_id,
                empresa_id=empresa_id,
                path_segments=path,
            )
            return jsonify({"ok": True, "data": value})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500

    def patch_json(self, entity: str, record_id: int, json_field: str):
        # Agrega/actualiza una ruta; si no hay path, hace merge a nivel superior
        try:
            empresa_id = self._require_empresa_id()
            table, json_column = self._validate_entity_and_field(entity, json_field)
            body = request.get_json(silent=True) or {}
            path = self._parse_path(body.get("path"))
            value = body.get("value")

            if path is None and not isinstance(value, dict):
                raise ValueError(
                    "Cuando no se provee 'path', 'value' debe ser un objeto para merge"
                )

            # Validación opcional contra catálogo
            should_validate = (
                request.args.get("validate") == "true"
                or request.headers.get("X-Validate-JSON") == "true"
            )
            if should_validate:
                defs = self.schema_model.get_schema(
                    empresa_id=empresa_id, entity=entity, json_column=json_column
                )
                allowed = {d["key"]: d for d in defs if isinstance(d, dict) and "key" in d}
                if path is None:
                    # merge top-level: validar todas las claves
                    for k, v in (value or {}).items():
                        if k not in allowed:
                            raise ValueError(f"Clave no permitida: {k}")
                else:
                    if len(path) != 1:
                        raise ValueError("Solo claves top-level permitidas con validación")
                    if path[0] not in allowed:
                        raise ValueError(f"Clave no permitida: {path[0]}")

            updated = self.model.update_json_field(
                table_name=table,
                json_column=json_column,
                record_id=record_id,
                empresa_id=empresa_id,
                path_segments=path,
                value=value,
            )
            return jsonify({"ok": True, "data": updated})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500

    def delete_json(self, entity: str, record_id: int, json_field: str):
        # Elimina una clave (path requerido)
        try:
            empresa_id = self._require_empresa_id()
            table, json_column = self._validate_entity_and_field(entity, json_field)
            path = self._parse_path(request.args.get("path"))
            if not path:
                raise ValueError("'path' es requerido para eliminar")

            deleted = self.model.delete_json_field(
                table_name=table,
                json_column=json_column,
                record_id=record_id,
                empresa_id=empresa_id,
                path_segments=path,
            )
            return jsonify({"ok": True, "data": deleted})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500


