from flask import Blueprint
from flask_cors import cross_origin

from controllers.auth_controller import AuthController

auth = Blueprint("auth", __name__)
con_auth = AuthController()


@auth.route("/login", methods=["POST"])
@cross_origin()
def login():
    """Login de usuario."""
    return con_auth.login()


@auth.route("/verify", methods=["GET"])
@cross_origin()
def verify_token():
    """Verificar token JWT."""
    return con_auth.verify_token()


@auth.route("/logout", methods=["POST"])
@cross_origin()
def logout():
    """Logout de usuario."""
    return con_auth.logout()


@auth.route("/refresh", methods=["POST"])
@cross_origin()
def refresh_token():
    """Refrescar token JWT."""
    return con_auth.refresh_token()
