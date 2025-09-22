from flask import Blueprint
from flask_cors import cross_origin

from controllers.usuarios_controller import UsuariosController

usuarios = Blueprint("usuarios", __name__)
con_usuarios = UsuariosController()


@usuarios.route("/", methods=["GET"])
@cross_origin()
def list_usuarios():
    """Lista todos los usuarios de una empresa."""
    return con_usuarios.list()


@usuarios.route("/", methods=["POST"])
@cross_origin()
def create_usuario():
    """Crea un nuevo usuario para una empresa."""
    return con_usuarios.create()


@usuarios.route("/<int:id>", methods=["GET"])
@cross_origin()
def get_usuario(id):
    """Obtiene un usuario específico por ID."""
    return con_usuarios.get_one(id)


@usuarios.route("/<int:id>", methods=["PUT", "PATCH"])
@cross_origin()
def update_usuario(id):
    """Actualiza un usuario específico por ID."""
    return con_usuarios.update(id)


@usuarios.route("/<int:id>", methods=["DELETE"])
@cross_origin()
def delete_usuario(id):
    """Elimina un usuario específico por ID."""
    return con_usuarios.delete(id)


@usuarios.route("/<int:supervisor_id>/team", methods=["GET"])
@cross_origin()
def get_team_members(supervisor_id):
    """Obtiene los miembros del equipo de un supervisor."""
    return con_usuarios.get_team_members(supervisor_id)
