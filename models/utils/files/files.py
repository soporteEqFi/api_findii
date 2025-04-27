from models.utils.files.utils import create_unique_filename
import uuid
def exist_files_in_request(request):
    if 'archivos' in request.files:
        files = request.files.getlist('archivos')
        print(len(files))
        return files
    else:
        return None
    
def upload_files(files_data, user_data, supabase):

    files = files_data["archivos"]
    id_solicitante = user_data.get('id_solicitante')

    for file in files:
        try:
            # Data como nombre del archivo, nombre único y extensión
            file_metadata = create_unique_filename(file)
            file_path = f"documents/{file_metadata['unique_filename']}"
            file_name = file_metadata['file_name']
            file_extension = file_metadata['file_extension']

            # Leer archivo y convertir a bytes
            file_data = file.read()

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

            return {
                "archivo_id": str(uuid.uuid4()),
                "nombre": file_name,
                "url": archivo_url,
            }

        except Exception as e:
            print(f"Error procesando archivo {file.filename}: {e}")
            continue