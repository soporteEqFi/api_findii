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
import json
import os
import uuid
from werkzeug.utils import secure_filename
from data.supabase_conn import supabase
from models.documentos_model import DocumentosModel


class SolicitantesController:
    def __init__(self):
        self.model = SolicitantesModel()
        self.ubicaciones_model = UbicacionesModel()
        self.actividad_model = ActividadEconomicaModel()
        self.financiera_model = InformacionFinancieraModel()
        self.referencias_model = ReferenciasModel()
        self.solicitudes_model = SolicitudesModel()
        self.documentos_model = DocumentosModel()

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

            # Soportar JSON puro y multipart/form-data con 'payload' + archivos
            content_type = request.content_type or ""
            if "multipart/form-data" in content_type:
                print(f"   📨 Content-Type recibido: {content_type}")
                try:
                    print(f"   📝 Form keys: {list(request.form.keys())}")
                    print(f"   📁 Files keys: {list(request.files.keys())}")
                except Exception as _e:
                    print(f"   ⚠️ No se pudieron listar keys de form/files: {_e}")
                raw_payload = request.form.get("payload")
                body = json.loads(raw_payload) if raw_payload else {}
                # Recolectar posibles campos de archivos enviados
                files_list = []
                for key in [
                    "documentos", "documentos[]", "files", "files[]", "file"
                ]:
                    if key in request.files:
                        # getlist también funciona para una sola entrada
                        files_list.extend(request.files.getlist(key))
                print(f"   📎 Archivos recibidos (multipart): {len(files_list)}")
            else:
                print(f"   📨 Content-Type recibido: {content_type} (sin multipart, no hay archivos)")
                body = request.get_json(silent=True) or {}
                files_list = []

            print(f"\n📋 EMPRESA ID: {empresa_id}")
            print(f"\n📦 DATOS RECIBIDOS:")
            print(f"   Claves principales: {list(body.keys())}")

            # Extraer datos de cada entidad
            datos_solicitante = body.get("solicitante", {})
            print(f"   🔍 Body completo: {body}")
            print(f"   🔍 Claves en body: {list(body.keys())}")
            print(f"   🔍 datos_solicitante: {datos_solicitante}")
            print(f"   🔍 Tipo datos_solicitante: {type(datos_solicitante)}")

            # Manejar ubicaciones (puede ser objeto o lista)
            ubicacion_obj = body.get("ubicacion", {})
            ubicaciones_list = body.get("ubicaciones", [])
            datos_ubicaciones = [ubicacion_obj] if ubicacion_obj else ubicaciones_list

            datos_actividad = body.get("actividad_economica", {})
            datos_financiera = body.get("informacion_financiera", {})

            # Manejar referencias (puede ser objeto o lista)
            referencia_obj = body.get("referencia", {})
            referencias_list = body.get("referencias", [])
            datos_referencias = [referencia_obj] if referencia_obj else referencias_list

            # Manejar solicitudes (puede ser objeto o lista)
            solicitud_obj = body.get("solicitud", {})
            solicitudes_list = body.get("solicitudes", [])
            datos_solicitudes = [solicitud_obj] if solicitud_obj else solicitudes_list

            print(f"\n🔍 DATOS EXTRAÍDOS:")
            print(f"   Solicitante: {len(datos_solicitante)} campos")
            print(f"   Ubicaciones: {len(datos_ubicaciones)} registros")
            print(f"   Actividad económica: {'✅ Presente' if datos_actividad else '❌ Vacío'}")
            print(f"   Info financiera: {'✅ Presente' if datos_financiera else '❌ Vacío'}")
            print(f"   Referencias: {len(datos_referencias)} registros")
            print(f"   Solicitudes: {len(datos_solicitudes)} registros")

            # Debug: mostrar qué se encontró
            if ubicacion_obj:
                print(f"   📍 Ubicación encontrada como objeto")
            if referencia_obj:
                print(f"   👥 Referencia encontrada como objeto")
            if solicitud_obj:
                print(f"   📋 Solicitud encontrada como objeto")

            # 1. CREAR SOLICITANTE
            print(f"\n1️⃣ CREANDO SOLICITANTE...")
            if not datos_solicitante or len(datos_solicitante) == 0:
                raise ValueError("Datos del solicitante son requeridos")

            datos_solicitante["empresa_id"] = empresa_id
            print(f"   Datos a guardar: {datos_solicitante}")

            solicitante_creado = self.model.create(**datos_solicitante)
            solicitante_id = solicitante_creado["id"]
            print(f"   ✅ Solicitante creado con ID: {solicitante_id}")

            # 1.b SUBIR DOCUMENTOS (si vinieron en multipart)
            documentos_creados = []
            if files_list:
                print(f"\n1️⃣b SUBIENDO DOCUMENTOS ({len(files_list)})...")
                storage = supabase.storage.from_("document")
                for idx, file in enumerate(files_list):
                    try:
                        original_name = secure_filename(file.filename or f"documento_{idx+1}")
                        ext = os.path.splitext(original_name)[1]
                        unique_name = f"{uuid.uuid4().hex}{ext}" if ext else uuid.uuid4().hex
                        storage_path = f"solicitantes/{solicitante_id}/{unique_name}"

                        content_type = getattr(file, "mimetype", None) or "application/octet-stream"
                        file_bytes = file.read()
                        storage.upload(
                            storage_path,
                            file_bytes,
                            file_options={
                                "content-type": content_type,
                                "upsert": "true",
                            },
                        )

                        public_url_resp = storage.get_public_url(storage_path)
                        public_url = None
                        if isinstance(public_url_resp, dict):
                            public_url = public_url_resp.get("publicUrl") or (
                                public_url_resp.get("data", {}) if isinstance(public_url_resp.get("data"), dict) else {}
                            ).get("publicUrl")
                        elif hasattr(public_url_resp, "data"):
                            data_dict = getattr(public_url_resp, "data", {})
                            if isinstance(data_dict, dict):
                                public_url = data_dict.get("publicUrl")
                        if not public_url:
                            public_url = str(public_url_resp)

                        doc_saved = self.documentos_model.create(
                            nombre=original_name,
                            documento_url=public_url,
                            solicitante_id=solicitante_id,
                        )
                        documentos_creados.append(doc_saved)
                        print(f"   ✅ Documento subido: {original_name}")
                    except Exception as e:
                        print(f"   ❌ Error subiendo documento {idx+1}: {e}")
                print(f"   📊 Total documentos subidos y guardados: {len(documentos_creados)}")

            # 2. CREAR UBICACIONES
            ubicaciones_creadas = []
            if datos_ubicaciones:
                print(f"\n2️⃣ CREANDO UBICACIONES...")
                for idx, ubicacion_data in enumerate(datos_ubicaciones):
                    print(f"   Ubicación {idx + 1} original: {ubicacion_data}")

                    # Procesar campos dinámicos para ubicaciones
                    detalle_direccion = ubicacion_data.get("detalle_direccion", {})

                    # Mover campos que están en la raíz pero deben ir en detalle_direccion
                    # NOTA: ciudad_residencia y departamento_residencia son campos fijos, NO se mueven
                    campos_para_mover = [
                        "direccion", "direccion_residencia", "tipo_direccion", "barrio", "estrato",
                        "telefono", "celular", "correo_personal", "recibir_correspondencia",
                        "tipo_vivienda", "paga_arriendo", "valor_mensual_arriendo", "arrendador",
                        "id_autenticacion"
                    ]
                    for campo in campos_para_mover:
                        if campo in ubicacion_data:
                            detalle_direccion[campo] = ubicacion_data.pop(campo)
                            print(f"   🔄 Movido '{campo}' a detalle_direccion")

                    # Actualizar ubicacion_data con detalle_direccion procesado
                    ubicacion_data["detalle_direccion"] = detalle_direccion

                    print(f"   Ubicación {idx + 1} procesada: {ubicacion_data}")
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
                print(f"   Datos originales: {datos_actividad}")

                # Procesar campos dinámicos para actividad económica
                detalle_actividad = datos_actividad.get("detalle_actividad", {})

                # Mover campos que están en la raíz pero deben ir en detalle_actividad
                campos_para_mover = ["tipo_actividad", "tipo_actividad_economica"]
                for campo in campos_para_mover:
                    if campo in datos_actividad:
                        detalle_actividad[campo] = datos_actividad.pop(campo)
                        print(f"   🔄 Movido '{campo}' a detalle_actividad")

                # Actualizar datos_actividad con detalle_actividad procesado
                datos_actividad["detalle_actividad"] = detalle_actividad

                print(f"   Datos procesados: {datos_actividad}")
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
                print(f"   Datos originales: {datos_financiera}")

                # Procesar campos dinámicos para información financiera
                detalle_financiera = datos_financiera.get("detalle_financiera", {})

                # Mover campos que están en la raíz pero deben ir en detalle_financiera
                campos_para_mover = [
                    "ingreso_basico_mensual", "ingreso_variable_mensual", "otros_ingresos_mensuales",
                    "gastos_financieros_mensuales", "gastos_personales_mensuales", "ingresos_fijos_pension",
                    "ingresos_por_ventas", "ingresos_varios", "honorarios", "arriendos",
                    "ingresos_actividad_independiente", "detalle_otros_ingresos", "declara_renta"
                ]
                for campo in campos_para_mover:
                    if campo in datos_financiera:
                        detalle_financiera[campo] = datos_financiera.pop(campo)
                        print(f"   🔄 Movido '{campo}' a detalle_financiera")

                # Actualizar datos_financiera con detalle_financiera procesado
                datos_financiera["detalle_financiera"] = detalle_financiera

                print(f"   Datos procesados: {datos_financiera}")
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
                    print(f"   Referencia {idx + 1} original: {referencia_data}")

                    # Procesar campos dinámicos para referencias
                    detalle_referencia = referencia_data.get("detalle_referencia", {})

                    # Mover campos que están en la raíz pero deben ir en detalle_referencia
                    # NOTA: tipo_referencia es campo fijo, NO se mueve
                    campos_para_mover = [
                        "nombre_completo", "telefono", "celular_referencia", "relacion_referencia",
                        "nombre", "ciudad", "departamento", "direccion"
                    ]
                    for campo in campos_para_mover:
                        if campo in referencia_data:
                            detalle_referencia[campo] = referencia_data.pop(campo)
                            print(f"   🔄 Movido '{campo}' a detalle_referencia")

                    # Actualizar referencia_data con detalle_referencia procesado
                    referencia_data["detalle_referencia"] = detalle_referencia

                    print(f"   Referencia {idx + 1} procesada: {referencia_data}")
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

                    # Extraer banco y ciudad desde detalle_credito (campos dinámicos)
                    detalle_credito = solicitud_data.get("detalle_credito", {})
                    banco_nombre = None
                    ciudad = None

                    # Buscar banco en la raíz del JSON detalle_credito
                    banco_nombre = detalle_credito.get("banco")
                    ciudad = detalle_credito.get("ciudad_solicitud")

                    print(f"   🏦 Banco extraído: {banco_nombre}")
                    print(f"   🏙️ Ciudad extraída: {ciudad}")

                    # Asegurar que el banco y ciudad estén en la raíz del JSON
                    if banco_nombre:
                        detalle_credito["banco"] = banco_nombre
                    if ciudad:
                        detalle_credito["ciudad_solicitud"] = ciudad

                    # Obtener user_id del header
                    user_id = request.headers.get("X-User-Id")
                    if not user_id:
                        raise ValueError("X-User-Id header es requerido para crear solicitudes")

                    # Preparar datos para el modelo (solo campos que acepta el modelo)
                    datos_para_modelo = {
                        "empresa_id": empresa_id,
                        "solicitante_id": solicitante_id,
                        "created_by_user_id": int(user_id),
                        "estado": solicitud_data.get("estado", "Pendiente"),
                        "detalle_credito": detalle_credito
                    }

                    # Agregar campos opcionales solo si están presentes
                    if banco_nombre:
                        datos_para_modelo["banco_nombre"] = banco_nombre
                    if ciudad:
                        datos_para_modelo["ciudad"] = ciudad  # El modelo espera 'ciudad', no 'ciudad_solicitud'

                    solicitud_creada = self.solicitudes_model.create(**datos_para_modelo)
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
                    "documentos": documentos_creados,
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

            # 1. Obtener datos del solicitante principal
            solicitante = self.model.get_by_id(id=solicitante_id, empresa_id=empresa_id)
            if not solicitante:
                return jsonify({"ok": False, "error": "Solicitante no encontrado"}), 404

            # 2. Obtener ubicaciones
            try:
                ubicaciones = self.ubicaciones_model.list(empresa_id=empresa_id, solicitante_id=solicitante_id)
            except Exception as e:
                ubicaciones = []

            # 3. Obtener actividad económica
            try:
                actividad_economica_list = self.actividad_model.list(empresa_id=empresa_id, solicitante_id=solicitante_id)
                actividad_economica = actividad_economica_list[0] if actividad_economica_list else None
            except Exception as e:
                actividad_economica = None

            # 4. Obtener información financiera
            try:
                financiera_list = self.financiera_model.list(empresa_id=empresa_id, solicitante_id=solicitante_id)
                informacion_financiera = financiera_list[0] if financiera_list else None
            except Exception as e:
                print(f"   ❌ Error obteniendo información financiera: {e}")
                informacion_financiera = None

            # 5. Obtener referencias
            try:
                referencias = self.referencias_model.list(empresa_id=empresa_id, solicitante_id=solicitante_id)
            except Exception as e:
                print(f"   ❌ Error obteniendo referencias: {e}")
                referencias = []

            # 6. Obtener solicitudes
            try:
                solicitudes = self.solicitudes_model.list(empresa_id=empresa_id, solicitante_id=solicitante_id)
            except Exception as e:
                print(f"   ❌ Error obteniendo solicitudes: {e}")
                solicitudes = []

            # 7. Obtener documentos
            try:
                documentos = self.documentos_model.list(solicitante_id=solicitante_id)
            except Exception as e:
                print(f"   ❌ Error obteniendo documentos: {e}")
                documentos = []

            # 8. Combinar toda la información
            datos_completos = {
                "solicitante": solicitante,
                "ubicaciones": ubicaciones or [],
                "actividad_economica": actividad_economica,
                "informacion_financiera": informacion_financiera,
                "referencias": referencias or [],
                "solicitudes": solicitudes or [],
                "documentos": documentos or [],
                "resumen": {
                    "total_ubicaciones": len(ubicaciones) if ubicaciones else 0,
                    "tiene_actividad_economica": bool(actividad_economica),
                    "tiene_informacion_financiera": bool(informacion_financiera),
                    "total_referencias": len(referencias) if referencias else 0,
                    "total_solicitudes": len(solicitudes) if solicitudes else 0,
                    "total_documentos": len(documentos) if documentos else 0
                }
            }

            response_data = {"ok": True, "data": datos_completos}
            log_response(response_data)

            return jsonify(response_data)

        except ValueError as ve:
            log_error(ve, "ERROR DE VALIDACIÓN")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            log_error(ex, "ERROR INESPERADO")
            return jsonify({"ok": False, "error": str(ex)}), 500
