from model.records.records_model import *

mod_records = recordsModel()

class recordsControlador():
    pass

    def post_add_record(self):
            query = mod_records.add_record()
            return query
    