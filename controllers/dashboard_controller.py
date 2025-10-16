from flask import request, jsonify
from data.supabase_conn import supabase

class DashboardController:
    @staticmethod
    def _obtener_usuario_autenticado():
        """Obtener información del usuario autenticado desde la base de datos"""
        try:
            # Obtener el token del header Authorization
            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                print(f"   ❌ Authorization header inválido o faltante")
                return None

            # Obtener user_id del header o query parameter
            user_id = request.headers.get("X-User-Id") or request.args.get("user_id")

            if not user_id:
                print(f"   ❌ User ID faltante (header X-User-Id o query user_id)")
                return None

            # Consultar la base de datos para obtener información completa del usuario
            # print(f"   🔍 Consultando usuario con ID: {user_id}")
            user_response = supabase.table("usuarios").select("id, rol, info_extra").eq("id", int(user_id)).execute()
            # print(f"   📊 Respuesta de BD: {user_response.data}")

            user_data = user_response.data[0] if user_response.data else None

            if not user_data:
                print(f"   ❌ Usuario no encontrado en BD")
                return None

            # Extraer banco_nombre y ciudad del info_extra del usuario
            info_extra = user_data.get("info_extra", {})
            banco_nombre = info_extra.get("banco_nombre")
            ciudad = info_extra.get("ciudad")

            usuario_info = {
                "id": user_data["id"],
                "rol": user_data.get("rol", "empresa"),
                "banco_nombre": banco_nombre,  # Desde info_extra del usuario
                "ciudad": ciudad  # Desde info_extra del usuario
            }

            return usuario_info

        except Exception as e:
            print(f"   ❌ Error obteniendo usuario autenticado: {e}")
            return None

    @staticmethod
    def get_dashboard_data(empresa_id):
        try:
            # Obtener información del usuario autenticado
            usuario_info = DashboardController._obtener_usuario_autenticado()

            # Obtener datos del solicitante
            solicitante_data = supabase.table('solicitantes').select('*').eq('empresa_id', empresa_id).execute()

            if not solicitante_data.data:
                return jsonify({"ok": True, "data": []})

            solicitante_id = solicitante_data.data[0]['id']

            # Obtener datos relacionados
            actividad_economica = supabase.table('actividad_economica').select('*').eq('empresa_id', empresa_id).execute()
            informacion_financiera = supabase.table('informacion_financiera').select('*').eq('empresa_id', empresa_id).execute()
            referencias = supabase.table('referencias').select('*').eq('empresa_id', empresa_id).execute()

            # Usar el método del modelo de solicitudes que ya tiene el JOIN implementado
            from models.solicitudes_model import SolicitudesModel
            solicitudes_model = SolicitudesModel()

            # Obtener solicitudes con filtros de permisos por rol y JOIN con usuarios
            solicitud_data = solicitudes_model.list_con_filtros_rol(
                empresa_id=empresa_id,
                usuario_info=usuario_info,
                limit=1000  # Límite alto para el dashboard
            )

            # Convertir a formato compatible con el resto del código
            solicitud = type('obj', (object,), {'data': solicitud_data})()
            ubicacion = supabase.table('ubicacion').select('*').eq('empresa_id', empresa_id).execute()

            # # print(f"   📄 Solicitudes encontradas: {len(solicitud.data) if solicitud.data else 0}")
            # if solicitud.data:
            #     for s in solicitud.data:
            #         print(f"      - ID: {s.get('id')}, Estado: {s.get('estado')}, Banco: {s.get('banco_nombre')}, Solicitante: {s.get('solicitante_id')}")

            # Construir respuesta consolidada
            response_data = []

            # Obtener solo los solicitantes que tienen solicitudes filtradas
            solicitantes_con_solicitudes = set()
            if solicitud.data:
                for s in solicitud.data:
                    solicitantes_con_solicitudes.add(s.get('solicitante_id'))

            for sol in solicitante_data.data:
                sol_id = sol['id']

                # Solo incluir solicitantes que tienen solicitudes filtradas
                if sol_id not in solicitantes_con_solicitudes:
                    continue

                # Encontrar datos relacionados
                act_eco = next((ae for ae in actividad_economica.data if ae.get('solicitante_id') == sol_id), {})
                info_fin = next((inf for inf in informacion_financiera.data if inf.get('solicitante_id') == sol_id), {})
                refs = [r for r in referencias.data if r.get('solicitante_id') == sol_id]
                soli = next((s for s in solicitud.data if s.get('solicitante_id') == sol_id), {})
                ubi = next((u for u in ubicacion.data if u.get('solicitante_id') == sol_id), {})

                                # Aplicar filtro de ciudad para usuarios banco
                if usuario_info and usuario_info.get("rol") == "banco" and usuario_info.get("ciudad"):
                    ciudad_usuario = usuario_info.get("ciudad")

                    # Buscar ciudad en el campo fijo ciudad_solicitud de la solicitud
                    ciudad_solicitante = None
                    if soli:
                        # ciudad_solicitud es un campo fijo en la tabla solicitudes
                        ciudad_solicitante = soli.get('ciudad_solicitud')

                    if ciudad_solicitante and ciudad_solicitante != ciudad_usuario:
                        # print(f"   🏙️ Saltando solicitante {sol_id} (ciudad: {ciudad_solicitante}, usuario: {ciudad_usuario})")
                        continue
                        # print(f"   🏙️ Ciudad coincidente: {ciudad_solicitante}")

                response_data.append({
                    "solicitante": sol,
                    "actividad_economica": act_eco,
                    "informacion_financiera": info_fin,
                    "referencias": refs,
                    "solicitud": soli,
                    "ubicacion": ubi
                })

            return jsonify({
                "ok": True,
                "data": response_data
            })

        except Exception as e:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500
