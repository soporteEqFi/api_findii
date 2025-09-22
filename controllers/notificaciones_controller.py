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

    def _obtener_usuario_autenticado(self):
        """Obtener información del usuario autenticado desde la base de datos"""
        try:
            # Obtener el token del header Authorization
            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                print(f"   ❌ Authorization header inválido o faltante")
                return None

            # Obtener user_id del header o query parameter
            user_id = request.headers.get("X-User-Id") or request.args.get("user_id")

            if not user_id:
                print(f"   ❌ User ID faltante (header X-User-Id o query user_id)")
                return None

            # Consultar la base de datos para obtener información completa del usuario
            print(f"   🔍 Consultando usuario con ID: {user_id}")
            from data.supabase_conn import supabase
            user_response = supabase.table("usuarios").select("id, rol, info_extra").eq("id", int(user_id)).execute()
            print(f"   📊 Respuesta de BD: {user_response.data}")

            user_data = user_response.data[0] if user_response.data else None

            if not user_data:
                print(f"   ❌ Usuario no encontrado en BD")
                return None

            # Extraer banco_nombre y ciudad del info_extra del usuario
            info_extra = user_data.get("info_extra") or {}
            banco_nombre = info_extra.get("banco_nombre") if isinstance(info_extra, dict) else None
            ciudad = info_extra.get("ciudad") if isinstance(info_extra, dict) else None

            usuario_info = {
                "id": user_data["id"],
                "rol": user_data.get("rol", "empresa"),
                "banco_nombre": banco_nombre,
                "ciudad": ciudad
            }

            return usuario_info

        except Exception as e:
            print(f"   ❌ Error obteniendo usuario autenticado: {e}")
            return None

    def _verificar_permiso_notificacion(self, notificacion: dict, usuario_info: dict = None) -> bool:
        """Verifica si el usuario tiene permisos para acceder a una notificación específica"""
        if not usuario_info:
            return False

        rol = usuario_info.get("rol")
        user_id = usuario_info.get("id")
        notif_user_id = notificacion.get("usuario_id")

        # Admin y empresa ven todas las notificaciones
        if rol in ["admin", "empresa"]:
            return True

        # Asesor: ve sus notificaciones + las notificaciones de su supervisor
        if rol == "asesor":
            if notif_user_id == user_id:
                return True

            # Verificar si es de su supervisor
            from models.usuarios_model import UsuariosModel
            usuarios_model = UsuariosModel()
            asesor_info = usuarios_model.get_by_id(user_id, notificacion.get("empresa_id"))

            if asesor_info and asesor_info.get("reports_to_id"):
                supervisor_id = asesor_info["reports_to_id"]
                return notif_user_id == supervisor_id
            return False

        # Supervisor: ve notificaciones de su equipo + las suyas propias
        if rol == "supervisor":
            if notif_user_id == user_id:
                return True

            # Verificar si es de su equipo
            from models.usuarios_model import UsuariosModel
            usuarios_model = UsuariosModel()
            team_members = usuarios_model.get_team_members(user_id, notificacion.get("empresa_id"))
            if team_members:
                team_ids = [member["id"] for member in team_members]
                return notif_user_id in team_ids
            return False

        # Banco: ve notificaciones de su banco y ciudad
        if rol == "banco":
            banco_nombre = usuario_info.get("banco_nombre")
            ciudad = usuario_info.get("ciudad")
            metadata = notificacion.get("metadata", {})

            # Verificar si la notificación es de su banco o ciudad
            notif_banco = metadata.get("banco_nombre")
            notif_ciudad = metadata.get("ciudad")

            return (banco_nombre and notif_banco == banco_nombre) or (ciudad and notif_ciudad == ciudad)

        return False

    def list(self):
        """Lista notificaciones con filtros opcionales y permisos por rol."""
        log_request_details("LISTAR NOTIFICACIONES", "notificaciones")

        try:
            empresa_id = self._empresa_id()
            usuario_info = self._obtener_usuario_autenticado()

            print(f"\n📋 EMPRESA ID: {empresa_id}")
            print(f"👤 USUARIO INFO: {usuario_info}")

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

            # Obtener notificaciones con filtros de rol
            # Si no hay usuario autenticado, mostrar todas las notificaciones (comportamiento anterior)
            if usuario_info is None:
                print("⚠️ Usuario no autenticado - mostrando todas las notificaciones")
                notificaciones = self.model.list(empresa_id, **filtros)
            else:
                notificaciones = self.model.list(empresa_id, usuario_info, **filtros)

            log_operation_result(notificaciones, f"NOTIFICACIONES OBTENIDAS: {len(notificaciones)}")

            response_data = {
                "ok": True,
                "data": notificaciones,
                "usuario_rol": usuario_info.get("rol") if usuario_info else None
            }
            log_response(response_data)

            return jsonify(response_data)

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def get_one(self, id: int):
        """Obtiene una notificación específica con verificación de permisos."""
        log_request_details(f"OBTENER NOTIFICACIÓN {id}", "notificaciones")

        try:
            empresa_id = self._empresa_id()
            usuario_info = self._obtener_usuario_autenticado()

            print(f"\n📋 EMPRESA ID: {empresa_id}")
            print(f"👤 USUARIO INFO: {usuario_info}")
            print(f"🔔 NOTIFICACIÓN ID: {id}")

            # Obtener notificación específica
            notificacion = self.model.get_by_id(notificacion_id=id, empresa_id=empresa_id)

            if not notificacion:
                log_error("Notificación no encontrada", "NO ENCONTRADO")
                return jsonify({"ok": False, "error": "Notificación no encontrada"}), 404

            # Verificar permisos de acceso a la notificación (solo si hay usuario autenticado)
            if usuario_info is not None and not self._verificar_permiso_notificacion(notificacion, usuario_info):
                log_error("Sin permisos para acceder a esta notificación", "SIN PERMISOS")
                return jsonify({"ok": False, "error": "Sin permisos para acceder a esta notificación"}), 403

            log_operation_result(notificacion, "NOTIFICACIÓN OBTENIDA")

            response_data = {
                "ok": True,
                "data": notificacion,
                "usuario_rol": usuario_info.get("rol") if usuario_info else None
            }
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
            usuario_info = self._obtener_usuario_autenticado()
            body = request.get_json(silent=True) or {}

            print(f"\n📋 EMPRESA ID: {empresa_id}")
            print(f"👤 USUARIO INFO: {usuario_info}")
            print(f"📝 DATOS RECIBIDOS: {body}")

            # Validar campos requeridos
            campos_requeridos = ["tipo", "titulo", "mensaje", "fecha_recordatorio"]
            for campo in campos_requeridos:
                if campo not in body:
                    log_error(f"Campo requerido faltante: {campo}", "ERROR DE VALIDACIÓN")
                    return jsonify({"ok": False, "error": f"Campo requerido faltante: {campo}"}), 400

            # Manejar usuario_id
            if usuario_info and usuario_info.get("id"):
                usuario_autenticado_id = usuario_info["id"]

                # Si el frontend envía usuario_id, verificar que sea el mismo usuario autenticado
                if "usuario_id" in body:
                    if body["usuario_id"] != usuario_autenticado_id:
                        log_error(f"Usuario ID enviado ({body['usuario_id']}) no coincide con usuario autenticado ({usuario_autenticado_id})", "ERROR DE VALIDACIÓN")
                        return jsonify({"ok": False, "error": "No puedes crear notificaciones para otros usuarios"}), 403
                    print(f"✅ Usuario ID validado: {body['usuario_id']}")
                else:
                    # Si no se envía usuario_id, asignar el del usuario autenticado
                    body["usuario_id"] = usuario_autenticado_id
                    print(f"✅ Usuario ID asignado automáticamente: {usuario_autenticado_id}")
            else:
                # Si no hay usuario autenticado, no se puede crear notificación
                log_error("Usuario no autenticado", "ERROR DE AUTENTICACIÓN")
                return jsonify({"ok": False, "error": "Usuario no autenticado"}), 401

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
        """Obtiene notificaciones pendientes con filtros por rol."""
        log_request_details("OBTENER NOTIFICACIONES PENDIENTES", "notificaciones")

        try:
            empresa_id = self._empresa_id()
            usuario_info = self._obtener_usuario_autenticado()
            usuario_id = request.args.get("usuario_id")

            print(f"\n📋 EMPRESA ID: {empresa_id}")
            print(f"👤 USUARIO INFO: {usuario_info}")
            if usuario_id:
                print(f"👤 USUARIO ID (query): {usuario_id}")
                try:
                    usuario_id = int(usuario_id)
                except ValueError:
                    return jsonify({"ok": False, "error": "usuario_id debe ser un número entero"}), 400

            # Obtener notificaciones pendientes con filtros de rol
            # Si no hay usuario autenticado, mostrar todas las notificaciones pendientes (comportamiento anterior)
            if usuario_info is None:
                print("⚠️ Usuario no autenticado - mostrando todas las notificaciones pendientes")
                notificaciones = self.model.obtener_pendientes(empresa_id=empresa_id, usuario_id=usuario_id)
            else:
                notificaciones = self.model.obtener_pendientes(empresa_id=empresa_id, usuario_info=usuario_info, usuario_id=usuario_id)

            log_operation_result(notificaciones, f"NOTIFICACIONES PENDIENTES: {len(notificaciones)}")

            response_data = {
                "ok": True,
                "data": notificaciones,
                "usuario_rol": usuario_info.get("rol") if usuario_info else None
            }
            log_response(response_data)

            return jsonify(response_data)

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500
