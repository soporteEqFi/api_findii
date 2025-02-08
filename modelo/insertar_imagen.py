from librerias import *
from modelo.generales.generales import *
from io import BytesIO 
import uuid  # Para generar nombres únicos
from datetime import datetime

class insertar():

     def insertar_imagen(self):  
        try:
            # Obtener el archivo de la imagen del formulario
            nombre = request.form.get('nombre')
            file = request.files.get('imagen')

            if not file:
                return jsonify({"success": False, "error": "No se proporcionó ninguna imagen"}), 400

            # 🔹 Crear un nombre único para la imagen usando UUID y timestamp
            extension = file.filename.split('.')[-1]  # Obtener la extensión del archivo
            unique_filename = f"{uuid.uuid4().hex}_{int(datetime.timestamp(datetime.now()))}.{extension}"
            file_path = f"images/{unique_filename}"

            # Leer el archivo en memoria y convertirlo en bytes
            file_data = file.read() 

            # 🔹 Subir la imagen a Supabase Storage
            res = supabase.storage.from_("findii").upload(file_path, file_data, file_options={"content-type": file.mimetype})

            #Verificar si la subida fue exitosa
            if isinstance(res, dict) and "error" in res:
                return jsonify({"success": False, "error": res["error"]["message"]}), 500
            
        #  # 🔹 Hacer que el archivo sea público (importante para PDFs)
        #     supabase.storage.from_("findii").update(file_path, {'public': True})

            
            # Obtener la URL pública de la imagen subida
            image_url = supabase.storage.from_("findii").get_public_url(file_path)

            # Insertar la URL en la base de datos
            datos_insertar = {
                "nombre": nombre,
                "imagen": image_url
                }

            res_db = supabase.table("PRUEBA_IMAGEN").insert(datos_insertar).execute()

            # ✅ Verificar si la inserción fue exitosa
            if hasattr(res_db, 'status_code') and res_db.status_code != 200:
                print("Error al insertar en la base de datos:", res_db)
                return jsonify({"success": False, "error": "Error al guardar la URL en la base de datos"}), 500

            print("Imagen subida correctamente y guardada en la BD")
            return jsonify({"registro_usuario_status": "OK", "imagen_url": image_url}), 200

        except Exception as e:
            print("Ocurrió un error:", str(e))
            return jsonify({"mensaje": "Ocurrió un error al procesar la solicitud.", "error": str(e)}), 500
