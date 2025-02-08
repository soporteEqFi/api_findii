from controller.controlador_inicio_sesion import  *
from librerias import * 

con_inicio_seion = iniciarSesionControlador()

#rutas
inicio_de_sesion = Blueprint('iniciar_sesion', __name__)

@inicio_de_sesion.route('/iniciar-sesion/', methods=['POST'])
@cross_origin()
def iniciar_sesion():
    return con_inicio_seion.inicio_de_sesion()