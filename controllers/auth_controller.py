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
            print("\n" + "="*60)
            print("[LOGIN] 🚀 INICIO DE LOGIN")
            print("="*60)

            body = request.get_json(silent=True) or {}

            # Validar campos requeridos
            correo = body.get("correo") or body.get("email")  # Soportar ambos nombres
            contraseña = body.get("contraseña") or body.get("password")  # Soportar ambos nombres

            if not correo or not contraseña:
                print("[LOGIN] ❌ ERROR: Campos faltantes")
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
            print(f"[LOGIN] 🔍 Intentando autenticar usuario: {correo}")
            usuario = self.model.authenticate_user(correo, contraseña)
            print(f"[LOGIN] 📊 Resultado autenticación: {usuario is not None}")

            if usuario:
                print(f"[LOGIN] ✅ Usuario autenticado - ID: {usuario.get('id')}, Nombre: {usuario.get('nombre')}")
            else:
                print(f"[LOGIN] ❌ Usuario NO autenticado (None retornado)")

            if not usuario:
                print(f"[LOGIN] 🔍 Verificando si es usuario temporal (para mensaje específico)...")
                # Verificar si el usuario existe pero está inactivo o expirado
                try:
                    usuario_info = self.model._verificar_usuario_temporal(correo)
                    print(f"[LOGIN] 📊 Resultado verificación temporal: {usuario_info}")

                    if usuario_info:
                        if usuario_info.get("inactivo"):
                            print("[LOGIN] ❌ ERROR: Usuario temporal inactivo")
                            return jsonify({
                                "ok": False,
                                "error": "Usuario inactivo",
                                "message": "Tu cuenta temporal está desactivada. Contacta al administrador.",
                                "error_code": "USER_INACTIVE"
                            }), 403
                        elif usuario_info.get("expirado"):
                            print("[LOGIN] ❌ ERROR: Usuario temporal expirado")
                            return jsonify({
                                "ok": False,
                                "error": "Cuenta expirada",
                                "message": f"Tu cuenta temporal expiró el {usuario_info.get('fecha_expiracion', '')}. Contacta al administrador para renovar el acceso.",
                                "error_code": "USER_EXPIRED"
                            }), 403
                except Exception as verif_error:
                    print(f"[LOGIN] ⚠️ Error verificando usuario temporal: {verif_error}")

                print("[LOGIN] ❌ ERROR: Usuario no autenticado - Credenciales inválidas")
                return jsonify({
                    "ok": False,
                    "error": "Credenciales inválidas",
                    "message": "Correo o contraseña incorrectos"
                }), 401

            # Crear token JWT
            print(f"[LOGIN] 🔐 Creando token JWT para usuario ID: {usuario.get('id')}")
            try:
                expires = timedelta(hours=24)  # Token válido por 24 horas
                access_token = create_access_token(
                    identity=usuario["id"],
                    expires_delta=expires
                )
                print(f"[LOGIN] ✅ Token JWT creado exitosamente")
            except Exception as token_error:
                print(f"[LOGIN] ❌ ERROR creando token JWT: {token_error}")
                import traceback
                traceback.print_exc()
                raise

            # Obtener información de la empresa
            empresa_info = None
            if usuario.get("empresa_id"):
                try:
                    empresa_info = self.model.get_empresa_info(usuario["empresa_id"])
                except Exception as empresa_error:
                    empresa_info = None

            respuesta = {
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
            }

            print(f"[LOGIN] ✅ LOGIN EXITOSO - Enviando respuesta")
            print("="*60 + "\n")

            return jsonify(respuesta), 200

        except Exception as ex:
            print(f"\n[LOGIN] ❌❌❌ ERROR EXCEPCIÓN EN LOGIN ❌❌❌")
            print(f"[LOGIN] Tipo de error: {type(ex).__name__}")
            print(f"[LOGIN] Mensaje: {str(ex)}")
            print(f"[LOGIN] 📋 Traceback completo:")
            import traceback
            traceback.print_exc()
            print("="*60 + "\n")

            return jsonify({
                "ok": False,
                "error": str(ex),
                "message": "Error interno del servidor",
                "error_type": type(ex).__name__
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
