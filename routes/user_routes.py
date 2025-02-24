from controller.user_controller import  *
from librerias import * 

con_user = userController()

#rutas
user = Blueprint('crear_usuario', __name__)

@user.route('/crear-user/', methods=['POST'])
@cross_origin()
def crear_usuario():
    return con_user.user_create()