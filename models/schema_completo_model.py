from data.supabase_conn import supabase

class SchemaCompletoModel:
    def __init__(self):
        # Mapeo de entidades a sus tablas y columnas JSON
        self._entity_map = {
            "solicitante": {
                "table": "solicitantes",
                "json_column": "info_extra",
                "campos_fijos": [
                    {"key": "nombres", "type": "string", "required": True, "description": "Nombres"},
                    {"key": "primer_apellido", "type": "string", "required": True, "description": "Primer apellido"},
                    {"key": "segundo_apellido", "type": "string", "required": False, "description": "Segundo apellido"},
                    {"key": "tipo_identificacion", "type": "string", "required": True, "description": "Tipo de identificación"},
                    {"key": "numero_documento", "type": "string", "required": True, "description": "Número de documento"},
                    {"key": "fecha_nacimiento", "type": "string", "required": True, "description": "Fecha de nacimiento"},
                    {"key": "genero", "type": "string", "required": True, "description": "Género"},
                    {"key": "correo", "type": "string", "required": True, "description": "Correo electrónico"}
                ]
            },
            "ubicacion": {
                "table": "ubicacion",
                "json_column": "detalle_direccion",
                "campos_fijos": [
                    {"key": "ciudad_residencia", "type": "string", "required": True, "description": "Ciudad"},
                    {"key": "departamento_residencia", "type": "string", "required": True, "description": "Departamento"}
                ]
            },
            "actividad_economica": {
                "table": "actividad_economica",
                "json_column": "detalle_actividad",
                "campos_fijos": []
            },
            "informacion_financiera": {
                "table": "informacion_financiera",
                "json_column": "detalle_financiera",
                "campos_fijos": [
                    {"key": "total_ingresos_mensuales", "type": "number", "required": True, "description": "Ingresos mensuales"},
                    {"key": "total_egresos_mensuales", "type": "number", "required": True, "description": "Egresos mensuales"},
                    {"key": "total_activos", "type": "number", "required": False, "description": "Total activos"},
                    {"key": "total_pasivos", "type": "number", "required": False, "description": "Total pasivos"}
                ]
            },
            "referencia": {
                "table": "referencias",
                "json_column": "detalle_referencia",
                "campos_fijos": [
                    {"key": "tipo_referencia", "type": "string", "required": True, "description": "Tipo de referencia"},
                ]
            },
            "solicitud": {
                "table": "solicitudes",
                "json_column": "detalle_credito",
                "campos_fijos": [
                    {"key": "estado", "type": "string", "required": True, "description": "Estado de la solicitud"}
                ]
            }
        }

    def get_schema_completo(self, entity, empresa_id):
        """Obtiene esquema completo: campos fijos + dinámicos"""
        try:
            # Validar entidad
            if entity not in self._entity_map:
                return None, f"Entidad '{entity}' no encontrada"

            entity_info = self._entity_map[entity]

            # 1. Obtener campos fijos (estructura predefinida)
            campos_fijos = entity_info["campos_fijos"]

            # 2. Obtener campos dinámicos de json_field_definition
            response = supabase.table("json_field_definition").select("*").eq("entity", entity).eq("json_column", entity_info["json_column"]).eq("empresa_id", empresa_id).execute()

            if hasattr(response, 'data'):
                campos_dinamicos = response.data or []
            else:
                campos_dinamicos = []

            # 3. Formatear campos dinámicos
            campos_dinamicos_formateados = []
            for campo in campos_dinamicos:
                campo_formateado = {
                    "key": campo["key"],
                    "type": campo["type"],
                    "required": campo.get("required", False),
                    "description": campo.get("description", ""),
                    "default_value": campo.get("default_value"),
                    "list_values": campo.get("list_values"),
                    "conditional_on": campo.get("conditional_on")
                }
                campos_dinamicos_formateados.append(campo_formateado)

            # 4. Combinar resultado
            schema_completo = {
                "entidad": entity,
                "tabla": entity_info["table"],
                "json_column": entity_info["json_column"],
                "campos_fijos": campos_fijos,
                "campos_dinamicos": campos_dinamicos_formateados,
                "total_campos": len(campos_fijos) + len(campos_dinamicos_formateados)
            }

            return schema_completo, None

        except Exception as e:
            print(f"Error en get_schema_completo: {str(e)}")
            return None, f"Error obteniendo schema: {str(e)}"
