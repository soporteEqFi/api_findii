from __future__ import annotations

import os
from datetime import datetime, timedelta
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.auth_model import AuthModel


class AuthController:
    """Controlador para autenticación y manejo de JWT."""

    def __init__(self):
        self.model = AuthModel()

    def login(self):
        """Endpoint de login."""
        try:
            # Debug: imprimir datos recibidos
            # print("=== DEBUG LOGIN ===")
            # print(f"Content-Type: {request.content_type}")
            # print(f"Raw data: {request.get_data()}")

            # body = request.get_json(silent=True) or {}
            # print(f"Parsed JSON: {body}")

            # Validar campos requeridos
            correo = body.get("correo") or body.get("email")  # Soportar ambos nombres
            contraseña = body.get("contraseña") or body.get("password")  # Soportar ambos nombres

            print(f"Correo extraído: {correo}")
            print(f"Contraseña extraída: {'***' if contraseña else None}")

            if not correo or not contraseña:
                print("ERROR: Campos faltantes")
                return jsonify({
                    "ok": False,
                    "error": "Correo y contraseña son requeridos",
                    "message": "Credenciales incompletas",
                    "debug": {
                        "received_fields": list(body.keys()) if body else [],
                        "content_type": request.content_type
                    }
                }), 400

                        # Autenticar usuario
            print(f"Intentando autenticar: {correo}")
            usuario = self.model.authenticate_user(correo, contraseña)
            print(f"Resultado autenticación: {usuario is not None}")

            if not usuario:
                print("ERROR: Usuario no autenticado")
                return jsonify({
                    "ok": False,
                    "error": "Credenciales inválidas",
                    "message": "Correo o contraseña incorrectos"
                }), 401

            # Crear token JWT
            expires = timedelta(hours=24)  # Token válido por 24 horas
            access_token = create_access_token(
                identity=usuario["id"],
                expires_delta=expires
            )

            print(f"Usuario: {usuario}")

            # Obtener información de la empresa
            empresa_info = None
            if usuario.get("empresa_id"):
                empresa_info = self.model.get_empresa_info(usuario["empresa_id"])

            return jsonify({
                "ok": True,
                "access_token": access_token,
                "user": {
                    "id": usuario["id"],
                    "nombre": usuario["nombre"],
                    "email": usuario["email"],
                    "rol": usuario["rol"],
                    "cedula": usuario["cedula"],
                    "empresa_id": usuario.get("empresa_id"),
                    "info_extra": usuario["info_extra"]
                },
                "empresa": empresa_info,
                "message": "Login exitoso"
            }), 200

        except Exception as ex:
            return jsonify({
                "ok": False,
                "error": str(ex),
                "message": "Error interno del servidor"
            }), 500

    @jwt_required()
    def verify_token(self):
        """Verifica si el token JWT es válido y retorna info del usuario."""
        try:
            current_user_id = get_jwt_identity()

            # Obtener información actualizada del usuario
            usuario = self.model.get_user_by_id(current_user_id)

            if not usuario:
                return jsonify({
                    "ok": False,
                    "error": "Usuario no encontrado",
                    "message": "Token válido pero usuario no existe"
                }), 404

            # Obtener información de la empresa
            empresa_info = None
            if usuario.get("empresa_id"):
                empresa_info = self.model.get_empresa_info(usuario["empresa_id"])

            return jsonify({
                "ok": True,
                "user": {
                    "id": usuario["id"],
                    "nombre": usuario["nombre"],
                    "email": usuario["email"],
                    "rol": usuario["rol"],
                    "cedula": usuario["cedula"],
                    "empresa_id": usuario.get("empresa_id"),
                    "info_extra": usuario["info_extra"]
                },
                "empresa": empresa_info,
                "message": "Token válido"
            }), 200

        except Exception as ex:
            return jsonify({
                "ok": False,
                "error": str(ex),
                "message": "Error verificando token"
            }), 500

    @jwt_required()
    def logout(self):
        """Logout (en este caso, solo confirma que el token es válido)."""
        try:
            return jsonify({
                "ok": True,
                "message": "Logout exitoso"
            }), 200

        except Exception as ex:
            return jsonify({
                "ok": False,
                "error": str(ex),
                "message": "Error en logout"
            }), 500

    def refresh_token(self):
        """Refresca el token JWT."""
        try:
            # Obtener token del header Authorization
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    "ok": False,
                    "error": "Token no proporcionado",
                    "message": "Authorization header requerido"
                }), 401

            # Este endpoint requiere un token válido para generar uno nuevo
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request()

            current_user_id = get_jwt_identity()
            usuario = self.model.get_user_by_id(current_user_id)

            if not usuario:
                return jsonify({
                    "ok": False,
                    "error": "Usuario no encontrado",
                    "message": "No se puede refrescar el token"
                }), 404

            # Crear nuevo token
            expires = timedelta(hours=24)
            new_token = create_access_token(
                identity=usuario["id"],
                expires_delta=expires
            )

            return jsonify({
                "ok": True,
                "access_token": new_token,
                "user": {
                    "id": usuario["id"],
                    "nombre": usuario["nombre"],
                    "email": usuario["email"],
                    "rol": usuario["rol"],
                    "cedula": usuario["cedula"],
                    "info_extra": usuario["info_extra"]
                },
                "message": "Token renovado exitosamente"
            }), 200

        except Exception as ex:
            return jsonify({
                "ok": False,
                "error": str(ex),
                "message": "Error renovando token"
            }), 500
