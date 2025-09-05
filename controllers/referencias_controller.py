from __future__ import annotations

from flask import request, jsonify
from models.referencias_model import ReferenciasModel


class ReferenciasController:
    def __init__(self):
        self.model = ReferenciasModel()

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
            required_fields = ["solicitante_id", "tipo_referencia"]
            for field in required_fields:
                if not body.get(field):
                    raise ValueError(f"Campo requerido: {field}")

            data = self.model.create(
                empresa_id=empresa_id,
                solicitante_id=body["solicitante_id"],
                tipo_referencia=body["tipo_referencia"],
                detalle_referencia=body.get("detalle_referencia"),
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
            solicitante_id = request.args.get("solicitante_id")
            solicitante_id = int(solicitante_id) if solicitante_id else None
            tipo_referencia = request.args.get("tipo_referencia")
            limit = int(request.args.get("limit", 50))
            offset = int(request.args.get("offset", 0))
            data = self.model.list(
                empresa_id=empresa_id,
                solicitante_id=solicitante_id,
                tipo_referencia=tipo_referencia,
                limit=limit,
                offset=offset
            )
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

    # ======================== ENDPOINTS JSON-ARRAY ========================
    def obtener_por_solicitante(self):
        """Obtiene el registro de referencias (contenedor JSON) para un solicitante."""
        try:
            empresa_id = self._empresa_id()
            solicitante_id = request.args.get("solicitante_id")
            if not solicitante_id:
                raise ValueError("solicitante_id es requerido")

            data = self.model.get_by_solicitante(empresa_id=empresa_id, solicitante_id=int(solicitante_id))
            if not data:
                return jsonify({"ok": False, "error": "No hay referencias para el solicitante"}), 404
            return jsonify({"ok": True, "data": data})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500
    def agregar_referencia(self):
        """Agregar una referencia al arreglo JSON de un solicitante.
        Body: { solicitante_id, referencia: { ...campos... } }
        """
        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}
            solicitante_id = body.get("solicitante_id")
            if not solicitante_id:
                raise ValueError("solicitante_id es requerido")

            referencia_obj = body.get("referencia") or body.get("data") or {}
            if not isinstance(referencia_obj, dict) or not referencia_obj:
                raise ValueError("referencia es requerida y debe ser objeto")

            # Depuración y validación para evitar crear referencias vacías
            try:
                print(f"[REFERENCIAS][ADD] empresa_id={empresa_id} solicitante_id={solicitante_id} keys={list(referencia_obj.keys())}")
            except Exception:
                pass

            # Limpiar campos vacíos simples (strings vacíos)
            cleaned = {k: v for k, v in referencia_obj.items() if v not in (None, "", [])}
            # Validar que haya al menos un campo informativo además de tipo_referencia
            allowed_only = set(cleaned.keys()) <= {"tipo_referencia"}
            if allowed_only:
                return jsonify({
                    "ok": False,
                    "error": "La referencia no puede estar vacía: envía al menos un campo de información además de tipo_referencia",
                    "detalle": {"keys_recibidas": list(referencia_obj.keys())}
                }), 400

            data = self.model.add_referencia(
                empresa_id=empresa_id,
                solicitante_id=int(solicitante_id),
                referencia=cleaned,
            )
            return jsonify({"ok": True, "data": data}), 201
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def actualizar_referencia(self):
        """Actualizar campos de una referencia dentro del JSON.
        Body: { solicitante_id, referencia_id, updates: { ... } }
        """
        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or (request.form.to_dict() if request.form else {}) or {}
            solicitante_id = body.get("solicitante_id")
            referencia_id = body.get("referencia_id") or body.get("id")
            updates = body.get("updates") or body.get("data") or {}

            if not solicitante_id:
                raise ValueError("solicitante_id es requerido")
            if referencia_id is None:
                raise ValueError("referencia_id es requerido")
            if not isinstance(updates, dict) or not updates:
                raise ValueError("updates es requerido y debe ser objeto")

            # Ya no se requiere id_tipo_referencia; solo referencia_id + campos de información

            data = self.model.update_referencia_fields(
                empresa_id=empresa_id,
                solicitante_id=int(solicitante_id),
                referencia_id=int(referencia_id),
                updates=updates,
            )
            if data is None:
                # Ayuda de depuración: devolver ids disponibles
                cont = self.model.get_by_solicitante(empresa_id=empresa_id, solicitante_id=int(solicitante_id))
                ids_disponibles = []
                try:
                    refs = (cont or {}).get("detalle_referencia", {}).get("referencias", [])
                    ids_disponibles = [r.get("referencia_id") for r in refs]
                except Exception:
                    pass
                return jsonify({
                    "ok": False,
                    "error": "Referencia no encontrada",
                    "detalle": {
                        "referencia_id_solicitado": int(referencia_id),
                        "ids_disponibles": ids_disponibles
                    }
                }), 404
            return jsonify({"ok": True, "data": data})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def eliminar_referencia(self):
        """Eliminar una referencia del JSON.
        Body: { solicitante_id, referencia_id }
        """
        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or (request.form.to_dict() if request.form else {}) or {}
            solicitante_id = body.get("solicitante_id") or request.args.get("solicitante_id")
            referencia_id = body.get("referencia_id") or body.get("id") or request.args.get("referencia_id") or request.args.get("id")

            if not solicitante_id:
                raise ValueError("solicitante_id es requerido")
            if referencia_id is None:
                raise ValueError("referencia_id es requerido")
            data = self.model.delete_referencia(
                empresa_id=empresa_id,
                solicitante_id=int(solicitante_id),
                referencia_id=int(referencia_id),
            )
            if data is None:
                return jsonify({"ok": False, "error": "Referencia no encontrada"}), 404
            return jsonify({"ok": True, "data": data})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500
