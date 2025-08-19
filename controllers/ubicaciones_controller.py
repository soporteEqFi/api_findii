from __future__ import annotations

from flask import request, jsonify
from models.ubicaciones_model import UbicacionesModel
from utils.debug_helpers import (
    log_request_details, log_validation_results,
    log_data_to_save, log_operation_result, log_response, log_error
)


class UbicacionesController:
    def __init__(self):
        self.model = UbicacionesModel()

    def _empresa_id(self) -> int:
        empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
        if not empresa_id:
            raise ValueError("empresa_id es requerido")
        try:
            return int(empresa_id)
        except Exception as exc:
            raise ValueError("empresa_id debe ser entero") from exc

    def create(self):
        log_request_details("CREAR UBICACIÓN", "ubicacion")

        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}

            print(f"\n📋 EMPRESA ID: {empresa_id}")

            # Campos requeridos
            required_fields = ["solicitante_id", "ciudad_residencia", "departamento_residencia"]

            # Validar campos requeridos
            print(f"\n🔍 VERIFICANDO SOLICITANTE_ID:")
            print(f"   solicitante_id en body: {body.get('solicitante_id')}")
            print(f"   Tipo: {type(body.get('solicitante_id'))}")

            if not log_validation_results(required_fields, body):
                print(f"\n❌ CAMPOS FALTANTES DETECTADOS:")
                for field in required_fields:
                    value = body.get(field)
                    if not value:
                        print(f"   ❌ {field}: {value}")
                raise ValueError("Faltan campos requeridos")

            print(f"\n✅ VALIDACIÓN EXITOSA - Todos los campos presentes")

            # Preparar datos para guardar
            datos_a_guardar = {
                "empresa_id": empresa_id,
                "solicitante_id": body["solicitante_id"],
                "ciudad_residencia": body["ciudad_residencia"],
                "departamento_residencia": body["departamento_residencia"],
                "detalle_direccion": body.get("detalle_direccion"),
            }

            log_data_to_save(datos_a_guardar)

            # Crear en BD
            data = self.model.create(**datos_a_guardar)

            log_operation_result(data, "UBICACIÓN CREADA")

            response_data = {"ok": True, "data": data}
            log_response(response_data)

            return jsonify(response_data), 201
        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
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
            limit = int(request.args.get("limit", 50))
            offset = int(request.args.get("offset", 0))
            data = self.model.list(
                empresa_id=empresa_id,
                solicitante_id=solicitante_id,
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
