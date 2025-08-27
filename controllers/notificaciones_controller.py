from __future__ import annotations

from flask import request, jsonify
from models.notificaciones_model import NotificacionesModel
from utils.debug_helpers import (
    log_request_details, log_operation_result, log_response, log_error
)

class NotificacionesController:
    def __init__(self):
        self.model = NotificacionesModel()

    def _empresa_id(self) -> int:
        """Obtiene el empresa_id de los headers o query parameters."""
        empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
        if not empresa_id:
            raise ValueError("empresa_id es requerido")
        try:
            return int(empresa_id)
        except Exception as exc:
            raise ValueError("empresa_id debe ser entero") from exc

    def list(self):
        """Lista notificaciones con filtros opcionales."""
        log_request_details("LISTAR NOTIFICACIONES", "notificaciones")

        try:
            empresa_id = self._empresa_id()
            print(f"\n📋 EMPRESA ID: {empresa_id}")

            # Obtener filtros de query params
            filtros = {}
            for param in ["tipo", "estado", "solicitud_id", "usuario_id", "prioridad"]:
                valor = request.args.get(param)
                if valor:
                    if param in ["solicitud_id", "usuario_id"]:
                        try:
                            filtros[param] = int(valor)
                        except ValueError:
                            return jsonify({"ok": False, "error": f"{param} debe ser un número entero"}), 400
                    else:
                        filtros[param] = valor

            # Obtener notificaciones
            notificaciones = self.model.list(empresa_id, **filtros)

            log_operation_result(notificaciones, f"NOTIFICACIONES OBTENIDAS: {len(notificaciones)}")

            response_data = {"ok": True, "data": notificaciones}
            log_response(response_data)

            return jsonify(response_data)

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def get_one(self, id: int):
        """Obtiene una notificación específica."""
        log_request_details(f"OBTENER NOTIFICACIÓN {id}", "notificaciones")

        try:
            empresa_id = self._empresa_id()
            print(f"\n📋 EMPRESA ID: {empresa_id}")
            print(f"🔔 NOTIFICACIÓN ID: {id}")

            # Obtener notificación específica
            notificacion = self.model.get_by_id(notificacion_id=id, empresa_id=empresa_id)

            if not notificacion:
                log_error("Notificación no encontrada", "NO ENCONTRADO")
                return jsonify({"ok": False, "error": "Notificación no encontrada"}), 404

            log_operation_result(notificacion, "NOTIFICACIÓN OBTENIDA")

            response_data = {"ok": True, "data": notificacion}
            log_response(response_data)

            return jsonify(response_data)

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def create(self):
        """Crea una nueva notificación."""
        log_request_details("CREAR NOTIFICACIÓN", "notificaciones")

        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}

            print(f"\n📋 EMPRESA ID: {empresa_id}")
            print(f"📝 DATOS RECIBIDOS: {body}")

            # Validar campos requeridos
            campos_requeridos = ["tipo", "titulo", "mensaje", "fecha_recordatorio"]
            for campo in campos_requeridos:
                if campo not in body:
                    log_error(f"Campo requerido faltante: {campo}", "ERROR DE VALIDACIÓN")
                    return jsonify({"ok": False, "error": f"Campo requerido faltante: {campo}"}), 400

            # Crear notificación
            notificacion_creada = self.model.create(empresa_id=empresa_id, **body)

            if not notificacion_creada:
                log_error("No se pudo crear la notificación", "ERROR DE CREACIÓN")
                return jsonify({"ok": False, "error": "No se pudo crear la notificación. Verifica que los datos sean válidos según la configuración."}), 500

            log_operation_result(notificacion_creada, "NOTIFICACIÓN CREADA")

            response_data = {"ok": True, "data": notificacion_creada}
            log_response(response_data)

            return jsonify(response_data), 201

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def update(self, id: int):
        """Actualiza una notificación específica."""
        log_request_details(f"ACTUALIZAR NOTIFICACIÓN {id}", "notificaciones")

        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}

            print(f"\n📋 EMPRESA ID: {empresa_id}")
            print(f"🔔 NOTIFICACIÓN ID: {id}")
            print(f"📝 DATOS A ACTUALIZAR: {body}")

            # Validar que hay datos para actualizar
            if not body:
                log_error("No hay datos para actualizar", "ERROR DE VALIDACIÓN")
                return jsonify({"ok": False, "error": "No hay datos para actualizar"}), 400

            # Actualizar notificación
            notificacion_actualizada = self.model.update(notificacion_id=id, empresa_id=empresa_id, **body)

            if not notificacion_actualizada:
                log_error("Notificación no encontrada o no se pudo actualizar", "NO ENCONTRADO")
                return jsonify({"ok": False, "error": "Notificación no encontrada o no se pudo actualizar"}), 404

            log_operation_result(notificacion_actualizada, "NOTIFICACIÓN ACTUALIZADA")

            response_data = {"ok": True, "data": notificacion_actualizada}
            log_response(response_data)

            return jsonify(response_data)

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def delete(self, id: int):
        """Elimina una notificación específica."""
        log_request_details(f"ELIMINAR NOTIFICACIÓN {id}", "notificaciones")

        try:
            empresa_id = self._empresa_id()
            print(f"\n📋 EMPRESA ID: {empresa_id}")
            print(f"🔔 NOTIFICACIÓN ID: {id}")

            # Eliminar notificación
            eliminada = self.model.delete(notificacion_id=id, empresa_id=empresa_id)

            if not eliminada:
                log_error("Notificación no encontrada o no se pudo eliminar", "NO ENCONTRADO")
                return jsonify({"ok": False, "error": "Notificación no encontrada o no se pudo eliminar"}), 404

            log_operation_result(f"Notificación {id} eliminada", "NOTIFICACIÓN ELIMINADA")

            response_data = {"ok": True, "message": "Notificación eliminada correctamente"}
            log_response(response_data)

            return jsonify(response_data)

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def marcar_leida(self, id: int):
        """Marca una notificación como leída."""
        log_request_details(f"MARCAR NOTIFICACIÓN COMO LEÍDA {id}", "notificaciones")

        try:
            empresa_id = self._empresa_id()
            print(f"\n📋 EMPRESA ID: {empresa_id}")
            print(f"🔔 NOTIFICACIÓN ID: {id}")

            # Marcar como leída
            notificacion_actualizada = self.model.marcar_como_leida(notificacion_id=id, empresa_id=empresa_id)

            if not notificacion_actualizada:
                log_error("Notificación no encontrada o no se pudo actualizar", "NO ENCONTRADO")
                return jsonify({"ok": False, "error": "Notificación no encontrada o no se pudo actualizar"}), 404

            log_operation_result(notificacion_actualizada, "NOTIFICACIÓN MARCADA COMO LEÍDA")

            response_data = {"ok": True, "data": notificacion_actualizada}
            log_response(response_data)

            return jsonify(response_data)

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def pendientes(self):
        """Obtiene notificaciones pendientes."""
        log_request_details("OBTENER NOTIFICACIONES PENDIENTES", "notificaciones")

        try:
            empresa_id = self._empresa_id()
            usuario_id = request.args.get("usuario_id")

            print(f"\n📋 EMPRESA ID: {empresa_id}")
            if usuario_id:
                print(f"👤 USUARIO ID: {usuario_id}")
                try:
                    usuario_id = int(usuario_id)
                except ValueError:
                    return jsonify({"ok": False, "error": "usuario_id debe ser un número entero"}), 400

            # Obtener notificaciones pendientes
            notificaciones = self.model.obtener_pendientes(empresa_id=empresa_id, usuario_id=usuario_id)

            log_operation_result(notificaciones, f"NOTIFICACIONES PENDIENTES: {len(notificaciones)}")

            response_data = {"ok": True, "data": notificaciones}
            log_response(response_data)

            return jsonify(response_data)

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500
