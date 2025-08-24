#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del campo order_index
"""

import json
from models.schema_completo_model import SchemaCompletoModel
from models.json_schema_model import JSONSchemaModel

def test_order_index():
    """Prueba el funcionamiento del campo order_index"""

    print("🧪 Iniciando pruebas de order_index...")

    # Crear instancias de los modelos
    schema_model = SchemaCompletoModel()
    json_schema_model = JSONSchemaModel()

    # Datos de prueba
    empresa_id = 1
    entity = "solicitante"
    json_column = "info_extra"

    # Ejemplo 1: Array con enum y order_index
    print("\n📋 Ejemplo 1: Array con enum y order_index")
    ejemplo_enum = {
        "enum": ["empleado", "independiente", "pensionado", "empresario"],
        "order_index": 1
    }
    print(f"Input: {json.dumps(ejemplo_enum, indent=2)}")

    # Ejemplo 2: Array de objetos con order_index
    print("\n📋 Ejemplo 2: Array de objetos con order_index")
    ejemplo_objetos = {
        "array_type": "object",
        "object_structure": [
            {
                "key": "nombre_negocio",
                "type": "string",
                "required": False,
                "description": "Nombre del negocio",
                "order_index": 1
            },
            {
                "key": "tipo_negocio",
                "type": "string",
                "required": True,
                "description": "Tipo de negocio",
                "order_index": 2
            },
            {
                "key": "ingresos_mensuales",
                "type": "number",
                "required": False,
                "description": "Ingresos mensuales",
                "order_index": 3
            }
        ]
    }
    print(f"Input: {json.dumps(ejemplo_objetos, indent=2)}")

    # Probar el procesamiento de list_values
    print("\n🔧 Probando procesamiento de list_values...")

    # Procesar array simple
    array_simple = ["soltero", "casado", "viudo", "divorciado"]
    resultado_simple = schema_model._procesar_list_values_con_order_index(array_simple)
    print(f"Array simple: {json.dumps(resultado_simple, indent=2)}")

    # Procesar array de objetos
    array_objetos = [
        {"key": "campo1", "type": "string", "order_index": 2},
        {"key": "campo2", "type": "number", "order_index": 1}
    ]
    resultado_objetos = schema_model._procesar_list_values_con_order_index(array_objetos)
    print(f"Array objetos: {json.dumps(resultado_objetos, indent=2)}")

    # Probar ordenamiento de campos
    print("\n🔧 Probando ordenamiento de campos...")

    campos_prueba = [
        {"key": "campo3", "order_index": 3},
        {"key": "campo1", "order_index": 1},
        {"key": "campo2", "order_index": 2},
        {"key": "campo_sin_order", "description": "Sin order_index"}
    ]

    campos_ordenados = schema_model._ordenar_campos_por_order_index(campos_prueba)
    print("Campos ordenados:")
    for campo in campos_ordenados:
        print(f"  - {campo['key']}: order_index={campo.get('order_index', 'N/A')}")

    # Probar con campos que tienen list_values con order_index
    print("\n🔧 Probando campos con list_values y order_index...")

    campos_con_list_values = [
        {
            "key": "tipo_empleo",
            "list_values": {"enum": ["a", "b", "c"], "order_index": 2},
            "order_index": 1
        },
        {
            "key": "datos_negocio",
            "list_values": {
                "array_type": "object",
                "object_structure": [
                    {"key": "nombre", "order_index": 1},
                    {"key": "tipo", "order_index": 2}
                ]
            },
            "order_index": 3
        }
    ]

    campos_ordenados_avanzado = schema_model._ordenar_campos_por_order_index(campos_con_list_values)
    print("Campos con list_values ordenados:")
    for campo in campos_ordenados_avanzado:
        print(f"  - {campo['key']}: order_index={campo.get('order_index', 'N/A')}")

    print("\n✅ Pruebas completadas exitosamente!")

def test_schema_completo():
    """Prueba el método get_schema_completo con order_index"""

    print("\n🧪 Probando get_schema_completo con order_index...")

    schema_model = SchemaCompletoModel()
    empresa_id = 1
    entity = "solicitante"

    try:
        schema, error = schema_model.get_schema_completo(entity, empresa_id)

        if error:
            print(f"❌ Error: {error}")
            return

        print("✅ Schema obtenido exitosamente")
        print(f"📊 Total campos dinámicos: {len(schema['campos_dinamicos'])}")

        # Mostrar algunos campos dinámicos con order_index
        print("\n📋 Campos dinámicos (primeros 5):")
        for i, campo in enumerate(schema['campos_dinamicos'][:5]):
            print(f"  {i+1}. {campo['key']}: order_index={campo.get('order_index', 'N/A')}")

    except Exception as e:
        print(f"❌ Error en get_schema_completo: {e}")

if __name__ == "__main__":
    test_order_index()
    test_schema_completo()
