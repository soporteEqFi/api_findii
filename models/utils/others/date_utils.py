from datetime import datetime

def iso_date():
    return datetime.now().isoformat()


def format_date(date_str):
    """
        Formatea una fecha en formato dd/mm/yyyy
    """

    try:
        if date_str == "N/A":
            return "N/A"
        
        from datetime import datetime
        import dateutil.parser
        
        # Limpiamos la cadena
        date_str = date_str.strip().rstrip("'")
        
        # Usamos dateutil.parser que es más flexible con los formatos
        fecha = dateutil.parser.parse(date_str)
        
        # Formateamos la fecha como dd/mm/yyyy
        return fecha.strftime('%d/%m/%Y')
    except Exception as e:
        print(f"Error al formatear fecha: {e}")
        print(f"Fecha problemática: {date_str}")
        return date_str