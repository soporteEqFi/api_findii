from model.records.records_model import *

mod_records = recordsModel()

class recordsControlador():
    pass

    def post_add_record(self):
            query = mod_records.add_record()
            return query
    
    def get_all_data(self):
        query = mod_records.get_all_data()
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
    
    def actualizar_estado(self):
         query = mod_records.editar_estado()
         return query
    
    def filtrar_por_fecha(self):
         query = mod_records.mostrar_por_fecha()
         return query