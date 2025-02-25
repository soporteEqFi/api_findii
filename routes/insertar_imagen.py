from controllers.controlador_imagen import * 
from librerias import *

con_insertar = insertar_imagen_controlador()

insertar = Blueprint('insertar_imagen', __name__)

@insertar.route('/insertar-imagen/', methods=['POST'])
@cross_origin()
def insertar_imagen():
    return con_insertar.insertar_imagen()