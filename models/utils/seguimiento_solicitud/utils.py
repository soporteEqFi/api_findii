from models.utils.files.files import exist_files_in_request, upload_files
from models.utils.tracking.etapas import files_dict
from models.utils.others.date_utils import iso_date
from flask import jsonify

def handle_new_files(request, etapa_selected:str, user_data:dict, supabase):
    print("Entraste a handle_new_files")
    files = exist_files_in_request(request, "archivos")
    if not files:
        print("No parece haber archivos para subir")
        # return jsonify({"error": "No se recibieron archivos"}), 400

    if 'archivos' not in etapa_selected:
        etapa_selected['archivos'] = []

    # Subir archivos a Supabase Storage
    uploaded_files_data = upload_files({"archivos": files}, user_data, supabase)
    # Añadir el nuevo archivo a la etapa específica
    files_new_data = files_dict(uploaded_files_data, user_data["id_solicitante"])

    return files_new_data

def handle_update_files(request, supabase):
    print("Entraste a handle_update_files")
    files = exist_files_in_request(request, "archivo_reemplazar")
    if not files:
        print("No parece haber archivos para subir")
        return jsonify({"error": "No se recibieron archivos"}), 400

    file = files[0] # Tomamos el primer archivo
    existing_file_route = request.form.get('ruta_archivo_reemplazar')
    print(existing_file_route)

    # Extraer la ruta después de "findii/"
    if "findii/" in existing_file_route:
        existing_file_route_split = existing_file_route.split("findii/")[1].split("?")[0]
        print(f"Ruta del archivo extraída: {existing_file_route_split}")

    # 2. Elimina el archivo anterior
    supabase.storage.from_('findii').remove([existing_file_route_split])

    # 3. Sube el nuevo archivo en la misma ruta
    file_data = file.read()
    supabase.storage.from_('findii').upload(
        existing_file_route_split,
        file_data,
        file_options={"content-type": file.mimetype}
    )

    return True

def handle_history_update(request, etapa_selected:dict):
    """
        Actualiza el historial de la etapa.
    """
    print("Entraste a handle_history_update")
    
    comentario_historial = request.form.get('comentario_historial')
    estado_historial = request.form.get('estado_historial')
    usuario_id = request.form.get('usuario_id')

    print(estado_historial, comentario_historial, usuario_id)

    if 'historial' not in etapa_selected:
        etapa_selected['historial'] = []

    history_new_data = {
        "fecha": iso_date(),
        "estado": estado_historial,
        "comentario": comentario_historial if comentario_historial else "No hay comentarios",
        "usuario_id": usuario_id
    }

    # etapa_selected['historial'].append(history_data)

    return history_new_data
