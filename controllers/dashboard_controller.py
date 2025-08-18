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
            actividad_economica = supabase.table('actividad_economica').select('*').eq('solicitante_id', solicitante_id).eq('empresa_id', empresa_id).execute()
            informacion_financiera = supabase.table('informacion_financiera').select('*').eq('solicitante_id', solicitante_id).eq('empresa_id', empresa_id).execute()
            referencias = supabase.table('referencias').select('*').eq('solicitante_id', solicitante_id).eq('empresa_id', empresa_id).execute()
            solicitud = supabase.table('solicitudes').select('*').eq('solicitante_id', solicitante_id).eq('empresa_id', empresa_id).execute()
            ubicacion = supabase.table('ubicacion').select('*').eq('solicitante_id', solicitante_id).eq('empresa_id', empresa_id).execute()
            
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
