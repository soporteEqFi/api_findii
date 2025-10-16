from __future__ import annotations

from flask import request, jsonify
from models.usuarios_model import UsuariosModel
from utils.debug_helpers import (
    log_request_details, log_operation_result, log_response, log_error
)

class UsuariosController:
    def __init__(self):
        self.model = UsuariosModel()

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
        """Lista todos los usuarios de una empresa."""
        log_request_details("LISTAR USUARIOS", "usuarios")

        try:
            empresa_id = self._empresa_id()
            print(f"\n📋 EMPRESA ID: {empresa_id}")

            # Intentar identificar al usuario solicitante para aplicar filtros por rol
            user_id = request.headers.get("X-User-Id") or request.args.get("user_id")
            usuarios = []

            if user_id:
                try:
                    user_id_int = int(user_id)
                except Exception:
                    user_id_int = None

                if user_id_int is not None:
                    # Obtener datos del usuario para conocer su rol
                    usuario_req = self.model.get_by_id(user_id_int, empresa_id)
                    rol_req = usuario_req.get("rol") if usuario_req else None

                    # Si es SUPERVISOR: solo retornar su equipo (usuarios con reports_to_id = supervisor_id)
                    if rol_req == "supervisor":
                        print(f"   👨‍💼 Solicitante es SUPERVISOR (id={user_id_int}). Devolviendo solo su equipo…")
                        usuarios = self.model.get_team_members(user_id_int, empresa_id) or []
                    else:
                        # Otros roles o rol no identificado: comportamiento actual (todos los usuarios de la empresa)
                        usuarios = self.model.list_by_empresa(empresa_id)
                else:
                    # ID inválido: comportamiento actual
                    usuarios = self.model.list_by_empresa(empresa_id)
            else:
                # Sin user_id: comportamiento actual
                usuarios = self.model.list_by_empresa(empresa_id)

            log_operation_result(usuarios, f"USUARIOS OBTENIDOS: {len(usuarios)}")

            response_data = {"ok": True, "data": usuarios}
            log_response(response_data)

            return jsonify(response_data)

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def get_one(self, id: int):
        """Obtiene un usuario específico por ID."""
        log_request_details(f"OBTENER USUARIO {id}", "usuarios")

        try:
            empresa_id = self._empresa_id()
            # print(f"\n📋 EMPRESA ID: {empresa_id}")
            # print(f"👤 USER ID: {id}")

            # Obtener usuario específico
            usuario = self.model.get_by_id(user_id=id, empresa_id=empresa_id)

            if not usuario:
                log_error("Usuario no encontrado", "NO ENCONTRADO")
                return jsonify({"ok": False, "error": "Usuario no encontrado"}), 404

            log_operation_result(usuario, "USUARIO OBTENIDO")

            response_data = {"ok": True, "data": usuario}
            log_response(response_data)

            return jsonify(response_data)

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def update(self, id: int):
        """Actualiza un usuario específico por ID."""
        log_request_details(f"ACTUALIZAR USUARIO {id}", "usuarios")

        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}

            # print(f"\n📋 EMPRESA ID: {empresa_id}")
            # print(f"👤 USER ID: {id}")
            # print(f"📝 DATOS A ACTUALIZAR: {body}")

            # Validar que hay datos para actualizar
            if not body:
                log_error("No hay datos para actualizar", "ERROR DE VALIDACIÓN")
                return jsonify({"ok": False, "error": "No hay datos para actualizar"}), 400

            # Validar campos permitidos
            campos_permitidos = ["nombre", "cedula", "correo", "rol", "info_extra", "reports_to_id", "contraseña"]
            datos_validos = {}

            for campo in campos_permitidos:
                if campo in body:
                    datos_validos[campo] = body[campo]

            if not datos_validos:
                log_error("No hay campos válidos para actualizar", "ERROR DE VALIDACIÓN")
                return jsonify({"ok": False, "error": "No hay campos válidos para actualizar"}), 400

            # Actualizar usuario
            usuario_actualizado = self.model.update(user_id=id, empresa_id=empresa_id, **datos_validos)

            if not usuario_actualizado:
                log_error("Usuario no encontrado o no se pudo actualizar", "NO ENCONTRADO")
                return jsonify({"ok": False, "error": "Usuario no encontrado o no se pudo actualizar"}), 404

            log_operation_result(usuario_actualizado, "USUARIO ACTUALIZADO")

            response_data = {"ok": True, "data": usuario_actualizado}
            log_response(response_data)

            return jsonify(response_data)

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def create(self):
        """Crea un nuevo usuario para una empresa."""
        log_request_details("CREAR USUARIO", "usuarios")

        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}

            # print(f"\n📋 EMPRESA ID: {empresa_id}")
            # print(f"📝 DATOS RECIBIDOS: {body}")

            # Validar campos requeridos
            campos_requeridos = ["nombre", "cedula", "correo", "contraseña", "rol"]
            for campo in campos_requeridos:
                if campo not in body:
                    log_error(f"Campo requerido faltante: {campo}", "ERROR DE VALIDACIÓN")
                    return jsonify({"ok": False, "error": f"Campo requerido faltante: {campo}"}), 400

            # Crear usuario
            usuario_creado = self.model.create(empresa_id=empresa_id, **body)

            if not usuario_creado:
                log_error("No se pudo crear el usuario", "ERROR DE CREACIÓN")
                return jsonify({"ok": False, "error": "No se pudo crear el usuario"}), 500

            log_operation_result(usuario_creado, "USUARIO CREADO")

            response_data = {"ok": True, "data": usuario_creado}
            log_response(response_data)

            return jsonify(response_data), 201

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def delete(self, id: int):
        """Elimina un usuario específico por ID."""
        log_request_details(f"ELIMINAR USUARIO {id}", "usuarios")

        try:
            empresa_id = self._empresa_id()
            # print(f"\n📋 EMPRESA ID: {empresa_id}")
            # print(f"👤 USER ID: {id}")

            # Eliminar usuario
            eliminado = self.model.delete(user_id=id, empresa_id=empresa_id)

            if not eliminado:
                log_error("Usuario no encontrado o no se pudo eliminar", "NO ENCONTRADO")
                return jsonify({"ok": False, "error": "Usuario no encontrado o no se pudo eliminar"}), 404

            log_operation_result(f"Usuario {id} eliminado", "USUARIO ELIMINADO")

            response_data = {"ok": True, "message": "Usuario eliminado correctamente"}
            log_response(response_data)

            return jsonify(response_data)

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def get_team_members(self, supervisor_id: int):
        """Obtiene los miembros del equipo de un supervisor."""
        log_request_details(f"OBTENER EQUIPO DEL SUPERVISOR {supervisor_id}", "usuarios")

        try:
            empresa_id = self._empresa_id()
            # print(f"\n📋 EMPRESA ID: {empresa_id}")
            # print(f"👨‍💼 SUPERVISOR ID: {supervisor_id}")

            # Obtener miembros del equipo
            team_members = self.model.get_team_members(supervisor_id, empresa_id)

            log_operation_result(team_members, f"MIEMBROS DEL EQUIPO OBTENIDOS: {len(team_members)}")

            response_data = {"ok": True, "data": team_members}
            log_response(response_data)

            return jsonify(response_data)

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500

