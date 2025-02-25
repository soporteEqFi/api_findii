from models.records_model import *

mod_records = recordsModel()

class recordsControlador():

    def post_add_record(self):  
        query = mod_records.add_record()
        return query
    
    def get_all_data(self):
        query = mod_records.get_all_data()
        return query 
    
    def filtrar_tabla(self):
        query = mod_records.filtrar_tabla()
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
    
    def filtro_intervalo(self):
         query = mod_records.mostrar_por_intervalo()
         return query