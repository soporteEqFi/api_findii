from __future__ import annotations
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from data.supabase_conn import supabase

def _get_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp

class NotificacionesModel:
    """Modelo para gestión de notificaciones."""

    def __init__(self):
        self.notificaciones_table = "notificaciones"
        self.configuraciones_table = "configuraciones"

    def get_configuracion_notificaciones(self, empresa_id: int) -> Optional[Dict]:
        """Obtiene la configuración de notificaciones para una empresa."""
        try:
            resp = supabase.table(self.configuraciones_table).select("*").eq("empresa_id", empresa_id).eq("categoria", "notificaciones_recordatorio").eq("activo", True).execute()

            data = _get_data(resp)
            if not data or len(data) == 0:
                return None

            return data[0]
        except Exception as e:
            print(f"Error al obtener configuración de notificaciones: {e}")
            return None

    def validar_notificacion(self, empresa_id: int, datos: Dict) -> tuple[bool, str]:
        """Valida una notificación contra la configuración de la empresa."""
        try:
            config = self.get_configuracion_notificaciones(empresa_id)
            if not config:
                return False, "No se encontró configuración de notificaciones para la empresa"

            config_data = config.get("configuracion", {})
            tipos_disponibles = config_data.get("tipos_disponibles", [])

            # Validar tipo
            tipo = datos.get("tipo")
            tipo_config = None
            for t in tipos_disponibles:
                if t.get("tipo") == tipo:
                    tipo_config = t
                    break

            if not tipo_config:
                return False, f"Tipo de notificación '{tipo}' no está configurado"

            # Validar prioridad
            prioridad = datos.get("prioridad", "normal")
            prioridades_validas = tipo_config.get("prioridades", [])
            if prioridad not in prioridades_validas:
                return False, f"Prioridad '{prioridad}' no es válida. Opciones: {prioridades_validas}"

            # Validar estado
            estado = datos.get("estado", "pendiente")
            estados_validos = tipo_config.get("estados", [])
            if estado not in estados_validos:
                return False, f"Estado '{estado}' no es válido. Opciones: {estados_validos}"

            # Validar metadata
            metadata = datos.get("metadata", {})
            metadata_estructura = tipo_config.get("metadata_estructura", {})

            for campo, config_campo in metadata_estructura.items():
                if config_campo.get("requerido", False) and campo not in metadata:
                    return False, f"Campo requerido faltante en metadata: {campo}"

                if campo in metadata:
                    valor = metadata[campo]
                    tipo_esperado = config_campo.get("tipo")

                    # Validar tipo
                    if tipo_esperado == "string" and not isinstance(valor, str):
                        return False, f"Campo '{campo}' debe ser string"
                    elif tipo_esperado == "number" and not isinstance(valor, (int, float)):
                        return False, f"Campo '{campo}' debe ser number"
                    elif tipo_esperado == "boolean" and not isinstance(valor, bool):
                        return False, f"Campo '{campo}' debe ser boolean"

                    # Validar opciones si existen
                    opciones = config_campo.get("opciones")
                    if opciones and valor not in opciones:
                        return False, f"Valor '{valor}' no es válido para '{campo}'. Opciones: {opciones}"

            return True, "Validación exitosa"

        except Exception as e:
            return False, f"Error en validación: {str(e)}"

    def create(self, empresa_id: int, **kwargs) -> Optional[Dict]:
        """Crea una nueva notificación."""
        try:
            # Validar datos
            es_valida, mensaje = self.validar_notificacion(empresa_id, kwargs)
            if not es_valida:
                print(f"Error de validación: {mensaje}")
                return None

            # Preparar datos
            datos_notificacion = {
                "empresa_id": empresa_id,
                "tipo": kwargs["tipo"],
                "titulo": kwargs["titulo"],
                "mensaje": kwargs["mensaje"],
                "fecha_recordatorio": kwargs["fecha_recordatorio"],
                "fecha_vencimiento": kwargs.get("fecha_vencimiento"),
                "estado": kwargs.get("estado", "pendiente"),
                "prioridad": kwargs.get("prioridad", "normal"),
                "solicitud_id": kwargs.get("solicitud_id"),
                "usuario_id": kwargs.get("usuario_id"),
                "metadata": kwargs.get("metadata", {})
            }

            # Crear en BD
            resp = supabase.table(self.notificaciones_table).insert(datos_notificacion).execute()

            data = _get_data(resp)
            if not data or len(data) == 0:
                return None

            return data[0]

        except Exception as e:
            print(f"Error al crear notificación: {e}")
            return None

    def list(self, empresa_id: int, **filtros) -> List[Dict]:
        """Lista notificaciones con filtros opcionales."""
        try:
            query = supabase.table(self.notificaciones_table).select("*").eq("empresa_id", empresa_id)

            # Aplicar filtros
            if filtros.get("tipo"):
                query = query.eq("tipo", filtros["tipo"])
            if filtros.get("estado"):
                query = query.eq("estado", filtros["estado"])
            if filtros.get("solicitud_id"):
                query = query.eq("solicitud_id", filtros["solicitud_id"])
            if filtros.get("usuario_id"):
                query = query.eq("usuario_id", filtros["usuario_id"])
            if filtros.get("prioridad"):
                query = query.eq("prioridad", filtros["prioridad"])

            # Ordenar por fecha de recordatorio
            query = query.order("fecha_recordatorio", desc=False)

            resp = query.execute()
            return _get_data(resp) or []

        except Exception as e:
            print(f"Error al listar notificaciones: {e}")
            return []

    def get_by_id(self, notificacion_id: int, empresa_id: int) -> Optional[Dict]:
        """Obtiene una notificación específica."""
        try:
            resp = supabase.table(self.notificaciones_table).select("*").eq("id", notificacion_id).eq("empresa_id", empresa_id).execute()

            data = _get_data(resp)
            if not data or len(data) == 0:
                return None

            return data[0]

        except Exception as e:
            print(f"Error al obtener notificación: {e}")
            return None

    def update(self, notificacion_id: int, empresa_id: int, **kwargs) -> Optional[Dict]:
        """Actualiza una notificación."""
        try:
            # Verificar que existe
            notificacion_actual = self.get_by_id(notificacion_id, empresa_id)
            if not notificacion_actual:
                return None

            # Validar datos si se están actualizando campos críticos
            if "tipo" in kwargs or "metadata" in kwargs:
                datos_completos = {**notificacion_actual, **kwargs}
                es_valida, mensaje = self.validar_notificacion(empresa_id, datos_completos)
                if not es_valida:
                    print(f"Error de validación en actualización: {mensaje}")
                    return None

            # Actualizar
            resp = supabase.table(self.notificaciones_table).update(kwargs).eq("id", notificacion_id).execute()

            data = _get_data(resp)
            if not data or len(data) == 0:
                return None

            return data[0]

        except Exception as e:
            print(f"Error al actualizar notificación: {e}")
            return None

    def delete(self, notificacion_id: int, empresa_id: int) -> bool:
        """Elimina una notificación."""
        try:
            resp = supabase.table(self.notificaciones_table).delete().eq("id", notificacion_id).eq("empresa_id", empresa_id).execute()

            data = _get_data(resp)
            return data is not None and len(data) > 0

        except Exception as e:
            print(f"Error al eliminar notificación: {e}")
            return False

    def marcar_como_leida(self, notificacion_id: int, empresa_id: int) -> Optional[Dict]:
        """Marca una notificación como leída."""
        return self.update(notificacion_id, empresa_id, estado="leida")

    def obtener_pendientes(self, empresa_id: int, usuario_id: Optional[int] = None) -> List[Dict]:
        """Obtiene notificaciones pendientes."""
        filtros = {"estado": "pendiente"}
        if usuario_id:
            filtros["usuario_id"] = usuario_id
        return self.list(empresa_id, **filtros)
