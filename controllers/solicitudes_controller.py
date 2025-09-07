from __future__ import annotations

from flask import request, jsonify
from models.solicitudes_model import SolicitudesModel
from models.json_schema_model import JSONSchemaModel
from models.configuraciones_model import ConfiguracionesModel


class SolicitudesController:
    def __init__(self):
        self.model = SolicitudesModel()
        self.schema_model = JSONSchemaModel()
        self.config_model = ConfiguracionesModel()

    def _empresa_id(self) -> int:
        empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
        if not empresa_id:
            raise ValueError("empresa_id es requerido")
        try:
            return int(empresa_id)
        except Exception as exc:  # noqa: B902
            raise ValueError("empresa_id debe ser entero") from exc

    def _obtener_usuario_autenticado(self):
        """Obtener información del usuario autenticado desde la base de datos"""
        try:
            # Obtener el token del header Authorization
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None

            # Por ahora, usaremos un header personalizado para el user_id
            # En una implementación real, decodificarías el JWT aquí
            user_id = request.headers.get("X-User-Id")
            if not user_id:
                return None

            # Consultar la base de datos para obtener información completa del usuario
            from data.supabase_conn import supabase

            user_response = supabase.table("usuarios").select("id, rol, info_extra").eq("id", int(user_id)).execute()
            user_data = user_response.data[0] if user_response.data else None

            if not user_data:
                return None

            # Extraer banco_nombre y ciudad del info_extra del usuario
            info_extra_raw = user_data.get("info_extra", {})

            # Parsear info_extra si es string JSON
            if isinstance(info_extra_raw, str):
                import json
                try:
                    info_extra = json.loads(info_extra_raw)
                except json.JSONDecodeError:
                    info_extra = {}
            else:
                info_extra = info_extra_raw

            banco_nombre = info_extra.get("banco_nombre")
            ciudad_solicitud = info_extra.get("ciudad")  # En la BD está como "ciudad"

            print(f"🔍 INFO USUARIO:")
            print(f"   👤 User ID: {user_data['id']}")
            print(f"   🏷️ Rol: {user_data.get('rol', 'empresa')}")
            print(f"   📋 Info Extra Raw: {info_extra_raw}")
            print(f"   📋 Info Extra Parsed: {info_extra}")
            print(f"   🏦 Banco extraído: {banco_nombre}")
            print(f"   🏙️ Ciudad extraída: {ciudad_solicitud}")

            return {
                "id": user_data["id"],
                "rol": user_data.get("rol", "empresa"),
                "banco_nombre": banco_nombre,  # Desde info_extra del usuario
                "ciudad_solicitud": ciudad_solicitud  # Desde info_extra del usuario
            }
        except Exception as e:
            print(f"Error obteniendo usuario autenticado: {e}")
            return None

    def _aplicar_filtros_por_rol(self, query, usuario_info):
        """Aplicar filtros de permisos basados en el rol del usuario"""
        if not usuario_info:
            return query

        rol = usuario_info.get("rol")

        if rol == "admin":
            # Admin ve todas las solicitudes de la empresa
            return query
        elif rol == "banco":
            # Usuario banco solo ve solicitudes de su banco y ciudad
            banco_nombre = usuario_info.get("banco_nombre")
            ciudad_solicitud = usuario_info.get("ciudad_solicitud")

            if banco_nombre:
                query = query.eq("banco_nombre", banco_nombre)
            else:
                # Si no tiene banco asignado, no ve nada
                return query.eq("id", -1)  # Query imposible

            # Aplicar filtro de ciudad_solicitud si está disponible
            if ciudad_solicitud:
                query = query.eq("ciudad_solicitud", ciudad_solicitud)
                print(f"   🏙️ Aplicando filtro de ciudad_solicitud: {ciudad_solicitud}")
            else:
                print(f"   ⚠️ Usuario banco no tiene ciudad_solicitud asignada")

            return query
        else:
            # Rol desconocido, no ve nada
            return query.eq("id", -1)  # Query imposible

    def obtener_bancos_disponibles(self):
        """Obtener lista de bancos desde tabla configuraciones"""
        try:
            empresa_id = self._empresa_id()

            bancos = self.config_model.obtener_por_categoria(
                empresa_id=empresa_id,
                categoria="bancos"
            )

            print(f"   📋 Bancos encontrados: {bancos}")

            return jsonify({
                "ok": True,
                "data": {
                    "bancos": bancos,
                    "total": len(bancos)
                },
                "message": f"Se encontraron {len(bancos)} bancos disponibles"
            })

        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500

    def obtener_ciudades_disponibles(self):
        """Obtener lista de ciudades desde tabla configuraciones"""
        try:
            empresa_id = self._empresa_id()

            ciudades = self.config_model.obtener_por_categoria(
                empresa_id=empresa_id,
                categoria="ciudades"
            )

            print(f"   📋 Ciudades encontradas: {ciudades}")

            return jsonify({
                "ok": True,
                "data": {
                    "ciudades": ciudades,
                    "total": len(ciudades)
                },
                "message": f"Se encontraron {len(ciudades)} ciudades disponibles"
            })

        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500

    def obtener_estados_disponibles(self):
        """Obtener lista de estados desde tabla configuraciones"""
        try:
            empresa_id = self._empresa_id()

            estados = self.config_model.obtener_por_categoria(
                empresa_id=empresa_id,
                categoria="estados"
            )

            print(f"   📋 Estados encontrados: {estados}")

            return jsonify({
                "ok": True,
                "data": {
                    "estados": estados,
                    "total": len(estados)
                },
                "message": f"Se encontraron {len(estados)} estados disponibles"
            })

        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500

    # CRUD
    def create(self):
        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}
            usuario_info = self._obtener_usuario_autenticado()

            # Extraer banco y ciudad desde campos fijos (raíz del objeto solicitud)
            banco_nombre = body.get("banco_nombre")
            ciudad = body.get("ciudad_solicitud")
            detalle_credito = body.get("detalle_credito", {})
            observacion_inicial = body.get("observacion")

            if not banco_nombre:
                return jsonify({"ok": False, "error": "banco_nombre es requerido"}), 400

            if not ciudad:
                return jsonify({"ok": False, "error": "ciudad_solicitud es requerida"}), 400

            # Validar que el banco existe en los campos dinámicos (opcional)
            bancos_disponibles = self._obtener_bancos_validos(empresa_id)

            if bancos_disponibles and banco_nombre not in bancos_disponibles:
                print(f"   ⚠️ Banco '{banco_nombre}' no está en la lista de bancos disponibles")
                print(f"   📋 Bancos válidos: {bancos_disponibles}")

            # Validar que la ciudad existe en los campos dinámicos (opcional)
            ciudades_disponibles = self._obtener_ciudades_validas(empresa_id)

            if ciudades_disponibles and ciudad not in ciudades_disponibles:
                print(f"   ⚠️ Ciudad '{ciudad}' no está en la lista de ciudades disponibles")
                print(f"   📋 Ciudades válidas: {ciudades_disponibles}")

            print(f"\n📝 CREANDO SOLICITUD:")
            print(f"   📋 Empresa ID: {empresa_id}")
            print(f"   🏦 Banco: {banco_nombre}")
            print(f"   🏙️ Ciudad: {ciudad}")
            if observacion_inicial:
                print(f"   📝 Observación inicial: {observacion_inicial[:50]}...")

            data = self.model.create(
                empresa_id=empresa_id,
                solicitante_id=body.get("solicitante_id"),
                created_by_user_id=body.get("created_by_user_id"),
                assigned_to_user_id=body.get("assigned_to_user_id"),
                banco_nombre=banco_nombre,
                ciudad_solicitud=ciudad,
                estado=body.get("estado"),
                detalle_credito=detalle_credito,
                observacion_inicial=observacion_inicial,
                usuario_info=usuario_info
            )

            print(f"   ✅ Solicitud creada con ID: {data.get('id')}")
            return jsonify({"ok": True, "data": data}), 201
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500

    def _obtener_bancos_validos(self, empresa_id: int) -> list:
        """Método interno para obtener bancos válidos desde tabla configuraciones"""
        try:
            return self.config_model.obtener_por_categoria(
                empresa_id=empresa_id,
                categoria="bancos"
            )
        except Exception:
            return []

    def _obtener_ciudades_validas(self, empresa_id: int):
        """Método interno para obtener ciudades válidas desde tabla configuraciones"""
        try:
            ciudades = self.config_model.obtener_por_categoria(
                empresa_id=empresa_id,
                categoria="ciudades"
            )
            return [c.get("valor") for c in ciudades if c.get("valor")]
        except Exception:
            return []

    def _procesar_archivos_en_campos(self, data: dict) -> dict:
        """Procesa los campos de tipo 'file' en los datos dinámicos

        Args:
            data: Diccionario con los datos a procesar

        Returns:
            Diccionario con las URLs de los archivos reemplazando los objetos de archivo
        """
        if not isinstance(data, dict):
            return data

        from data.supabase_conn import supabase
        from datetime import datetime
        import os

        for key, value in list(data.items()):
            # Si el campo es un diccionario con propiedades de archivo
            if isinstance(value, dict) and value.get('type', '').startswith('image/'):
                try:
                    # Generar un nombre único para el archivo
                    timestamp = int(datetime.utcnow().timestamp() * 1000)
                    ext = value.get('name', '').split('.')[-1] if '.' in value.get('name', '') else 'bin'
                    file_name = f"{key}_{timestamp}.{ext}"

                    # Subir el archivo a Supabase Storage
                    file_path = f"empresas/{self._empresa_id()}/documentos/{file_name}"

                    # Convertir el base64 a bytes y subirlo
                    file_data = value.get('base64', '').split('base64,')[-1]
                    import base64
                    file_bytes = base64.b64decode(file_data)

                    # Subir el archivo
                    supabase.storage.from_("documentos").upload(
                        path=file_path,
                        file=file_bytes,
                        file_options={"content-type": value.get('type', 'application/octet-stream')}
                    )

                    # Obtener la URL pública
                    url = supabase.storage.from_("documentos").get_public_url(file_path)

                    # Reemplazar el objeto de archivo por la URL
                    data[key] = url

                except Exception as e:
                    print(f"Error procesando archivo {key}: {str(e)}")
                    data[key] = None

            # Si el valor es un diccionario o lista, procesar recursivamente
            elif isinstance(value, dict):
                data[key] = self._procesar_archivos_en_campos(value)
            elif isinstance(value, list):
                data[key] = [self._procesar_archivos_en_campos(item) if isinstance(item, dict) else item for item in value]

        return data

    def get_one(self, id: int):
        try:
            empresa_id = self._empresa_id()

            # Obtener información del usuario autenticado
            usuario_info = self._obtener_usuario_autenticado()

            data = self.model.get_by_id_con_filtros_rol(
                id=id,
                empresa_id=empresa_id,
                usuario_info=usuario_info
            )

            if not data:
                return jsonify({"ok": False, "error": "No encontrado o sin permisos"}), 404
            return jsonify({"ok": True, "data": data})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500

    def list(self):
        try:
            empresa_id = self._empresa_id()
            estado = request.args.get("estado")
            solicitante_id = request.args.get("solicitante_id")
            solicitante_id = int(solicitante_id) if solicitante_id else None
            limit = int(request.args.get("limit", 50))
            offset = int(request.args.get("offset", 0))

            # Obtener información del usuario autenticado
            usuario_info = self._obtener_usuario_autenticado()

            print(f"\n📋 LISTANDO SOLICITUDES:")
            print(f"   📋 Empresa ID: {empresa_id}")
            print(f"   👤 Usuario: {usuario_info}")
            print(f"   🔍 Filtros: estado={estado}, solicitante_id={solicitante_id}")

            # Aplicar filtros de permisos por rol (incluye filtro de ciudad automáticamente)
            data = self.model.list_con_filtros_rol(
                empresa_id=empresa_id,
                usuario_info=usuario_info,
                estado=estado,
                solicitante_id=solicitante_id,
                limit=limit,
                offset=offset,
            )

            print(f"   📄 Solicitudes encontradas: {len(data)}")
            return jsonify({"ok": True, "data": data})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500

    def update(self, id: int):
        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}

            # Handle observaciones if present
            observaciones = body.pop('observaciones', None)

            base_updates = {}
            for field in [
                "estado",
                "assigned_to_user_id",
                "banco_nombre",
                "ciudad_solicitud",
            ]:
                if field in body:
                    base_updates[field] = body[field]

            print(f"\n📝 ACTUALIZANDO SOLICITUD {id}:")
            print(f"   📋 Empresa ID: {empresa_id}")
            print(f"   🔄 Campos a actualizar: {list(base_updates.keys())}")
            if observaciones:
                print(f"   📝 Incluye {len(observaciones)} observaciones")

            detalle_credito_merge = body.get("detalle_credito")

            # Procesar archivos en los campos dinámicos
            if detalle_credito_merge:
                detalle_credito_merge = self._procesar_archivos_en_campos(detalle_credito_merge)

            # Si hay observaciones, procesarlas primero
            if observaciones and isinstance(observaciones, list):
                for obs in observaciones:
                    self.model.agregar_observacion_simple(
                        id=id,
                        observacion=obs
                    )

            # Realizar la actualización normal
            data = self.model.update(
                id=id,
                empresa_id=empresa_id,
                base_updates=base_updates or None,
                detalle_credito_merge=detalle_credito_merge,
            )

            print(f"   ✅ Solicitud actualizada")
            return jsonify({"ok": True, "data": data})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500

    def delete(self, id: int):
        """Eliminar solicitud y todos los registros relacionados del solicitante"""
        try:
            empresa_id = self._empresa_id()
            print(f"🗑️ DELETE request para solicitud: id={id}, empresa_id={empresa_id}")

            # Verificar que la solicitud existe antes de eliminar
            solicitud_existente = self.model.get_by_id(id=id, empresa_id=empresa_id)
            if not solicitud_existente:
                print(f"❌ Solicitud {id} no encontrada en empresa {empresa_id}")
                return jsonify({
                    "ok": False,
                    "error": f"Solicitud {id} no encontrada",
                    "deleted": 0
                }), 404

            solicitante_id = solicitud_existente.get('solicitante_id')
            print(f"✅ Solicitud encontrada: estado={solicitud_existente.get('estado')}, banco={solicitud_existente.get('banco_nombre')}")
            print(f"📋 Eliminando solicitante_id: {solicitante_id}")

            # Importar modelos para eliminar registros relacionados
            from models.documentos_model import DocumentosModel
            from models.referencias_model import ReferenciasModel
            from models.informacion_financiera_model import InformacionFinancieraModel
            from models.actividad_economica_model import ActividadEconomicaModel
            from models.ubicaciones_model import UbicacionesModel
            from models.solicitantes_model import SolicitantesModel

            # Contadores para el reporte
            eliminados = {
                "solicitud": 0,
                "documentos": 0,
                "referencias": 0,
                "informacion_financiera": 0,
                "actividad_economica": 0,
                "ubicaciones": 0,
                "solicitante": 0
            }

            try:
                # 1. Eliminar documentos
                documentos_model = DocumentosModel()
                eliminados["documentos"] = documentos_model.delete_by_solicitante(solicitante_id=solicitante_id, empresa_id=empresa_id)
                print(f"   📄 Documentos eliminados: {eliminados['documentos']}")

                # 2. Eliminar referencias
                referencias_model = ReferenciasModel()
                eliminados["referencias"] = referencias_model.delete_by_solicitante(solicitante_id=solicitante_id, empresa_id=empresa_id)
                print(f"   👥 Referencias eliminadas: {eliminados['referencias']}")

                # 3. Eliminar información financiera
                info_financiera_model = InformacionFinancieraModel()
                eliminados["informacion_financiera"] = info_financiera_model.delete_by_solicitante(solicitante_id=solicitante_id, empresa_id=empresa_id)
                print(f"   💰 Información financiera eliminada: {eliminados['informacion_financiera']}")

                # 4. Eliminar actividad económica
                actividad_model = ActividadEconomicaModel()
                eliminados["actividad_economica"] = actividad_model.delete_by_solicitante(solicitante_id=solicitante_id, empresa_id=empresa_id)
                print(f"   🏢 Actividad económica eliminada: {eliminados['actividad_economica']}")

                # 5. Eliminar ubicaciones
                ubicaciones_model = UbicacionesModel()
                eliminados["ubicaciones"] = ubicaciones_model.delete_by_solicitante(solicitante_id=solicitante_id, empresa_id=empresa_id)
                print(f"   📍 Ubicaciones eliminadas: {eliminados['ubicaciones']}")

                # 6. Eliminar la solicitud
                eliminados["solicitud"] = self.model.delete(id=id, empresa_id=empresa_id)
                print(f"   📋 Solicitud eliminada: {eliminados['solicitud']}")

                # 7. Eliminar el solicitante
                solicitantes_model = SolicitantesModel()
                eliminados["solicitante"] = solicitantes_model.delete(id=solicitante_id, empresa_id=empresa_id)
                print(f"   👤 Solicitante eliminado: {eliminados['solicitante']}")

                total_eliminados = sum(eliminados.values())
                print(f"✅ Eliminación completa: {total_eliminados} registros eliminados")

                return jsonify({
                    "ok": True,
                    "deleted": total_eliminados,
                    "message": f"Registro completo eliminado exitosamente",
                    "detalle_eliminacion": eliminados,
                    "solicitud_eliminada": {
                        "id": id,
                        "estado": solicitud_existente.get('estado'),
                        "banco": solicitud_existente.get('banco_nombre'),
                        "solicitante_id": solicitante_id
                    }
                })

            except Exception as e:
                print(f"❌ Error durante eliminación en cascada: {e}")
                return jsonify({
                    "ok": False,
                    "error": f"Error durante eliminación: {str(e)}",
                    "deleted": 0
                }), 500

        except ValueError as ve:
            print(f"❌ Error de validación: {ve}")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            print(f"💥 Error eliminando solicitud {id}: {ex}")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def obtener_observaciones(self, id: int):
        """Obtener el historial de observaciones de una solicitud"""
        try:
            empresa_id = self._empresa_id()

            # Obtener la solicitud con las observaciones
            solicitud = self.model.get_by_id(id=id, empresa_id=empresa_id)
            if not solicitud:
                return jsonify({"ok": False, "error": "Solicitud no encontrada"}), 404

            # Devolver el historial de observaciones o un array vacío si no hay
            observaciones = solicitud.get('observaciones', {}).get('historial', [])

            return jsonify({
                "ok": True,
                "data": {
                    "solicitud_id": id,
                    "total_observaciones": len(observaciones),
                    "observaciones": observaciones
                }
            })

        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def agregar_observacion(self, id: int):
        """Agregar una observación a una solicitud existente

        Estructura esperada en el body:
        {
            "observacion": "Texto de la observación",
            "fecha_creacion": "2025-09-01T20:30:00-05:00"
        }
        """
        try:
            body = request.get_json(silent=True) or {}

            observacion = body.get("observacion")
            fecha_creacion = body.get("fecha_creacion")

            if not observacion:
                return jsonify({"ok": False, "error": "La observación es requerida"}), 400

            if not fecha_creacion:
                return jsonify({"ok": False, "error": "La fecha de creación es requerida"}), 400

            print(f"\n📝 AGREGANDO OBSERVACIÓN A SOLICITUD {id}:")
            print(f"   📝 Observación: {observacion[:50]}...")
            print(f"   📅 Fecha creación: {fecha_creacion}")

            # Estructura simplificada que se guardará directamente
            nueva_observacion = {
                "observacion": observacion,
                "fecha_creacion": fecha_creacion
            }

            # Agregar la observación al array de observaciones
            data = self.model.agregar_observacion_simple(
                id=id,
                observacion=nueva_observacion
            )

            if not data:
                return jsonify({"ok": False, "error": "No se pudo agregar la observación"}), 400

            return jsonify({"ok": True, "data": data})

        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def actualizar_estado(self):
        """Actualizar solo el estado de una solicitud con opción de agregar observación"""
        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}
            usuario_info = self._obtener_usuario_autenticado()

            # Validar campos requeridos
            if not body.get("id"):
                return jsonify({"ok": False, "error": "ID de la solicitud es requerido"}), 400

            if not body.get("estado"):
                return jsonify({"ok": False, "error": "Nuevo estado es requerido"}), 400

            solicitud_id = int(body["id"])
            nuevo_estado = body["estado"]
            observacion = body.get("observacion")

            print(f"\n🔄 ACTUALIZANDO ESTADO DE SOLICITUD:")
            print(f"   📋 Empresa ID: {empresa_id}")
            print(f"   🆔 Solicitud ID: {solicitud_id}")
            print(f"   📊 Nuevo estado: {nuevo_estado}")
            if observacion:
                print(f"   📝 Incluye observación: {observacion[:50]}...")

            # Verificar si la solicitud existe antes de actualizar
            print(f"\n🔍 VERIFICANDO EXISTENCIA DE SOLICITUD...")
            solicitud_existente = self.model.get_by_id(id=solicitud_id, empresa_id=empresa_id)
            if not solicitud_existente:
                print(f"   ❌ Solicitud {solicitud_id} no encontrada en empresa {empresa_id}")
                return jsonify({"ok": False, "error": f"Solicitud {solicitud_id} no encontrada"}), 404

            estado_anterior = solicitud_existente.get('estado', 'N/A')
            print(f"   ✅ Solicitud encontrada: {estado_anterior}")

            # Usar el método que maneja observaciones
            data = self.model.actualizar_con_observacion(
                id=solicitud_id,
                empresa_id=empresa_id,
                base_updates={"estado": nuevo_estado},
                detalle_credito_merge=None,
                observacion=observacion,
                usuario_info=usuario_info
            )

            if not data:
                print(f"   ❌ Error al actualizar la solicitud")
                return jsonify({"ok": False, "error": "Error al actualizar la solicitud"}), 500

            print(f"   ✅ Estado actualizado exitosamente")

            response_data = {
                "ok": True,
                "data": data,
                "message": f"Estado de solicitud {solicitud_id} actualizado de '{estado_anterior}' a '{nuevo_estado}'"
            }

            if observacion:
                response_data["message"] += " con observación"

            return jsonify(response_data)

        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500

    def asignar_banco(self):
        """Asignar una solicitud a un banco específico"""
        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}

            # Validar campos requeridos
            if not body.get("id"):
                return jsonify({"ok": False, "error": "ID de la solicitud es requerido"}), 400

            if not body.get("banco_nombre"):
                return jsonify({"ok": False, "error": "Nombre del banco es requerido"}), 400

            solicitud_id = int(body["id"])
            banco_nombre = body["banco_nombre"]

            print(f"\n🏦 ASIGNANDO BANCO A SOLICITUD:")
            print(f"   📋 Empresa ID: {empresa_id}")
            print(f"   🆔 Solicitud ID: {solicitud_id}")
            print(f"   🏦 Banco: {banco_nombre}")

            # Verificar si la solicitud existe
            solicitud_existente = self.model.get_by_id(id=solicitud_id, empresa_id=empresa_id)
            if not solicitud_existente:
                return jsonify({"ok": False, "error": f"Solicitud {solicitud_id} no encontrada"}), 404

            # Actualizar banco
            data = self.model.update(
                id=solicitud_id,
                empresa_id=empresa_id,
                base_updates={"banco_nombre": banco_nombre},
                detalle_credito_merge=None
            )

            if not data:
                return jsonify({"ok": False, "error": "Error al asignar banco"}), 500

            print(f"   ✅ Banco asignado exitosamente")

            response_data = {
                "ok": True,
                "data": data,
                "message": f"Solicitud {solicitud_id} asignada al banco '{banco_nombre}'"
            }

            return jsonify(response_data)

        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500


