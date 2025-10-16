from flask import Blueprint, jsonify
from flask_cors import cross_origin
import functools

from controllers.json_fields_controller import JSONFieldsController
from models.json_schema_model import JSONSchemaModel

def handle_errors(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(f"💥 ERROR en {f.__name__}: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"ok": False, "error": str(e)}), 500
    return decorated_function


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
@handle_errors
def get_json_schema(entity: str, json_field: str):
    from flask import request, jsonify

    empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
    if not empresa_id:
        return jsonify({"ok": False, "error": "empresa_id es requerido"}), 400

    try:
        empresa_id = int(empresa_id)
    except ValueError:
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
    # print(f"📋 PATH: {request.path}")
    # print(f"📋 ARGS: {dict(request.args)}")
    print(f"📋 METHOD: {request.method}")

    # HEADERS
    # print(f"\n🔖 HEADERS RECIBIDOS:")
    # for header_name, header_value in request.headers:
    #     print(f"   {header_name}: {header_value}")

    # # QUERY PARAMS
    # print(f"\n🔍 QUERY PARAMS:")
    # for key, value in request.args.items():
    #     print(f"   {key} = {value}")

    # BODY
    # print(f"\n📦 BODY RAW:")
    # try:
    #     raw_data = request.get_data(as_text=True)
    #     print(f"   Raw data: {raw_data}")
    # except Exception as e:
    #     print(f"   Error leyendo raw data: {e}")

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

        # print(f"\n🏗️ DEFINITIONS:")
        # print(f"   Body completo: {body}")
        # print(f"   Definitions extraídas: {definitions}")
        # print(f"   Tipo definitions: {type(definitions)}")
        # print(f"   Cantidad de definitions: {len(definitions) if isinstance(definitions, list) else 'No es lista'}")

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


@json_fields.route("/definitions/<entity>/<json_field>/reorder", methods=["PATCH"])
@cross_origin()
@handle_errors
def reorder_field_definitions(entity: str, json_field: str):
    """Actualizar el order_index de múltiples campos dinámicos"""
    from flask import request, jsonify

    try:
        empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
        if not empresa_id:
            return jsonify({"ok": False, "error": "empresa_id es requerido"}), 400
        empresa_id = int(empresa_id)

        body = request.get_json(silent=True) or {}
        field_orders = body.get("field_orders", [])

        print(f"🔄 Reordenando campos para {entity}.{json_field}")
        print(f"📋 Nuevos órdenes: {field_orders}")

        if not isinstance(field_orders, list):
            return jsonify({"ok": False, "error": "field_orders debe ser una lista"}), 400

        if not field_orders:
            return jsonify({"ok": False, "error": "field_orders no puede estar vacía"}), 400

        # Validar estructura de field_orders
        for idx, field_order in enumerate(field_orders):
            if not isinstance(field_order, dict):
                return jsonify({"ok": False, "error": f"field_orders[{idx}] debe ser un objeto"}), 400
            if "key" not in field_order or "order_index" not in field_order:
                return jsonify({"ok": False, "error": f"field_orders[{idx}] debe incluir 'key' y 'order_index'"}), 400

        # Actualizar cada campo con su nuevo order_index
        updated_fields = []
        for field_order in field_orders:
            key = field_order["key"]
            new_order_index = field_order["order_index"]

            # Buscar la definición existente por key
            existing_defs = schema_model.get_schema(
                empresa_id=empresa_id,
                entity=entity,
                json_column=json_field
            )

            existing_def = next((d for d in existing_defs if d["key"] == key), None)
            if existing_def:
                # Actualizar usando el ID de la definición existente
                result = schema_model.update_definition(
                    definition_id=existing_def["id"],
                    updates={"order_index": new_order_index}
                )
                updated_fields.append(result)
                print(f"✅ Campo '{key}' actualizado a order_index {new_order_index}")
            else:
                print(f"⚠️ Campo '{key}' no encontrado, saltando...")

        return jsonify({
            "ok": True,
            "data": updated_fields,
            "message": f"Reordenados {len(updated_fields)} campos para {entity}.{json_field}"
        })

    except ValueError as ve:
        return jsonify({"ok": False, "error": str(ve)}), 400
    except Exception as ex:
        return jsonify({"ok": False, "error": str(ex)}), 500


@json_fields.route("/definitions/<definition_id>", methods=["PATCH"])
@cross_origin()
@handle_errors
def update_field_definition(definition_id: str):
    """Actualizar una definición específica de campo dinámico por ID"""
    from flask import request, jsonify

    # Validar que definition_id sea un UUID válido
    import re
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
    if not uuid_pattern.match(definition_id):
        print(f"❌ ERROR: definition_id debe ser un UUID válido, recibido: {definition_id}")
        return jsonify({
            "ok": False,
            "error": f"definition_id debe ser un UUID válido, recibido: {definition_id}"
        }), 400

    print("\n" + "="*80)
    print(f"🔄 PATCH /json/definitions/{definition_id}")
    print("="*80)

    # IMPRIMIR TODO EL REQUEST
    print(f"📋 URL COMPLETA: {request.url}")
    # print(f"📋 PATH: {request.path}")
    # print(f"📋 ARGS: {dict(request.args)}")
    print(f"📋 METHOD: {request.method}")

    # # HEADERS
    # print(f"\n🔖 HEADERS RECIBIDOS:")
    # for header_name, header_value in request.headers:
    #     print(f"   {header_name}: {header_value}")

    # # BODY
    # print(f"\n📦 BODY RAW:")
    # try:
    #     raw_data = request.get_data(as_text=True)
    #     print(f"   Raw data: {raw_data}")
    # except Exception as e:
    #     print(f"   Error leyendo raw data: {e}")

    # print(f"\n📦 BODY JSON:")
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
        # EMPRESA ID (opcional para validación)
        empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
        if empresa_id:
            empresa_id = int(empresa_id)
            print(f"\n📋 EMPRESA ID: {empresa_id}")

        # BODY
        body = request.get_json(silent=True) or {}
        print(f"\n📦 BODY RECIBIDO: {body}")

        # VALIDACIONES
        if not isinstance(body, dict):
            print("❌ Error: body debe ser un objeto")
            return jsonify({"ok": False, "error": "body debe ser un objeto"}), 400

        if not body:
            print("❌ Error: body está vacío")
            return jsonify({"ok": False, "error": "body no puede estar vacío"}), 400

        # Validar campos permitidos para actualización
        campos_permitidos = {
            "conditional_on", "type", "required", "list_values",
            "description", "default_value", "order_index"  # Agregar order_index
        }

        campos_invalidos = set(body.keys()) - campos_permitidos
        if campos_invalidos:
            print(f"❌ Error: campos no permitidos: {campos_invalidos}")
            return jsonify({
                "ok": False,
                "error": f"Campos no permitidos para actualización: {list(campos_invalidos)}"
            }), 400

        print(f"\n✅ CAMPOS VÁLIDOS PARA ACTUALIZAR:")
        for campo, valor in body.items():
            print(f"   {campo}: {valor}")
            # Print especial para conditional_on
            if campo == "conditional_on":
                print(f"   🎯 CONDITIONAL_ON ACTUALIZADO: {valor}")

        print(f"\n💾 ACTUALIZANDO EN BD:")
        print(f"   definition_id: {definition_id}")
        print(f"   updates: {body}")

        result = schema_model.update_definition(
            definition_id=definition_id,
            updates=body
        )

        print(f"\n✅ RESULTADO:")
        print(f"   Definición actualizada: {result}")

        # Print especial si se actualizó conditional_on
        if "conditional_on" in body:
            print(f"   🎯 CONDITIONAL_ON ACTUALIZADO EXITOSAMENTE para definición {definition_id}")
            print(f"   📋 Nuevo valor: {body['conditional_on']}")

        response_data = {
            "ok": True,
            "data": result,
            "message": f"Definición {definition_id} actualizada correctamente"
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


