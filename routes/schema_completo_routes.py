from flask import Blueprint
from flask_cors import cross_origin
from controllers.schema_completo_controller import SchemaCompletoController

# Inicializar controlador
con_schema = SchemaCompletoController()

# Crear blueprint
schema_completo = Blueprint('schema_completo', __name__)

@schema_completo.route('/ping', methods=['GET'])
@cross_origin()
def ping():
    """Endpoint de prueba para verificar que el blueprint funciona"""
    return {"ok": True, "message": "Schema completo blueprint funcionando"}, 200

@schema_completo.route('/<string:entity>', methods=['GET'])
@cross_origin()
def get_schema_completo(entity):
    """
    Obtiene esquema completo (campos fijos + dinámicos) para una entidad

    Ejemplo: GET /schema/solicitante?empresa_id=1
    """
    return con_schema.get_schema_completo(entity)
