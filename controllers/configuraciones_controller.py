from __future__ import annotations
from flask import request, jsonify
from models.configuraciones_model import ConfiguracionesModel

class ConfiguracionesController:
    def __init__(self):
        self.model = ConfiguracionesModel()

    def _empresa_id(self) -> int:
        empresa_id = request.headers.get("X-Empresa-Id") or request.args.get("empresa_id")
        if not empresa_id:
            raise ValueError("empresa_id es requerido")
        try:
            return int(empresa_id)
        except Exception as exc:
            raise ValueError("empresa_id debe ser entero") from exc

    def obtener_por_categoria(self, categoria: str):
        """Obtener configuración por categoría específica"""
        try:
            empresa_id = self._empresa_id()

            configuracion = self.model.obtener_por_categoria(
                empresa_id=empresa_id,
                categoria=categoria
            )

            return jsonify({
                "ok": True,
                "data": {
                    "categoria": categoria,
                    "valores": configuracion,
                    "total": len(configuracion)
                },
                "message": f"Se encontraron {len(configuracion)} valores para {categoria}"
            })

        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def obtener_todas(self):
        """Obtener todas las configuraciones de la empresa"""
        try:
            empresa_id = self._empresa_id()

            configuraciones = self.model.obtener_todas_categorias(
                empresa_id=empresa_id
            )

            return jsonify({
                "ok": True,
                "data": {
                    "configuraciones": configuraciones,
                    "total_categorias": len(configuraciones)
                },
                "message": f"Se encontraron {len(configuraciones)} categorías de configuración"
            })

        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def obtener_columnas_tabla(self):
        """Obtener configuración de columnas para tablas"""
        try:
            empresa_id = self._empresa_id()

            configuracion_columnas = self.model.obtener_columnas_tabla(
                empresa_id=empresa_id
            )

            if not configuracion_columnas:
                return jsonify({
                    "ok": False,
                    "error": "No se encontró configuración de columnas para la tabla"
                }), 404

            return jsonify({
                "ok": True,
                "data": configuracion_columnas,
                "message": "Configuración de columnas obtenida exitosamente"
            })

        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500
