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
       
    def get_user_info(self, cedula):
         query = mod_records.get_user_info(cedula)
         return query
    
    def filtrar_tabla(self):
        query = mod_records.filtrar_tabla()
        return query
    
    def get_agent_info(self, cedula):
        query = mod_records.get_agent_info(cedula)
        return query
    
    def descargar_ventas_realizadas(self):
        query = mod_records.descargar_ventas_realizadas()
        return query