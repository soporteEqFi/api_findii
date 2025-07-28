from librerias import *
from models.generales.generales import *
from models.utils.files.utils import create_unique_filename
from io import BytesIO 
import uuid  # Para generar nombres únicos
from datetime import datetime

class insertar():
    
    def upload_files(files_data, user_data, supabase):
        files = files_data["archivos"]
        id_solicitante = user_data.get('id_solicitante')
        uploaded_files = []

        for file in files:
            try:
                # Data como nombre del archivo, nombre único y extensión
                file_metadata = create_unique_filename(file)
                file_path = f"documents/{file_metadata['unique_filename']}"
                file_name = file_metadata['file_name']
                file_extension = file_metadata['file_extension']

                # Leer archivo y convertir a bytes
                file_data = file.read()
                file.seek(0)  # Reset file pointer for next read

                # Subir archivo a Supabase Storage
                res = supabase.storage.from_("findii").upload(
                    file_path,
                    file_data,
                    file_options={"content-type": file.mimetype}
                )

                # Obtener URL pública
                archivo_url = supabase.storage.from_("findii").get_public_url(file_path)

                # Insertar en la tabla PRUEBA_IMAGEN
                supabase.table("PRUEBA_IMAGEN").insert({
                    "imagen": archivo_url,
                    "nombre": file_name,
                    "id_solicitante": id_solicitante
                }).execute()
                print("insertaste en la tabla PRUEBA_IMAGEN")

                uploaded_files.append({
                    "archivo_id": str(uuid.uuid4()),
                    "nombre": file_name,
                    "url": archivo_url,
                })
                print("insertaste en la lista de archivos")
            except Exception as e:
                print(f"Error procesando archivo {file.filename}: {e}")
                continue

        print("saliste de upload_files")
        return uploaded_files

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
