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

            # Total de solicitantes (aplicando filtros de rol optimizados)
            total_solicitantes = self._contar_solicitantes_por_rol(empresa_id, usuario_info)

            # Total de solicitudes (con filtros de rol)
            solicitudes_query = supabase.table("solicitudes").select("id", count="exact").eq("empresa_id", empresa_id)
            solicitudes_query = self._aplicar_query_filtros_rol(solicitudes_query, usuario_info, empresa_id)
            solicitudes_resp = solicitudes_query.execute()
            total_solicitudes = solicitudes_resp.count or 0

            # Solicitudes por estado
            estados_query = supabase.table("solicitudes").select("estado", count="exact").eq("empresa_id", empresa_id)
            estados_query = self._aplicar_query_filtros_rol(estados_query, usuario_info, empresa_id)
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
                bancos_query = self._aplicar_query_filtros_rol(bancos_query, usuario_info, empresa_id)
                bancos_resp = bancos_query.execute()
                bancos_data = _get_data(bancos_resp) or []

                for solicitud in bancos_data:
                    banco = solicitud.get("banco_nombre", "Sin Banco")
                    solicitudes_por_banco[banco] = solicitudes_por_banco.get(banco, 0) + 1

            # Solicitudes por ciudad (solo si el usuario puede ver múltiples ciudades)
            solicitudes_por_ciudad = {}
            if not usuario_info or usuario_info.get("rol") in ["admin", "supervisor", "empresa"]:
                ciudades_query = supabase.table("solicitudes").select("ciudad_solicitud", count="exact").eq("empresa_id", empresa_id)
                ciudades_query = self._aplicar_query_filtros_rol(ciudades_query, usuario_info, empresa_id)
                ciudades_resp = ciudades_query.execute()
                ciudades_data = _get_data(ciudades_resp) or []

                for solicitud in ciudades_data:
                    ciudad = solicitud.get("ciudad_solicitud", "Sin Ciudad")
                    solicitudes_por_ciudad[ciudad] = solicitudes_por_ciudad.get(ciudad, 0) + 1

            # Total de documentos (aplicando filtros de empresa y rol optimizados)
            total_documentos = self._contar_documentos_por_rol(empresa_id, usuario_info)

            # Solicitudes por día (últimos 30 días para gráfico de línea de tiempo)
            from datetime import datetime, timedelta
            fecha_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

            solicitudes_tiempo_query = supabase.table("solicitudes").select("created_at").eq("empresa_id", empresa_id).gte("created_at", fecha_inicio)
            solicitudes_tiempo_query = self._aplicar_query_filtros_rol(solicitudes_tiempo_query, usuario_info, empresa_id)
            solicitudes_tiempo_resp = solicitudes_tiempo_query.execute()
            solicitudes_tiempo_data = _get_data(solicitudes_tiempo_resp) or []

            # Agrupar por fecha
            solicitudes_por_dia = {}
            for solicitud in solicitudes_tiempo_data:
                fecha = solicitud.get("created_at", "")[:10]  # Solo la fecha YYYY-MM-DD
                solicitudes_por_dia[fecha] = solicitudes_por_dia.get(fecha, 0) + 1

            # Métricas de radicaciones y montos
            # Definir estados que consideramos como radicaciones para métricas
            estados_radicados = ["Radicado", "Aprobado", "Rechazado"]

            # Consultar solicitudes radicadas (filtradas por rol)
            radicados_query = (
                supabase
                .table("solicitudes")
                .select("estado,banco_nombre,detalle_credito")
                .eq("empresa_id", empresa_id)
                .in_("estado", estados_radicados)
            )
            radicados_query = self._aplicar_query_filtros_rol(radicados_query, usuario_info, empresa_id)
            radicados_resp = radicados_query.execute()
            radicados_data = _get_data(radicados_resp) or []

            # Helper para extraer monto del detalle_credito de forma robusta
            def _extraer_monto(detalle: dict) -> float:
                if not isinstance(detalle, dict):
                    return 0.0
                # Candidatos comunes
                for k in ("monto_radicado", "monto_solicitado", "monto", "valor_solicitado"):
                    v = detalle.get(k)
                    if isinstance(v, (int, float)):
                        return float(v)
                    if isinstance(v, str):
                        try:
                            return float(v)
                        except:
                            pass
                # Buscar en tipos de crédito específicos
                for sub in ("credito_vehicular", "credito_hipotecario", "credito_consumo", "credito_comercial", "microcredito", "credito_educativo"):
                    subobj = detalle.get(sub)
                    if isinstance(subobj, dict):
                        v = subobj.get("monto_solicitado") or subobj.get("monto")
                        if isinstance(v, (int, float)):
                            return float(v)
                        if isinstance(v, str):
                            try:
                                return float(v)
                            except:
                                pass
                return 0.0

            total_creditos = 0
            total_monto = 0.0
            radicaciones_por_estado: Dict[str, int] = {}
            monto_por_estado: Dict[str, float] = {}
            radicaciones_por_banco: Dict[str, int] = {}
            monto_por_banco: Dict[str, float] = {}

            for item in radicados_data:
                estado_item = item.get("estado", "Sin Estado")
                banco_item = item.get("banco_nombre", "Sin Banco")
                detalle = item.get("detalle_credito") or {}

                monto = _extraer_monto(detalle)

                total_creditos += 1
                total_monto += monto

                radicaciones_por_estado[estado_item] = radicaciones_por_estado.get(estado_item, 0) + 1
                monto_por_estado[estado_item] = round(monto_por_estado.get(estado_item, 0.0) + monto, 2)

                # Solo exponer desglose por banco cuando el usuario puede ver múltiples bancos
                if not usuario_info or usuario_info.get("rol") in ["admin", "supervisor", "empresa"]:
                    radicaciones_por_banco[banco_item] = radicaciones_por_banco.get(banco_item, 0) + 1
                    monto_por_banco[banco_item] = round(monto_por_banco.get(banco_item, 0.0) + monto, 2)

            return {
                "total_solicitantes": total_solicitantes,
                "total_solicitudes": total_solicitudes,
                "solicitudes_por_estado": solicitudes_por_estado,
                "solicitudes_por_banco": solicitudes_por_banco,
                "solicitudes_por_ciudad": solicitudes_por_ciudad,
                "total_documentos": total_documentos,
                "solicitudes_por_dia": solicitudes_por_dia,
                # Nuevas métricas solicitadas
                "total_creditos": total_creditos,
                "radicaciones_por_banco": radicaciones_por_banco,
                "radicaciones_por_estado": radicaciones_por_estado,
                "total_monto": round(total_monto, 2),
                "monto_por_banco": monto_por_banco,
                "monto_por_estado": monto_por_estado,
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
                "solicitudes_por_dia": {},
                # Nuevas métricas (defaults)
                "total_creditos": 0,
                "radicaciones_por_banco": {},
                "radicaciones_por_estado": {},
                "total_monto": 0,
                "monto_por_banco": {},
                "monto_por_estado": {},
            }

    def estadisticas_rendimiento(self, empresa_id: int, usuario_info: dict = None, dias: int = 30) -> Dict[str, Any]:
        """Obtiene estadísticas de rendimiento del sistema"""
        try:
            from datetime import datetime, timedelta

            fecha_inicio = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')

            # Solicitudes creadas por día (últimos N días)
            solicitudes_query = supabase.table("solicitudes").select("created_at").eq("empresa_id", empresa_id).gte("created_at", fecha_inicio)
            solicitudes_query = self._aplicar_query_filtros_rol(solicitudes_query, usuario_info, empresa_id)
            solicitudes_resp = solicitudes_query.execute()
            solicitudes_data = _get_data(solicitudes_resp) or []

            # Agrupar por fecha
            solicitudes_por_dia = {}
            for solicitud in solicitudes_data:
                fecha = solicitud.get("created_at", "")[:10]  # Solo la fecha YYYY-MM-DD
                solicitudes_por_dia[fecha] = solicitudes_por_dia.get(fecha, 0) + 1

            # Solicitudes completadas vs pendientes
            completadas_query = supabase.table("solicitudes").select("id", count="exact").eq("empresa_id", empresa_id).neq("estado", "Pendiente")
            completadas_query = self._aplicar_query_filtros_rol(completadas_query, usuario_info, empresa_id)
            completadas_resp = completadas_query.execute()
            solicitudes_completadas = completadas_resp.count or 0

            pendientes_query = supabase.table("solicitudes").select("id", count="exact").eq("empresa_id", empresa_id).eq("estado", "Pendiente")
            pendientes_query = self._aplicar_query_filtros_rol(pendientes_query, usuario_info, empresa_id)
            pendientes_resp = pendientes_query.execute()
            solicitudes_pendientes = pendientes_resp.count or 0

            # Productividad por usuario (solo para admin/supervisor)
            productividad_usuarios = {}
            if not usuario_info or usuario_info.get("rol") in ["admin", "supervisor"]:
                usuarios_query = supabase.table("solicitudes").select("assigned_to_user_id, usuarios(id, info_extra)").eq("empresa_id", empresa_id)
                usuarios_query = self._aplicar_query_filtros_rol(usuarios_query, usuario_info, empresa_id)
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
            # Rangos de ingresos y actividad económica (optimizado con filtros directos por user_id)
            financiera_data, actividades_data = self._obtener_datos_financieros_por_rol(empresa_id, usuario_info)

            # Procesar rangos de ingresos
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

            # Procesar tipos de actividad económica
            tipos_actividad = {}
            for actividad in actividades_data:
                detalle = actividad.get("detalle_actividad", {})
                tipo = detalle.get("tipo_actividad", "Sin Especificar")
                tipos_actividad[tipo] = tipos_actividad.get(tipo, 0) + 1

            # Referencias y documentos promedio (optimizado con filtros directos por user_id)
            total_solicitantes = self._contar_solicitantes_por_rol(empresa_id, usuario_info) or 1  # Evitar división por cero
            total_referencias = self._contar_referencias_por_rol(empresa_id, usuario_info)
            total_documentos = self._contar_documentos_por_rol(empresa_id, usuario_info)

            referencias_promedio = round(total_referencias / total_solicitantes, 2)
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

    def _aplicar_query_filtros_rol(self, query, usuario_info: dict = None, empresa_id: int = None):
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
        elif rol == "supervisor":
            # Usuario supervisor ve las solicitudes de su equipo + las suyas propias
            user_id = usuario_info.get("id")
            if user_id and empresa_id:
                # Obtener IDs de usuarios de su equipo
                from models.usuarios_model import UsuariosModel
                usuarios_model = UsuariosModel()
                team_members = usuarios_model.get_team_members(user_id, empresa_id)

                # Incluir su propio ID + IDs de su equipo
                user_ids = [user_id]  # Su propio ID
                if team_members:
                    team_ids = [member["id"] for member in team_members]
                    user_ids.extend(team_ids)

                # Filtrar por created_by_user_id o assigned_to_user_id
                query = query.or_(f"created_by_user_id.in.({','.join(map(str, user_ids))}),assigned_to_user_id.in.({','.join(map(str, user_ids))})")
        elif rol == "asesor":
            # Usuario asesor ve solo sus propias solicitudes (priorizando created_by_user_id)
            user_id = usuario_info.get("id")
            if user_id:
                # Priorizar solicitudes creadas por el usuario, incluir también las asignadas
                query = query.or_(f"created_by_user_id.eq.{user_id},assigned_to_user_id.eq.{user_id}")

        return query

    def _contar_solicitantes_por_rol(self, empresa_id: int, usuario_info: dict = None) -> int:
        """Cuenta solicitantes aplicando filtros de rol de manera optimizada usando user_id directamente"""
        try:
            if not usuario_info or usuario_info.get("rol") in ["admin", "empresa"]:
                # Admin y empresa ven todos los solicitantes de la empresa
                resp = supabase.table("solicitantes").select("id", count="exact").eq("empresa_id", empresa_id).execute()
                return resp.count or 0

            rol = usuario_info.get("rol")
            user_id = usuario_info.get("id")

            if rol == "supervisor" and user_id:
                # Supervisor ve solo solicitantes de solicitudes creadas por él y su equipo
                from models.usuarios_model import UsuariosModel
                usuarios_model = UsuariosModel()
                team_members = usuarios_model.get_team_members(user_id, empresa_id)

                # Incluir su propio ID + IDs de su equipo
                user_ids = [user_id]  # Su propio ID
                if team_members:
                    team_ids = [member["id"] for member in team_members]
                    user_ids.extend(team_ids)

                # Contar solicitantes que tienen solicitudes creadas por el supervisor o su equipo
                resp = supabase.table("solicitantes").select(
                    "id, solicitudes!inner(created_by_user_id)",
                    count="exact"
                ).eq("empresa_id", empresa_id).in_(
                    "solicitudes.created_by_user_id", user_ids
                ).execute()
                return resp.count or 0

            elif rol == "asesor" and user_id:
                # Asesor ve solo solicitantes de solicitudes creadas por él (created_by_user_id es la variable principal)
                # Usar join directo con solicitudes filtrando principalmente por created_by_user_id
                resp = supabase.table("solicitantes").select(
                    "id, solicitudes!inner(created_by_user_id, assigned_to_user_id)",
                    count="exact"
                ).eq("empresa_id", empresa_id).eq(
                    "solicitudes.created_by_user_id", user_id
                ).execute()
                return resp.count or 0

            elif rol == "banco":
                # Usuario banco ve solicitantes filtrados por banco y ciudad
                banco_nombre = usuario_info.get("banco_nombre")
                ciudad = usuario_info.get("ciudad")

                if not banco_nombre and not ciudad:
                    return 0

                # Usar join directo con solicitudes filtrando por banco/ciudad
                query = supabase.table("solicitantes").select(
                    "id, solicitudes!inner(banco_nombre, ciudad_solicitud)",
                    count="exact"
                ).eq("empresa_id", empresa_id)

                filters = []
                if banco_nombre:
                    filters.append(f"solicitudes.banco_nombre.eq.{banco_nombre}")
                if ciudad:
                    filters.append(f"solicitudes.ciudad_solicitud.eq.{ciudad}")

                if filters:
                    query = query.or_(",".join(filters))

                resp = query.execute()
                return resp.count or 0

            return 0

        except Exception as e:
            print(f"❌ Error contando solicitantes por rol: {e}")
            return 0

    def _contar_documentos_por_rol(self, empresa_id: int, usuario_info: dict = None) -> int:
        """Cuenta documentos aplicando filtros de rol de manera optimizada usando user_id directamente"""
        try:
            if not usuario_info or usuario_info.get("rol") in ["admin", "empresa"]:
                # Admin y empresa ven todos los documentos de la empresa
                resp = supabase.table("documentos").select(
                    "id, solicitantes!inner(empresa_id)",
                    count="exact"
                ).eq("solicitantes.empresa_id", empresa_id).execute()
                return resp.count or 0

            rol = usuario_info.get("rol")
            user_id = usuario_info.get("id")

            if rol == "supervisor" and user_id:
                # Supervisor ve solo documentos de solicitantes de solicitudes creadas por él y su equipo
                from models.usuarios_model import UsuariosModel
                usuarios_model = UsuariosModel()
                team_members = usuarios_model.get_team_members(user_id, empresa_id)

                # Incluir su propio ID + IDs de su equipo
                user_ids = [user_id]  # Su propio ID
                if team_members:
                    team_ids = [member["id"] for member in team_members]
                    user_ids.extend(team_ids)

                # Contar documentos de solicitantes que tienen solicitudes creadas por el supervisor o su equipo
                resp = supabase.table("documentos").select(
                    "id, solicitantes!inner(empresa_id, solicitudes!inner(created_by_user_id))",
                    count="exact"
                ).eq("solicitantes.empresa_id", empresa_id).in_(
                    "solicitantes.solicitudes.created_by_user_id", user_ids
                ).execute()
                return resp.count or 0

            elif rol == "asesor" and user_id:
                # Asesor ve solo documentos de solicitantes de solicitudes creadas por él (created_by_user_id principal)
                # Usar doble join: documentos -> solicitantes -> solicitudes, filtrando por created_by_user_id
                resp = supabase.table("documentos").select(
                    "id, solicitantes!inner(empresa_id, solicitudes!inner(created_by_user_id))",
                    count="exact"
                ).eq("solicitantes.empresa_id", empresa_id).eq(
                    "solicitantes.solicitudes.created_by_user_id", user_id
                ).execute()
                return resp.count or 0

            elif rol == "banco":
                # Usuario banco ve documentos filtrados por banco y ciudad
                banco_nombre = usuario_info.get("banco_nombre")
                ciudad = usuario_info.get("ciudad")

                if not banco_nombre and not ciudad:
                    return 0

                # Usar doble join: documentos -> solicitantes -> solicitudes, filtrando por banco/ciudad
                query = supabase.table("documentos").select(
                    "id, solicitantes!inner(empresa_id, solicitudes!inner(banco_nombre, ciudad_solicitud))",
                    count="exact"
                ).eq("solicitantes.empresa_id", empresa_id)

                if banco_nombre:
                    query = query.eq("solicitantes.solicitudes.banco_nombre", banco_nombre)
                if ciudad:
                    query = query.eq("solicitantes.solicitudes.ciudad_solicitud", ciudad)

                resp = query.execute()
                return resp.count or 0

            return 0

        except Exception as e:
            print(f"❌ Error contando documentos por rol: {e}")
            return 0

    def _obtener_datos_financieros_por_rol(self, empresa_id: int, usuario_info: dict = None) -> tuple:
        """Obtiene datos financieros y de actividad económica aplicando filtros de rol optimizados"""
        try:
            if not usuario_info or usuario_info.get("rol") in ["admin", "empresa"]:
                # Admin y empresa ven toda la información de la empresa
                financiera_resp = supabase.table("informacion_financiera").select("detalle_financiera").eq("empresa_id", empresa_id).execute()
                financiera_data = _get_data(financiera_resp) or []

                actividades_resp = supabase.table("actividad_economica").select("detalle_actividad").eq("empresa_id", empresa_id).execute()
                actividades_data = _get_data(actividades_resp) or []

                return financiera_data, actividades_data

            rol = usuario_info.get("rol")
            user_id = usuario_info.get("id")

            if rol == "supervisor" and user_id:
                # Supervisor ve solo información de solicitantes de solicitudes creadas por él y su equipo
                from models.usuarios_model import UsuariosModel
                usuarios_model = UsuariosModel()
                team_members = usuarios_model.get_team_members(user_id, empresa_id)

                # Incluir su propio ID + IDs de su equipo
                user_ids = [user_id]  # Su propio ID
                if team_members:
                    team_ids = [member["id"] for member in team_members]
                    user_ids.extend(team_ids)

                # Información financiera con filtro de equipo
                financiera_resp = supabase.table("informacion_financiera").select(
                    "detalle_financiera, solicitantes!inner(empresa_id, solicitudes!inner(created_by_user_id))"
                ).eq("solicitantes.empresa_id", empresa_id).in_(
                    "solicitantes.solicitudes.created_by_user_id", user_ids
                ).execute()
                financiera_data = _get_data(financiera_resp) or []

                # Actividad económica con el mismo filtro
                actividades_resp = supabase.table("actividad_economica").select(
                    "detalle_actividad, solicitantes!inner(empresa_id, solicitudes!inner(created_by_user_id))"
                ).eq("solicitantes.empresa_id", empresa_id).in_(
                    "solicitantes.solicitudes.created_by_user_id", user_ids
                ).execute()
                actividades_data = _get_data(actividades_resp) or []

                return financiera_data, actividades_data

            elif rol == "asesor" and user_id:
                # Asesor ve solo información de solicitantes de solicitudes creadas por él (created_by_user_id principal)
                # Usar join directo: informacion_financiera -> solicitantes -> solicitudes, filtrando por created_by_user_id
                financiera_resp = supabase.table("informacion_financiera").select(
                    "detalle_financiera, solicitantes!inner(empresa_id, solicitudes!inner(created_by_user_id))"
                ).eq("solicitantes.empresa_id", empresa_id).eq(
                    "solicitantes.solicitudes.created_by_user_id", user_id
                ).execute()
                financiera_data = _get_data(financiera_resp) or []

                # Actividad económica con el mismo filtro
                actividades_resp = supabase.table("actividad_economica").select(
                    "detalle_actividad, solicitantes!inner(empresa_id, solicitudes!inner(created_by_user_id))"
                ).eq("solicitantes.empresa_id", empresa_id).eq(
                    "solicitantes.solicitudes.created_by_user_id", user_id
                ).execute()
                actividades_data = _get_data(actividades_resp) or []

                return financiera_data, actividades_data

            elif rol == "banco":
                # Usuario banco ve información filtrada por banco y ciudad
                banco_nombre = usuario_info.get("banco_nombre")
                ciudad = usuario_info.get("ciudad")

                if not banco_nombre and not ciudad:
                    return [], []

                # Información financiera con filtro de banco/ciudad
                query_financiera = supabase.table("informacion_financiera").select(
                    "detalle_financiera, solicitantes!inner(empresa_id, solicitudes!inner(banco_nombre, ciudad_solicitud))"
                ).eq("solicitantes.empresa_id", empresa_id)

                if banco_nombre:
                    query_financiera = query_financiera.eq("solicitantes.solicitudes.banco_nombre", banco_nombre)
                if ciudad:
                    query_financiera = query_financiera.eq("solicitantes.solicitudes.ciudad_solicitud", ciudad)

                financiera_resp = query_financiera.execute()
                financiera_data = _get_data(financiera_resp) or []

                # Actividad económica con el mismo filtro
                query_actividades = supabase.table("actividad_economica").select(
                    "detalle_actividad, solicitantes!inner(empresa_id, solicitudes!inner(banco_nombre, ciudad_solicitud))"
                ).eq("solicitantes.empresa_id", empresa_id)

                if banco_nombre:
                    query_actividades = query_actividades.eq("solicitantes.solicitudes.banco_nombre", banco_nombre)
                if ciudad:
                    query_actividades = query_actividades.eq("solicitantes.solicitudes.ciudad_solicitud", ciudad)

                actividades_resp = query_actividades.execute()
                actividades_data = _get_data(actividades_resp) or []

                return financiera_data, actividades_data

            return [], []

        except Exception as e:
            print(f"❌ Error obteniendo datos financieros por rol: {e}")
            return [], []

    def _contar_referencias_por_rol(self, empresa_id: int, usuario_info: dict = None) -> int:
        """Cuenta referencias aplicando filtros de rol de manera optimizada usando user_id directamente"""
        try:
            if not usuario_info or usuario_info.get("rol") in ["admin", "empresa"]:
                # Admin y empresa ven todas las referencias de la empresa
                resp = supabase.table("referencias").select("id", count="exact").eq("empresa_id", empresa_id).execute()
                return resp.count or 0

            rol = usuario_info.get("rol")
            user_id = usuario_info.get("id")

            if rol == "supervisor" and user_id:
                # Supervisor ve solo referencias de solicitantes de solicitudes creadas por él y su equipo
                from models.usuarios_model import UsuariosModel
                usuarios_model = UsuariosModel()
                team_members = usuarios_model.get_team_members(user_id, empresa_id)

                # Incluir su propio ID + IDs de su equipo
                user_ids = [user_id]  # Su propio ID
                if team_members:
                    team_ids = [member["id"] for member in team_members]
                    user_ids.extend(team_ids)

                # Contar referencias de solicitantes que tienen solicitudes creadas por el supervisor o su equipo
                resp = supabase.table("referencias").select(
                    "id, solicitantes!inner(empresa_id, solicitudes!inner(created_by_user_id))",
                    count="exact"
                ).eq("solicitantes.empresa_id", empresa_id).in_(
                    "solicitantes.solicitudes.created_by_user_id", user_ids
                ).execute()
                return resp.count or 0

            elif rol == "asesor" and user_id:
                # Asesor ve solo referencias de solicitantes de solicitudes creadas por él (created_by_user_id principal)
                # Usar doble join: referencias -> solicitantes -> solicitudes, filtrando por created_by_user_id
                resp = supabase.table("referencias").select(
                    "id, solicitantes!inner(empresa_id, solicitudes!inner(created_by_user_id))",
                    count="exact"
                ).eq("solicitantes.empresa_id", empresa_id).eq(
                    "solicitantes.solicitudes.created_by_user_id", user_id
                ).execute()
                return resp.count or 0

            elif rol == "banco":
                # Usuario banco ve referencias filtradas por banco y ciudad
                banco_nombre = usuario_info.get("banco_nombre")
                ciudad = usuario_info.get("ciudad")

                if not banco_nombre and not ciudad:
                    return 0

                # Usar doble join: referencias -> solicitantes -> solicitudes, filtrando por banco/ciudad
                query = supabase.table("referencias").select(
                    "id, solicitantes!inner(empresa_id, solicitudes!inner(banco_nombre, ciudad_solicitud))",
                    count="exact"
                ).eq("solicitantes.empresa_id", empresa_id)

                if banco_nombre:
                    query = query.eq("solicitantes.solicitudes.banco_nombre", banco_nombre)
                if ciudad:
                    query = query.eq("solicitantes.solicitudes.ciudad_solicitud", ciudad)

                resp = query.execute()
                return resp.count or 0

            return 0

        except Exception as e:
            print(f"❌ Error contando referencias por rol: {e}")
            return 0
