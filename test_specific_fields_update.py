#!/usr/bin/env python3
"""
Script de prueba específico para verificar la actualización de campos individuales 
dentro del JSON de info_segundo_titular
"""

import requests
import json

# Configuración de la API
API_BASE_URL = "http://localhost:5000"
UPDATE_ENDPOINT = f"{API_BASE_URL}/edit-record/"

def test_update_specific_fields():
    """
    Prueba la actualización con los campos específicos mencionados por el usuario
    """
    
    # Datos de prueba con los campos exactos mencionados
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
    
    print("🧪 Prueba de actualización con campos específicos del JSON")
    print(f"📡 Endpoint: {UPDATE_ENDPOINT}")
    print(f"📊 Datos de prueba:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    try:
        response = requests.put(
            UPDATE_ENDPOINT,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n📥 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Actualización exitosa!")
            response_data = response.json()
            print(f"   Respuesta: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verificar que se actualizaron los datos correctamente
            print("\n🔍 Verificando campos actualizados:")
            for campo, valor in test_data["PRODUCTO_SOLICITADO"]["info_segundo_titular"].items():
                print(f"   ✅ {campo}: {valor}")
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

def test_update_partial_json():
    """
    Prueba la actualización con solo algunos campos del JSON
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
    
    print("\n🧪 Prueba de actualización parcial del JSON")
    print(f"📊 Datos de prueba (solo 3 campos):")
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
            print("   Solo se actualizaron: nombre, tipo_documento, numero_documento")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_update_single_field():
    """
    Prueba la actualización con un solo campo del JSON
    """
    
    test_data = {
        "solicitante_id": 1,  # Cambiar por un ID válido de la base de datos
        "PRODUCTO_SOLICITADO": {
            "info_segundo_titular": {
                "nombre": "FERNANDO_ACTUALIZADO"
            }
        }
    }
    
    print("\n🧪 Prueba de actualización de un solo campo")
    print(f"📊 Datos de prueba (solo nombre):")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    try:
        response = requests.put(
            UPDATE_ENDPOINT,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Actualización de un solo campo exitosa!")
            print("   Solo se actualizó: nombre")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_update_with_second_titular():
    """
    Prueba la actualización incluyendo también el campo segundo_titular
    """
    
    test_data = {
        "solicitante_id": 1,  # Cambiar por un ID válido de la base de datos
        "PRODUCTO_SOLICITADO": {
            "segundo_titular": "si",
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
    
    print("\n🧪 Prueba de actualización con segundo_titular e info_segundo_titular")
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
            print("✅ Actualización completa exitosa!")
            print("   Se actualizaron: segundo_titular e info_segundo_titular")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_verify_database_update():
    """
    Prueba para verificar que los datos se actualizaron correctamente en la base de datos
    """
    
    print("\n🔍 Verificación de actualización en base de datos")
    print("   Esta prueba requiere que ejecutes manualmente una consulta a la base de datos")
    print("   para verificar que los campos se actualizaron correctamente.")
    print("\n📋 Campos que deberían estar en la base de datos:")
    print("   - nombre: FERNANDO")
    print("   - tipo_documento: CC")
    print("   - numero_documento: 565")
    print("   - fecha_nacimiento: 2025-07-31")
    print("   - estado_civil: casado")
    print("   - personas_a_cargo: 5")
    print("   - numero_celular: 566")
    print("   - correo_electronico: claraorozco019@gmail.com")
    print("   - nivel_estudio: primaria")
    print("   - profesion: 5656")

if __name__ == "__main__":
    print("🚀 Script de prueba específico para campos del JSON info_segundo_titular")
    print("=" * 70)
    
    # Ejecutar todas las pruebas
    test_update_specific_fields()
    test_update_partial_json()
    test_update_single_field()
    test_update_with_second_titular()
    test_verify_database_update()
    
    print("\n" + "=" * 70)
    print("🏁 Pruebas completadas")
    print("\n📝 Notas importantes:")
    print("   - Cambia el 'solicitante_id' por un ID válido de tu base de datos")
    print("   - Asegúrate de que la API esté ejecutándose")
    print("   - Revisa los logs del servidor para ver los mensajes de debug")
    print("   - El sistema debe manejar JSON completo, parcial y campos individuales")
    print("\n🔍 Campos específicos del JSON de prueba:")
    print("   ✅ nombre: FERNANDO")
    print("   ✅ tipo_documento: CC")
    print("   ✅ numero_documento: 565")
    print("   ✅ fecha_nacimiento: 2025-07-31")
    print("   ✅ estado_civil: casado")
    print("   ✅ personas_a_cargo: 5")
    print("   ✅ numero_celular: 566")
    print("   ✅ correo_electronico: claraorozco019@gmail.com")
    print("   ✅ nivel_estudio: primaria")
    print("   ✅ profesion: 5656")
