from flask import Blueprint
from controllers.estadisticas_controller import EstadisticasController

# Crear blueprint
estadisticas_bp = Blueprint('estadisticas', __name__)

# Instanciar controller
estadisticas_controller = EstadisticasController()

@estadisticas_bp.route('/generales', methods=['GET'])
def get_estadisticas_generales():
    """
    Obtener estadísticas generales del sistema
    - Total de solicitantes
    - Total de solicitudes
    - Solicitudes por estado
    - Solicitudes por banco (según permisos)
    - Solicitudes por ciudad (según permisos)
    - Total de documentos
    """
    return estadisticas_controller.estadisticas_generales()

@estadisticas_bp.route('/rendimiento', methods=['GET'])
def get_estadisticas_rendimiento():
    """
    Obtener estadísticas de rendimiento
    Query params:
    - dias: número de días para el análisis (default: 30)
    
    Retorna:
    - Solicitudes creadas por día
    - Solicitudes completadas vs pendientes
    - Productividad por usuario (según permisos)
    """
    return estadisticas_controller.estadisticas_rendimiento()

@estadisticas_bp.route('/financieras', methods=['GET'])
def get_estadisticas_financieras():
    """
    Obtener estadísticas financieras y de calidad
    - Rangos de ingresos de solicitantes
    - Tipos de actividad económica más comunes
    - Referencias promedio por solicitante
    - Documentos promedio por solicitante
    """
    return estadisticas_controller.estadisticas_financieras()

@estadisticas_bp.route('/usuarios', methods=['GET'])
def get_estadisticas_usuarios():
    """
    Obtener estadísticas de usuarios por empresa
    Solo disponible para admin y supervisor
    
    Retorna:
    - Total de usuarios
    - Usuarios por rol
    - Usuarios por banco (desde info_extra)
    - Usuarios por ciudad (desde info_extra)
    """
    return estadisticas_controller.estadisticas_usuarios()

@estadisticas_bp.route('/completas', methods=['GET'])
def get_estadisticas_completas():
    """
    Obtener todas las estadísticas en una sola llamada
    Query params:
    - dias: número de días para análisis de rendimiento (default: 30)
    
    Retorna todas las categorías de estadísticas:
    - Generales
    - Rendimiento  
    - Financieras
    - Usuarios (solo admin/supervisor)
    """
    return estadisticas_controller.estadisticas_completas()

# Alias para compatibilidad
estadisticas = estadisticas_bp
