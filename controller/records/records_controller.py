from model.records.records_model import *

mod_records = recordsModel()

class recordsControlador():
    pass

    def post_add_record(self):
            query = mod_records.add_record()
            return query
    
    def select_cont(self):
        query = mod_records.select_data()
        return query    
    def get_data_user(self, cedula):
         query = mod_records.mostrar_datos_personales(cedula)
         return query