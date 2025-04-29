from models.utils.files.utils import create_unique_filename
import uuid

def exist_files_in_request(request, column_name:str = "archivos"):
    if column_name in request.files:
        files = request.files.getlist(column_name)
        return files
    else:
        return None
    
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