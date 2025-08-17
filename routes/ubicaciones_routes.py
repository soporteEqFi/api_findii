from flask import Blueprint
from flask_cors import cross_origin

from controllers.ubicaciones_controller import UbicacionesController

ubicaciones = Blueprint("ubicaciones", __name__)
con_ubicaciones = UbicacionesController()


@ubicaciones.route("/", methods=["GET"])
@cross_origin()
def list_ubicaciones():
    return con_ubicaciones.list()


@ubicaciones.route("/", methods=["POST"])
@cross_origin()
def create_ubicacion():
    return con_ubicaciones.create()


@ubicaciones.route("/<int:id>", methods=["GET"])
@cross_origin()
def get_ubicacion(id: int):
    return con_ubicaciones.get_one(id)


@ubicaciones.route("/<int:id>", methods=["PATCH"])
@cross_origin()
def update_ubicacion(id: int):
    return con_ubicaciones.update(id)


@ubicaciones.route("/<int:id>", methods=["DELETE"])
@cross_origin()
def delete_ubicacion(id: int):
    return con_ubicaciones.delete(id)
