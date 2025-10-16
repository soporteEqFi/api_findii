from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from routes.json_fields_routes import json_fields
from routes.solicitudes_routes import solicitudes
from routes.solicitantes_routes import solicitantes
from routes.ubicaciones_routes import ubicaciones
from routes.actividad_economica_routes import actividad_economica
from routes.informacion_financiera_routes import informacion_financiera
from routes.referencias_routes import referencias
from routes.auth_routes import auth
from routes.schema_completo_routes import schema_completo
from routes.dashboard_routes import dashboard_bp as dashboard
from routes.documentos_routes import documentos
from routes.configuraciones_routes import configuraciones
from routes.usuarios_routes import usuarios
from routes.notificaciones_routes import notificaciones
from routes.estadisticas_routes import estadisticas

load_dotenv()

app = Flask(__name__)
jwt = JWTManager(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# Configurar Flask para manejar redirecciones CORS
app.config['CORS_HEADERS'] = 'Content-Type'

# Middleware para logging de requests
# @app.before_request
# def log_request_info():
#     from flask import request
#     print(f"\n🔍 REQUEST RECIBIDA:")
#     print(f"   Method: {request.method}")
#     print(f"   URL: {request.url}")
#     print(f"   Path: {request.path}")
#     print(f"   Args: {dict(request.args)}")
#     print(f"   Headers: {dict(request.headers)}")
#     if request.method in ['POST', 'PUT', 'PATCH']:
#         try:
#             body = request.get_json(silent=True)
#             print(f"   Body: {body}")
#         except:
#             print(f"   Body: {request.get_data(as_text=True)}")

# @app.after_request
# def log_response_info(response):
#     print(f"📤 RESPONSE ENVIADA:")
#     print(f"   Status: {response.status_code}")
#     # print(f"   Headers: {dict(response.headers)}")
#     if response.status_code >= 400:
#         print(f"   ❌ ERROR {response.status_code} - {response.get_data(as_text=True)}")
#     print("="*50)
#     return response

app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(json_fields, url_prefix="/json")
app.register_blueprint(schema_completo, url_prefix="/schema")
app.register_blueprint(solicitudes, url_prefix="/solicitudes")
app.register_blueprint(solicitantes, url_prefix="/solicitantes")
app.register_blueprint(ubicaciones, url_prefix="/ubicacion")
app.register_blueprint(actividad_economica, url_prefix="/actividad_economica")
app.register_blueprint(informacion_financiera, url_prefix="/informacion_financiera")
app.register_blueprint(referencias, url_prefix="/referencias")
app.register_blueprint(dashboard, url_prefix="/dashboard")
app.register_blueprint(documentos, url_prefix="/documentos")
app.register_blueprint(configuraciones, url_prefix="/configuraciones")
app.register_blueprint(usuarios, url_prefix="/usuarios")
app.register_blueprint(notificaciones, url_prefix="/notificaciones")
app.register_blueprint(estadisticas, url_prefix="/estadisticas")

def pagina_no_encontrada(error):
    print(f"❌ 404 - PÁGINA NO ENCONTRADA: {error}")
    print(f"   URL: {error.code if hasattr(error, 'code') else 'N/A'}")
    return {"ok": False, "error": "Página no encontrada"}, 404

def error_interno(error):
    print(f"💥 ERROR INTERNO NO MANEJADO: {error}")
    import traceback
    traceback.print_exc()
    return {"ok": False, "error": "Error interno del servidor"}, 500

def error_bad_request(error):
    print(f"❌ ERROR BAD REQUEST: {error}")
    return {"ok": False, "error": "Solicitud incorrecta"}, 400

if __name__ == "__main__":
    app.register_error_handler(404, pagina_no_encontrada)
    app.register_error_handler(500, error_interno)
    app.register_error_handler(400, error_bad_request)
    app.run(host="0.0.0.0", port=5000, debug=True)