from models.utils.tracking.states import get_state_avaiable
from models.utils.others.date_utils import iso_date
from flask import jsonify

def get_etapa_by_radicado(id_radicado, supabase):
    query = supabase.table('SEGUIMIENTO_SOLICITUDES').select('*')
    query = query.eq('id_radicado', id_radicado)
    seguimiento = query.execute()

    if not seguimiento.data:
        return jsonify({"error": "Seguimiento no encontrado"}), 404
    
    return seguimiento.data

def update_modification_date(etapa):
    etapa['fecha_actualizacion'] = iso_date()
    return etapa

def files_dict(uploaded_files_data, usuario_id):
    etapa_file = {
        "archivo_id": uploaded_files_data['archivo_id'],
        "nombre": uploaded_files_data['nombre'],
        "url": uploaded_files_data['url'],
        "estado": get_state_avaiable()['pendiente'], # Valor por defecto ya que son archivos nuevos y no se han procesado
        "comentario": "",
        "modificado": False,
        "usuario_id": usuario_id,
        "fecha_modificacion": iso_date(),
        "ultima_fecha_modificacion": iso_date()
    }
    return etapa_file