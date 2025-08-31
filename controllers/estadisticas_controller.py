from flask import request, jsonify
from models.estadisticas_model import EstadisticasModel
from data.supabase_conn import supabase

class EstadisticasController:
    def __init__(self):
        self.model = EstadisticasModel()

    def _empresa_id(self) -> int:
        """Obtener empresa_id del header o query parameter"""
        empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
        if not empresa_id:
            raise ValueError("empresa_id es requerido")
        try:
            return int(empresa_id)
        except Exception as exc:
            raise ValueError("empresa_id debe ser entero") from exc

    def _obtener_usuario_autenticado(self):
        """Obtener información del usuario autenticado desde la base de datos"""
        try:
            # Obtener el token del header Authorization
            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                print(f"   ❌ Authorization header inválido o faltante")
                return None

            # Obtener user_id del header o query parameter
            user_id = request.headers.get("X-User-Id") or request.args.get("user_id")

            if not user_id:
                print(f"   ❌ User ID faltante (header X-User-Id o query user_id)")
                return None

            # Consultar la base de datos para obtener información completa del usuario
            print(f"   🔍 Consultando usuario con ID: {user_id}")
            user_response = supabase.table("usuarios").select("id, rol, info_extra").eq("id", int(user_id)).execute()
            print(f"   📊 Respuesta de BD: {user_response.data}")

            user_data = user_response.data[0] if user_response.data else None

            if not user_data:
                print(f"   ❌ Usuario no encontrado en BD")
                return None

            # Extraer banco_nombre y ciudad del info_extra del usuario
            info_extra = user_data.get("info_extra", {})
            banco_nombre = info_extra.get("banco_nombre")
            ciudad = info_extra.get("ciudad")

            usuario_info = {
                "id": user_data["id"],
                "rol": user_data.get("rol", "empresa"),
                "banco_nombre": banco_nombre,
                "ciudad": ciudad
            }

            return usuario_info

        except Exception as e:
            print(f"   ❌ Error obteniendo usuario autenticado: {e}")
            return None

    def estadisticas_generales(self):
        """Endpoint para obtener estadísticas generales"""
        try:
            print(f"\n📊 OBTENIENDO ESTADÍSTICAS GENERALES")
            
            empresa_id = self._empresa_id()
            usuario_info = self._obtener_usuario_autenticado()
            
            print(f"   🏢 Empresa ID: {empresa_id}")
            print(f"   👤 Usuario info: {usuario_info}")
            
            # Obtener estadísticas del modelo
            estadisticas = self.model.estadisticas_generales(empresa_id, usuario_info)
            
            print(f"   📈 Estadísticas obtenidas: {estadisticas}")
            
            response_data = {
                "ok": True,
                "data": {
                    "tipo": "generales",
                    "empresa_id": empresa_id,
                    "usuario_rol": usuario_info.get("rol") if usuario_info else None,
                    "estadisticas": estadisticas
                }
            }
            
            return jsonify(response_data)
            
        except ValueError as ve:
            print(f"❌ Error de validación: {ve}")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            print(f"❌ Error inesperado: {ex}")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def estadisticas_rendimiento(self):
        """Endpoint para obtener estadísticas de rendimiento"""
        try:
            print(f"\n⚡ OBTENIENDO ESTADÍSTICAS DE RENDIMIENTO")
            
            empresa_id = self._empresa_id()
            usuario_info = self._obtener_usuario_autenticado()
            
            # Obtener parámetro de días (por defecto 30)
            dias = int(request.args.get("dias", 30))
            
            print(f"   🏢 Empresa ID: {empresa_id}")
            print(f"   👤 Usuario info: {usuario_info}")
            print(f"   📅 Período: {dias} días")
            
            # Obtener estadísticas del modelo
            estadisticas = self.model.estadisticas_rendimiento(empresa_id, usuario_info, dias)
            
            print(f"   📈 Estadísticas obtenidas: {estadisticas}")
            
            response_data = {
                "ok": True,
                "data": {
                    "tipo": "rendimiento",
                    "empresa_id": empresa_id,
                    "usuario_rol": usuario_info.get("rol") if usuario_info else None,
                    "periodo_dias": dias,
                    "estadisticas": estadisticas
                }
            }
            
            return jsonify(response_data)
            
        except ValueError as ve:
            print(f"❌ Error de validación: {ve}")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            print(f"❌ Error inesperado: {ex}")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def estadisticas_financieras(self):
        """Endpoint para obtener estadísticas financieras y de calidad"""
        try:
            print(f"\n💰 OBTENIENDO ESTADÍSTICAS FINANCIERAS")
            
            empresa_id = self._empresa_id()
            usuario_info = self._obtener_usuario_autenticado()
            
            print(f"   🏢 Empresa ID: {empresa_id}")
            print(f"   👤 Usuario info: {usuario_info}")
            
            # Obtener estadísticas del modelo
            estadisticas = self.model.estadisticas_financieras(empresa_id, usuario_info)
            
            print(f"   📈 Estadísticas obtenidas: {estadisticas}")
            
            response_data = {
                "ok": True,
                "data": {
                    "tipo": "financieras",
                    "empresa_id": empresa_id,
                    "usuario_rol": usuario_info.get("rol") if usuario_info else None,
                    "estadisticas": estadisticas
                }
            }
            
            return jsonify(response_data)
            
        except ValueError as ve:
            print(f"❌ Error de validación: {ve}")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            print(f"❌ Error inesperado: {ex}")
            return jsonify({"ok": False, "error": str(ex)}), 500

    def estadisticas_completas(self):
        """Endpoint para obtener todas las estadísticas en una sola llamada"""
        try:
            print(f"\n🎯 OBTENIENDO ESTADÍSTICAS COMPLETAS")
            
            empresa_id = self._empresa_id()
            usuario_info = self._obtener_usuario_autenticado()
            
            # Obtener parámetro de días para rendimiento
            dias = int(request.args.get("dias", 30))
            
            print(f"   🏢 Empresa ID: {empresa_id}")
            print(f"   👤 Usuario info: {usuario_info}")
            print(f"   📅 Período: {dias} días")
            
            # Obtener todas las estadísticas
            estadisticas_generales = self.model.estadisticas_generales(empresa_id, usuario_info)
            estadisticas_rendimiento = self.model.estadisticas_rendimiento(empresa_id, usuario_info, dias)
            estadisticas_financieras = self.model.estadisticas_financieras(empresa_id, usuario_info)
            
            response_data = {
                "ok": True,
                "data": {
                    "tipo": "completas",
                    "empresa_id": empresa_id,
                    "usuario_rol": usuario_info.get("rol") if usuario_info else None,
                    "periodo_dias": dias,
                    "estadisticas": {
                        "generales": estadisticas_generales,
                        "rendimiento": estadisticas_rendimiento,
                        "financieras": estadisticas_financieras
                    }
                }
            }
            
            print(f"   ✅ Todas las estadísticas obtenidas exitosamente")
            
            return jsonify(response_data)
            
        except ValueError as ve:
            print(f"❌ Error de validación: {ve}")
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            print(f"❌ Error inesperado: {ex}")
            return jsonify({"ok": False, "error": str(ex)}), 500
