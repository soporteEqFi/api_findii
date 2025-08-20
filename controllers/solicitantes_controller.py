from __future__ import annotations

from flask import request, jsonify
from models.solicitantes_model import SolicitantesModel
from models.ubicaciones_model import UbicacionesModel
from models.actividad_economica_model import ActividadEconomicaModel
from models.informacion_financiera_model import InformacionFinancieraModel
from models.referencias_model import ReferenciasModel
from models.solicitudes_model import SolicitudesModel
from utils.debug_helpers import (
    log_request_details, log_validation_results,
    log_data_to_save, log_operation_result, log_response, log_error
)


class SolicitantesController:
    def __init__(self):
        self.model = SolicitantesModel()
        self.ubicaciones_model = UbicacionesModel()
        self.actividad_model = ActividadEconomicaModel()
        self.financiera_model = InformacionFinancieraModel()
        self.referencias_model = ReferenciasModel()
        self.solicitudes_model = SolicitudesModel()

    def _empresa_id(self) -> int:
        empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
        if not empresa_id:
            raise ValueError("empresa_id es requerido")
        try:
            return int(empresa_id)
        except Exception as exc:
            raise ValueError("empresa_id debe ser entero") from exc

    def create(self):
        log_request_details("CREAR SOLICITANTE", "solicitantes")

        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}

            print(f"\n📋 EMPRESA ID: {empresa_id}")

            # Campos requeridos
            required_fields = [
                "nombres", "primer_apellido", "segundo_apellido",
                "tipo_identificacion", "numero_documento",
                "fecha_nacimiento", "genero", "correo"
            ]

            # Validar campos requeridos
            if not log_validation_results(required_fields, body):
                raise ValueError("Faltan campos requeridos")

            # Preparar datos para guardar
            datos_a_guardar = {
                "empresa_id": empresa_id,
                "nombres": body["nombres"],
                "primer_apellido": body["primer_apellido"],
                "segundo_apellido": body["segundo_apellido"],
                "tipo_identificacion": body["tipo_identificacion"],
                "numero_documento": body["numero_documento"],
                "fecha_nacimiento": body["fecha_nacimiento"],
                "genero": body["genero"],
                "correo": body["correo"],
                "info_extra": body.get("info_extra"),
            }

            log_data_to_save(datos_a_guardar)

            # Crear en BD
            data = self.model.create(**datos_a_guardar)

            log_operation_result(data, "SOLICITANTE CREADO")

            response_data = {"ok": True, "data": data}
            log_response(response_data)

            return jsonify(response_data), 201
        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def get_one(self, id: int):
        try:
            empresa_id = self._empresa_id()
            data = self.model.get_by_id(id=id, empresa_id=empresa_id)
            if not data:
                return jsonify({"ok": False, "error": "No encontrado"}), 404
            return jsonify({"ok": True, "data": data})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def list(self):
        try:
            empresa_id = self._empresa_id()
            limit = int(request.args.get("limit", 50))
            offset = int(request.args.get("offset", 0))
            data = self.model.list(empresa_id=empresa_id, limit=limit, offset=offset)
            return jsonify({"ok": True, "data": data})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def update(self, id: int):
        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}
            if not body:
                raise ValueError("Body requerido para actualizar")

            data = self.model.update(id=id, empresa_id=empresa_id, updates=body)
            return jsonify({"ok": True, "data": data})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def delete(self, id: int):
        try:
            empresa_id = self._empresa_id()
            deleted = self.model.delete(id=id, empresa_id=empresa_id)
            return jsonify({"ok": True, "deleted": deleted})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def crear_registro_completo(self):
        """Crear un registro completo: solicitante + ubicaciones + actividad económica + info financiera + referencias + solicitudes"""
        log_request_details("CREAR REGISTRO COMPLETO", "solicitante + todas las entidades relacionadas")

        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}

            print(f"\n📋 EMPRESA ID: {empresa_id}")
            print(f"\n📦 DATOS RECIBIDOS:")
            print(f"   Claves principales: {list(body.keys())}")

            # Extraer datos de cada entidad
            datos_solicitante = body.get("solicitante", {})
            datos_ubicaciones = body.get("ubicaciones", [])
            datos_actividad = body.get("actividad_economica", {})
            datos_financiera = body.get("informacion_financiera", {})
            datos_referencias = body.get("referencias", [])
            datos_solicitudes = body.get("solicitudes", [])

            print(f"\n🔍 DATOS EXTRAÍDOS:")
            print(f"   Solicitante: {len(datos_solicitante)} campos")
            print(f"   Ubicaciones: {len(datos_ubicaciones)} registros")
            print(f"   Actividad económica: {'✅ Presente' if datos_actividad else '❌ Vacío'}")
            print(f"   Info financiera: {'✅ Presente' if datos_financiera else '❌ Vacío'}")
            print(f"   Referencias: {len(datos_referencias)} registros")
            print(f"   Solicitudes: {len(datos_solicitudes)} registros")

            # 1. CREAR SOLICITANTE
            print(f"\n1️⃣ CREANDO SOLICITANTE...")
            if not datos_solicitante:
                raise ValueError("Datos del solicitante son requeridos")

            datos_solicitante["empresa_id"] = empresa_id
            print(f"   Datos a guardar: {datos_solicitante}")

            solicitante_creado = self.model.create(**datos_solicitante)
            solicitante_id = solicitante_creado["id"]
            print(f"   ✅ Solicitante creado con ID: {solicitante_id}")

            # 2. CREAR UBICACIONES
            ubicaciones_creadas = []
            if datos_ubicaciones:
                print(f"\n2️⃣ CREANDO UBICACIONES...")
                for idx, ubicacion_data in enumerate(datos_ubicaciones):
                    print(f"   Ubicación {idx + 1}: {ubicacion_data}")
                    ubicacion_data["empresa_id"] = empresa_id
                    ubicacion_data["solicitante_id"] = solicitante_id

                    ubicacion_creada = self.ubicaciones_model.create(**ubicacion_data)
                    ubicaciones_creadas.append(ubicacion_creada)
                    print(f"   ✅ Ubicación {idx + 1} creada con ID: {ubicacion_creada['id']}")
            else:
                print(f"\n2️⃣ UBICACIONES: No hay datos para crear")

            # 3. CREAR ACTIVIDAD ECONÓMICA
            actividad_creada = None
            if datos_actividad:
                print(f"\n3️⃣ CREANDO ACTIVIDAD ECONÓMICA...")
                print(f"   Datos: {datos_actividad}")
                datos_actividad["empresa_id"] = empresa_id
                datos_actividad["solicitante_id"] = solicitante_id

                actividad_creada = self.actividad_model.create(**datos_actividad)
                print(f"   ✅ Actividad económica creada con ID: {actividad_creada['id']}")
            else:
                print(f"\n3️⃣ ACTIVIDAD ECONÓMICA: No hay datos para crear")

            # 4. CREAR INFORMACIÓN FINANCIERA
            financiera_creada = None
            if datos_financiera:
                print(f"\n4️⃣ CREANDO INFORMACIÓN FINANCIERA...")
                print(f"   Datos: {datos_financiera}")
                datos_financiera["empresa_id"] = empresa_id
                datos_financiera["solicitante_id"] = solicitante_id

                financiera_creada = self.financiera_model.create(**datos_financiera)
                print(f"   ✅ Información financiera creada con ID: {financiera_creada['id']}")
            else:
                print(f"\n4️⃣ INFORMACIÓN FINANCIERA: No hay datos para crear")

            # 5. CREAR REFERENCIAS
            referencias_creadas = []
            if datos_referencias:
                print(f"\n5️⃣ CREANDO REFERENCIAS...")
                for idx, referencia_data in enumerate(datos_referencias):
                    print(f"   Referencia {idx + 1}: {referencia_data}")
                    referencia_data["empresa_id"] = empresa_id
                    referencia_data["solicitante_id"] = solicitante_id

                    referencia_creada = self.referencias_model.create(**referencia_data)
                    referencias_creadas.append(referencia_creada)
                    print(f"   ✅ Referencia {idx + 1} creada con ID: {referencia_creada['id']}")
            else:
                print(f"\n5️⃣ REFERENCIAS: No hay datos para crear")

            # 6. CREAR SOLICITUDES
            solicitudes_creadas = []
            if datos_solicitudes:
                print(f"\n6️⃣ CREANDO SOLICITUDES...")
                for idx, solicitud_data in enumerate(datos_solicitudes):
                    print(f"   Solicitud {idx + 1}: {solicitud_data}")

                    # Extraer banco desde detalle_credito (campo dinámico)
                    detalle_credito = solicitud_data.get("detalle_credito", {})
                    banco_nombre = None

                    # Buscar banco en diferentes ubicaciones posibles dentro de detalle_credito
                    if "banco" in detalle_credito:
                        banco_nombre = detalle_credito["banco"]
                    elif "tipo_credito_testeo" in detalle_credito:
                        tipo_credito = detalle_credito["tipo_credito_testeo"]
                        if "nombre_banco" in tipo_credito:
                            banco_nombre = tipo_credito["nombre_banco"]

                    print(f"   🏦 Banco extraído: {banco_nombre}")

                    # Preparar datos para el modelo
                    solicitud_data["empresa_id"] = empresa_id
                    solicitud_data["solicitante_id"] = solicitante_id
                    if banco_nombre:
                        solicitud_data["banco_nombre"] = banco_nombre

                    solicitud_creada = self.solicitudes_model.create(**solicitud_data)
                    solicitudes_creadas.append(solicitud_creada)
                    print(f"   ✅ Solicitud {idx + 1} creada con ID: {solicitud_creada['id']}")
            else:
                print(f"\n6️⃣ SOLICITUDES: No hay datos para crear")

            # 7. PREPARAR RESPUESTA
            print(f"\n🔗 PREPARANDO RESPUESTA FINAL...")
            response_data = {
                "ok": True,
                "data": {
                    "solicitante": solicitante_creado,
                    "ubicaciones": ubicaciones_creadas,
                    "actividad_economica": actividad_creada,
                    "informacion_financiera": financiera_creada,
                    "referencias": referencias_creadas,
                    "solicitudes": solicitudes_creadas,
                    "resumen": {
                        "solicitante_id": solicitante_id,
                        "total_ubicaciones": len(ubicaciones_creadas),
                        "tiene_actividad_economica": bool(actividad_creada),
                        "tiene_informacion_financiera": bool(financiera_creada),
                        "total_referencias": len(referencias_creadas),
                        "total_solicitudes": len(solicitudes_creadas)
                    }
                },
                "message": f"Registro completo creado exitosamente. Solicitante ID: {solicitante_id}"
            }

            print(f"\n📊 RESUMEN FINAL:")
            print(f"   👤 Solicitante: {solicitante_id}")
            print(f"   📍 Ubicaciones: {len(ubicaciones_creadas)}")
            print(f"   💼 Actividad económica: {'✅' if actividad_creada else '❌'}")
            print(f"   💰 Info financiera: {'✅' if financiera_creada else '❌'}")
            print(f"   👥 Referencias: {len(referencias_creadas)}")
            print(f"   📄 Solicitudes: {len(solicitudes_creadas)}")

            log_response(response_data)
            return jsonify(response_data), 201

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def traer_todos_registros(self, solicitante_id: int):
        """Trae toda la información combinada de un solicitante incluyendo campos dinámicos"""
        log_request_details("TRAER TODOS REGISTROS", f"solicitante_id={solicitante_id}")

        try:
            empresa_id = self._empresa_id()
            print(f"\n📋 EMPRESA ID: {empresa_id}")
            print(f"🔍 SOLICITANTE ID: {solicitante_id}")

            # 1. Obtener datos del solicitante principal
            print(f"\n1️⃣ OBTENIENDO SOLICITANTE...")
            solicitante = self.model.get_by_id(id=solicitante_id, empresa_id=empresa_id)
            if not solicitante:
                return jsonify({"ok": False, "error": "Solicitante no encontrado"}), 404
            print(f"   ✅ Solicitante encontrado: {solicitante.get('nombres', 'N/A')} {solicitante.get('primer_apellido', 'N/A')}")

            # 2. Obtener ubicaciones
            print(f"\n2️⃣ OBTENIENDO UBICACIONES...")
            try:
                ubicaciones = self.ubicaciones_model.list(empresa_id=empresa_id, solicitante_id=solicitante_id)
                print(f"   📍 Ubicaciones encontradas: {len(ubicaciones) if ubicaciones else 0}")
            except Exception as e:
                print(f"   ❌ Error obteniendo ubicaciones: {e}")
                ubicaciones = []

            # 3. Obtener actividad económica
            print(f"\n3️⃣ OBTENIENDO ACTIVIDAD ECONÓMICA...")
            try:
                actividad_economica_list = self.actividad_model.list(empresa_id=empresa_id, solicitante_id=solicitante_id)
                actividad_economica = actividad_economica_list[0] if actividad_economica_list else None
                print(f"   💼 Actividad económica: {'✅ Encontrada' if actividad_economica else '❌ No encontrada'}")
            except Exception as e:
                print(f"   ❌ Error obteniendo actividad económica: {e}")
                actividad_economica = None

            # 4. Obtener información financiera
            print(f"\n4️⃣ OBTENIENDO INFORMACIÓN FINANCIERA...")
            try:
                financiera_list = self.financiera_model.list(empresa_id=empresa_id, solicitante_id=solicitante_id)
                informacion_financiera = financiera_list[0] if financiera_list else None
                print(f"   💰 Información financiera: {'✅ Encontrada' if informacion_financiera else '❌ No encontrada'}")
            except Exception as e:
                print(f"   ❌ Error obteniendo información financiera: {e}")
                informacion_financiera = None

            # 5. Obtener referencias
            print(f"\n5️⃣ OBTENIENDO REFERENCIAS...")
            try:
                referencias = self.referencias_model.list(empresa_id=empresa_id, solicitante_id=solicitante_id)
                print(f"   👥 Referencias encontradas: {len(referencias) if referencias else 0}")
            except Exception as e:
                print(f"   ❌ Error obteniendo referencias: {e}")
                referencias = []

            # 6. Obtener solicitudes
            print(f"\n6️⃣ OBTENIENDO SOLICITUDES...")
            try:
                solicitudes = self.solicitudes_model.list(empresa_id=empresa_id, solicitante_id=solicitante_id)
                print(f"   📄 Solicitudes encontradas: {len(solicitudes) if solicitudes else 0}")
            except Exception as e:
                print(f"   ❌ Error obteniendo solicitudes: {e}")
                solicitudes = []

            # 7. Combinar toda la información
            print(f"\n🔗 COMBINANDO INFORMACIÓN...")
            datos_completos = {
                "solicitante": solicitante,
                "ubicaciones": ubicaciones or [],
                "actividad_economica": actividad_economica,
                "informacion_financiera": informacion_financiera,
                "referencias": referencias or [],
                "solicitudes": solicitudes or [],
                "resumen": {
                    "total_ubicaciones": len(ubicaciones) if ubicaciones else 0,
                    "tiene_actividad_economica": bool(actividad_economica),
                    "tiene_informacion_financiera": bool(informacion_financiera),
                    "total_referencias": len(referencias) if referencias else 0,
                    "total_solicitudes": len(solicitudes) if solicitudes else 0
                }
            }

            print(f"\n📊 RESUMEN DE DATOS:")
            print(f"   👤 Solicitante: {solicitante.get('nombres', 'N/A')}")
            print(f"   📍 Ubicaciones: {datos_completos['resumen']['total_ubicaciones']}")
            print(f"   💼 Actividad económica: {datos_completos['resumen']['tiene_actividad_economica']}")
            print(f"   💰 Info financiera: {datos_completos['resumen']['tiene_informacion_financiera']}")
            print(f"   👥 Referencias: {datos_completos['resumen']['total_referencias']}")
            print(f"   📄 Solicitudes: {datos_completos['resumen']['total_solicitudes']}")

            response_data = {"ok": True, "data": datos_completos}
            log_response(response_data)

            return jsonify(response_data)

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500
