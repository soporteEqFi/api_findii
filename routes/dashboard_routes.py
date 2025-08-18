from flask import Blueprint, request
from controllers.dashboard_controller import DashboardController

# Crear blueprint para las rutas del dashboard
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/tabla', methods=['GET'])
def get_dashboard_data():
    # Obtener empresa_id de query params o headers
    empresa_id = request.args.get('empresa_id') or request.headers.get('X-Empresa-Id')
    
    if not empresa_id:
        return {"ok": False, "error": "Se requiere el parámetro 'empresa_id'"}, 400
    
    try:
        empresa_id = int(empresa_id)
    except ValueError:
        return {"ok": False, "error": "'empresa_id' debe ser un número entero"}, 400
    
    return DashboardController.get_dashboard_data(empresa_id)
