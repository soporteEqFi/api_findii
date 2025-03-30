from controllers.credit_types_controller import  *
from librerias import * 

con_credit_types = credit_typesControlador()

#rutas
credit_types = Blueprint('credit_types', __name__)

@credit_types.route('/get-all-credit-types/', methods=['POST'])
@cross_origin()
def get_all_credit_types():
    return con_credit_types.get_all_credit_types()

@credit_types.route('/add-credit-type/', methods=['POST'])
@cross_origin()
def add_credit_type():
    return con_credit_types.add_credit_type()

@credit_types.route('/edit-credit-type/', methods=['POST'])
@cross_origin()
def edit_credit_type():
    return con_credit_types.edit_credit_type()