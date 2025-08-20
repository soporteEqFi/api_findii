from flask import request, jsonify
from data.supabase_conn import supabase

class DashboardController:
    @staticmethod
    def _obtener_usuario_autenticado():
        """Obtener información del usuario autenticado desde la base de datos"""
        try:
            print(f"\n🔍 DIAGNÓSTICO DE AUTENTICACIÓN:")
            print(f"   Headers recibidos: {dict(request.headers)}")
            print(f"   Query params: {dict(request.args)}")

            # Obtener el token del header Authorization
            auth_header = request.headers.get("Authorization")
            print(f"   Authorization header: {auth_header}")

            if not auth_header or not auth_header.startswith("Bearer "):
                print(f"   ❌ Authorization header inválido o faltante")
                return None

            # Obtener user_id del header o query parameter
            user_id = request.headers.get("X-User-Id") or request.args.get("user_id")
            print(f"   User ID (header): {request.headers.get('X-User-Id')}")
            print(f"   User ID (query): {request.args.get('user_id')}")
            print(f"   User ID final: {user_id}")

            if not user_id:
                print(f"   ❌ User ID faltante (header X-User-Id o query user_id)")
                return None

            # Consultar la base de datos para obtener información completa del usuario
            print(f"   🔍 Consultando usuario con ID: {user_id}")
            user_response = supabase.table("usuarios").select("id, rol, info_extra").eq("id", int(user_id)).execute()
            print(f"   📊 Respuesta de BD: {user_response.data}")

            user_data = user_response.data[0] if user_response.data else None

            if not user_data:
                print(f"   ❌ Usuario no encontrado en BD")
                return None

            # Extraer banco_nombre del info_extra del usuario
            info_extra = user_data.get("info_extra", {})
            banco_nombre = info_extra.get("banco_nombre")

            usuario_info = {
                "id": user_data["id"],
                "rol": user_data.get("rol", "empresa"),
                "banco_nombre": banco_nombre  # Desde info_extra del usuario
            }

            print(f"   ✅ Usuario autenticado: {usuario_info}")
            return usuario_info

        except Exception as e:
            print(f"   ❌ Error obteniendo usuario autenticado: {e}")
            return None

    @staticmethod
    def get_dashboard_data(empresa_id):
        try:
            # Obtener información del usuario autenticado
            usuario_info = DashboardController._obtener_usuario_autenticado()

            print(f"\n📊 OBTENIENDO DATOS PARA EMPRESA {empresa_id}")
            print(f"   👤 Usuario: {usuario_info}")

            # Obtener datos del solicitante
            solicitante_data = supabase.table('solicitantes').select('*').eq('empresa_id', empresa_id).execute()

            if not solicitante_data.data:
                return jsonify({"ok": True, "data": []})

            solicitante_id = solicitante_data.data[0]['id']

            # Obtener datos relacionados
            actividad_economica = supabase.table('actividad_economica').select('*').eq('empresa_id', empresa_id).execute()
            informacion_financiera = supabase.table('informacion_financiera').select('*').eq('empresa_id', empresa_id).execute()
            referencias = supabase.table('referencias').select('*').eq('empresa_id', empresa_id).execute()

            # Obtener solicitudes con filtros de permisos por rol
            solicitud_query = supabase.table('solicitudes').select('*').eq('empresa_id', empresa_id)

            # Aplicar filtros de permisos por rol
            if usuario_info:
                rol = usuario_info.get("rol")

                if rol == "banco":
                    # Usuario banco solo ve solicitudes de su banco
                    banco_nombre = usuario_info.get("banco_nombre")
                    if banco_nombre:
                        solicitud_query = solicitud_query.eq("banco_nombre", banco_nombre)
                        print(f"   🏦 Aplicando filtro de banco: {banco_nombre}")
                    else:
                        # Si no tiene banco asignado, no ve nada
                        print(f"   ⚠️ Usuario banco sin banco asignado")
                        return jsonify({"ok": True, "data": []})
                elif rol == "admin":
                    # Admin ve todas las solicitudes
                    print(f"   👑 Admin: viendo todas las solicitudes")
                elif rol == "empresa":
                    # Usuario empresa ve todas las solicitudes de su empresa
                    print(f"   🏢 Empresa: viendo todas las solicitudes")
                else:
                    # Rol desconocido, no ve nada
                    print(f"   ❌ Rol desconocido: {rol}")
                    return jsonify({"ok": True, "data": []})

            solicitud = solicitud_query.execute()
            ubicacion = supabase.table('ubicacion').select('*').eq('empresa_id', empresa_id).execute()

            print(f"   📄 Solicitudes encontradas: {len(solicitud.data) if solicitud.data else 0}")
            if solicitud.data:
                for s in solicitud.data:
                    print(f"      - ID: {s.get('id')}, Estado: {s.get('estado')}, Banco: {s.get('banco_nombre')}, Solicitante: {s.get('solicitante_id')}")

            # Construir respuesta consolidada
            response_data = []

            # Obtener solo los solicitantes que tienen solicitudes filtradas
            solicitantes_con_solicitudes = set()
            if solicitud.data:
                for s in solicitud.data:
                    solicitantes_con_solicitudes.add(s.get('solicitante_id'))

            print(f"   🎯 Solicitantes con solicitudes filtradas: {solicitantes_con_solicitudes}")

            for sol in solicitante_data.data:
                sol_id = sol['id']

                # Solo incluir solicitantes que tienen solicitudes filtradas
                if sol_id not in solicitantes_con_solicitudes:
                    print(f"   ⏭️ Saltando solicitante {sol_id} (sin solicitudes filtradas)")
                    continue

                # Encontrar datos relacionados
                act_eco = next((ae for ae in actividad_economica.data if ae.get('solicitante_id') == sol_id), {})
                info_fin = next((inf for inf in informacion_financiera.data if inf.get('solicitante_id') == sol_id), {})
                refs = [r for r in referencias.data if r.get('solicitante_id') == sol_id]
                soli = next((s for s in solicitud.data if s.get('solicitante_id') == sol_id), {})
                ubi = next((u for u in ubicacion.data if u.get('solicitante_id') == sol_id), {})

                # Agregar a la respuesta
                print(f"\n🔗 COMBINANDO DATOS PARA SOLICITANTE {sol_id}:")
                print(f"   📄 Solicitud: {'✅ ID ' + str(soli.get('id')) + ' - Estado: ' + str(soli.get('estado')) + ' - Banco: ' + str(soli.get('banco_nombre')) if soli else '❌ No encontrada'}")

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
