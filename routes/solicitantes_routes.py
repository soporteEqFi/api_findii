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


@solicitantes.route("/<int:id>/editar-registro-completo", methods=["PATCH"])
@cross_origin()
def editar_registro_completo(id: int):
    """Editar un registro completo con todas las entidades relacionadas"""
    return con_solicitantes.editar_registro_completo(id)


@solicitantes.route("/descargar-ventas", methods=["GET", "POST"])
@cross_origin()
def descargar_ventas_excel():
    """Descargar todos los solicitantes en formato Excel"""
    return con_solicitantes.descargar_ventas_excel()


@solicitantes.route("/<int:solicitante_id>/enviar-emails", methods=["POST"])
@cross_origin()
def enviar_emails_registro_completo(solicitante_id: int):
    """
    Envía los emails de confirmación después de que se hayan subido todos los documentos.

    Este endpoint debe ser llamado por el frontend después de subir todos los documentos.
    Los emails se enviarán con todos los documentos adjuntos.

    Body opcional (para pasar correos si no están en la BD):
    {
        "correo_asesor": "asesor@ejemplo.com",
        "nombre_asesor": "Nombre Asesor",
        "correo_banco_usuario": "banco@ejemplo.com",
        "nombre_banco_usuario": "Nombre Banco Usuario"
    }
    """
    return con_solicitantes.enviar_emails_registro_completo(solicitante_id)