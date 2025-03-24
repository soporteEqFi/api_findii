from models.generales.generales import *

class credit_typesModel():

    def get_all_credit_types(self):
        try:
            res = supabase.table('TIPOS_CREDITOS_CONFIG').select('*').execute()
            return jsonify(res.data), 200
        except Exception as e:
            return jsonify({"mensaje": "Ocurrió un error al obtener el tipo de crédito."}), 500
        
    def add_credit_type(self):
        try:
            data = request.json

            name = data['name']
            display_name = data['display_name']
            description = data['description']
            fields = data['fields']
            is_active = data['is_active']

            data_to_send = {
                "name": name,
                "display_name": display_name,
                "description": description,
                "fields": fields,
                "is_active": is_active
            }

            print(data_to_send)

            # print(fields)
            # print(data)
            res = supabase.table('TIPOS_CREDITOS_CONFIG').insert(data_to_send).execute()
            print(res)
            return jsonify({"prueba": "si"})
        except Exception as e:
            print(e)
            return jsonify({"mensaje": "Ocurrió un error al agregar el tipo de crédito."}), 500