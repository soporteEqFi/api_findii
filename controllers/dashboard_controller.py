from flask import request, jsonify
from data.supabase_conn import supabase

class DashboardController:
    @staticmethod
    def get_dashboard_data(empresa_id):
        try:
            # Obtener datos del solicitante
            solicitante_data = supabase.table('solicitantes').select('*').eq('empresa_id', empresa_id).execute()

            if not solicitante_data.data:
                return jsonify({"ok": True, "data": []})

            solicitante_id = solicitante_data.data[0]['id']

            # Obtener datos relacionados
            print(f"\n📊 OBTENIENDO DATOS PARA EMPRESA {empresa_id}")

            actividad_economica = supabase.table('actividad_economica').select('*').eq('empresa_id', empresa_id).execute()
            informacion_financiera = supabase.table('informacion_financiera').select('*').eq('empresa_id', empresa_id).execute()
            referencias = supabase.table('referencias').select('*').eq('empresa_id', empresa_id).execute()
            solicitud = supabase.table('solicitudes').select('*').eq('empresa_id', empresa_id).execute()
            ubicacion = supabase.table('ubicacion').select('*').eq('empresa_id', empresa_id).execute()

            print(f"   📄 Solicitudes encontradas: {len(solicitud.data) if solicitud.data else 0}")
            if solicitud.data:
                for s in solicitud.data:
                    print(f"      - ID: {s.get('id')}, Estado: {s.get('estado')}, Solicitante: {s.get('solicitante_id')}")

            # Construir respuesta consolidada
            response_data = []

            for sol in solicitante_data.data:
                sol_id = sol['id']

                # Encontrar datos relacionados
                act_eco = next((ae for ae in actividad_economica.data if ae.get('solicitante_id') == sol_id), {})
                info_fin = next((inf for inf in informacion_financiera.data if inf.get('solicitante_id') == sol_id), {})
                refs = [r for r in referencias.data if r.get('solicitante_id') == sol_id]
                soli = next((s for s in solicitud.data if s.get('solicitante_id') == sol_id), {})
                ubi = next((u for u in ubicacion.data if u.get('solicitante_id') == sol_id), {})

                # Agregar a la respuesta
                print(f"\n🔗 COMBINANDO DATOS PARA SOLICITANTE {sol_id}:")
                print(f"   📄 Solicitud: {'✅ ID ' + str(soli.get('id')) + ' - Estado: ' + str(soli.get('estado')) if soli else '❌ No encontrada'}")

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
