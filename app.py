from librerias import *
from routes.ruta_inicio_sesion import *
from routes.insertar_imagen import *
from routes.records.records_routes import *
from dotenv import load_dotenv

import os

load_dotenv()

app = Flask(__name__)
jwt = JWTManager(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

app.register_blueprint(inicio_de_sesion)
app.register_blueprint(insertar)
app.register_blueprint(records)
app.register_blueprint(get_records)
app.register_blueprint(usuario_crear)
app.register_blueprint(get_data_user)
app.register_blueprint(filtrar_tabla)

def pagina_no_encontrada(error):

    return "<h1>Pagina no encontrada ...<h1>"

if __name__ == "__main__":
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(host="0.0.0.0", port=5600, debug=True)