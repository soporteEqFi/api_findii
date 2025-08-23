from __future__ import annotations

from flask import request, jsonify
from models.solicitudes_model import SolicitudesModel
from models.json_schema_model import JSONSchemaModel


class SolicitudesController:
    def __init__(self):
        self.model = SolicitudesModel()
        self.schema_model = JSONSchemaModel()

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
            info_extra = user_data.get("info_extra", {})
            banco_nombre = info_extra.get("banco_nombre")
            ciudad = info_extra.get("ciudad")

            return {
                "id": user_data["id"],
                "rol": user_data.get("rol", "empresa"),
                "banco_nombre": banco_nombre,  # Desde info_extra del usuario
                "ciudad": ciudad  # Desde info_extra del usuario
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
            # Usuario banco solo ve solicitudes de su banco
            banco_nombre = usuario_info.get("banco_nombre")
            ciudad = usuario_info.get("ciudad")

            if banco_nombre:
                query = query.eq("banco_nombre", banco_nombre)
            else:
                # Si no tiene banco asignado, no ve nada
                return query.eq("id", -1)  # Query imposible

            # Nota: El filtro de ciudad se manejará a nivel de aplicación
            # ya que la ciudad está en tablas relacionadas, no en solicitudes directamente
            print(f"   🏙️ Ciudad del usuario: {ciudad} (se aplicará filtro posterior)")

            return query
        else:
            # Rol desconocido, no ve nada
            return query.eq("id", -1)  # Query imposible

    def obtener_bancos_disponibles(self):
        """Obtener lista de bancos desde campos dinámicos"""
        try:
            empresa_id = self._empresa_id()

            # Buscar específicamente en solicitudes.detalle_credito con clave "banco"
            bancos_encontrados = []

            try:
                definiciones = self.schema_model.get_schema(
                    empresa_id=empresa_id,
                    entity="solicitud",
                    json_column="detalle_credito"
                )

                for definicion in definiciones:
                    if definicion.get("key") == "banco":
                        if definicion.get("list_values"):
                            bancos_encontrados.extend(definicion["list_values"])
                    elif "banco" in definicion.get("key", "").lower():
                        print(f"   📝 Campo relacionado con banco: {definicion['key']}")

            except Exception as e:
                print(f"   ⚠️ Error buscando en solicitud.detalle_credito: {e}")

            # Eliminar duplicados y ordenar
            bancos_unicos = sorted(list(set(bancos_encontrados)))

            print(f"   📋 Bancos encontrados: {bancos_unicos}")

            return jsonify({
                "ok": True,
                "data": {
                    "bancos": bancos_unicos,
                    "total": len(bancos_unicos)
                },
                "message": f"Se encontraron {len(bancos_unicos)} bancos disponibles"
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

            # Extraer banco desde detalle_credito (campo dinámico)
            detalle_credito = body.get("detalle_credito", {})
            banco_nombre = None

            # Buscar banco en la raíz del JSON detalle_credito
            banco_nombre = detalle_credito.get("banco")

            if not banco_nombre:
                return jsonify({"ok": False, "error": "banco es requerido en detalle_credito"}), 400

            # Validar que el banco existe en los campos dinámicos (opcional)
            bancos_disponibles = self._obtener_bancos_validos(empresa_id)

            if bancos_disponibles and banco_nombre not in bancos_disponibles:
                print(f"   ⚠️ Banco '{banco_nombre}' no está en la lista de bancos disponibles")
                print(f"   📋 Bancos válidos: {bancos_disponibles}")

            # Asegurar que el banco esté en la raíz del JSON
            detalle_credito["banco"] = banco_nombre

            print(f"\n📝 CREANDO SOLICITUD:")
            print(f"   📋 Empresa ID: {empresa_id}")
            print(f"   🏦 Banco extraído y sincronizado: {banco_nombre}")

            data = self.model.create(
                empresa_id=empresa_id,
                solicitante_id=body.get("solicitante_id"),
                created_by_user_id=body.get("created_by_user_id"),
                assigned_to_user_id=body.get("assigned_to_user_id"),
                banco_nombre=banco_nombre,  # Asignar a la columna banco_nombre
                estado=body.get("estado"),
                detalle_credito=detalle_credito,  # Guardar con banco sincronizado
            )

            print(f"   ✅ Solicitud creada con ID: {data.get('id')}")
            return jsonify({"ok": True, "data": data}), 201
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500

    def _obtener_bancos_validos(self, empresa_id: int) -> list:
        """Método interno para obtener bancos válidos desde campos dinámicos"""
        try:
            bancos_encontrados = []

            try:
                definiciones = self.schema_model.get_schema(
                    empresa_id=empresa_id,
                    entity="solicitud",
                    json_column="detalle_credito"
                )

                for definicion in definiciones:
                    if definicion.get("key") == "banco":
                        if definicion.get("list_values"):
                            bancos_encontrados.extend(definicion["list_values"])

            except Exception:
                pass

            return sorted(list(set(bancos_encontrados)))

        except Exception:
            return []

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

            # Aplicar filtros de permisos por rol
            data = self.model.list_con_filtros_rol(
                empresa_id=empresa_id,
                usuario_info=usuario_info,
                estado=estado,
                solicitante_id=solicitante_id,
                limit=limit,
                offset=offset,
            )

                        # Aplicar filtro de ciudad para usuarios banco
            if usuario_info and usuario_info.get("rol") == "banco" and usuario_info.get("ciudad"):
                ciudad_usuario = usuario_info.get("ciudad")
                print(f"   🏙️ Aplicando filtro de ciudad: {ciudad_usuario}")

                # Filtrar solicitudes por ciudad desde el JSON detalle_credito
                solicitudes_filtradas = []
                for solicitud in data:
                    detalle_credito = solicitud.get('detalle_credito', {})
                    if isinstance(detalle_credito, str):
                        import json
                        try:
                            detalle_credito = json.loads(detalle_credito)
                        except:
                            detalle_credito = {}

                                        # Buscar ciudad en la raíz del JSON
                    ciudad_solicitante = detalle_credito.get('ciudad')

                    if ciudad_solicitante == ciudad_usuario:
                        solicitudes_filtradas.append(solicitud)
                        print(f"   🏙️ Incluyendo solicitud {solicitud.get('id')} (ciudad: {ciudad_solicitante})")
                    else:
                        print(f"   🏙️ Saltando solicitud {solicitud.get('id')} (ciudad: {ciudad_solicitante}, usuario: {ciudad_usuario})")

                data = solicitudes_filtradas
                print(f"   📄 Solicitudes después del filtro de ciudad: {len(data)}")

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
            base_updates = {}
            for field in [
                "estado",
                "assigned_to_user_id",
                "banco_nombre",
            ]:
                if field in body:
                    base_updates[field] = body[field]

            print(f"\n📝 ACTUALIZANDO SOLICITUD {id}:")
            print(f"   📋 Empresa ID: {empresa_id}")
            print(f"   🔄 Campos a actualizar: {list(base_updates.keys())}")

            detalle_credito_merge = body.get("detalle_credito")
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
        try:
            empresa_id = self._empresa_id()
            deleted = self.model.delete(id=id, empresa_id=empresa_id)
            return jsonify({"ok": True, "deleted": deleted})
        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(ex)}), 500

    def actualizar_estado(self):
        """Actualizar solo el estado de una solicitud"""
        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}
            print(body)

            # Validar campos requeridos
            if not body.get("id"):
                return jsonify({"ok": False, "error": "ID de la solicitud es requerido"}), 400

            if not body.get("estado"):
                return jsonify({"ok": False, "error": "Nuevo estado es requerido"}), 400

            solicitud_id = int(body["id"])
            nuevo_estado = body["estado"]

            print(f"\n🔄 ACTUALIZANDO ESTADO DE SOLICITUD:")
            print(f"   📋 Empresa ID: {empresa_id}")
            print(f"   🆔 Solicitud ID: {solicitud_id}")
            print(f"   📊 Nuevo estado: {nuevo_estado}")

            # Verificar si la solicitud existe antes de actualizar
            print(f"\n🔍 VERIFICANDO EXISTENCIA DE SOLICITUD...")
            solicitud_existente = self.model.get_by_id(id=solicitud_id, empresa_id=empresa_id)
            if not solicitud_existente:
                print(f"   ❌ Solicitud {solicitud_id} no encontrada en empresa {empresa_id}")
                return jsonify({"ok": False, "error": f"Solicitud {solicitud_id} no encontrada"}), 404

            print(f"   ✅ Solicitud encontrada: {solicitud_existente.get('estado', 'N/A')}")

            # Actualizar solo el estado
            print(f"\n📝 ACTUALIZANDO ESTADO...")
            data = self.model.update(
                id=solicitud_id,
                empresa_id=empresa_id,
                base_updates={"estado": nuevo_estado},
                detalle_credito_merge=None
            )

            if not data:
                print(f"   ❌ Error al actualizar la solicitud")
                return jsonify({"ok": False, "error": "Error al actualizar la solicitud"}), 500

            print(f"   ✅ Estado actualizado exitosamente")

            response_data = {
                "ok": True,
                "data": data,
                "message": f"Estado de solicitud {solicitud_id} actualizado a '{nuevo_estado}'"
            }

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


