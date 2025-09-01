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

    def actualizar_columnas_tabla(self):
        """Actualizar configuración completa de columnas"""
        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}
            
            columnas = body.get("columnas", [])
            if not columnas:
                raise ValueError("Se requiere el campo 'columnas'")

            resultado = self.model.actualizar_columnas_tabla(
                empresa_id=empresa_id,
                columnas=columnas
            )

            return jsonify({
                "ok": True,
                "data": resultado,
                "message": "Configuración de columnas actualizada exitosamente"
            })

        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def agregar_columna(self):
        """Agregar una nueva columna a la configuración"""
        try:
            empresa_id = self._empresa_id()
            body = request.get_json(silent=True) or {}
            
            nombre_columna = body.get("nombre")
            if not nombre_columna:
                raise ValueError("Se requiere el campo 'nombre'")

            resultado = self.model.agregar_columna(
                empresa_id=empresa_id,
                nombre_columna=nombre_columna
            )

            return jsonify({
                "ok": True,
                "data": resultado,
                "message": f"Columna '{nombre_columna}' agregada exitosamente"
            })

        except ValueError as ve:
            return jsonify({"ok": False, "error": str(ve)}), 400
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500
