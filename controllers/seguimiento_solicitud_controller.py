# controllers/seguimiento_solicitud_controller.py
from models.seguimiento_solicitud import trackingModel

class trackingController():
    def __init__(self):
        self.tracking_model = trackingModel()
    
    def crear_seguimiento(self):
        return self.tracking_model.crear_seguimiento()
    
    def consultar_seguimiento_por_radicado(self, id_radicado):
        return self.tracking_model.consultar_seguimiento(id_radicado=id_radicado)
        
    def consultar_seguimiento_por_solicitante(self, id_solicitante):
        return self.tracking_model.consultar_seguimiento(id_solicitante=id_solicitante)
    
    def actualizar_etapa(self):
        return self.tracking_model.actualizar_etapa()
        
    def actualizar_documentos(self):
        return self.tracking_model.actualizar_documentos()
    
    def consultar_seguimiento_publico(self, id_radicado):
        return self.tracking_model.consultar_seguimiento_por_radicado_publico(id_radicado)