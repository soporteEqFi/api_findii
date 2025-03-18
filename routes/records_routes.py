from controllers.records_controller import  *
from librerias import * 

con_records = recordsControlador()

#rutas
records = Blueprint('records', __name__)

@records.route('/add-record/', methods=['POST'])
@cross_origin()
def post_add_record():
    return con_records.post_add_record()

@records.route('/edit-record/', methods=['PUT'])
@cross_origin()
def edit_record():
    return con_records.edit_record()
    
@records.route("/get-all-data/", methods = ['GET'])
@cross_origin()
def get_all_data():
    return con_records.get_all_data()

@records.route('/filtrar-tabla/', methods=['POST'])
@cross_origin()
def post_filtrar_tabla():
   return con_records.filtrar_tabla()

@records.route('/descargar-ventas/', methods=['GET'])
@cross_origin()
def get_descargar_ventas_realizadas():
   return con_records.descargar_ventas_realizadas()

@records.route('/editar-estado/', methods=['PUT'])
@cross_origin()
def editar_estado():
    return con_records.actualizar_estado()

@records.route('/datos-por-fecha/',methods=['POST'])
@cross_origin()
def mostrar_fecha():
    return con_records.filtrar_por_fecha()

@records.route('/mostrar-por-intervalo/', methods=['POST'])
@cross_origin()
def mostrar_intervalo():
    return con_records.filtro_intervalo()

@records.route('/get-combined-data', methods=['GET'])
def get_combined_data_route():
    return con_records.get_combined_data()

@records.route('/filtrar-tabla-combinada', methods=['POST'])
def filtrar_tabla_combinada_route():
    return con_records.filtrar_tabla_combinada()

@records.route('/delete-record', methods=['DELETE'])
def delete_record_route():
    return con_records.delete_record()
