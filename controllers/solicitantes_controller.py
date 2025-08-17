from __future__ import annotations

from flask import request, jsonify
from models.solicitantes_model import SolicitantesModel


class SolicitantesController:
    def __init__(self):
        self.model = SolicitantesModel()

    def _empresa_id(self) -> int:
        empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
        if not empresa_id:
            raise ValueError("empresa_id es requerido")
        try:
            return int(empresa_id)
        except Exception as exc:
            raise ValueError("empresa_id debe ser entero") from exc

    def create(self):
        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}

            # Campos requeridos
            required_fields = [
                "nombres", "primer_apellido", "segundo_apellido",
                "tipo_identificacion", "numero_documento",
                "fecha_nacimiento", "genero", "correo"
            ]

            for field in required_fields:
                if not body.get(field):
                    raise ValueError(f"Campo requerido: {field}")

            data = self.model.create(
                empresa_id=empresa_id,
                nombres=body["nombres"],
                primer_apellido=body["primer_apellido"],
                segundo_apellido=body["segundo_apellido"],
                tipo_identificacion=body["tipo_identificacion"],
                numero_documento=body["numero_documento"],
                fecha_nacimiento=body["fecha_nacimiento"],
                genero=body["genero"],
                correo=body["correo"],
                info_extra=body.get("info_extra"),
            )
            return jsonify({"ok": True, "data": data}), 201
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def get_one(self, id: int):
        try:
            empresa_id = self._empresa_id()
            data = self.model.get_by_id(id=id, empresa_id=empresa_id)
            if not data:
                return jsonify({"ok": False, "error": "No encontrado"}), 404
            return jsonify({"ok": True, "data": data})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def list(self):
        try:
            empresa_id = self._empresa_id()
            limit = int(request.args.get("limit", 50))
            offset = int(request.args.get("offset", 0))
            data = self.model.list(empresa_id=empresa_id, limit=limit, offset=offset)
            return jsonify({"ok": True, "data": data})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def update(self, id: int):
        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}
            if not body:
                raise ValueError("Body requerido para actualizar")

            data = self.model.update(id=id, empresa_id=empresa_id, updates=body)
            return jsonify({"ok": True, "data": data})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def delete(self, id: int):
        try:
            empresa_id = self._empresa_id()
            deleted = self.model.delete(id=id, empresa_id=empresa_id)
            return jsonify({"ok": True, "deleted": deleted})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500
