from __future__ import annotations
from typing import Any, Dict, List, Optional
from data.supabase_conn import supabase

def _get_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp
class SolicitantesModel:
    """CRUD para entidad solicitante."""

    TABLE = "solicitantes"

    def create(self, *, empresa_id: int, nombres: str, primer_apellido: str, segundo_apellido: str, tipo_identificacion: str, numero_documento: str, fecha_nacimiento: str, genero: str, correo: str, info_extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {
            "empresa_id": empresa_id,
            "nombres": nombres,
            "primer_apellido": primer_apellido,
            "segundo_apellido": segundo_apellido,
            "tipo_identificacion": tipo_identificacion,
            "numero_documento": numero_documento,
            "fecha_nacimiento": fecha_nacimiento,
            "genero": genero,
            "correo": correo,
            "info_extra": info_extra or {},
        }
        resp = supabase.table(self.TABLE).insert(payload).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else data

    def get_by_id(self, *, id: int, empresa_id: int) -> Optional[Dict[str, Any]]:
        resp = supabase.table(self.TABLE).select("*").eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def list(self, *, empresa_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        # Hacer JOIN con tablas relacionadas para obtener información completa
        query = """
            *,
            ubicacion(ciudad_residencia, departamento_residencia),
            solicitudes(detalle_credito, banco_nombre, estado, created_by_user_id, assigned_to_user_id)
        """
        
        resp = supabase.table(self.TABLE).select(query).eq("empresa_id", empresa_id).order("created_at", desc=True).range(offset, offset + max(limit - 1, 0)).execute()
        data = _get_data(resp) or []
        
        # Obtener todos los IDs de usuarios únicos para hacer JOIN manual
        user_ids = set()
        for item in data:
            solicitudes = item.get("solicitudes", [])
            for solicitud in solicitudes:
                if solicitud.get("created_by_user_id"):
                    user_ids.add(solicitud["created_by_user_id"])
                if solicitud.get("assigned_to_user_id"):
                    user_ids.add(solicitud["assigned_to_user_id"])
        
        # Consultar usuarios y supervisores
        usuarios_map = {}
        supervisores_map = {}
        if user_ids:
            usuarios_resp = supabase.table("usuarios").select("id, nombre, reports_to_id").in_("id", list(user_ids)).execute()
            usuarios_data = _get_data(usuarios_resp) or []
            usuarios_map = {usuario["id"]: usuario["nombre"] for usuario in usuarios_data}
            
            # Obtener supervisores
            supervisor_ids = set()
            for usuario in usuarios_data:
                if usuario.get("reports_to_id"):
                    supervisor_ids.add(usuario["reports_to_id"])
            
            if supervisor_ids:
                supervisores_resp = supabase.table("usuarios").select("id, nombre").in_("id", list(supervisor_ids)).execute()
                supervisores_data = _get_data(supervisores_resp) or []
                supervisores_map = {supervisor["id"]: supervisor["nombre"] for supervisor in supervisores_data}
        
        # Procesar los datos para aplanar la estructura
        processed_data = []
        for item in data:
            # Datos base del solicitante
            solicitante = {
                "id": item.get("id"),
                "nombres": item.get("nombres"),
                "primer_apellido": item.get("primer_apellido"),
                "segundo_apellido": item.get("segundo_apellido"),
                "tipo_identificacion": item.get("tipo_identificacion"),
                "numero_documento": item.get("numero_documento"),
                "fecha_nacimiento": item.get("fecha_nacimiento"),
                "genero": item.get("genero"),
                "correo": item.get("correo"),
                "created_at": item.get("created_at"),
                "empresa_id": item.get("empresa_id")
            }
            
            # Agregar información de ubicación
            ubicaciones = item.get("ubicacion", [])
            if ubicaciones and len(ubicaciones) > 0:
                ubicacion = ubicaciones[0]  # Tomar la primera ubicación
                solicitante["ciudad_residencia"] = ubicacion.get("ciudad_residencia")
                solicitante["departamento_residencia"] = ubicacion.get("departamento_residencia")
            else:
                solicitante["ciudad_residencia"] = None
                solicitante["departamento_residencia"] = None
            
            # Agregar información de solicitudes (tipo de crédito)
            solicitudes = item.get("solicitudes", [])
            if solicitudes and len(solicitudes) > 0:
                solicitud = solicitudes[0]  # Tomar la primera solicitud
                detalle_credito = solicitud.get("detalle_credito", {})
                solicitante["tipo_credito"] = detalle_credito.get("tipo_credito")
                solicitante["banco_nombre"] = solicitud.get("banco_nombre")
                solicitante["estado_solicitud"] = solicitud.get("estado")
                
                # Obtener creado por y supervisor
                created_by_user_id = solicitud.get("created_by_user_id")
                solicitante["created_by_user_name"] = usuarios_map.get(created_by_user_id) if created_by_user_id else None
                
                # Obtener supervisor del usuario creador
                created_by_supervisor_name = None
                if created_by_user_id:
                    for usuario in usuarios_data:
                        if usuario["id"] == created_by_user_id and usuario.get("reports_to_id"):
                            supervisor_id = usuario["reports_to_id"]
                            created_by_supervisor_name = supervisores_map.get(supervisor_id)
                            break
                solicitante["created_by_supervisor_name"] = created_by_supervisor_name
            else:
                solicitante["tipo_credito"] = None
                solicitante["banco_nombre"] = None
                solicitante["estado_solicitud"] = None
                solicitante["created_by_user_name"] = None
                solicitante["created_by_supervisor_name"] = None
            
            # Agregar información extra (celular)
            info_extra = item.get("info_extra", {})
            solicitante["celular"] = info_extra.get("celular") or info_extra.get("telefono")
            
            processed_data.append(solicitante)
        
        return processed_data

    def list_completo_para_excel(self, *, empresa_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Obtener lista completa de solicitantes con TODA la información para exportar a Excel
        IMPORTANTE: Solo trae solicitantes que tengan al menos una solicitud (igual que la tabla del frontend)
        """
        try:
            # Hacer JOIN con TODAS las tablas relacionadas
            # IMPORTANTE: solicitudes!inner() = solo trae solicitantes que TENGAN solicitudes
            query = """
                *,
                ubicacion(*),
                actividad_economica(*),
                informacion_financiera(*),
                referencias(*),
                solicitudes!inner(*)
            """
            
            resp = supabase.table(self.TABLE).select(query).eq("empresa_id", empresa_id).order("created_at", desc=True).range(offset, offset + max(limit - 1, 0)).execute()
            data = _get_data(resp) or []
            print(f"   ✅ Query con !inner: {len(data)} solicitantes con solicitudes")
        except Exception as e:
            print(f"❌ Error en query principal: {e}")
            # Fallback a query simple si falla
            resp = supabase.table(self.TABLE).select("*").eq("empresa_id", empresa_id).order("created_at", desc=True).range(offset, offset + max(limit - 1, 0)).execute()
            data = _get_data(resp) or []
        
        # Obtener usuarios y supervisores
        user_ids = set()
        for item in data:
            solicitudes = item.get("solicitudes", [])
            for solicitud in solicitudes:
                if solicitud.get("created_by_user_id"):
                    user_ids.add(solicitud["created_by_user_id"])
                if solicitud.get("assigned_to_user_id"):
                    user_ids.add(solicitud["assigned_to_user_id"])
        
        usuarios_map = {}
        supervisores_map = {}
        if user_ids:
            usuarios_resp = supabase.table("usuarios").select("id, nombre, reports_to_id").in_("id", list(user_ids)).execute()
            usuarios_data = _get_data(usuarios_resp) or []
            usuarios_map = {usuario["id"]: usuario["nombre"] for usuario in usuarios_data}
            
            supervisor_ids = set()
            for usuario in usuarios_data:
                if usuario.get("reports_to_id"):
                    supervisor_ids.add(usuario["reports_to_id"])
            
            if supervisor_ids:
                supervisores_resp = supabase.table("usuarios").select("id, nombre").in_("id", list(supervisor_ids)).execute()
                supervisores_data = _get_data(supervisores_resp) or []
                supervisores_map = {supervisor["id"]: supervisor["nombre"] for supervisor in supervisores_data}
        
        # Obtener documentos de todos los solicitantes
        solicitante_ids = [item.get("id") for item in data if item.get("id")]
        documentos_map = {}
        if solicitante_ids:
            try:
                docs_resp = supabase.table("documentos").select("*").in_("solicitante_id", solicitante_ids).execute()
                docs_data = _get_data(docs_resp) or []
                # Agrupar documentos por solicitante_id
                for doc in docs_data:
                    sol_id = doc.get("solicitante_id")
                    if sol_id not in documentos_map:
                        documentos_map[sol_id] = []
                    documentos_map[sol_id].append(doc)
            except Exception as e:
                print(f"⚠️ Error al obtener documentos: {e}")
        
        # Procesar datos completos
        processed_data = []
        for item in data:
            # Datos base del solicitante
            solicitante = {
                "id": item.get("id"),
                "nombres": item.get("nombres"),
                "primer_apellido": item.get("primer_apellido"),
                "segundo_apellido": item.get("segundo_apellido"),
                "tipo_identificacion": item.get("tipo_identificacion"),
                "numero_documento": item.get("numero_documento"),
                "fecha_nacimiento": item.get("fecha_nacimiento"),
                "genero": item.get("genero"),
                "correo": item.get("correo"),
                "created_at": item.get("created_at"),
                "empresa_id": item.get("empresa_id"),
                "info_extra": item.get("info_extra", {}),
            }
            
            # Ubicaciones completas
            ubicaciones = item.get("ubicacion", [])
            solicitante["ubicaciones"] = ubicaciones
            
            # Actividad económica completa
            actividad_economica = item.get("actividad_economica", [])
            solicitante["actividad_economica"] = actividad_economica
            
            # Información financiera completa
            informacion_financiera = item.get("informacion_financiera", [])
            solicitante["informacion_financiera"] = informacion_financiera
            
            # Referencias completas
            referencias = item.get("referencias", [])
            solicitante["referencias"] = referencias
            
            # Documentos del solicitante
            solicitante_id = item.get("id")
            solicitante["documentos"] = documentos_map.get(solicitante_id, [])
            
            # Solicitudes completas
            solicitudes = item.get("solicitudes", [])
            if solicitudes and len(solicitudes) > 0:
                solicitud = solicitudes[0]
                solicitante["solicitud"] = solicitud
                
                # Agregar nombres de usuarios
                created_by_user_id = solicitud.get("created_by_user_id")
                solicitante["created_by_user_name"] = usuarios_map.get(created_by_user_id) if created_by_user_id else None
                
                created_by_supervisor_name = None
                if created_by_user_id:
                    for usuario in usuarios_data:
                        if usuario["id"] == created_by_user_id and usuario.get("reports_to_id"):
                            supervisor_id = usuario["reports_to_id"]
                            created_by_supervisor_name = supervisores_map.get(supervisor_id)
                            break
                solicitante["created_by_supervisor_name"] = created_by_supervisor_name
            else:
                solicitante["solicitud"] = None
                solicitante["created_by_user_name"] = None
                solicitante["created_by_supervisor_name"] = None
            
            processed_data.append(solicitante)
        
        return processed_data

    def update(self, *, id: int, empresa_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        resp = supabase.table(self.TABLE).update(updates).eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def delete(self, *, id: int, empresa_id: int) -> int:
        resp = supabase.table(self.TABLE).delete().eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return len(data) if isinstance(data, list) else 0
