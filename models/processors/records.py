from flask import jsonify

class RecordsDataProcessor:
    def __init__(self, request) -> None:
        # Inicialización de los datos del solicitante
        self.applicant_id = None
        self.request = request
            
    def set_applicant_id(self, id):
        # Establecer el ID del solicitante
        self.applicant_id = id

    def get_applicant_data(self):
        return {
            "nombre_completo": self.request.form.get('nombre_completo'),
            "tipo_documento": self.request.form.get('tipo_documento'), 
            "numero_documento": self.request.form.get('numero_documento'),
            "fecha_nacimiento": self.request.form.get('fecha_nacimiento'),
            "numero_celular": self.request.form.get('numero_celular'),
            "correo_electronico": self.request.form.get('correo_electronico'),
            "nivel_estudio": self.request.form.get('nivel_estudio'),
            "profesion": self.request.form.get('profesion'),  # Campo opcional
            "estado_civil": self.request.form.get('estado_civil'),
            "personas_a_cargo": self.request.form.get('personas_a_cargo')
        }
        
    def get_location_data(self):
        # Obtener datos de ubicación
        return {
            "solicitante_id": self.applicant_id,
            "direccion_residencia": self.request.form.get('direccion_residencia'),
            "tipo_vivienda": self.request.form.get('tipo_vivienda'), 
            "barrio": self.request.form.get('barrio'),
            "departamento": self.request.form.get('departamento'),
            "estrato": self.request.form.get('estrato'),
            "ciudad_gestion": self.request.form.get('ciudad_gestion')
        }
        
    def get_economic_activity_data(self):
        # Obtener datos de actividad económica
        return {
            "solicitante_id": self.applicant_id,
            "actividad_economica": self.request.form.get('actividad_economica'),
            "empresa_labora": self.request.form.get('empresa_labora'),
            "fecha_vinculacion": self.request.form.get('fecha_vinculacion'),
            "direccion_empresa": self.request.form.get('direccion_empresa'),
            "telefono_empresa": self.request.form.get('telefono_empresa'),
            "tipo_contrato": self.request.form.get('tipo_contrato'),
            "cargo_actual": self.request.form.get('cargo_actual')
        }
        
    def get_financial_data(self):
        # Obtener datos financieros
        return {
            "solicitante_id": self.applicant_id,
            "ingresos": self.request.form.get('ingresos'),
            "valor_inmueble": self.request.form.get('valor_inmueble'),
            "cuota_inicial": self.request.form.get('cuota_inicial'),
            "porcentaje_financiar": self.request.form.get('porcentaje_financiar'),
            "total_egresos": self.request.form.get('total_egresos'),
            "total_activos": self.request.form.get('total_activos'),
            "total_pasivos": self.request.form.get('total_pasivos')
        }
        
    def get_product_data(self):
        # Obtener datos del producto
        return {
            "solicitante_id": self.applicant_id,
            "tipo_credito": self.request.form.get('tipo_credito'),
            "plazo_meses": self.request.form.get('plazo_meses'),
            "segundo_titular": True if self.request.form.get('segundo_titular') == 's' else False,
            "observacion": self.request.form.get('observacion'),
            "estado": "Radicado"
        }
        
    def get_request_data(self):
        # Obtener datos de la solicitud
        return {
            "solicitante_id": self.applicant_id,
            "banco": self.request.form.get('banco')
        }
        
    def get_bank(self):
        # Obtener banco
        return self.request.form.get('banco')
