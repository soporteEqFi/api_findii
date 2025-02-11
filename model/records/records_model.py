from librerias import *
from model.generales.generales import *
from uuid import uuid4
from datetime import datetime

class recordsModel():
    def add_record(self):
        try:
            # Generar UUID para el solicitante
            asesores_info = supabase.table("ASESORES").select('*').eq('usuario', request.json.get('asesor_usuario')).execute()
            print("Asesores info")
            print(asesores_info.data)
            asesor_id = asesores_info.data[0]['id']

            # Crear registro del solicitante
            solicitante = {
                "nombre_completo":  request.json.get('nombre_completo'),
                "tipo_documento": request.json.get('tipo_documento'),
                "numero_documento": request.json.get('numero_documento'),
                "fecha_nacimiento": request.json.get('fecha_nacimiento'),
                "numero_celular": request.json.get('numero_celular'),
                "correo_electronico": request.json.get('correo_electronico'),
                "nivel_estudio":  request.json.get('nivel_estudio'),
                "profesion": request.json.get('profesion'),  # Campo opcional
                "estado_civil": request.json.get('estado_civil'),
                "personas_a_cargo": request.json.get('personas_a_cargo')
            }

            res = supabase.table('SOLICITANTES').insert(solicitante).execute()
            print("Solicitante")
            print(res.data)

            solicitante_id = res.data[0]['id']

            # Crear registro de ubicación
            ubicacion = {
                "solicitante_id": solicitante_id,
                "direccion_residencia": request.json.get('direccion_residencia'),
                "tipo_vivienda": request.json.get('tipo_vivienda'),
                "barrio": request.json.get('barrio'),
                "departamento": request.json.get('departamento'),
                "estrato": request.json.get('estrato'),
                "ciudad_gestion": request.json.get('ciudad_gestion')
            }

            res = supabase.table('UBICACION').insert(ubicacion).execute()

            print("Ubicaciones")
            print(res.data)
            
            # Crear registro de actividad económica
            actividad_economica = {
                "solicitante_id": solicitante_id,
                "actividad_economica": request.json.get('actividad_economica'),
                "empresa_labora": request.json.get('empresa_labora'),
                "fecha_vinculacion": datetime.strptime(request.json.get('fecha_vinculacion'), '%Y-%m-%d').strftime('%Y,%m,%d'),  # Comentado debido al error
                "direccion_empresa": request.json.get('direccion_empresa'),
                "telefono_empresa": request.json.get('telefono_empresa'),
                "tipo_contrato": request.json.get('tipo_contrato'),
                "cargo_actual": request.json.get('cargo_actual')
            }

            res = supabase.table('ACTIVIDAD_ECONOMICA').insert(actividad_economica).execute()

            print("Actividad economica")
            print(res.data)
            
            # Crear registro de información financiera
            info_financiera = {
                "solicitante_id": solicitante_id,
                "ingresos": request.json.get('ingresos'),
                "valor_inmueble": request.json.get('valor_inmueble'),
                "cuota_inicial": request.json.get('cuota_inicial'),
                "porcentaje_financiar": request.json.get('porcentaje_financiar'),
                "total_egresos": request.json.get('total_egresos'),
                "total_activos": request.json.get('total_activos'),
                "total_pasivos": request.json.get('total_pasivos')
            }

            res = supabase.table('INFORMACION_FINANCIERA').insert(info_financiera).execute()

            print("Informacion financiera")
            print(res.data)
            
            # Crear registro de producto solicitado
            producto = {
                "solicitante_id": solicitante_id,
                "tipo_credito": request.json.get('tipo_credito'),
                "plazo_meses": request.json.get('plazo_meses'),
                "segundo_titular": request.json.get('segundo_titular'),
                "observacion": request.json.get('observacion')
            }

            res = supabase.table('PRODUCTO_SOLICITADO').insert(producto).execute()
            print("Producto solicitado")
            print(res.data)
            
            # Crear registro de solicitud
            solicitud = {
                "solicitante_id": solicitante_id,
                "asesor_id": asesor_id,
                "banco": request.json.get('banco'),
                # "fecha_solicitud": datetime.now().strftime('%d/%m/%Y %H %M %S')
            }

            res = supabase.table('SOLICITUDES').insert(solicitud).execute()
            print("Solicitud")
            print(res.data)

            print(solicitante)
            print(ubicacion)
            print(actividad_economica)
            print(info_financiera)
            print(producto)
            print(solicitud)
            
            return jsonify({
                "mensaje": "Registro creado exitosamente",
            }), 200
            
        except Exception as e:
            print("Ocurrió un error:", e)
            return jsonify({"mensaje": "Ocurrió un error al procesar la solicitud."}), 500