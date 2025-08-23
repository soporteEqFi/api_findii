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


@solicitudes.route("/bancos-disponibles", methods=["GET"])
@cross_origin()
def obtener_bancos_disponibles():
    return con_solicitudes.obtener_bancos_disponibles()


@solicitudes.route("/ciudades-disponibles", methods=["GET"])
@cross_origin()
def obtener_ciudades_disponibles():
    return con_solicitudes.obtener_ciudades_disponibles()


