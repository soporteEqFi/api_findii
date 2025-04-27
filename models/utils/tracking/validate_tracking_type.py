import json

# with open('models/utils/tracking/tracking_types.json', 'r') as f:
#     tracking_types = json.load(f)

tracking_types = ["documentos", "banco", "desembolso"]

def validate_etapa_type(etapa_selected):
    """
        Valida de qué tipo se trata el tracking.
    """
    for etapa_type in tracking_types:
        if etapa_type == etapa_selected:
            return etapa_type
        else:
            return 'No se encontró la etapa'