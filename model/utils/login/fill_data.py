from model.generales.generales import *

def get_business_image(self):
    try:
        response = supabase.storage.from_('business_images').download('default.jpg')
        return response
    except Exception as e:
        return jsonify({"msg": "Error al obtener la imagen de la empresa: " + str(e)}), 500