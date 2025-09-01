from __future__ import annotations
from typing import Any, Dict, List, Optional
from data.supabase_conn import supabase

def _get_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp

class ConfiguracionesModel:
    """Operaciones para la tabla configuraciones usando Supabase."""

    TABLE = "configuraciones"

    def obtener_por_categoria(self, *, empresa_id: int, categoria: str) -> List[str]:
        """Obtener configuración por categoría (ej: ciudades, bancos)"""
        try:
            resp = supabase.table(self.TABLE).select("configuracion").eq("empresa_id", empresa_id).eq("categoria", categoria).eq("activo", True).execute()
            data = _get_data(resp)

            if data and len(data) > 0:
                # configuracion es un JSONB que contiene una lista
                return data[0].get("configuracion", [])
            return []

        except Exception as e:
            print(f"❌ Error obteniendo configuración {categoria}: {e}")
            return []

    def obtener_todas_categorias(self, *, empresa_id: int) -> Dict[str, List[str]]:
        """Obtener todas las configuraciones de una empresa"""
        try:
            resp = supabase.table(self.TABLE).select("categoria, configuracion").eq("empresa_id", empresa_id).eq("activo", True).execute()
            data = _get_data(resp)

            configuraciones = {}
            for item in data:
                categoria = item.get("categoria")
                configuracion = item.get("configuracion", [])
                if categoria:
                    configuraciones[categoria] = configuracion

            return configuraciones

        except Exception as e:
            print(f"❌ Error obteniendo configuraciones: {e}")
            return {}

    def obtener_columnas_tabla(self, *, empresa_id: int) -> Dict[str, Any]:
        """Obtener configuración de columnas para tablas"""
        try:
            resp = supabase.table(self.TABLE).select("*").eq("empresa_id", empresa_id).eq("categoria", "columnas_tabla").eq("activo", True).execute()
            data = _get_data(resp)

            if data and len(data) > 0:
                configuracion = data[0].get("configuracion", [])
                
                # Si la configuración es una lista simple, convertirla al nuevo formato
                if configuracion and isinstance(configuracion[0], str):
                    configuracion = [
                        {
                            "nombre": col,
                            "activo": True,
                            "orden": idx
                        } for idx, col in enumerate(configuracion)
                    ]
                
                return {
                    "id": data[0].get("id"),
                    "categoria": data[0].get("categoria"),
                    "columnas": configuracion,
                    "descripcion": data[0].get("descripcion"),
                    "created_at": data[0].get("created_at"),
                    "updated_at": data[0].get("updated_at")
                }
            return {}

        except Exception as e:
            print(f"❌ Error obteniendo configuración de columnas: {e}")
            return {}

    def actualizar_columnas_tabla(self, *, empresa_id: int, columnas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Actualizar configuración de columnas para tablas"""
        try:
            # Buscar la configuración existente
            resp = supabase.table(self.TABLE).select("id").eq("empresa_id", empresa_id).eq("categoria", "columnas_tabla").execute()
            data = _get_data(resp)

            if data and len(data) > 0:
                # Actualizar configuración existente
                config_id = data[0]["id"]
                resp = supabase.table(self.TABLE).update({
                    "configuracion": columnas,
                    "updated_at": "now()"
                }).eq("id", config_id).execute()
                
                updated_data = _get_data(resp)
                return updated_data[0] if updated_data else {}
            else:
                # Crear nueva configuración
                resp = supabase.table(self.TABLE).insert({
                    "empresa_id": empresa_id,
                    "categoria": "columnas_tabla",
                    "configuracion": columnas,
                    "descripcion": "Configuración de columnas de tabla",
                    "activo": True
                }).execute()
                
                created_data = _get_data(resp)
                return created_data[0] if created_data else {}

        except Exception as e:
            print(f"❌ Error actualizando configuración de columnas: {e}")
            return {}

    def agregar_columna(self, *, empresa_id: int, nombre_columna: str) -> Dict[str, Any]:
        """Agregar una nueva columna a la configuración"""
        try:
            config_actual = self.obtener_columnas_tabla(empresa_id=empresa_id)
            
            if not config_actual:
                # Si no existe configuración, crear una nueva
                nueva_columna = [{
                    "nombre": nombre_columna,
                    "activo": True,
                    "orden": 0
                }]
            else:
                columnas_actuales = config_actual.get("columnas", [])
                
                # Verificar si la columna ya existe
                if any(col.get("nombre") == nombre_columna for col in columnas_actuales):
                    raise ValueError(f"La columna '{nombre_columna}' ya existe")
                
                # Agregar nueva columna al final
                nuevo_orden = max([col.get("orden", 0) for col in columnas_actuales], default=-1) + 1
                columnas_actuales.append({
                    "nombre": nombre_columna,
                    "activo": True,
                    "orden": nuevo_orden
                })
                nueva_columna = columnas_actuales

            return self.actualizar_columnas_tabla(empresa_id=empresa_id, columnas=nueva_columna)

        except Exception as e:
            print(f"❌ Error agregando columna: {e}")
            raise e
