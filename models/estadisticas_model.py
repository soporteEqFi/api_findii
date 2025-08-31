from __future__ import annotations
from typing import Any, Dict, List, Optional
from data.supabase_conn import supabase

def _get_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp

class EstadisticasModel:
    """Modelo para consultas agregadas y estadísticas del sistema."""

    def __init__(self):
        pass

    def estadisticas_generales(self, empresa_id: int, usuario_info: dict = None) -> Dict[str, Any]:
        """Obtiene estadísticas generales del sistema aplicando filtros por rol"""
        try:
            # Aplicar filtros base por empresa
            filtros_base = {"empresa_id": empresa_id}
            
            # Aplicar filtros adicionales según el rol
            filtros_solicitudes = self._aplicar_filtros_rol(filtros_base.copy(), usuario_info)
            
            # Total de solicitantes
            solicitantes_resp = supabase.table("solicitantes").select("id", count="exact").eq("empresa_id", empresa_id).execute()
            total_solicitantes = solicitantes_resp.count or 0
            
            # Total de solicitudes (con filtros de rol)
            solicitudes_query = supabase.table("solicitudes").select("id", count="exact").eq("empresa_id", empresa_id)
            solicitudes_query = self._aplicar_query_filtros_rol(solicitudes_query, usuario_info)
            solicitudes_resp = solicitudes_query.execute()
            total_solicitudes = solicitudes_resp.count or 0
            
            # Solicitudes por estado
            estados_query = supabase.table("solicitudes").select("estado", count="exact").eq("empresa_id", empresa_id)
            estados_query = self._aplicar_query_filtros_rol(estados_query, usuario_info)
            estados_resp = estados_query.execute()
            solicitudes_data = _get_data(estados_resp) or []
            
            # Agrupar por estado
            solicitudes_por_estado = {}
            for solicitud in solicitudes_data:
                estado = solicitud.get("estado", "Sin Estado")
                solicitudes_por_estado[estado] = solicitudes_por_estado.get(estado, 0) + 1
            
            # Solicitudes por banco (solo si el usuario puede ver múltiples bancos)
            solicitudes_por_banco = {}
            if not usuario_info or usuario_info.get("rol") in ["admin", "supervisor", "empresa"]:
                bancos_query = supabase.table("solicitudes").select("banco_nombre", count="exact").eq("empresa_id", empresa_id)
                bancos_query = self._aplicar_query_filtros_rol(bancos_query, usuario_info)
                bancos_resp = bancos_query.execute()
                bancos_data = _get_data(bancos_resp) or []
                
                for solicitud in bancos_data:
                    banco = solicitud.get("banco_nombre", "Sin Banco")
                    solicitudes_por_banco[banco] = solicitudes_por_banco.get(banco, 0) + 1
            
            # Solicitudes por ciudad (solo si el usuario puede ver múltiples ciudades)
            solicitudes_por_ciudad = {}
            if not usuario_info or usuario_info.get("rol") in ["admin", "supervisor", "empresa"]:
                ciudades_query = supabase.table("solicitudes").select("ciudad_solicitud", count="exact").eq("empresa_id", empresa_id)
                ciudades_query = self._aplicar_query_filtros_rol(ciudades_query, usuario_info)
                ciudades_resp = ciudades_query.execute()
                ciudades_data = _get_data(ciudades_resp) or []
                
                for solicitud in ciudades_data:
                    ciudad = solicitud.get("ciudad_solicitud", "Sin Ciudad")
                    solicitudes_por_ciudad[ciudad] = solicitudes_por_ciudad.get(ciudad, 0) + 1
            
            # Total de documentos
            documentos_resp = supabase.table("documentos").select("id", count="exact").execute()
            total_documentos = documentos_resp.count or 0
            
            # Solicitudes por día (últimos 30 días para gráfico de línea de tiempo)
            from datetime import datetime, timedelta
            fecha_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            solicitudes_tiempo_query = supabase.table("solicitudes").select("created_at").eq("empresa_id", empresa_id).gte("created_at", fecha_inicio)
            solicitudes_tiempo_query = self._aplicar_query_filtros_rol(solicitudes_tiempo_query, usuario_info)
            solicitudes_tiempo_resp = solicitudes_tiempo_query.execute()
            solicitudes_tiempo_data = _get_data(solicitudes_tiempo_resp) or []
            
            # Agrupar por fecha
            solicitudes_por_dia = {}
            for solicitud in solicitudes_tiempo_data:
                fecha = solicitud.get("created_at", "")[:10]  # Solo la fecha YYYY-MM-DD
                solicitudes_por_dia[fecha] = solicitudes_por_dia.get(fecha, 0) + 1
            
            return {
                "total_solicitantes": total_solicitantes,
                "total_solicitudes": total_solicitudes,
                "solicitudes_por_estado": solicitudes_por_estado,
                "solicitudes_por_banco": solicitudes_por_banco,
                "solicitudes_por_ciudad": solicitudes_por_ciudad,
                "total_documentos": total_documentos,
                "solicitudes_por_dia": solicitudes_por_dia
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas generales: {e}")
            return {
                "total_solicitantes": 0,
                "total_solicitudes": 0,
                "solicitudes_por_estado": {},
                "solicitudes_por_banco": {},
                "solicitudes_por_ciudad": {},
                "total_documentos": 0,
                "solicitudes_por_dia": {}
            }

    def estadisticas_rendimiento(self, empresa_id: int, usuario_info: dict = None, dias: int = 30) -> Dict[str, Any]:
        """Obtiene estadísticas de rendimiento del sistema"""
        try:
            from datetime import datetime, timedelta
            
            fecha_inicio = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
            
            # Solicitudes creadas por día (últimos N días)
            solicitudes_query = supabase.table("solicitudes").select("created_at").eq("empresa_id", empresa_id).gte("created_at", fecha_inicio)
            solicitudes_query = self._aplicar_query_filtros_rol(solicitudes_query, usuario_info)
            solicitudes_resp = solicitudes_query.execute()
            solicitudes_data = _get_data(solicitudes_resp) or []
            
            # Agrupar por fecha
            solicitudes_por_dia = {}
            for solicitud in solicitudes_data:
                fecha = solicitud.get("created_at", "")[:10]  # Solo la fecha YYYY-MM-DD
                solicitudes_por_dia[fecha] = solicitudes_por_dia.get(fecha, 0) + 1
            
            # Solicitudes completadas vs pendientes
            completadas_query = supabase.table("solicitudes").select("id", count="exact").eq("empresa_id", empresa_id).neq("estado", "Pendiente")
            completadas_query = self._aplicar_query_filtros_rol(completadas_query, usuario_info)
            completadas_resp = completadas_query.execute()
            solicitudes_completadas = completadas_resp.count or 0
            
            pendientes_query = supabase.table("solicitudes").select("id", count="exact").eq("empresa_id", empresa_id).eq("estado", "Pendiente")
            pendientes_query = self._aplicar_query_filtros_rol(pendientes_query, usuario_info)
            pendientes_resp = pendientes_query.execute()
            solicitudes_pendientes = pendientes_resp.count or 0
            
            # Productividad por usuario (solo para admin/supervisor)
            productividad_usuarios = {}
            if not usuario_info or usuario_info.get("rol") in ["admin", "supervisor"]:
                usuarios_query = supabase.table("solicitudes").select("assigned_to_user_id, usuarios(id, info_extra)").eq("empresa_id", empresa_id)
                usuarios_query = self._aplicar_query_filtros_rol(usuarios_query, usuario_info)
                usuarios_resp = usuarios_query.execute()
                usuarios_data = _get_data(usuarios_resp) or []
                
                for solicitud in usuarios_data:
                    user_id = solicitud.get("assigned_to_user_id")
                    if user_id:
                        productividad_usuarios[user_id] = productividad_usuarios.get(user_id, 0) + 1
            
            return {
                "periodo_dias": dias,
                "solicitudes_por_dia": solicitudes_por_dia,
                "solicitudes_completadas": solicitudes_completadas,
                "solicitudes_pendientes": solicitudes_pendientes,
                "productividad_usuarios": productividad_usuarios
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas de rendimiento: {e}")
            return {
                "periodo_dias": dias,
                "solicitudes_por_dia": {},
                "solicitudes_completadas": 0,
                "solicitudes_pendientes": 0,
                "productividad_usuarios": {}
            }

    def estadisticas_usuarios(self, empresa_id: int, usuario_info: dict = None) -> Dict[str, Any]:
        """Obtiene estadísticas de usuarios por empresa"""
        try:
            # Solo admin y supervisor pueden ver estadísticas de usuarios
            if usuario_info and usuario_info.get("rol") not in ["admin", "supervisor"]:
                return {
                    "error": "Sin permisos para ver estadísticas de usuarios",
                    "total_usuarios": 0,
                    "usuarios_por_rol": {},
                    "usuarios_por_banco": {},
                    "usuarios_por_ciudad": {}
                }
            
            # Total de usuarios de la empresa
            usuarios_resp = supabase.table("usuarios").select("*").eq("empresa_id", empresa_id).execute()
            usuarios_data = _get_data(usuarios_resp) or []
            total_usuarios = len(usuarios_data)
            
            # Usuarios por rol
            usuarios_por_rol = {}
            for usuario in usuarios_data:
                rol = usuario.get("rol", "Sin Rol")
                usuarios_por_rol[rol] = usuarios_por_rol.get(rol, 0) + 1
            
            # Usuarios por banco (desde info_extra)
            usuarios_por_banco = {}
            for usuario in usuarios_data:
                info_extra = usuario.get("info_extra") or {}
                banco = info_extra.get("banco_nombre", "Sin Banco") if isinstance(info_extra, dict) else "Sin Banco"
                usuarios_por_banco[banco] = usuarios_por_banco.get(banco, 0) + 1
            
            # Usuarios por ciudad (desde info_extra)
            usuarios_por_ciudad = {}
            for usuario in usuarios_data:
                info_extra = usuario.get("info_extra") or {}
                ciudad = info_extra.get("ciudad", "Sin Ciudad") if isinstance(info_extra, dict) else "Sin Ciudad"
                usuarios_por_ciudad[ciudad] = usuarios_por_ciudad.get(ciudad, 0) + 1
            
            return {
                "total_usuarios": total_usuarios,
                "usuarios_por_rol": usuarios_por_rol,
                "usuarios_por_banco": usuarios_por_banco,
                "usuarios_por_ciudad": usuarios_por_ciudad
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas de usuarios: {e}")
            return {
                "total_usuarios": 0,
                "usuarios_por_rol": {},
                "usuarios_por_banco": {},
                "usuarios_por_ciudad": {}
            }

    def estadisticas_financieras(self, empresa_id: int, usuario_info: dict = None) -> Dict[str, Any]:
        """Obtiene estadísticas financieras y de calidad"""
        try:
            # Rangos de ingresos (desde información financiera)
            financiera_resp = supabase.table("informacion_financiera").select("detalle_financiera").eq("empresa_id", empresa_id).execute()
            financiera_data = _get_data(financiera_resp) or []
            
            rangos_ingresos = {"0-1M": 0, "1M-3M": 0, "3M-5M": 0, "5M+": 0}
            
            for info in financiera_data:
                detalle = info.get("detalle_financiera", {})
                ingreso_basico = detalle.get("ingreso_basico_mensual", 0)
                
                try:
                    ingreso = float(ingreso_basico) if ingreso_basico else 0
                    if ingreso < 1000000:
                        rangos_ingresos["0-1M"] += 1
                    elif ingreso < 3000000:
                        rangos_ingresos["1M-3M"] += 1
                    elif ingreso < 5000000:
                        rangos_ingresos["3M-5M"] += 1
                    else:
                        rangos_ingresos["5M+"] += 1
                except:
                    pass
            
            # Tipos de actividad económica más comunes
            actividades_resp = supabase.table("actividad_economica").select("detalle_actividad").eq("empresa_id", empresa_id).execute()
            actividades_data = _get_data(actividades_resp) or []
            
            tipos_actividad = {}
            for actividad in actividades_data:
                detalle = actividad.get("detalle_actividad", {})
                tipo = detalle.get("tipo_actividad", "Sin Especificar")
                tipos_actividad[tipo] = tipos_actividad.get(tipo, 0) + 1
            
            # Referencias promedio por solicitante
            referencias_resp = supabase.table("referencias").select("solicitante_id", count="exact").eq("empresa_id", empresa_id).execute()
            total_referencias = referencias_resp.count or 0
            
            solicitantes_resp = supabase.table("solicitantes").select("id", count="exact").eq("empresa_id", empresa_id).execute()
            total_solicitantes = solicitantes_resp.count or 1  # Evitar división por cero
            
            referencias_promedio = round(total_referencias / total_solicitantes, 2)
            
            # Documentos promedio por solicitante
            documentos_resp = supabase.table("documentos").select("id", count="exact").execute()
            total_documentos = documentos_resp.count or 0
            
            documentos_promedio = round(total_documentos / total_solicitantes, 2)
            
            return {
                "rangos_ingresos": rangos_ingresos,
                "tipos_actividad_economica": tipos_actividad,
                "referencias_promedio": referencias_promedio,
                "documentos_promedio": documentos_promedio,
                "total_referencias": total_referencias,
                "total_documentos": total_documentos
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas financieras: {e}")
            return {
                "rangos_ingresos": {},
                "tipos_actividad_economica": {},
                "referencias_promedio": 0,
                "documentos_promedio": 0,
                "total_referencias": 0,
                "total_documentos": 0
            }

    def _aplicar_filtros_rol(self, filtros_base: dict, usuario_info: dict = None) -> dict:
        """Aplica filtros adicionales según el rol del usuario"""
        if not usuario_info:
            return filtros_base
            
        rol = usuario_info.get("rol")
        
        if rol == "banco":
            banco_nombre = usuario_info.get("banco_nombre")
            ciudad = usuario_info.get("ciudad")
            
            if banco_nombre:
                filtros_base["banco_nombre"] = banco_nombre
            if ciudad:
                filtros_base["ciudad_solicitud"] = ciudad
                
        return filtros_base

    def _aplicar_query_filtros_rol(self, query, usuario_info: dict = None):
        """Aplica filtros de rol a una query de Supabase"""
        if not usuario_info:
            return query
            
        rol = usuario_info.get("rol")
        
        if rol == "banco":
            banco_nombre = usuario_info.get("banco_nombre")
            ciudad = usuario_info.get("ciudad")
            
            if banco_nombre:
                query = query.eq("banco_nombre", banco_nombre)
            if ciudad:
                query = query.eq("ciudad_solicitud", ciudad)
                
        return query
