from flask import Blueprint
from flask_cors import cross_origin

from controllers.json_fields_controller import JSONFieldsController
from models.json_schema_model import JSONSchemaModel


json_fields = Blueprint("json_fields", __name__)
con_json = JSONFieldsController()
schema_model = JSONSchemaModel()


@json_fields.route("/ping", methods=["GET"])
@cross_origin()
def ping():
    return {"ok": True}

@json_fields.route("/<entity>/<int:record_id>/<json_field>", methods=["GET"])
@cross_origin()
def get_json_field(entity: str, record_id: int, json_field: str):
    return con_json.get_json(entity=entity, record_id=record_id, json_field=json_field)


@json_fields.route("/<entity>/<int:record_id>/<json_field>", methods=["PATCH"])
@cross_origin()
def patch_json_field(entity: str, record_id: int, json_field: str):
    return con_json.patch_json(entity=entity, record_id=record_id, json_field=json_field)


@json_fields.route("/<entity>/<int:record_id>/<json_field>", methods=["DELETE"])
@cross_origin()
def delete_json_field(entity: str, record_id: int, json_field: str):
    return con_json.delete_json(entity=entity, record_id=record_id, json_field=json_field)


@json_fields.route("/schema/<entity>/<json_field>", methods=["GET"])
@cross_origin()
def get_json_schema(entity: str, json_field: str):
    from flask import request, jsonify

    empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
    if not empresa_id:
        return jsonify({"ok": False, "error": "empresa_id es requerido"}), 400
    try:
        empresa_id = int(empresa_id)
    except Exception:
        return jsonify({"ok": False, "error": "empresa_id debe ser entero"}), 400

    defs = schema_model.get_schema(empresa_id=empresa_id, entity=entity, json_column=json_field)
    return jsonify({"ok": True, "data": defs})


