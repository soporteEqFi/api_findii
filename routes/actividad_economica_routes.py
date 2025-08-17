from flask import Blueprint
from flask_cors import cross_origin

from controllers.actividad_economica_controller import ActividadEconomicaController

actividad_economica = Blueprint("actividad_economica", __name__)
con_actividad = ActividadEconomicaController()


@actividad_economica.route("/", methods=["GET"])
@cross_origin()
def list_actividad_economica():
    return con_actividad.list()


@actividad_economica.route("/", methods=["POST"])
@cross_origin()
def create_actividad_economica():
    return con_actividad.create()


@actividad_economica.route("/<int:id>", methods=["GET"])
@cross_origin()
def get_actividad_economica(id: int):
    return con_actividad.get_one(id)


@actividad_economica.route("/<int:id>", methods=["PATCH"])
@cross_origin()
def update_actividad_economica(id: int):
    return con_actividad.update(id)


@actividad_economica.route("/<int:id>", methods=["DELETE"])
@cross_origin()
def delete_actividad_economica(id: int):
    return con_actividad.delete(id)
