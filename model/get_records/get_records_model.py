from librerias import *
from model.generales.generales import *
# from datetime import datetime

class select_model():

    def select_data(self):

        try:
            agents_info = supabase.table("ASESORES").select('*').order('id.desc').execute()
            solicitantes = supabase.table(tabla_solicitantes).select("*").order('id.desc').execute()
            location = supabase.table("UBICACION").select("*").order('id.desc').execute()
            economic_activity= supabase.table("ACTIVIDAD_ECONOMICA").select("*").order('id.desc').execute()
            financial_info = supabase.table("INFORMACION_FINANCIERA").select("*").order('id.desc').execute()
            product = supabase.table("PRODUCTO_SOLICITADO").select("*").order('id.desc').execute()
            solicitud = supabase.table("SOLICITUDES").select("*").order('id.desc').execute()
            
            registros = {
                "agents_info": agents_info.data,
                "solicitantes": solicitantes.data,
                "location": location.data,
                "economic_activity": economic_activity.data,
                "financial_info": financial_info.data,
                "product": product.data,
                "solicitud": solicitud.data
            }

            

            print(registros)


            if all(len(value) == 0 for value in registros.values()):
                return jsonify({"mensaje": "No hay registros en estas tablas"}), 200

            return jsonify({"registros": registros}), 200
            

        except Exception as e:
            print("Ocurrio un error", e)
            return jsonify({"mensaje": "Error en la lectura"}), 500