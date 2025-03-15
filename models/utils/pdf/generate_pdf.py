def generar_pdf_desde_html(data):
    try:
        from xhtml2pdf import pisa
        from io import BytesIO
        import os
        
        # Crear un buffer para el PDF
        buffer = BytesIO()
        
        # Ruta al archivo de plantilla HTML
        template_path = r'models\utils\pdf\pdf_template.html'
        
        # Leer la plantilla HTML
        with open(template_path, 'r', encoding='utf-8') as file:
            html_template = file.read()

        print(data)
        print(data.get('nombre_completo'))
        
        # Reemplazar los marcadores de posición con los datos reales
        # Extraer datos de la estructura anidada
        solicitante = data.get('solicitante', {})
        ubicacion = data.get('ubicacion', {})
        actividad_economica = data.get('actividad_economica', {})
        informacion_financiera = data.get('informacion_financiera', {})
        producto = data.get('producto', {})
        
        # Formatear nombre completo
        nombre_completo = f"{solicitante.get('nombre', '')} {solicitante.get('apellido', '')}"
        
        html = html_template.format(
            nombre_completo=nombre_completo,
            tipo_documento=solicitante.get('tipo_documento', ''),
            numero_documento=solicitante.get('numero_documento', ''),
            fecha_nacimiento=solicitante.get('fecha_nacimiento', ''),
            numero_celular=solicitante.get('numero_celular', ''),
            correo_electronico=solicitante.get('email', ''),
            nivel_estudio=solicitante.get('nivel_estudio', ''),
            profesion=solicitante.get('profesion', ''),
            estado_civil=solicitante.get('estado_civil', ''),
            personas_a_cargo=solicitante.get('personas_a_cargo', ''),
            direccion_residencia=ubicacion.get('direccion', ''),
            tipo_vivienda=ubicacion.get('tipo_vivienda', ''),
            barrio=ubicacion.get('tiempo_residencia', ''),
            departamento=ubicacion.get('departamento', ''),
            estrato=ubicacion.get('estrato', ''),
            ciudad_gestion=ubicacion.get('ciudad', ''),
            actividad_economica=actividad_economica.get('actividad', ''),
            empresa_labora=actividad_economica.get('empresa', ''),
            fecha_vinculacion=actividad_economica.get('fecha_vinculacion', ''),
            direccion_empresa=actividad_economica.get('direccion_empresa', ''),
            telefono_empresa=actividad_economica.get('telefono_empresa', ''),
            tipo_contrato=actividad_economica.get('tipo_contrato', ''),
            cargo_actual=actividad_economica.get('cargo', ''),
            ingresos=informacion_financiera.get('ingresos', ''),
            valor_inmueble=informacion_financiera.get('valor_inmueble', ''),
            cuota_inicial=informacion_financiera.get('cuota_inicial', ''),
            porcentaje_financiar=informacion_financiera.get('porcentaje_financiar', ''),
            total_egresos=informacion_financiera.get('total_egresos', ''),
            total_activos=informacion_financiera.get('total_activos', ''),
            total_pasivos=informacion_financiera.get('total_pasivos', ''),
            tipo_credito=producto.get('tipo_credito', ''),
            plazo_meses=producto.get('plazo_meses', ''),
            segundo_titular="Sí" if producto.get('segundo_titular') else "No",
            observacion=producto.get('observacion', ''),
            banco=data.get('banco', '')
        )
        # Convertir HTML a PDF
        pisa_status = pisa.CreatePDF(html, dest=buffer)
        
        # Verificar si la conversión fue exitosa
        if pisa_status.err:
            return None
        
        # Obtener el contenido del PDF
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
        
    except Exception as e:
        print(f"Error generando PDF desde HTML: {str(e)}")
        return None