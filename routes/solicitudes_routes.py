from flask import Blueprint
from flask_cors import cross_origin

from controllers.solicitudes_controller import SolicitudesController


solicitudes = Blueprint("solicitudes", __name__)
con_solicitudes = SolicitudesController()


@solicitudes.route("/", methods=["GET"])
@cross_origin()
def list_solicitudes():
    return con_solicitudes.list()


@solicitudes.route("/", methods=["POST"])
@cross_origin()
def create_solicitud():
    return con_solicitudes.create()


@solicitudes.route("/<int:id>", methods=["GET"])
@cross_origin()
def get_solicitud(id: int):
    return con_solicitudes.get_one(id)


@solicitudes.route("/<int:id>", methods=["PATCH"])
@cross_origin()
def update_solicitud(id: int):
    return con_solicitudes.update(id)


@solicitudes.route("/<int:id>", methods=["DELETE"])
@cross_origin()
def delete_solicitud(id: int):
    return con_solicitudes.delete(id)


@solicitudes.route("/actualizar-estado", methods=["PATCH"])
@cross_origin()
def actualizar_estado_solicitud():
    return con_solicitudes.actualizar_estado()


@solicitudes.route("/asignar-banco", methods=["PATCH"])
@cross_origin()
def asignar_banco_solicitud():
    return con_solicitudes.asignar_banco()


@solicitudes.route("/<int:id>/observaciones", methods=["GET"])
@cross_origin()
def obtener_observaciones(id: int):
    """
    Obtiene el historial de observaciones de una solicitud
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID de la solicitud
    responses:
      200:
        description: Lista de observaciones
        schema:
          type: object
          properties:
            ok:
              type: boolean
            data:
              type: object
              properties:
                solicitud_id:
                  type: integer
                total_observaciones:
                  type: integer
                observaciones:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                      fecha:
                        type: string
                      observacion:
                        type: string
                      tipo:
                        type: string
                      usuario_nombre:
                        type: string
      404:
        description: Solicitud no encontrada
      500:
        description: Error del servidor
    """
    return con_solicitudes.obtener_observaciones(id)


@solicitudes.route("/<int:id>/observaciones", methods=["POST"])
@cross_origin()
def agregar_observacion(id: int):
    """
    Agrega una observación a una solicitud
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID de la solicitud
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - observacion
          properties:
            observacion:
              type: string
              description: Texto de la observación
            tipo:
              type: string
              enum: [comentario, cambio_estado, sistema, advertencia]
              default: comentario
              description: Tipo de observación
    responses:
      200:
        description: Observación agregada exitosamente
      400:
        description: Error en la petición o datos inválidos
      401:
        description: No autorizado
      404:
        description: Solicitud no encontrada
    """
    return con_solicitudes.agregar_observacion(id)


@solicitudes.route("/bancos-disponibles", methods=["GET"])
@cross_origin()
def obtener_bancos_disponibles():
    return con_solicitudes.obtener_bancos_disponibles()


@solicitudes.route("/ciudades-disponibles", methods=["GET"])
@cross_origin()
def obtener_ciudades_disponibles():
    return con_solicitudes.obtener_ciudades_disponibles()


@solicitudes.route("/estados-disponibles", methods=["GET"])
@cross_origin()
def obtener_estados_disponibles():
    return con_solicitudes.obtener_estados_disponibles()


