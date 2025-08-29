from flask import Blueprint
from flask_cors import cross_origin
from controllers.configuraciones_controller import ConfiguracionesController

configuraciones = Blueprint('configuraciones', __name__)
con_config = ConfiguracionesController()

@configuraciones.route('/ping', methods=['GET'])
@cross_origin()
def ping():
    return {"ok": True, "message": "Configuraciones blueprint funcionando"}, 200

@configuraciones.route('/<string:categoria>', methods=['GET'])
@cross_origin()
def obtener_por_categoria(categoria):
    """
    Obtener configuración por categoría específica

    Ejemplo: GET /configuraciones/ciudades?empresa_id=1
    """
    return con_config.obtener_por_categoria(categoria)

@configuraciones.route('/', methods=['GET'])
@cross_origin()
def obtener_todas():
    """
    Obtener todas las configuraciones de la empresa

    Ejemplo: GET /configuraciones?empresa_id=1
    """
    return con_config.obtener_todas()

@configuraciones.route('/columnas-tabla', methods=['GET'])
@cross_origin()
def obtener_columnas_tabla():
    """
    Obtener configuración de columnas para tablas

    Ejemplo: GET /configuraciones/columnas-tabla?empresa_id=1
    """
    return con_config.obtener_columnas_tabla()
