from __future__ import annotations
from typing import Any, Dict, List, Optional
from data.supabase_conn import supabase

def _get_data(resp):
    if hasattr(resp, "data"):
        return resp.data
    if isinstance(resp, dict) and "data" in resp:
        return resp["data"]
    return resp

class ReferenciasModel:
    """CRUD para entidad referencia."""

    TABLE = "referencias"

    def create(self, *, empresa_id: int, solicitante_id: int, tipo_referencia: str, detalle_referencia: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {
            "empresa_id": empresa_id,
            "solicitante_id": solicitante_id,
            "tipo_referencia": tipo_referencia,
            "detalle_referencia": detalle_referencia or {},
        }
        resp = supabase.table(self.TABLE).insert(payload).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else data

    def get_by_id(self, *, id: int, empresa_id: int) -> Optional[Dict[str, Any]]:
        resp = supabase.table(self.TABLE).select("*").eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def list(self, *, empresa_id: int, solicitante_id: Optional[int] = None, tipo_referencia: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        q = supabase.table(self.TABLE).select("*").eq("empresa_id", empresa_id)
        if solicitante_id:
            q = q.eq("solicitante_id", solicitante_id)
        if tipo_referencia:
            q = q.eq("tipo_referencia", tipo_referencia)
        resp = q.range(offset, offset + max(limit - 1, 0)).execute()
        return _get_data(resp) or []

    def update(self, *, id: int, empresa_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        resp = supabase.table(self.TABLE).update(updates).eq("id", id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else None

    def delete(self, *, id: int, empresa_id: int) -> int:
        resp = (
            supabase.table(self.TABLE)
            .delete()
            .eq("id", id)
            .eq("empresa_id", empresa_id)
            .execute()
        )
        data = _get_data(resp)
        return len(data) if isinstance(data, list) else 0

    def delete_by_solicitante(self, *, solicitante_id: int, empresa_id: int) -> int:
        """Eliminar todas las referencias de un solicitante"""
        resp = supabase.table(self.TABLE).delete().eq("solicitante_id", solicitante_id).eq("empresa_id", empresa_id).execute()
        data = _get_data(resp)
        return len(data) if isinstance(data, list) else 0

    # ========================= NUEVOS MÉTODOS JSON =========================
    def get_by_solicitante(self, *, empresa_id: int, solicitante_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene el único registro de referencias por solicitante (si existe)."""
        resp = (
            supabase.table(self.TABLE)
            .select("*")
            .eq("empresa_id", empresa_id)
            .eq("solicitante_id", solicitante_id)
            .limit(1)
            .execute()
        )
        data = _get_data(resp) or []
        return data[0] if isinstance(data, list) and data else None

    def _ensure_row(self, *, empresa_id: int, solicitante_id: int) -> Dict[str, Any]:
        """Se asegura de que exista el registro contenedor para el solicitante.
        Si no existe, lo crea con arreglos vacíos.
        Estructura esperada:
          tipo_referencia: []  (arreglo de objetos {id_tipo_referencia, tipo_referencia})
          detalle_referencia: { referencias: [] }
        """
        existing = self.get_by_solicitante(empresa_id=empresa_id, solicitante_id=solicitante_id)
        if existing:
            return existing
        payload = {
            "empresa_id": empresa_id,
            "solicitante_id": solicitante_id,
            "detalle_referencia": {"referencias": []},
        }
        resp = supabase.table(self.TABLE).insert(payload).execute()
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else data

    def _normalize_tipo_obj(self, tipo: Any) -> Optional[Dict[str, Any]]:
        return None  # Tipos ya no se manejan a nivel de modelo (columna eliminada)

    def add_referencia(self, *, empresa_id: int, solicitante_id: int, referencia: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega una referencia al JSON del solicitante, generando referencia_id incremental.
        También actualiza el arreglo tipo_referencia agregando el tipo si no existe.
        """
        row = self._ensure_row(empresa_id=empresa_id, solicitante_id=solicitante_id)

        detalle = row.get("detalle_referencia") or {}
        referencias_arr = (detalle.get("referencias") or []) if isinstance(detalle, dict) else []

        # Calcular próximo referencia_id (inicia en 1)
        max_id = 0
        for r in referencias_arr:
            try:
                rid = int(r.get("referencia_id"))
                if rid > max_id:
                    max_id = rid
            except Exception:
                continue
        next_id = max_id + 1

        # Preparar referencia nueva
        nueva = dict(referencia) if referencia else {}
        # Asegurar que va dentro de la clave referencias
        nueva["referencia_id"] = next_id

        # Limpiar llaves no usadas; permitimos 'tipo_referencia' como parte del detalle
        nueva.pop("tipo", None)
        nueva.pop("id_tipo_referencia", None)

        referencias_arr.append(nueva)

        # Persistir cambios
        updates = {
            "detalle_referencia": {"referencias": referencias_arr},
        }
        updated = (
            supabase.table(self.TABLE)
            .update(updates)
            .eq("empresa_id", empresa_id)
            .eq("solicitante_id", solicitante_id)
            .execute()
        )
        data = _get_data(updated)
        return data[0] if isinstance(data, list) and data else updates

    def update_referencia_fields(self, *, empresa_id: int, solicitante_id: int, referencia_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualiza campos de una referencia dentro del JSON por referencia_id."""
        print(f"[REFERENCIAS][UPDATE] empresa_id={empresa_id} solicitante_id={solicitante_id} referencia_id={referencia_id} updates_keys={list(updates.keys())}")
        row = self.get_by_solicitante(empresa_id=empresa_id, solicitante_id=solicitante_id)
        if not row:
            print("[REFERENCIAS][UPDATE] Contenedor no encontrado para solicitante")
            return None
        detalle = row.get("detalle_referencia") or {}
        referencias_arr = (detalle.get("referencias") or []) if isinstance(detalle, dict) else []

        try:
            ids_disponibles = [r.get("referencia_id") for r in referencias_arr]
            print(f"[REFERENCIAS][UPDATE] referencia_id_disponibles={ids_disponibles}")
        except Exception:
            pass

        updated_any = False
        for idx, r in enumerate(referencias_arr):
            try:
                if int(r.get("referencia_id")) == int(referencia_id):
                    # No permitir cambiar la clave del ID
                    r_updated = dict(r)

                    # Aplicar updates de campos normales
                    for k, v in updates.items():
                        if k == "referencia_id":
                            continue
                        r_updated[k] = v

                    referencias_arr[idx] = r_updated
                    updated_any = True
                    break
            except Exception:
                continue

        if not updated_any:
            print("[REFERENCIAS][UPDATE] No se encontró la referencia para actualizar")
            return None

        new_payload = {"detalle_referencia": {"referencias": referencias_arr}}
        resp = (
            supabase.table(self.TABLE)
            .update(new_payload)
            .eq("empresa_id", empresa_id)
            .eq("solicitante_id", solicitante_id)
            .execute()
        )
        data = _get_data(resp)
        print("[REFERENCIAS][UPDATE] Actualización OK")
        return data[0] if isinstance(data, list) and data else new_payload

    def delete_referencia(self, *, empresa_id: int, solicitante_id: int, referencia_id: int) -> Optional[Dict[str, Any]]:
        """Elimina la referencia por referencia_id del detalle (ya no existe columna tipo_referencia)."""
        print(f"[REFERENCIAS][DELETE] empresa_id={empresa_id} solicitante_id={solicitante_id} referencia_id={referencia_id}")
        row = self.get_by_solicitante(empresa_id=empresa_id, solicitante_id=solicitante_id)
        if not row:
            print("[REFERENCIAS][DELETE] Contenedor no encontrado para solicitante")
            return None
        detalle = row.get("detalle_referencia") or {}
        referencias_arr = (detalle.get("referencias") or []) if isinstance(detalle, dict) else []

        # Eliminar por referencia_id (ya no dependemos del tipo en el item)
        removed = None
        remaining = []
        for r in referencias_arr:
            try:
                r_id = r.get("referencia_id")
                if r_id is not None and int(r_id) == int(referencia_id):
                    removed = r
                else:
                    remaining.append(r)
            except Exception:
                remaining.append(r)

        if removed is None:
            print("[REFERENCIAS][DELETE] Referencia no encontrada en detalle")
            return None

        updates = {
            "detalle_referencia": {"referencias": remaining},
        }
        resp = (
            supabase.table(self.TABLE)
            .update(updates)
            .eq("empresa_id", empresa_id)
            .eq("solicitante_id", solicitante_id)
            .execute()
        )
        data = _get_data(resp)
        print("[REFERENCIAS][DELETE] Eliminación OK")
        return data[0] if isinstance(data, list) and data else updates

    # --------- Helpers de resolución ---------
    def get_referencia_by_id(self, *, empresa_id: int, solicitante_id: int, referencia_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una referencia específica dentro del JSON por referencia_id."""
        row = self.get_by_solicitante(empresa_id=empresa_id, solicitante_id=solicitante_id)
        if not row:
            return None
        detalle = row.get("detalle_referencia") or {}
        referencias_arr = (detalle.get("referencias") or []) if isinstance(detalle, dict) else []
        for r in referencias_arr:
            try:
                if int(r.get("referencia_id")) == int(referencia_id):
                    return r
            except Exception:
                continue
        return None
    def delete_referencia_flexible(self, *, empresa_id: int, solicitante_id: int, referencia_id: int, id_tipo_referencia: Optional[int]) -> Optional[Dict[str, Any]]:
        """Compat: elimina por referencia_id (id_tipo_referencia ya no aplica)."""
        # Obtener contenedor y referencia objetivo
        row = self.get_by_solicitante(empresa_id=empresa_id, solicitante_id=solicitante_id)
        if not row:
            return None
        detalle = row.get("detalle_referencia") or {}
        referencias_arr = (detalle.get("referencias") or []) if isinstance(detalle, dict) else []

        ref = None
        for r in referencias_arr:
            try:
                if int(r.get("referencia_id")) == int(referencia_id):
                    ref = r
                    break
            except Exception:
                continue
        if ref is None:
            return None
        # Eliminar por referencia_id solamente
        remaining = []
        removed = None
        for r in referencias_arr:
            try:
                if int(r.get("referencia_id")) == int(referencia_id):
                    removed = r
                else:
                    remaining.append(r)
            except Exception:
                remaining.append(r)
        if removed is None:
            return None
        updates = {
            "detalle_referencia": {"referencias": remaining},
        }
        resp = (
            supabase.table(self.TABLE)
            .update(updates)
            .eq("empresa_id", empresa_id)
            .eq("solicitante_id", solicitante_id)
            .execute()
        )
        data = _get_data(resp)
        return data[0] if isinstance(data, list) and data else updates

    # --------- Helpers de resolución ---------
    def get_referencia_by_id(self, *, empresa_id: int, solicitante_id: int, referencia_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una referencia específica dentro del JSON por referencia_id."""
        row = self.get_by_solicitante(empresa_id=empresa_id, solicitante_id=solicitante_id)
        if not row:
            return None
        detalle = row.get("detalle_referencia") or {}
        referencias_arr = (detalle.get("referencias") or []) if isinstance(detalle, dict) else []
        for r in referencias_arr:
            try:
                if int(r.get("referencia_id")) == int(referencia_id):
                    return r
            except Exception:
                continue
        return None
