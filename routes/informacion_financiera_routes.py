from flask import Blueprint
from flask_cors import cross_origin

from controllers.informacion_financiera_controller import InformacionFinancieraController

informacion_financiera = Blueprint("informacion_financiera", __name__)
con_financiera = InformacionFinancieraController()


@informacion_financiera.route("/", methods=["GET"])
@cross_origin()
def list_informacion_financiera():
    return con_financiera.list()


@informacion_financiera.route("/", methods=["POST"])
@cross_origin()
def create_informacion_financiera():
    return con_financiera.create()


@informacion_financiera.route("/<int:id>", methods=["GET"])
@cross_origin()
def get_informacion_financiera(id: int):
    return con_financiera.get_one(id)


@informacion_financiera.route("/<int:id>", methods=["PATCH"])
@cross_origin()
def update_informacion_financiera(id: int):
    return con_financiera.update(id)


@informacion_financiera.route("/<int:id>", methods=["DELETE"])
@cross_origin()
def delete_informacion_financiera(id: int):
    return con_financiera.delete(id)
