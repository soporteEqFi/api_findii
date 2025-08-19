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


@json_fields.route("/definitions/<entity>/<json_field>", methods=["POST"])
@cross_origin()
def create_field_definitions(entity: str, json_field: str):
    """Crear/actualizar definiciones de campos dinámicos"""
    from flask import request, jsonify

    print("\n" + "="*80)
    print(f"🔄 POST /json/definitions/{entity}/{json_field}")
    print("="*80)

    # IMPRIMIR TODO EL REQUEST
    print(f"📋 URL COMPLETA: {request.url}")
    print(f"📋 PATH: {request.path}")
    print(f"📋 ARGS: {dict(request.args)}")
    print(f"📋 METHOD: {request.method}")

    # HEADERS
    print(f"\n🔖 HEADERS RECIBIDOS:")
    for header_name, header_value in request.headers:
        print(f"   {header_name}: {header_value}")

    # QUERY PARAMS
    print(f"\n🔍 QUERY PARAMS:")
    for key, value in request.args.items():
        print(f"   {key} = {value}")

    # BODY
    print(f"\n📦 BODY RAW:")
    try:
        raw_data = request.get_data(as_text=True)
        print(f"   Raw data: {raw_data}")
    except Exception as e:
        print(f"   Error leyendo raw data: {e}")

    print(f"\n📦 BODY JSON:")
    try:
        body = request.get_json(silent=True) or {}
        print(f"   Parsed JSON: {body}")
        print(f"   Tipo: {type(body)}")

        if isinstance(body, dict):
            print(f"   Claves: {list(body.keys())}")
            for key, value in body.items():
                print(f"   {key}: {value} (tipo: {type(value)})")
    except Exception as e:
        print(f"   Error parseando JSON: {e}")

    try:
        # EMPRESA ID
        empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
        print(f"\n📋 EMPRESA ID:")
        print(f"   De header X-Empresa-Id: {request.headers.get('X-Empresa-Id')}")
        print(f"   De query param: {request.args.get('empresa_id')}")
        print(f"   Empresa ID final: {empresa_id}")

        if not empresa_id:
            print("❌ Error: empresa_id no encontrado")
            return jsonify({"ok": False, "error": "empresa_id es requerido"}), 400

        empresa_id = int(empresa_id)
        print(f"   Empresa ID convertido: {empresa_id}")

        # DEFINITIONS
        body = request.get_json(silent=True) or {}
        definitions = body.get("definitions", [])

        print(f"\n🏗️ DEFINITIONS:")
        print(f"   Body completo: {body}")
        print(f"   Definitions extraídas: {definitions}")
        print(f"   Tipo definitions: {type(definitions)}")
        print(f"   Cantidad de definitions: {len(definitions) if isinstance(definitions, list) else 'No es lista'}")

        if isinstance(definitions, list):
            for idx, definition in enumerate(definitions):
                print(f"   Definition [{idx}]: {definition}")
                print(f"   Tipo: {type(definition)}")
                if isinstance(definition, dict):
                    print(f"   Claves: {list(definition.keys())}")

        # VALIDACIONES
        if not isinstance(definitions, list):
            print("❌ Error: definitions no es una lista")
            return jsonify({"ok": False, "error": "definitions debe ser una lista"}), 400

        if not definitions:
            print("❌ Error: definitions está vacía")
            return jsonify({"ok": False, "error": "definitions no puede estar vacía"}), 400

        # Validar que cada definición tenga los campos requeridos
        print(f"\n🔍 VALIDANDO DEFINITIONS:")
        for idx, definition in enumerate(definitions):
            print(f"   Validando definition {idx}: {definition}")
            if not isinstance(definition, dict):
                print(f"   ❌ Error en definición {idx}: no es objeto")
                return jsonify({"ok": False, "error": f"definitions[{idx}] debe ser un objeto"}), 400
            if "key" not in definition:
                print(f"   ❌ Error en definición {idx}: falta 'key'")
                return jsonify({"ok": False, "error": f"definitions[{idx}] debe incluir 'key'"}), 400
            print(f"   ✅ Definition {idx} válida: key='{definition['key']}'")

        print(f"\n💾 GUARDANDO EN BD:")
        print(f"   entity: {entity}")
        print(f"   json_column: {json_field}")
        print(f"   empresa_id: {empresa_id}")
        print(f"   items: {definitions}")

        result = schema_model.upsert_definitions(
            empresa_id=empresa_id,
            entity=entity,
            json_column=json_field,
            items=definitions
        )

        print(f"\n✅ RESULTADO:")
        print(f"   Registros procesados: {len(result)}")
        print(f"   Resultado completo: {result}")

        response_data = {
            "ok": True,
            "data": result,
            "message": f"Procesadas {len(definitions)} definiciones para {entity}.{json_field}"
        }

        print(f"\n📤 RESPUESTA A ENVIAR:")
        print(f"   {response_data}")
        print("="*80 + "\n")

        return jsonify(response_data)

    except ValueError as ve:
        print(f"\n❌ ERROR DE VALIDACIÓN: {ve}")
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(ve)}), 400
    except Exception as ex:
        print(f"\n💥 ERROR INESPERADO: {ex}")
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(ex)}), 500


