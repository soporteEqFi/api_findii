# Ejemplos de uso de Endpoints de Referencias (para Frontend)

Estos ejemplos muestran cómo consumir los endpoints de referencias. Asegúrate de enviar siempre el header `X-Empresa-Id`.

## Headers comunes
- `Content-Type: application/json`
- `X-Empresa-Id: 1`

---

## 1) Agregar referencia
- Método: POST
- URL: `http://localhost:5000/referencias/agregar`
- Body (raw JSON):
```json
{
  "solicitante_id": 123,
  "referencia": {
    "tipo_referencia": "personal",
    "si_o_no": "no",
    "snack_favorito": "Piazza",
    "ciudad_referencia": "Bogotá",
    "celular_referencia": "234234",
    "nombre_referencia": "FERNANDO",
    "relacion_referencia": "AMIGO",
    "direccion_referencia": "Cl 4 4a -30"
  }
}
```
- Notas:
  - El item se guarda dentro de `detalle_referencia.referencias` con un `referencia_id` incremental asignado por el backend.

---

## 2) Editar referencia (actualizar información)
- Método: PATCH
- URL: `http://localhost:5000/referencias/actualizar`
- Body:
```json
{
  "solicitante_id": 123,
  "referencia_id": 5,
  "updates": {
    "tipo_referencia": "familiar",
    "si_o_no": "no",
    "snack_favorito": "Piazza",
    "ciudad_referencia": "Bogotá",
    "celular_referencia": "234234",
    "nombre_referencia": "FERNANDO",
    "relacion_referencia": "AMIGO",
    "direccion_referencia": "Cl 4 4a -30"
  }
}
```
- Alias soportado para el id: `id` en lugar de `referencia_id`.
- Solo se actualizan los campos enviados; no se requiere ninguna información de tipo.

---

## 3) Eliminar referencia
- Método: DELETE
- URL: `http://localhost:5000/referencias/eliminar`
- Body:
```json
{
  "solicitante_id": 123,
  "referencia_id": 5
}
```
- Comportamiento:
  - Elimina el ítem del detalle por `referencia_id`.

---

## 4) Obtener contenedor de referencias del solicitante
- Método: GET
- URL: `http://localhost:5000/referencias/por-solicitante?solicitante_id=123`
- Body: (vacío)
- Respuesta esperada (resumen):
```json
{
  "ok": true,
  "data": {
    "detalle_referencia": {
      "referencias": [
        {
          "referencia_id": 0,
          "tipo_referencia": "personal",
          "si_o_no": "no",
          "snack_favorito": "Piazza",
          "ciudad_referencia": "Bogotá",
          "celular_referencia": "234234",
          "nombre_referencia": "FERNANDO",
          "relacion_referencia": "AMIGO",
          "direccion_referencia": "Cl 4 4a -30"
        },
        {
          "referencia_id": 1,
          "tipo_referencia": "laboral",
          "si_o_no": "si",
          "snack_favorito": "Flips",
          "ciudad_referencia": "Bogotá",
          "celular_referencia": "32423",
          "nombre_referencia": "mario",
          "relacion_referencia": "amigo",
          "direccion_referencia": "Cl 4 4a -30"
        }
      ]
    }
  }
}
```

---

## 5) Editar referencia dentro de `editar-registro-completo`
- Método: PATCH
- URL: `http://localhost:5000/solicitantes/123/editar-registro-completo`
- Body (actualizar una referencia existente):
```json
{
  "referencias": [
    {
      "referencia_id": 5,
      "tipo_referencia": "comercial",
      "si_o_no": "no",
      "snack_favorito": "Piazza",
      "ciudad_referencia": "Bogotá",
      "celular_referencia": "234234",
      "nombre_referencia": "FERNANDO",
      "relacion_referencia": "AMIGO",
      "direccion_referencia": "Cl 4 4a -30"
    }
  ]
}
```
- Body (agregar una nueva referencia):
```json
{
  "referencias": [
    {
      "tipo_referencia": "familiar",
      "si_o_no": "si",
      "snack_favorito": "Flips",
      "ciudad_referencia": "Bogotá",
      "celular_referencia": "32423",
      "nombre_referencia": "mario",
      "relacion_referencia": "amigo",
      "direccion_referencia": "Cl 4 4a -30"
    }
  ]
}
```
- Notas:
  - Para actualizar, incluye `referencia_id` (o alias `id`).
  - Si no envías `referencia_id`, se interpreta como “agregar”.

---

## Recomendaciones de integración (Frontend)
- **Persistir `referencia_id`**: guarda el `referencia_id` del GET por-solicitante para editar/eliminar correctamente.
- **Refrescar antes de operar**: usa el GET por-solicitante para obtener los ids vigentes y evitar errores 404.
