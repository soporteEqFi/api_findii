from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid
from data.supabase_conn import supabase

def _get_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp
class SolicitudesModel:
    """Operaciones CRUD para la entidad solicitud usando Supabase."""

    TABLE = "solicitudes"

    def create(self, *, empresa_id: int, solicitante_id: int, created_by_user_id: int, assigned_to_user_id: Optional[int] = None, banco_nombre: Optional[str] = None, ciudad_solicitud: Optional[str] = None, estado: Optional[str] = None, detalle_credito: Optional[Dict[str, Any]] = None, observacion_inicial: Optional[str] = None, usuario_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Crear observaciones inicial si se proporciona
        observaciones_data = {}
        if observacion_inicial and usuario_info:
            observaciones_data = self._crear_observacion_inicial(observacion_inicial, usuario_info)
        
        payload: Dict[str, Any] = {
            "empresa_id": empresa_id,
            "solicitante_id": solicitante_id,
            "created_by_user_id": created_by_user_id,
            "estado": estado or "Pendiente",
            "detalle_credito": detalle_credito or {},
            "observaciones": observaciones_data,
        }
        if assigned_to_user_id is not None:
            payload["assigned_to_user_id"] = assigned_to_user_id
        if banco_nombre is not None:
            payload["banco_nombre"] = banco_nombre
        if ciudad_solicitud is not None:
            payload["ciudad_solicitud"] = ciudad_solicitud

        resp = supabase.table(self.TABLE).insert(payload).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else data

    def get_by_id(self, *, id: int, empresa_id: int) -> Optional[Dict[str, Any]]:
        resp = supabase.table(self.TABLE).select("*").eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def list(self, *, empresa_id: int, estado: Optional[str] = None, solicitante_id: Optional[int] = None, banco_nombre: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        q = supabase.table(self.TABLE).select("*").eq("empresa_id", empresa_id)
        if estado:
            q = q.eq("estado", estado)
        if solicitante_id:
            q = q.eq("solicitante_id", solicitante_id)
        if banco_nombre:
            q = q.eq("banco_nombre", banco_nombre)
        q = q.range(offset, offset + max(limit - 1, 0))
        resp = q.execute()
        data = _get_data(resp)
        return data or []

    def update(
        self,
        *,
        id: int,
        empresa_id: int,
        base_updates: Optional[Dict[str, Any]] = None,
        detalle_credito_merge: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        # Leer actual para merge del JSON
        current_resp = (
            supabase.table(self.TABLE)
            .select("detalle_credito")
            .eq("id", id)
            .eq("empresa_id", empresa_id)
            .execute()
        )
        current_data = _get_data(current_resp) or []
        current = current_data[0] if isinstance(current_data, list) and current_data else {}
        current_json = current.get("detalle_credito") if isinstance(current, dict) else {}

        update_payload: Dict[str, Any] = {}
        if base_updates:
            update_payload.update(base_updates)
        if detalle_credito_merge:
            merged = {**(current_json or {}), **detalle_credito_merge}
            update_payload["detalle_credito"] = merged

        if not update_payload:
            return self.get_by_id(id=id, empresa_id=empresa_id)

        resp = supabase.table(self.TABLE).update(update_payload).eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def delete(self, *, id: int, empresa_id: int) -> int:
        # Primero verificar que el registro existe
        existing_record = self.get_by_id(id=id, empresa_id=empresa_id)
        if not existing_record:
            print(f"❌ Solicitud no encontrada para eliminar: id={id}, empresa_id={empresa_id}")
            return 0

        print(f"🗑️ Intentando eliminar solicitud: id={id}, empresa_id={empresa_id}")
        print(f"   📋 Datos de la solicitud: estado={existing_record.get('estado')}, banco={existing_record.get('banco_nombre')}")

        # Intentar eliminar
        resp = supabase.table(self.TABLE).delete().eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)

        deleted_count = len(data) if isinstance(data, list) else 0
        print(f"📊 Respuesta de eliminación de solicitud: {resp}")
        print(f"📊 Datos eliminados: {data}")
        print(f"📊 Cantidad eliminada: {deleted_count}")

        # Verificar que realmente se eliminó
        if deleted_count > 0:
            # Verificar que ya no existe
            still_exists = self.get_by_id(id=id, empresa_id=empresa_id)
            if still_exists:
                print(f"⚠️ Solicitud aún existe después de eliminar: {still_exists}")
            else:
                print(f"✅ Solicitud eliminada exitosamente")

        return deleted_count

    def list_con_filtros_rol(self, *, empresa_id: int, usuario_info: dict = None, estado: Optional[str] = None, solicitante_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Listar solicitudes aplicando filtros de permisos por rol"""
        q = supabase.table(self.TABLE).select("*").eq("empresa_id", empresa_id)

        # Aplicar filtros básicos
        if estado:
            q = q.eq("estado", estado)
        if solicitante_id:
            q = q.eq("solicitante_id", solicitante_id)

        # Aplicar filtros de permisos por rol
        if usuario_info:
            rol = usuario_info.get("rol")
            print(f"🔍 APLICANDO FILTROS POR ROL:")
            print(f"   🏷️ Rol del usuario: {rol}")
            print(f"   👤 Info completa del usuario: {usuario_info}")

            if rol == "admin":
                # Admin ve todas las solicitudes de la empresa
                print(f"   ✅ Admin - sin filtros aplicados")
                pass
            elif rol == "banco":
                # Usuario banco solo ve solicitudes de su banco y ciudad
                banco_nombre = usuario_info.get("banco_nombre")
                ciudad_solicitud = usuario_info.get("ciudad_solicitud")

                print(f"   🏦 Banco del usuario: {banco_nombre}")
                print(f"   🏙️ Ciudad del usuario: {ciudad_solicitud}")

                if banco_nombre:
                    q = q.eq("banco_nombre", banco_nombre)
                    print(f"   ✅ Filtro banco aplicado: {banco_nombre}")
                else:
                    # Si no tiene banco asignado, no ve nada
                    print(f"   ❌ Usuario sin banco asignado - retornando lista vacía")
                    return []

                # Aplicar filtro de ciudad_solicitud si está disponible
                if ciudad_solicitud:
                    q = q.eq("ciudad_solicitud", ciudad_solicitud)
                    print(f"   ✅ Filtro ciudad aplicado: {ciudad_solicitud}")
                else:
                    print(f"   ⚠️ Usuario sin ciudad asignada - solo filtro por banco")

                print(f"   🔍 FILTROS APLICADOS:")
                print(f"      🏦 banco_nombre = {banco_nombre}")
                print(f"      🏙️ ciudad_solicitud = {ciudad_solicitud}")
                print(f"      📋 Query final: banco_nombre='{banco_nombre}' AND ciudad_solicitud='{ciudad_solicitud}'")
            elif rol == "empresa":
                # Usuario empresa ve todas las solicitudes de su empresa
                print(f"   ✅ Empresa - sin filtros aplicados")
                pass
            elif rol == "supervisor":
                # Usuario supervisor ve todas las solicitudes de la empresa (similar a admin)
                print(f"   ✅ Supervisor - sin filtros aplicados")
                pass
            else:
                # Rol desconocido, no ve nada
                print(f"   ❌ Rol desconocido '{rol}' - retornando lista vacía")
                return []

        # Aplicar paginación
        q = q.range(offset, offset + max(limit - 1, 0))

        resp = q.execute()
        data = _get_data(resp)
        return data or []

    def get_by_id_con_filtros_rol(self, *, id: int, empresa_id: int, usuario_info: dict = None) -> Optional[Dict[str, Any]]:
        """Obtener una solicitud específica aplicando filtros de permisos por rol"""
        q = supabase.table(self.TABLE).select("*").eq("id", id).eq("empresa_id", empresa_id)

        # Aplicar filtros de permisos por rol
        if usuario_info:
            rol = usuario_info.get("rol")

            if rol == "admin":
                # Admin ve todas las solicitudes de la empresa
                pass
            elif rol == "banco":
                # Usuario banco solo ve solicitudes de su banco y ciudad
                banco_nombre = usuario_info.get("banco_nombre")
                ciudad_solicitud = usuario_info.get("ciudad_solicitud")

                if banco_nombre:
                    q = q.eq("banco_nombre", banco_nombre)
                else:
                    # Si no tiene banco asignado, no ve nada
                    return None

                # Aplicar filtro de ciudad_solicitud si está disponible
                if ciudad_solicitud:
                    q = q.eq("ciudad_solicitud", ciudad_solicitud)
            elif rol == "empresa":
                # Usuario empresa ve todas las solicitudes de su empresa
                pass
            elif rol == "supervisor":
                # Usuario supervisor ve todas las solicitudes de la empresa (similar a admin)
                pass
            else:
                # Rol desconocido, no ve nada
                return None

        resp = q.execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def _crear_observacion_inicial(self, observacion: str, usuario_info: Dict[str, Any]) -> Dict[str, Any]:
        """Crear la estructura inicial de observaciones"""
        return {
            "historial": [{
                "id": str(uuid.uuid4()),
                "fecha": datetime.utcnow().isoformat() + "Z",
                "usuario_id": usuario_info.get("id"),
                "usuario_nombre": usuario_info.get("nombre", "Usuario"),
                "tipo": "creacion",
                "estado_anterior": None,
                "estado_nuevo": "Pendiente",
                "observacion": observacion,
                "metadata": {
                    "sistema": "api",
                    "rol": usuario_info.get("rol")
                }
            }]
        }

    def agregar_observacion_simple(self, id: int, observacion: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega una observación simple a una solicitud existente.

        Args:
            id: ID de la solicitud
            observacion: Diccionario con la estructura {
                'observacion': 'texto',
                'fecha_creacion': 'fecha_iso'
            }

        Returns:
            La solicitud actualizada con la nueva observación
        """
        # Obtener la solicitud actual
        current = supabase.table(self.TABLE).select('observaciones').eq('id', id).execute()
        current_data = _get_data(current)

        if not current_data:
            raise ValueError("Solicitud no encontrada")

        # Inicializar observaciones si no existen
        observaciones = current_data[0].get('observaciones', {})
        if not observaciones or 'historial' not in observaciones:
            observaciones = {'historial': []}

        # Agregar la nueva observación al historial
        observaciones['historial'].append({
            'id': str(uuid.uuid4()),
            'fecha': observacion['fecha_creacion'],
            'tipo': 'comentario',
            'observacion': observacion['observacion']
        })

        # Actualizar la solicitud
        resp = (
            supabase.table(self.TABLE)
            .update({'observaciones': observaciones})
            .eq('id', id)
            .execute()
        )

        updated_data = _get_data(resp)
        return updated_data[0] if isinstance(updated_data, list) and updated_data else updated_data

    def _agregar_observacion(self, observaciones_actuales: Dict[str, Any], nueva_observacion: str, usuario_info: Dict[str, Any], tipo: str = "comentario", estado_anterior: Optional[str] = None, estado_nuevo: Optional[str] = None) -> Dict[str, Any]:
        """Agregar una nueva observación al historial existente"""
        if not observaciones_actuales:
            observaciones_actuales = {"historial": []}

        if "historial" not in observaciones_actuales:
            observaciones_actuales["historial"] = []
        
        nueva_entrada = {
            "id": str(uuid.uuid4()),
            "fecha": datetime.utcnow().isoformat() + "Z",
            "usuario_id": usuario_info.get("id"),
            "usuario_nombre": usuario_info.get("nombre", "Usuario"),
            "tipo": tipo,
            "estado_anterior": estado_anterior,
            "estado_nuevo": estado_nuevo,
            "observacion": nueva_observacion,
            "metadata": {
                "sistema": "api",
                "rol": usuario_info.get("rol")
            }
        }
        
        observaciones_actuales["historial"].append(nueva_entrada)
        return observaciones_actuales

    def agregar_observacion(self, *, id: int, empresa_id: int, observacion: str, usuario_info: Dict[str, Any], tipo: str = "comentario") -> Optional[Dict[str, Any]]:
        """Agregar una nueva observación a una solicitud existente"""
        # Obtener la solicitud actual
        solicitud_actual = self.get_by_id(id=id, empresa_id=empresa_id)
        if not solicitud_actual:
            return None
        
        # Obtener observaciones actuales
        observaciones_actuales = solicitud_actual.get("observaciones", {})
        
        # Agregar nueva observación
        observaciones_actualizadas = self._agregar_observacion(
            observaciones_actuales=observaciones_actuales,
            nueva_observacion=observacion,
            usuario_info=usuario_info,
            tipo=tipo
        )
        
        # Actualizar en la base de datos
        update_payload = {"observaciones": observaciones_actualizadas}
        resp = supabase.table(self.TABLE).update(update_payload).eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def actualizar_con_observacion(self, *, id: int, empresa_id: int, base_updates: Optional[Dict[str, Any]] = None, detalle_credito_merge: Optional[Dict[str, Any]] = None, observacion: Optional[str] = None, usuario_info: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Actualizar solicitud y agregar observación automáticamente si hay cambios de estado"""
        # Obtener solicitud actual
        solicitud_actual = self.get_by_id(id=id, empresa_id=empresa_id)
        if not solicitud_actual:
            return None
        
        # Detectar cambio de estado
        estado_anterior = solicitud_actual.get("estado")
        estado_nuevo = base_updates.get("estado") if base_updates else None
        
        # Realizar actualización normal
        solicitud_actualizada = self.update(
            id=id,
            empresa_id=empresa_id,
            base_updates=base_updates,
            detalle_credito_merge=detalle_credito_merge
        )
        
        # Agregar observación si se proporciona o hay cambio de estado
        if (observacion or estado_nuevo) and usuario_info:
            observaciones_actuales = solicitud_actualizada.get("observaciones", {})
            
            # Determinar tipo y mensaje de observación
            if estado_nuevo and estado_nuevo != estado_anterior:
                tipo_obs = "cambio_estado"
                mensaje_obs = observacion or f"Estado cambiado de '{estado_anterior}' a '{estado_nuevo}'"
            else:
                tipo_obs = "comentario"
                mensaje_obs = observacion
            
            if mensaje_obs:
                observaciones_actualizadas = self._agregar_observacion(
                    observaciones_actuales=observaciones_actuales,
                    nueva_observacion=mensaje_obs,
                    usuario_info=usuario_info,
                    tipo=tipo_obs,
                    estado_anterior=estado_anterior,
                    estado_nuevo=estado_nuevo
                )
                
                # Actualizar observaciones en BD
                update_payload = {"observaciones": observaciones_actualizadas}
                resp = supabase.table(self.TABLE).update(update_payload).eq("id", id).eq("empresa_id", empresa_id).execute()
                data = _get_data(resp)
                solicitud_actualizada = data[0] if isinstance(data, list) and data else solicitud_actualizada
        
        return solicitud_actualizada


