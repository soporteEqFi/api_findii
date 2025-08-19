"""
Utilidades para debugging y logs detallados de requests
"""
from flask import request


def log_request_details(endpoint_name: str, entity_name: str = ""):
    """
    Imprime todos los detalles de un request HTTP de forma detallada

    Args:
        endpoint_name: Nombre del endpoint (ej: "CREAR SOLICITANTE")
        entity_name: Nombre de la entidad opcional
    """
    print("\n" + "="*80)
    print(f"🔄 {request.method} {request.path} - {endpoint_name}")
    if entity_name:
        print(f"🏷️ Entidad: {entity_name}")
    print("="*80)

    # URL y METHOD
    print(f"📋 URL COMPLETA: {request.url}")
    print(f"📋 METHOD: {request.method}")
    print(f"📋 PATH: {request.path}")

    # HEADERS IMPORTANTES
    print(f"\n🔖 HEADERS IMPORTANTES:")
    important_headers = ['Content-Type', 'X-Empresa-Id', 'Origin', 'Authorization']
    for header in important_headers:
        value = request.headers.get(header)
        if value:
            print(f"   {header}: {value}")

    # QUERY PARAMS
    if request.args:
        print(f"\n🔍 QUERY PARAMS:")
        for key, value in request.args.items():
            print(f"   {key} = {value}")

    # BODY RAW
    print(f"\n📦 BODY RAW:")
    try:
        raw_data = request.get_data(as_text=True)
        if raw_data:
            print(f"   Raw data: {raw_data}")
        else:
            print(f"   (Sin body)")
    except Exception as e:
        print(f"   Error leyendo raw data: {e}")

    # BODY PARSEADO
    print(f"\n📦 BODY PARSEADO:")
    try:
        body = request.get_json(silent=True) or {}
        print(f"   Body completo: {body}")
        print(f"   Tipo: {type(body)}")

        if isinstance(body, dict):
            if body:
                print(f"   Claves recibidas: {list(body.keys())}")
                for key, value in body.items():
                    # Truncar valores muy largos para legibilidad
                    display_value = str(value)[:100] + "..." if len(str(value)) > 100 else value
                    print(f"   {key}: {display_value} (tipo: {type(value)})")
            else:
                print(f"   (Body vacío)")
        elif isinstance(body, list):
            print(f"   Lista con {len(body)} elementos")
            for idx, item in enumerate(body[:3]):  # Solo mostrar primeros 3
                print(f"   [{idx}]: {item}")
            if len(body) > 3:
                print(f"   ... y {len(body) - 3} elementos más")
    except Exception as e:
        print(f"   Error parseando JSON: {e}")


def log_validation_results(required_fields: list, body: dict):
    """
    Imprime resultados de validación de campos requeridos

    Args:
        required_fields: Lista de campos requeridos
        body: Diccionario con los datos recibidos
    """
    print(f"\n🔍 VALIDANDO CAMPOS REQUERIDOS:")
    missing_fields = []

    for field in required_fields:
        value = body.get(field)
        status = "✅ OK" if value else "❌ FALTA"
        print(f"   {field}: {value} ({status})")
        if not value:
            missing_fields.append(field)

    if missing_fields:
        print(f"\n❌ CAMPOS FALTANTES: {missing_fields}")
        return False
    else:
        print(f"\n✅ Todos los campos requeridos están presentes")
        return True


def log_data_to_save(data: dict, title: str = "DATOS A GUARDAR EN BD"):
    """
    Imprime los datos que se van a guardar en la base de datos

    Args:
        data: Diccionario con los datos a guardar
        title: Título para la sección de logs
    """
    print(f"\n💾 {title}:")
    for key, value in data.items():
        # Truncar valores muy largos
        display_value = str(value)[:200] + "..." if len(str(value)) > 200 else value
        print(f"   {key}: {display_value}")


def log_operation_result(result_data: dict, operation: str = "RESULTADO", entity_id_field: str = "id"):
    """
    Imprime el resultado de una operación

    Args:
        result_data: Datos del resultado
        operation: Nombre de la operación
        entity_id_field: Campo que contiene el ID de la entidad creada
    """
    print(f"\n✅ {operation}:")
    print(f"   Datos: {result_data}")

    if isinstance(result_data, dict) and entity_id_field in result_data:
        print(f"   ID generado: {result_data[entity_id_field]}")
    else:
        print(f"   ID: No disponible")


def log_response(response_data: dict):
    """
    Imprime la respuesta que se enviará al cliente

    Args:
        response_data: Datos de la respuesta
    """
    print(f"\n📤 RESPUESTA A ENVIAR:")
    # Truncar response si es muy largo
    if len(str(response_data)) > 500:
        print(f"   {str(response_data)[:500]}...")
    else:
        print(f"   {response_data}")
    print("="*80 + "\n")


def log_error(error: Exception, error_type: str = "ERROR"):
    """
    Imprime detalles de un error

    Args:
        error: La excepción
        error_type: Tipo de error (ej: "ERROR DE VALIDACIÓN")
    """
    print(f"\n❌ {error_type}: {error}")
    print(f"   Tipo de error: {type(error)}")

    # Imprimir traceback en errores inesperados
    if error_type == "ERROR INESPERADO":
        import traceback
        traceback.print_exc()

    print("="*80 + "\n")
