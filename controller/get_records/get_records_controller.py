from model.get_records.get_records_model import *

mod_select = select_model()

class select_controlador():

    def select_cont(self):
        query = mod_select.select_data()
        return query