from flask import Blueprint
from flask_cors import cross_origin

from controllers.solicitantes_controller import SolicitantesController

solicitantes = Blueprint("solicitantes", __name__)
con_solicitantes = SolicitantesController()


@solicitantes.route("/", methods=["GET"])
@cross_origin()
def list_solicitantes():
    return con_solicitantes.list()


@solicitantes.route("/", methods=["POST"])
@cross_origin()
def create_solicitante():
    return con_solicitantes.create()


@solicitantes.route("/<int:id>", methods=["GET"])
@cross_origin()
def get_solicitante(id: int):
    return con_solicitantes.get_one(id)


@solicitantes.route("/<int:id>", methods=["PATCH"])
@cross_origin()
def update_solicitante(id: int):
    return con_solicitantes.update(id)


@solicitantes.route("/<int:id>", methods=["DELETE"])
@cross_origin()
def delete_solicitante(id: int):
    return con_solicitantes.delete(id)
