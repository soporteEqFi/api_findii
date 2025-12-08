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
                    {"key": "estado", "type": "string", "required": True, "description": "Estado de la solicitud"},
                    {"key": "banco_nombre", "type": "string", "required": False, "description": "Nombre del banco"},
                    {"key": "ciudad_solicitud", "type": "string", "required": False, "description": "Ciudad de la solicitud"}
                ]
            }
        }

    def _procesar_list_values_con_order_index(self, list_values):
        """Procesa list_values para incluir order_index en arrays y objetos"""
        if not list_values:
            return list_values

        # Si es un array simple (enum)
        if isinstance(list_values, list) and all(isinstance(item, str) for item in list_values):
            return {
                "enum": list_values,
                "order_index": 1  # Valor por defecto
            }

        # Si ya es un objeto con enum
        if isinstance(list_values, dict) and "enum" in list_values:
            if "order_index" not in list_values:
                list_values["order_index"] = 1
            return list_values

        # Si es un array de objetos (object_structure)
        if isinstance(list_values, list) and len(list_values) > 0 and isinstance(list_values[0], dict):
            # Verificar si ya tiene order_index
            for item in list_values:
                if "order_index" not in item:
                    item["order_index"] = 1

            return {
                "array_type": "object",
                "object_structure": list_values
            }

        return list_values

    def _ordenar_campos_por_order_index(self, campos):
        """Ordena los campos por order_index si está presente"""
        def get_order_index(campo):
            # Prioridad 1: order_index en la columna fija (BD)
            if "order_index" in campo and campo["order_index"] is not None:
                return campo["order_index"]

            # Prioridad 2: order_index en list_values (JSON)
            if "list_values" in campo and isinstance(campo["list_values"], dict):
                order_index = campo["list_values"].get("order_index", 999)
                return order_index if order_index is not None else 999

            # Prioridad 3: order_index en object_structure
            if "list_values" in campo and isinstance(campo["list_values"], dict) and "object_structure" in campo["list_values"]:
                object_structure = campo["list_values"]["object_structure"]
                if object_structure and "order_index" in object_structure[0]:
                    order_index = object_structure[0]["order_index"]
                    return order_index if order_index is not None else 999

            return 999  # Valor por defecto para campos sin order_index

        return sorted(campos, key=get_order_index)

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

            # 3. Formatear campos dinámicos con soporte para order_index híbrido
            campos_dinamicos_formateados = []
            for campo in campos_dinamicos:
                # Procesar list_values para incluir order_index
                list_values_procesados = self._procesar_list_values_con_order_index(campo.get("list_values"))

                campo_formateado = {
                    "key": campo["key"],
                    "type": campo["type"],
                    "required": campo.get("required", False),
                    "description": campo.get("description", ""),
                    "default_value": campo.get("default_value"),
                    "list_values": list_values_procesados,
                    "conditional_on": campo.get("conditional_on"),
                    "order_index": campo.get("order_index", 999),  # Columna fija de BD
                    "min_value": campo.get("min_value"),  # Validación numérica mínima
                    "max_value": campo.get("max_value")   # Validación numérica máxima
                }
                campos_dinamicos_formateados.append(campo_formateado)

            # 4. Ordenar campos dinámicos por order_index (priorizando columna fija)
            campos_dinamicos_formateados = self._ordenar_campos_por_order_index(campos_dinamicos_formateados)

            # 5. Combinar resultado
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
