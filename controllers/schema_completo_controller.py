from models.schema_completo_model import SchemaCompletoModel
from flask import request

class SchemaCompletoController:
    def __init__(self):
        self.model = SchemaCompletoModel()

    def get_schema_completo(self, entity):
        """Obtiene esquema completo (campos fijos + dinámicos) para una entidad"""
        try:
            # Obtener empresa_id del query param
            empresa_id = request.args.get('empresa_id')
            if not empresa_id:
                return {
                    "ok": False,
                    "error": "Parámetro 'empresa_id' es requerido"
                }, 400

            print(f"[SCHEMA] Obteniendo schema completo para: {entity}, empresa_id: {empresa_id}")

            # Obtener schema del modelo
            schema, error = self.model.get_schema_completo(entity, empresa_id)

            if error:
                print(f"[SCHEMA] Error: {error}")
                return {
                    "ok": False,
                    "error": error
                }, 404

            print(f"[SCHEMA] Schema obtenido exitosamente")
            print(f"[SCHEMA] Campos fijos: {len(schema['campos_fijos'])}")
            print(f"[SCHEMA] Campos dinámicos: {len(schema['campos_dinamicos'])}")

            return {
                "ok": True,
                "data": schema
            }, 200

        except Exception as e:
            print(f"[SCHEMA] Error en get_schema_completo: {str(e)}")
            return {
                "ok": False,
                "error": f"Error interno: {str(e)}"
            }, 500
