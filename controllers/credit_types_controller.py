from models.credit_types_model import *

mod_credit_types = credit_typesModel()

class credit_typesControlador():

    def get_all_credit_types(self):
        query = mod_credit_types.get_all_credit_types()
        return query

    def add_credit_type(self):
        query = mod_credit_types.add_credit_type()
        return query

    def edit_credit_type(self):
        query = mod_credit_types.edit_credit_type()
        return query

