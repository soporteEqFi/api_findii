from models.records_model import *

mod_records = recordsModel()

class recordsControlador():

    def post_add_record(self):  
        query = mod_records.add_record()
        required_fields = {
            "nombre_completo", "tipo_documento", "numero_documento", "fecha_nacimiento",
            "numero_celular", "correo_electronico", "nivel_estudio", "profesion",
            "estado_civil", "personas_a_cargo", "direccion_residencia", "tipo_vivienda",
            "barrio", "departamento", "estrato", "ciudad_gestion", "actividad_economica",
            "empresa_labora", "fecha_vinculacion", "direccion_empresa", "telefono_empresa",
            "tipo_contrato", "cargo_actual", "ingresos", "valor_inmueble", "cuota_inicial",
            "porcentaje_financiar", "total_egresos", "total_activos", "total_pasivos",
            "tipo_credito", "plazo_meses", "segundo_titular", "observacion", "asesor_usuario",
            "banco", "informacion_producto" 
        }

        missing_fields = required_fields - set(request.form.keys())
        if missing_fields:
            print("Faltan campos requeridos")
            print(missing_fields)
            return jsonify({
                "error": "Faltan campos requeridos",
                "campos_faltantes": list(missing_fields)
            }), 400
        
        return query
        
    def get_all_data(self):
        query = mod_records.get_all_data()
        return query 
    
    def get_combined_data(self):
        query = mod_records.get_all_data()
        return query
    
    def filtrar_tabla_combinada(self):
        query = mod_records.filtrar_tabla()
        return query

    def filtrar_tabla(self):
        query = mod_records.filtrar_tabla()
        return query
    
    def descargar_ventas_realizadas(self):
        query = mod_records.descargar_ventas_realizadas()
        return query
    
    def actualizar_estado(self):
         query = mod_records.editar_estado()
         return query
    
    def filtrar_por_fecha(self):
         query = mod_records.mostrar_por_fecha()
         return query
    
    def filtro_intervalo(self):
         query = mod_records.mostrar_por_intervalo()
         return query
    
    def edit_record(self):
        query = mod_records.edit_record()
        return query

    def delete_record(self):
        query = mod_records.delete_record()
        return query

    def update_files(self):
        query = mod_records.update_files()
        return query

