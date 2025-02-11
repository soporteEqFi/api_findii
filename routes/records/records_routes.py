from controller.records.records_controller import  *
from librerias import * 

con_records = recordsControlador()

#rutas
records = Blueprint('records', __name__)
get_records = Blueprint("select_route", __name__)

@records.route('/add-record/', methods=['POST'])
@cross_origin()
def post_add_record():
    return con_records.post_add_record()
    
@get_records.route("/select-data/", methods = ['GET'])
@cross_origin()
def select_rou():
    return con_records.select_cont()
