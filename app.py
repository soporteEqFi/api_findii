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

load_dotenv()

app = Flask(__name__)
jwt = JWTManager(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

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

def pagina_no_encontrada(error):
    return "<h1>Pagina no encontrada ...<h1>"

if __name__ == "__main__":
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(host="0.0.0.0", port=5000, debug=True)