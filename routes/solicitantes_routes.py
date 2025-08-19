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


@solicitantes.route("/<int:id>/traer-todos-registros", methods=["GET"])
@cross_origin()
def get_todos_registros_solicitante(id: int):
    return con_solicitantes.traer_todos_registros(id)


@solicitantes.route("/crear-registro-completo", methods=["POST"])
@cross_origin()
def crear_registro_completo():
    """Crear un registro completo con todas las entidades relacionadas"""
    return con_solicitantes.crear_registro_completo()