@json_fields.route("/definitions/<entity>/<json_field>", methods=["PUT"])
@cross_origin()
def replace_field_definitions(entity: str, json_field: str):
    """Reemplazar todas las definiciones de campos dinámicos"""
    from flask import request, jsonify

    try:
        empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
        if not empresa_id:
            return jsonify({"ok": False, "error": "empresa_id es requerido"}), 400
        empresa_id = int(empresa_id)

        body = request.get_json(silent=True) or {}
        definitions = body.get("definitions", [])

        if not isinstance(definitions, list):
            return jsonify({"ok": False, "error": "definitions debe ser una lista"}), 400

        # Primero eliminar todas las definiciones existentes
        schema_model.delete_definition(
            empresa_id=empresa_id,
            entity=entity,
            json_column=json_field,
            key=None  # Elimina todas
        )

        # Luego crear las nuevas definiciones (si hay)
        if definitions:
            for idx, definition in enumerate(definitions):
                if not isinstance(definition, dict):
                    return jsonify({"ok": False, "error": f"definitions[{idx}] debe ser un objeto"}), 400
                if "key" not in definition:
                    return jsonify({"ok": False, "error": f"definitions[{idx}] debe incluir 'key'"}), 400

            result = schema_model.upsert_definitions(
                empresa_id=empresa_id,
                entity=entity,
                json_column=json_field,
                items=definitions
            )
        else:
            result = []

        return jsonify({"ok": True, "data": result})

    except ValueError as ve:
        return jsonify({"ok": False, "error": str(ve)}), 400
    except Exception as ex:
        return jsonify({"ok": False, "error": str(ex)}), 500


@json_fields.route("/definitions/<entity>/<json_field>/<key>", methods=["DELETE"])
@cross_origin()
def delete_field_definition(entity: str, json_field: str, key: str):
    """Eliminar una definición específica de campo dinámico"""
    from flask import request, jsonify

    try:
        empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
        if not empresa_id:
            return jsonify({"ok": False, "error": "empresa_id es requerido"}), 400
        empresa_id = int(empresa_id)

        deleted_count = schema_model.delete_definition(
            empresa_id=empresa_id,
            entity=entity,
            json_column=json_field,
            key=key
        )

        return jsonify({
            "ok": True,
            "data": {
                "deleted_count": deleted_count,
                "message": f"Eliminada definición de campo '{key}'"
            }
        })

    except ValueError as ve:
        return jsonify({"ok": False, "error": str(ve)}), 400
    except Exception as ex:
        return jsonify({"ok": False, "error": str(ex)}), 500


@json_fields.route("/definitions/<entity>/<json_field>", methods=["DELETE"])
@cross_origin()
def delete_all_field_definitions(entity: str, json_field: str):
    """Eliminar todas las definiciones de campos dinámicos de una entidad"""
    from flask import request, jsonify

    try:
        empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
        if not empresa_id:
            return jsonify({"ok": False, "error": "empresa_id es requerido"}), 400
        empresa_id = int(empresa_id)

        deleted_count = schema_model.delete_definition(
            empresa_id=empresa_id,
            entity=entity,
            json_column=json_field,
            key=None  # Elimina todas
        )

        return jsonify({
            "ok": True,
            "data": {
                "deleted_count": deleted_count,
                "message": f"Eliminadas todas las definiciones de {entity}.{json_field}"
            }
        })

    except ValueError as ve:
        return jsonify({"ok": False, "error": str(ve)}), 400
    except Exception as ex:
        return jsonify({"ok": False, "error": str(ex)}), 500


