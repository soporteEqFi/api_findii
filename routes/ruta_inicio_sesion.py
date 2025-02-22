from controller.controlador_inicio_sesion import  *
from librerias import * 

con_inicio_seion = iniciarSesionControlador()

#rutas
login = Blueprint('crear_usuario', __name__)

@login.route('/iniciar-sesion/', methods=['POST'])
@cross_origin()
def iniciar_sesion():
    return con_inicio_seion.inicio_de_sesion()

@login.route('/crear-user/', methods = ['POST'])
@cross_origin()
def crear_usuario():
    return con_inicio_seion.user_create()