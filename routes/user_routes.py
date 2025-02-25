from controller.user_controller import  *
from librerias import * 

con_user = userController()

#rutas
user = Blueprint('user', __name__)

@user.route('/create-user/', methods=['POST'])
@cross_origin()
def post_create_user():
    return con_user.post_create_user()

@user.route('/get-agent-info/<cedula>', methods=['GET'])
@cross_origin()
def get_agent_info(cedula):
    return con_user.get_agent_info(cedula)

@user.route('/get-user-info/<cedula>', methods=['GET'])
@cross_origin()
def get_user_info(cedula):
    return con_user.get_user_info(cedula)