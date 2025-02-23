from controller.records.records_controller import  *
from librerias import * 

con_records = recordsControlador()

#rutas
records = Blueprint('records', __name__)

@records.route('/add-record/', methods=['POST'])
@cross_origin()
def post_add_record():
    return con_records.post_add_record()
    
@records.route("/get-all-data/", methods = ['GET'])
@cross_origin()
def get_all_data():
    return con_records.get_all_data()

@records.route('/get-user-info/<cedula>', methods=['GET'])
@cross_origin()
def get_user_info(cedula):
    return con_records.get_user_info(cedula)

@records.route('/get-agent-info/<cedula>', methods=['GET'])
@cross_origin()
def get_agent_info(cedula):
    return con_records.get_agent_info(cedula)

@records.route('/filtrar-tabla/', methods=['POST'])
@cross_origin()
def post_filtrar_tabla():
   return con_records.filtrar_tabla()

@records.route('/descargar-ventas/', methods=['GET'])
@cross_origin()
def get_descargar_ventas_realizadas():
   return con_records.descargar_ventas_realizadas()