from models.utils.files.files import exist_files_in_request, upload_files
from models.utils.tracking.etapas import files_dict
from models.utils.others.date_utils import iso_date

def handle_files_update(request, etapa_selected:str, user_data:dict, supabase):
    files = exist_files_in_request(request)
    print("Entraste a handle_files_update")
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
