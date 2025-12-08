from __future__ import annotations
from typing import Any, Dict, List
from data.supabase_conn import supabase

def _get_resp_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp

class JSONSchemaModel:
    """Acceso al catálogo json_field_definition en Supabase."""

    TABLE = "json_field_definition"

    def get_schema(self, *, empresa_id: int, entity: str, json_column: str) -> List[Dict[str, Any]]:
        # Incluir order_index, min_value y max_value en la consulta
        resp = supabase.table(self.TABLE).select("id, empresa_id, entity, json_column, key, type, required, list_values, description, default_value, conditional_on, order_index, min_value, max_value, created_at").eq("empresa_id", empresa_id).eq("entity", entity).eq("json_column", json_column).execute()
        data = _get_resp_data(resp)
        return data or []

    def _procesar_order_index_hibrido(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa order_index tanto en columna fija como en list_values"""
        processed_item = item.copy()

        # Validar default_value: convertir strings vacíos a null
        if "default_value" in processed_item and processed_item["default_value"] == "":
            processed_item["default_value"] = None

        # Si hay order_index en el item principal, usarlo como prioridad
        if "order_index" in processed_item:
            # Si también hay list_values con order_index, mantener ambos
            if "list_values" in processed_item and isinstance(processed_item["list_values"], dict):
                # Para arrays con enum
                if "enum" in processed_item["list_values"]:
                    if "order_index" not in processed_item["list_values"]:
                        processed_item["list_values"]["order_index"] = processed_item["order_index"]

                # Para arrays de objetos
                elif "object_structure" in processed_item["list_values"]:
                    # Asegurar que cada objeto en object_structure tenga order_index
                    for obj in processed_item["list_values"]["object_structure"]:
                        if "order_index" not in obj:
                            obj["order_index"] = 1

        # Si no hay order_index en el item principal pero sí en list_values
        elif "list_values" in processed_item and isinstance(processed_item["list_values"], dict):
            if "order_index" in processed_item["list_values"]:
                processed_item["order_index"] = processed_item["list_values"]["order_index"]
            elif "object_structure" in processed_item["list_values"]:
                # Usar el order_index del primer elemento o valor por defecto
                object_structure = processed_item["list_values"]["object_structure"]
                if object_structure and "order_index" in object_structure[0]:
                    processed_item["order_index"] = object_structure[0]["order_index"]
                else:
                    processed_item["order_index"] = 999

        # Valor por defecto si no hay order_index en ningún lugar
        if "order_index" not in processed_item:
            processed_item["order_index"] = 999

        return processed_item

    def upsert_definitions(self, *, empresa_id: int, entity: str, json_column: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        print(f"🏗️ upsert_definitions llamado con:")
        print(f"   empresa_id: {empresa_id}")
        print(f"   entity: {entity}")
        print(f"   json_column: {json_column}")
        print(f"   items: {items}")

        # Normaliza items agregando claves fijas
        payload: List[Dict[str, Any]] = []
        for it in items:
            print(f"🔍 Procesando item: {it}")
            if not isinstance(it, dict) or "key" not in it:
                raise ValueError("Cada item debe incluir 'key'")

            # Procesar order_index híbrido
            processed_item = self._procesar_order_index_hibrido(it)

            normalized_item = {
                "empresa_id": empresa_id,
                "entity": entity,
                "json_column": json_column,
                "key": processed_item.get("key"),
                "type": processed_item.get("type", "string"),
                "required": bool(processed_item.get("required", False)),
                "list_values": processed_item.get("list_values"),
                "description": processed_item.get("description"),
                "default_value": processed_item.get("default_value"),
                "conditional_on": processed_item.get("conditional_on"),
                "order_index": processed_item.get("order_index", 999),  # Columna fija
                "min_value": processed_item.get("min_value"),  # Validación numérica mínima
                "max_value": processed_item.get("max_value"),  # Validación numérica máxima
            }
            print(f"✅ Item normalizado: {normalized_item}")
            payload.append(normalized_item)

        print(f"📦 Payload final para Supabase: {payload}")
        print(f"🎯 Tabla destino: {self.TABLE}")

        try:
            # Primero intentar eliminar registros existentes para evitar duplicados
            for item in payload:
                print(f"🗑️ Eliminando definición existente: {item['key']}")
                supabase.table(self.TABLE).delete().eq("empresa_id", item["empresa_id"]).eq("entity", item["entity"]).eq("json_column", item["json_column"]).eq("key", item["key"]).execute()

            # Luego insertar los nuevos registros
            resp = supabase.table(self.TABLE).insert(payload).execute()
            print(f"📡 Respuesta de Supabase: {resp}")

            data = _get_resp_data(resp)
            print(f"📊 Datos extraídos: {data}")
            return data or []

        except Exception as e:
            print(f"💥 Error en Supabase insert: {e}")
            print(f"💥 Tipo de error: {type(e)}")
            import traceback
            traceback.print_exc()
            raise

    def delete_definition(self, *, empresa_id: int, entity: str, json_column: str, key: str | None = None) -> int:
        q = (
            supabase.table(self.TABLE)
            .delete()
            .eq("empresa_id", empresa_id)
            .eq("entity", entity)
            .eq("json_column", json_column)
        )
        if key:
            q = q.eq("key", key)
        resp = q.execute()
        data = _get_resp_data(resp)
        # supabase devuelve deleted rows en data; retornamos cantidad
        if isinstance(data, list):
            return len(data)
        return 0

    def update_definition(self, *, definition_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Actualizar una definición específica por ID (UUID)"""
        print(f"🔄 update_definition llamado con:")
        print(f"   definition_id: {definition_id}")
        print(f"   updates: {updates}")

        try:
            # Validar default_value: convertir strings vacíos a null
            if "default_value" in updates and updates["default_value"] == "":
                updates["default_value"] = None
                print(f"   🔄 default_value convertido de '' a null")

            # Procesar order_index híbrido si está presente
            if "order_index" in updates or "list_values" in updates:
                # Obtener la definición actual para procesar correctamente
                current_def = self._get_definition_by_id(definition_id)
                if current_def:
                    # Combinar con las actualizaciones
                    combined_item = {**current_def, **updates}
                    processed_updates = self._procesar_order_index_hibrido(combined_item)

                    # Solo incluir los campos que se están actualizando
                    final_updates = {}
                    for key, value in processed_updates.items():
                        if key in updates or key == "order_index":
                            final_updates[key] = value

                    updates = final_updates

            resp = supabase.table(self.TABLE).update(updates).eq("id", definition_id).execute()
            print(f"📡 Respuesta de Supabase: {resp}")

            data = _get_resp_data(resp)
            print(f"📊 Datos extraídos: {data}")

            if data and isinstance(data, list) and len(data) > 0:
                return data[0]
            else:
                raise ValueError(f"No se encontró la definición con ID {definition_id}")

        except Exception as e:
            print(f"💥 Error en Supabase update: {e}")
            print(f"💥 Tipo de error: {type(e)}")
            import traceback
            traceback.print_exc()
            raise

    def _get_definition_by_id(self, definition_id: str) -> Dict[str, Any] | None:
        """Obtener una definición específica por ID"""
        try:
            resp = supabase.table(self.TABLE).select("*").eq("id", definition_id).execute()
            data = _get_resp_data(resp)
            if data and isinstance(data, list) and len(data) > 0:
                return data[0]
            return None
        except Exception as e:
            print(f"Error obteniendo definición por ID: {e}")
            return None


