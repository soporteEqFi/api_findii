from __future__ import annotations

from flask import request, jsonify
from models.solicitudes_model import SolicitudesModel


class SolicitudesController:
    def __init__(self):
        self.model = SolicitudesModel()

    def _empresa_id(self) -> int:
        empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
        if not empresa_id:
            raise ValueError("empresa_id es requerido")
        try:
            return int(empresa_id)
        except Exception as exc:  # noqa: B902
            raise ValueError("empresa_id debe ser entero") from exc

    # CRUD
    def create(self):
        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}
            data = self.model.create(
                empresa_id=empresa_id,
                solicitante_id=body.get("solicitante_id"),
                created_by_user_id=body.get("created_by_user_id"),
                assigned_to_user_id=body.get("assigned_to_user_id"),
                estado=body.get("estado"),
                detalle_credito=body.get("detalle_credito"),
            )
            return jsonify({"ok": True, "data": data}), 201
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
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
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500

    def list(self):
        try:
            empresa_id = self._empresa_id()
            estado = request.args.get("estado")
            solicitante_id = request.args.get("solicitante_id")
            solicitante_id = int(solicitante_id) if solicitante_id else None
            limit = int(request.args.get("limit", 50))
            offset = int(request.args.get("offset", 0))
            data = self.model.list(
                empresa_id=empresa_id,
                estado=estado,
                solicitante_id=solicitante_id,
                limit=limit,
                offset=offset,
            )
            return jsonify({"ok": True, "data": data})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500

    def update(self, id: int):
        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}
            base_updates = {}
            for field in [
                "estado",
                "assigned_to_user_id",
            ]:
                if field in body:
                    base_updates[field] = body[field]
            detalle_credito_merge = body.get("detalle_credito")
            data = self.model.update(
                id=id,
                empresa_id=empresa_id,
                base_updates=base_updates or None,
                detalle_credito_merge=detalle_credito_merge,
            )
            return jsonify({"ok": True, "data": data})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500

    def delete(self, id: int):
        try:
            empresa_id = self._empresa_id()
            deleted = self.model.delete(id=id, empresa_id=empresa_id)
            return jsonify({"ok": True, "deleted": deleted})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500

    def actualizar_estado(self):
        """Actualizar solo el estado de una solicitud"""
        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}
            print(body)

            # Validar campos requeridos
            if not body.get("id"):
                return jsonify({"ok": False, "error": "ID de la solicitud es requerido"}), 400

            if not body.get("estado"):
                return jsonify({"ok": False, "error": "Nuevo estado es requerido"}), 400

            solicitud_id = int(body["id"])
            nuevo_estado = body["estado"]

            print(f"\n🔄 ACTUALIZANDO ESTADO DE SOLICITUD:")
            print(f"   📋 Empresa ID: {empresa_id}")
            print(f"   🆔 Solicitud ID: {solicitud_id}")
            print(f"   📊 Nuevo estado: {nuevo_estado}")

            # Verificar si la solicitud existe antes de actualizar
            print(f"\n🔍 VERIFICANDO EXISTENCIA DE SOLICITUD...")
            solicitud_existente = self.model.get_by_id(id=solicitud_id, empresa_id=empresa_id)
            if not solicitud_existente:
                print(f"   ❌ Solicitud {solicitud_id} no encontrada en empresa {empresa_id}")
                return jsonify({"ok": False, "error": f"Solicitud {solicitud_id} no encontrada"}), 404

            print(f"   ✅ Solicitud encontrada: {solicitud_existente.get('estado', 'N/A')}")

            # Actualizar solo el estado
            print(f"\n📝 ACTUALIZANDO ESTADO...")
            data = self.model.update(
                id=solicitud_id,
                empresa_id=empresa_id,
                base_updates={"estado": nuevo_estado},
                detalle_credito_merge=None
            )

            if not data:
                print(f"   ❌ Error al actualizar la solicitud")
                return jsonify({"ok": False, "error": "Error al actualizar la solicitud"}), 500

            print(f"   ✅ Estado actualizado exitosamente")

            response_data = {
                "ok": True,
                "data": data,
                "message": f"Estado de solicitud {solicitud_id} actualizado a '{nuevo_estado}'"
            }

            return jsonify(response_data)

        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500


