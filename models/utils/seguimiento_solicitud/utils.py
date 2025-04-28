from models.utils.files.files import exist_files_in_request, upload_files
from models.utils.tracking.etapas import files_dict
from models.utils.others.date_utils import iso_date
from flask import jsonify
import uuid
from datetime import datetime

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

    # 1. Eliminar el archivo existente del storage
    supabase.storage.from_('findii').remove([existing_file_route_split])

    # 2. Subir el nuevo archivo con su nombre original
    file_data = file.read()
    # Reemplazar espacios por guiones bajos en el nombre del archivo
    file_name = file.filename.replace(" ", "_")
    # Subir el nuevo archivo
    supabase.storage.from_('findii').upload(
        file_name,
        file_data,
        file_options={"content-type": file.mimetype}
    )

    # 3. Obtener la URL del nuevo archivo
    image_url = supabase.storage.from_('findii').get_public_url(file_name)

    # 4. Actualizar el registro en la base de datos
    try:
        # Primero buscar el registro por la URL antigua
        registro = supabase.table('PRUEBA_IMAGEN').select('*').eq('imagen', existing_file_route).execute()
        
        if registro.data:
            # Actualizar el registro existente
            res = supabase.table('PRUEBA_IMAGEN').update({
                "nombre": file_name,
                "imagen": image_url
            }).eq('id', registro.data[0]['id']).execute()
            
            print("Registro actualizado:", res)
        else:
            print("No se encontró el registro para actualizar")
            return jsonify({"error": "No se encontró el registro para actualizar"}), 404

    except Exception as e:
        print("Error al actualizar el registro:", str(e))
        return jsonify({"error": f"Error al actualizar el registro: {str(e)}"}), 500

    # Preparar los datos actualizados para la etapa
    datos_actualizados = {
        "archivo_id": str(uuid.uuid4()),
        "nombre": file_name,
        "url": image_url,
        "estado": "pendiente",
        "comentario": "",
        "modificado": True,
        "fecha_modificacion": datetime.now().isoformat(),
        "ultima_fecha_modificacion": datetime.now().isoformat()
    }

    return datos_actualizados

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
