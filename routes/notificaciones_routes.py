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


@notificaciones.route("/tipos-configurados", methods=["GET"])
@cross_origin()
def get_tipos_configurados():
    """Obtiene los tipos, estados y prioridades de notificaciones configurados para la empresa."""
    try:
        from flask import request, jsonify

        empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
        if not empresa_id:
            return jsonify({"ok": False, "error": "empresa_id es requerido"}), 400

        empresa_id = int(empresa_id)

        # Obtener configuración de notificaciones
        config = con_notificaciones.model.get_configuracion_notificaciones(empresa_id)

        if not config:
            return jsonify({"ok": False, "error": "No se encontró configuración de notificaciones para la empresa"}), 404

        config_data = config.get("configuracion", {})
        tipos_disponibles = config_data.get("tipos_disponibles", [])
        estados_disponibles = config_data.get("estados_disponibles", [])
        prioridades_disponibles = config_data.get("prioridades_disponibles", [])
        estados_actuales_disponibles = config_data.get("estados_actuales_disponibles", [])
        acciones_requeridas_disponibles = config_data.get("acciones_requeridas_disponibles", [])
        configuracion_general = config_data.get("configuracion_general", {})

        return jsonify({
            "ok": True,
            "data": {
                "tipos": tipos_disponibles,
                "estados": estados_disponibles,
                "prioridades": prioridades_disponibles,
                "estadosActuales": estados_actuales_disponibles,
                "accionesRequeridas": acciones_requeridas_disponibles,
                "configuracion_general": configuracion_general,
                "configuracion_completa": config_data
            }
        })

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500