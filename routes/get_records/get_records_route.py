from librerias import * 
from controller.get_records.get_records_controller import *

con_select = select_controlador()

rou_select = Blueprint("select_route", __name__)

@rou_select.route("/select-data/", methods = ['GET'])
@cross_origin()
def select_rou():
    return con_select.select_cont()
