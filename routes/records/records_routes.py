from controller.records.records_controller import  *
from librerias import * 

con_records = recordsControlador()

#rutas
records = Blueprint('records', __name__)

@records.route('/add-record/', methods=['POST'])
@cross_origin()
def post_add_record():
    return con_records.post_add_record()
    
@records.route("/select-data/", methods = ['GET'])
@cross_origin()
def select_rou():
    return con_records.select_cont()

@records.route('/data-user/<cedula>', methods=['GET'])
@cross_origin()
def get_user_data(cedula):
    return con_records.get_data_user(cedula)

@records.route('/filtrar-tabla/', methods=['POST'])
@cross_origin()
def post_filtrar_tabla():
   return con_records.filtrar_tabla()