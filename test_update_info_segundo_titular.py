#!/usr/bin/env python3
"""
Script de prueba para verificar que la actualización del info_segundo_titular funcione correctamente
"""

import requests
import json

# Configuración de la API
API_BASE_URL = "http://localhost:5000"
UPDATE_ENDPOINT = f"{API_BASE_URL}/edit-record/"

def test_update_info_segundo_titular_complete():
    """
    Prueba la actualización del campo info_segundo_titular con todos los campos específicos
    """
    
    # Datos de prueba para actualizar con los campos exactos mencionados
    test_data = {
        "solicitante_id": 1,  # Cambiar por un ID válido de la base de datos
        "PRODUCTO_SOLICITADO": {
            "info_segundo_titular": {
                "nombre": "FERNANDO",
                "tipo_documento": "CC",
                "numero_documento": "565",
                "fecha_nacimiento": "2025-07-31",
                "estado_civil": "casado",
                "personas_a_cargo": "5",
                "numero_celular": "566",
                "correo_electronico": "claraorozco019@gmail.com",
                "nivel_estudio": "primaria",
                "profesion": "5656"
            }
        }
    }
    
    print("🧪 Iniciando prueba de actualización de info_segundo_titular (campos completos)")
    print(f"📡 Endpoint: {UPDATE_ENDPOINT}")
    print(f"📊 Datos de prueba:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    try:
        # Realizar la petición PUT
        response = requests.put(
            UPDATE_ENDPOINT,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n📥 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Actualización exitosa!")
            response_data = response.json()
            print(f"   Respuesta: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Error en la actualización")
            try:
                error_data = response.json()
                print(f"   Error: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"   Error: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: No se pudo conectar al servidor")
        print("   Asegúrate de que la API esté ejecutándose en http://localhost:5000")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

def test_update_info_segundo_titular_partial():
    """
    Prueba la actualización del campo info_segundo_titular con solo algunos campos
    """
    
    test_data = {
        "solicitante_id": 1,  # Cambiar por un ID válido de la base de datos
        "PRODUCTO_SOLICITADO": {
            "info_segundo_titular": {
                "nombre": "FERNANDO",
                "tipo_documento": "CC",
                "numero_documento": "565"
            }
        }
    }
    
    print("\n🧪 Prueba con campos parciales")
    print(f"📊 Datos de prueba:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    try:
        response = requests.put(
            UPDATE_ENDPOINT,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Actualización parcial exitosa!")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_update_info_segundo_titular_string():
    """
    Prueba la actualización con un valor de string simple
    """
    
    test_data = {
        "solicitante_id": 1,  # Cambiar por un ID válido de la base de datos
        "PRODUCTO_SOLICITADO": {
            "info_segundo_titular": "Información del segundo titular como string simple"
        }
    }
    
    print("\n🧪 Prueba con valor string simple")
    print(f"📊 Datos de prueba:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    try:
        response = requests.put(
            UPDATE_ENDPOINT,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Actualización con string exitosa!")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_update_info_segundo_titular_empty():
    """
    Prueba la actualización con un valor vacío
    """
    
    test_data = {
        "solicitante_id": 1,  # Cambiar por un ID válido de la base de datos
        "PRODUCTO_SOLICITADO": {
            "info_segundo_titular": ""
        }
    }
    
    print("\n🧪 Prueba con valor vacío")
    print(f"📊 Datos de prueba:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    try:
        response = requests.put(
            UPDATE_ENDPOINT,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Actualización con valor vacío exitosa!")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_update_info_segundo_titular_null():
    """
    Prueba la actualización con un valor null
    """
    
    test_data = {
        "solicitante_id": 1,  # Cambiar por un ID válido de la base de datos
        "PRODUCTO_SOLICITADO": {
            "info_segundo_titular": None
        }
    }
    
    print("\n🧪 Prueba con valor null")
    print(f"📊 Datos de prueba:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    try:
        response = requests.put(
            UPDATE_ENDPOINT,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Actualización con valor null exitosa!")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Script de prueba para info_segundo_titular")
    print("=" * 60)
    
    # Ejecutar todas las pruebas
    test_update_info_segundo_titular_complete()
    test_update_info_segundo_titular_partial()
    test_update_info_segundo_titular_string()
    test_update_info_segundo_titular_empty()
    test_update_info_segundo_titular_null()
    
    print("\n" + "=" * 60)
    print("🏁 Pruebas completadas")
    print("\n📝 Notas importantes:")
    print("   - Cambia el 'solicitante_id' por un ID válido de tu base de datos")
    print("   - Asegúrate de que la API esté ejecutándose")
    print("   - Revisa los logs del servidor para ver los mensajes de debug")
    print("   - El sistema debe manejar JSON completo, parcial, string, vacío y null")
    print("\n🔍 Campos específicos del JSON de prueba:")
    print("   - nombre, tipo_documento, numero_documento, fecha_nacimiento")
    print("   - estado_civil, personas_a_cargo, numero_celular")
    print("   - correo_electronico, nivel_estudio, profesion")
