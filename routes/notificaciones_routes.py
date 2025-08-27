from flask import Blueprint
from flask_cors import cross_origin

from controllers.notificaciones_controller import NotificacionesController

notificaciones = Blueprint("notificaciones", __name__)
con_notificaciones = NotificacionesController()


@notificaciones.route("/", methods=["GET"])
@cross_origin()
def list_notificaciones():
    """Lista notificaciones con filtros opcionales."""
    return con_notificaciones.list()


@notificaciones.route("", methods=["GET"])
@cross_origin()
def list_notificaciones_no_slash():
    """Lista notificaciones con filtros opcionales (sin barra final)."""
    return con_notificaciones.list()


@notificaciones.route("/", methods=["POST"])
@cross_origin()
def create_notificacion():
    """Crea una nueva notificación."""
    return con_notificaciones.create()


@notificaciones.route("", methods=["POST"])
@cross_origin()
def create_notificacion_no_slash():
    """Crea una nueva notificación (sin barra final)."""
    return con_notificaciones.create()


@notificaciones.route("/<int:id>", methods=["GET"])
@cross_origin()
def get_notificacion(id):
    """Obtiene una notificación específica."""
    return con_notificaciones.get_one(id)


@notificaciones.route("/<int:id>", methods=["PUT", "PATCH"])
@cross_origin()
def update_notificacion(id):
    """Actualiza una notificación específica."""
    return con_notificaciones.update(id)


@notificaciones.route("/<int:id>", methods=["DELETE"])
@cross_origin()
def delete_notificacion(id):
    """Elimina una notificación específica."""
    return con_notificaciones.delete(id)


@notificaciones.route("/<int:id>/marcar-leida", methods=["PATCH"])
@cross_origin()
def marcar_notificacion_leida(id):
    """Marca una notificación como leída."""
    return con_notificaciones.marcar_leida(id)


@notificaciones.route("/pendientes", methods=["GET"])
@cross_origin()
def get_notificaciones_pendientes():
    """Obtiene notificaciones pendientes."""
    return con_notificaciones.pendientes()
