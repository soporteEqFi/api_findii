from flask import Blueprint
from flask_cors import cross_origin

from controllers.documentos_controller import DocumentosController


documentos = Blueprint("documentos", __name__)
con_documentos = DocumentosController()


@documentos.route("/", methods=["GET"])
@cross_origin()
def list_documentos():
    return con_documentos.list()


@documentos.route("/", methods=["POST"])
@cross_origin()
def create_documento():
    return con_documentos.create()


@documentos.route("/<int:id>", methods=["DELETE"])
@cross_origin()
def delete_documento(id: int):
    return con_documentos.delete(id)


@documentos.route("/<int:id>", methods=["PATCH"])
@cross_origin()
def update_documento(id: int):
    return con_documentos.update(id)
