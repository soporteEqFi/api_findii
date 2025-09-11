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

@configuraciones.route('/categorias', methods=['GET'])
@cross_origin()
def obtener_categorias():
    """
    Obtener lista de categorías disponibles

    Ejemplo: GET /configuraciones/categorias?empresa_id=1
    """
    return con_config.obtener_categorias()

@configuraciones.route('/columnas-tabla', methods=['GET'])
@cross_origin()
def obtener_columnas_tabla():
    """
    Obtener configuración de columnas para tablas

    Ejemplo: GET /configuraciones/columnas-tabla?empresa_id=1
    """
    return con_config.obtener_columnas_tabla()

@configuraciones.route('/columnas-tabla', methods=['PUT'])
@cross_origin()
def actualizar_columnas_tabla():
    """
    Actualizar configuración completa de columnas

    Ejemplo: PUT /configuraciones/columnas-tabla?empresa_id=1
    Body: {"columnas": [{"nombre": "Nombre", "activo": true, "orden": 0}]}
    """
    return con_config.actualizar_columnas_tabla()

@configuraciones.route('/columnas-tabla/agregar', methods=['POST'])
@cross_origin()
def agregar_columna():
    """
    Agregar una nueva columna a la configuración

    Ejemplo: POST /configuraciones/columnas-tabla/agregar?empresa_id=1
    Body: {"nombre": "Nueva Columna"}
    """
    return con_config.agregar_columna()

@configuraciones.route('/<string:categoria>', methods=['PUT'])
@cross_origin()
def actualizar_categoria(categoria):
    """
    Actualizar configuración de una categoría existente o crear nueva

    Ejemplo: PUT /configuraciones/ciudades?empresa_id=1
    Body: {"configuracion": ["Bogotá", "Medellín", "Cali"], "descripcion": "Ciudades disponibles"}
    """
    return con_config.actualizar_categoria(categoria)

@configuraciones.route('/<string:categoria>', methods=['POST'])
@cross_origin()
def crear_categoria(categoria):
    """
    Crear nueva categoría de configuración

    Ejemplo: POST /configuraciones/tipos_documento?empresa_id=1
    Body: {"configuracion": ["Cédula", "Pasaporte"], "descripcion": "Tipos de documento"}
    """
    return con_config.crear_categoria(categoria)

@configuraciones.route('/<string:categoria>', methods=['DELETE'])
@cross_origin()
def eliminar_categoria(categoria):
    """
    Eliminar categoría de configuración (marcar como inactiva)

    Ejemplo: DELETE /configuraciones/ciudades?empresa_id=1
    """
    return con_config.eliminar_categoria(categoria)