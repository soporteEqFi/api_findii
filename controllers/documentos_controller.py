from __future__ import annotations

import os
import uuid
from typing import Any, Dict

from flask import request, jsonify
from werkzeug.utils import secure_filename

from data.supabase_conn import supabase
from models.documentos_model import DocumentosModel


class DocumentosController:
    def __init__(self):
        self.model = DocumentosModel()

    def create(self):
        try:
            # Soporta multipart/form-data (preferido) y JSON como fallback
            file = request.files.get("file")
            if not file:
                return jsonify({"ok": False, "error": "Archivo (file) es requerido"}), 400

            # Obtener solicitante_id desde form, query o JSON
            solicitante_id = (
                request.form.get("solicitante_id")
                or request.args.get("solicitante_id")
                or (request.get_json(silent=True) or {}).get("solicitante_id")
            )
            if not solicitante_id:
                return jsonify({"ok": False, "error": "solicitante_id es requerido"}), 400
            try:
                solicitante_id = int(solicitante_id)
            except Exception:
                return jsonify({"ok": False, "error": "solicitante_id debe ser entero"}), 400

            original_name = secure_filename(file.filename or "documento")
            ext = os.path.splitext(original_name)[1]
            unique_name = f"{uuid.uuid4().hex}{ext}" if ext else uuid.uuid4().hex
            storage_path = f"solicitantes/{solicitante_id}/{unique_name}"

            # Subir a Supabase Storage (bucket: document)
            content_type = file.mimetype or "application/octet-stream"
            file_bytes = file.read()
            storage = supabase.storage.from_("document")
            storage.upload(
                storage_path,
                file_bytes,
                file_options={
                    "content-type": content_type,
                    "upsert": "true",
                    # opcional: "cache-control": "3600",
                },
            )

            # Obtener URL pública
            public_url_resp = storage.get_public_url(storage_path)
            public_url: str | None = None
            if isinstance(public_url_resp, dict):
                public_url = public_url_resp.get("publicUrl") or (
                    public_url_resp.get("data", {}) if isinstance(public_url_resp.get("data"), dict) else {}
                ).get("publicUrl")
            elif hasattr(public_url_resp, "data"):
                data: Dict[str, Any] = getattr(public_url_resp, "data", {})
                if isinstance(data, dict):
                    public_url = data.get("publicUrl")

            if not public_url:
                # fallback por si la lib devuelve directamente el string
                public_url = str(public_url_resp)

            # Guardar registro en la tabla 'documentos'
            saved = self.model.create(
                nombre=original_name,
                documento_url=public_url,
                solicitante_id=solicitante_id,
            )

            return jsonify({"ok": True, "data": saved}), 201
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def list(self):
        try:
            solicitante_id = request.args.get("solicitante_id")
            if not solicitante_id:
                return jsonify({"ok": False, "error": "solicitante_id es requerido"}), 400
            try:
                solicitante_id = int(solicitante_id)
            except Exception:
                return jsonify({"ok": False, "error": "solicitante_id debe ser entero"}), 400

            limit = int(request.args.get("limit", 50))
            offset = int(request.args.get("offset", 0))
            data = self.model.list(solicitante_id=solicitante_id, limit=limit, offset=offset)
            return jsonify({"ok": True, "data": data})
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def delete(self, id: int):
        try:
            # Optional validation with solicitante_id
            provided_sid = request.args.get("solicitante_id")
            if not provided_sid and request.is_json:
                body = request.get_json(silent=True) or {}
                provided_sid = body.get("solicitante_id")
            if provided_sid is not None:
                try:
                    provided_sid = int(provided_sid)
                except Exception:
                    return jsonify({"ok": False, "error": "solicitante_id debe ser entero"}), 400

                current = self.model.get_by_id(id=id)
                if not current:
                    return jsonify({"ok": False, "error": "Documento no encontrado"}), 404
                if int(current.get("solicitante_id") or 0) != provided_sid:
                    return jsonify({"ok": False, "error": "solicitante_id no coincide con el documento"}), 400

            deleted = self.model.delete(id=id)
            return jsonify({"ok": True, "deleted": deleted, "solicitante_id": provided_sid}), 200
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500

    def update(self, id: int):
        try:
            # Puede venir JSON o multipart. Si viene archivo, se reemplaza en Storage y se actualiza URL.
            content_type = request.content_type or ""
            updates: Dict[str, Any] = {}

            current = self.model.get_by_id(id=id)
            if not current:
                return jsonify({"ok": False, "error": "Documento no encontrado"}), 404

            solicitante_id = current.get("solicitante_id")
            if not solicitante_id:
                return jsonify({"ok": False, "error": "Registro inválido: falta solicitante_id"}), 400

            # Optional provided solicitante_id for validation
            provided_sid = None
            if "multipart/form-data" in content_type:
                provided_sid = request.form.get("solicitante_id")
            else:
                body_probe = request.get_json(silent=True) or {}
                provided_sid = body_probe.get("solicitante_id")
            if provided_sid is not None:
                try:
                    provided_sid = int(provided_sid)
                except Exception:
                    return jsonify({"ok": False, "error": "solicitante_id debe ser entero"}), 400
                if int(solicitante_id) != provided_sid:
                    return jsonify({"ok": False, "error": "solicitante_id no coincide con el documento"}), 400

            storage = supabase.storage.from_("document")

            if "multipart/form-data" in content_type:
                # nombre opcional por form field
                nombre_override = request.form.get("nombre")
                if nombre_override:
                    updates["nombre"] = nombre_override

                file = request.files.get("file")
                if file:
                    original_name = secure_filename(file.filename or "documento")
                    ext = os.path.splitext(original_name)[1]
                    unique_name = f"{uuid.uuid4().hex}{ext}" if ext else uuid.uuid4().hex
                    storage_path = f"solicitantes/{solicitante_id}/{unique_name}"

                    content_type_up = file.mimetype or "application/octet-stream"
                    storage.upload(
                        storage_path,
                        file.read(),
                        file_options={
                            "content-type": content_type_up,
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

                    updates["nombre"] = original_name
                    updates["documento_url"] = public_url
            else:
                body = request.get_json(silent=True) or {}
                # Solo permitir actualizar nombre via JSON
                if "nombre" in body:
                    updates["nombre"] = body["nombre"]

            if not updates:
                return jsonify({"ok": False, "error": "No hay cambios para aplicar"}), 400

            updated = self.model.update(id=id, updates=updates)
            return jsonify({"ok": True, "data": updated})
        except Exception as ex:
            return jsonify({"ok": False, "error": str(ex)}), 500
