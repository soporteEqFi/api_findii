from flask import jsonify

def validate_etapa_data(request):
    """
        Valida los datos de la solicitud de seguimiento.
    """
            # Verificar si hay un ID de seguimiento
    if 'id_radicado' not in request.form:
        return jsonify({"error": "Falta el ID del radicado"}), 400
    
    # Verificar si se envió el ID de usuario
    if 'usuario_id' not in request.form:
        return jsonify({"error": "Falta el ID del usuario"}), 400
        
    # Verificar la etapa a modificar
    if 'etapa' not in request.form:
        return jsonify({"error": "Falta especificar la etapa a modificar"}), 400
    
    etapa = request.form.get('etapa')
    usuario_id = request.form.get('usuario_id')
    id_radicado = request.form.get('id_radicado')
    
    return id_radicado, usuario_id, etapa