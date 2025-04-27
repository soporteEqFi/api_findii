# routes/tracking_routes.py
from librerias import *
from controllers.seguimiento_solicitud_controller import trackingController

tracking = Blueprint('tracking', __name__)
controller = trackingController()

@tracking.route('/api/seguimiento/actualizar', methods=['POST'])
def update_status():
    return controller.update_status()

@tracking.route('/api/solicitudes/usuario/<cedula>', methods=['GET'])
def get_user_applications(cedula):
    return controller.get_user_applications(cedula)

# Crear nuevo seguimiento
@tracking.route('/api/seguimiento/crear', methods=['POST'])
def crear_seguimiento():
    return controller.crear_seguimiento()

# Consultar seguimiento por radicado (para usuarios)
@tracking.route('/api/seguimiento/radicado/<id_radicado>', methods=['GET'])
def consultar_por_radicado(id_radicado):
    return controller.consultar_seguimiento_por_radicado(id_radicado)

# Consultar seguimiento por solicitante (para admin)
@tracking.route('/api/seguimiento/solicitante/<id_solicitante>', methods=['GET'])
def consultar_por_solicitante(id_solicitante):
    return controller.consultar_seguimiento_por_solicitante(id_solicitante)

# Actualizar estado de una etapa
@tracking.route('/api/seguimiento/actualizar-etapa', methods=['POST'])
def actualizar_etapa():
    return controller.actualizar_etapa()

# Subir documentos
@tracking.route('/api/seguimiento/subir-documentos', methods=['POST'])
def actualizar_documentos():
    return controller.actualizar_documentos()

# Consulta pública por ID de radicado (para usuarios sin autenticación)
@tracking.route('/api/seguimiento/consulta/<id_radicado>', methods=['GET'])
def consultar_publico(id_radicado):
    return controller.consultar_seguimiento_publico(id_radicado)