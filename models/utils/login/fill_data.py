from model.generales.generales import *

def get_business_image():
    try:
        # response = supabase.storage.from_('business_images').download('default.jpg')
        default_image = "https://i.postimg.cc/RZJNTtyh/python.png"
        return default_image
    except Exception as e:
        return jsonify({"msg": "Error al obtener la imagen de la empresa: " + str(e)}), 500