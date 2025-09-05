from flask import Blueprint
from flask_cors import cross_origin

from controllers.referencias_controller import ReferenciasController

referencias = Blueprint("referencias", __name__)
con_referencias = ReferenciasController()


@referencias.route("/", methods=["GET"])
@cross_origin()
def list_referencias():
    return con_referencias.list()


@referencias.route("/", methods=["POST"])
@cross_origin()
def create_referencia():
    return con_referencias.create()


@referencias.route("/<int:id>", methods=["GET"])
@cross_origin()
def get_referencia(id: int):
    return con_referencias.get_one(id)


@referencias.route("/<int:id>", methods=["PATCH"])
@cross_origin()
def update_referencia(id: int):
    return con_referencias.update(id)


@referencias.route("/<int:id>", methods=["DELETE"])
@cross_origin()
def delete_referencia(id: int):
    return con_referencias.delete(id)


# ===================== RUTAS PARA JSON-ARRAY =====================
@referencias.route("/por-solicitante", methods=["GET"])
@cross_origin()
def obtener_referencias_por_solicitante():
    return con_referencias.obtener_por_solicitante()

@referencias.route("/agregar", methods=["POST"])
@cross_origin()
def agregar_referencia_json():
    return con_referencias.agregar_referencia()


@referencias.route("/actualizar", methods=["PATCH"])
@cross_origin()
def actualizar_referencia_json():
    return con_referencias.actualizar_referencia()


@referencias.route("/eliminar", methods=["DELETE"])
@cross_origin()
def eliminar_referencia_json():
    return con_referencias.eliminar_referencia()
