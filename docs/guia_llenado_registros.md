# Guía Paso a Paso - Llenado de Registros

> **Contexto:** API Flask + Supabase para gestión de solicitudes de crédito multi-tenant.
> **Objetivo:** Llenar un registro completo desde Postman simulando un formulario de usuario.

---

## Configuración Inicial

**URL Base:** `http://localhost:5000`
**Headers necesarios:** `Content-Type: application/json`
**Query param requerido:** `empresa_id=1` (en todas las peticiones)
**Alternativa:** Header `X-Empresa-Id: 1`

---

## Flujo Completo (11 Pasos)

### Paso 1: Crear Solicitante
**POST** `/solicitantes/?empresa_id=1`

```json
{
  "nombres": "Juan Carlos",
  "primer_apellido": "Pérez",
  "segundo_apellido": "García",
  "tipo_identificacion": "cc",
  "numero_documento": "123456789",
  "fecha_nacimiento": "1990-05-15",
  "genero": "M",
  "correo": "juan@email.com"
}
```

📋 **Guardar:** `solicitante_id` de la respuesta

---

### Paso 2: Llenar Datos Adicionales del Solicitante (JSON)
**PATCH** `/json/solicitante/{solicitante_id}/info_extra?empresa_id=1`

```json
{
  "value": {
    "fecha_expedicion": "2021-03-10",
    "nacionalidad": "COL",
    "lugar_nacimiento": "Medellín",
    "estado_civil": "soltero",
    "personas_a_cargo": 0,
    "nivel_estudio": "tecnico",
    "profesion": "Analista"
  }
}
```

---

### Paso 3: Crear Ubicación
**POST** `/ubicaciones/?empresa_id=1`

```json
{
  "solicitante_id": {solicitante_id},
  "ciudad_residencia": "Medellín",
  "departamento_residencia": "Antioquia"
}
```

📋 **Guardar:** `ubicacion_id` de la respuesta

---

### Paso 4: Llenar Detalles de Dirección (JSON)
**PATCH** `/json/ubicacion/{ubicacion_id}/detalle_direccion?empresa_id=1`

```json
{
  "value": {
    "direccion_residencia": "Cra 50 # 12-34",
    "telefono": "6041234567",
    "celular": "3001234567",
    "correo_personal": "juan@correo.com",
    "tipo_vivienda": "arrendada",
    "arrendador": {
      "nombre": "Carlos Pérez",
      "telefono": "3009998888",
      "ciudad": "Medellín",
      "departamento": "Antioquia"
    },
    "valor_mensual_arriendo": 1200000,
    "id_autenticacion": "abc-123",
    "recibir_correspondencia": "personal"
  }
}
```

---

### Paso 5: Crear Actividad Económica
**POST** `/actividad_economica/?empresa_id=1`

```json
{
  "solicitante_id": {solicitante_id},
  "tipo_actividad": "empleado",
  "sector_economico": "servicios"
}
```

📋 **Guardar:** `actividad_id` de la respuesta

---

### Paso 6: Llenar Detalles Laborales (JSON)
**PATCH** `/json/actividad_economica/{actividad_id}/detalle_actividad?empresa_id=1`

```json
{
  "value": {
    "empresa": "ACME S.A.",
    "ciudad_empresa": "Bogotá",
    "direccion_empresa": "Calle 10 # 5-20",
    "fecha_ingreso": "2022-01-15",
    "tipo_contrato": "indefinido",
    "telefono_empresa": "6013334444",
    "correo_oficina": "juan@acme.com",
    "tiene_negocio_propio": false,
    "nit": "900123456",
    "actividad_economica_principal": "Servicios",
    "declara_renta": true,
    "paga_impuestos_fuera": { "aplica": false },
    "empresa_pagadora_pension": null,
    "fecha_pension": null
  }
}
```

---

### Paso 7: Crear Información Financiera
**POST** `/informacion_financiera/?empresa_id=1`

```json
{
  "solicitante_id": {solicitante_id},
  "total_ingresos_mensuales": 3000000,
  "total_egresos_mensuales": 1500000,
  "total_activos": 50000000,
  "total_pasivos": 20000000
}
```

📋 **Guardar:** `financiera_id` de la respuesta

---

### Paso 8: Llenar Detalles Financieros (JSON)
**PATCH** `/json/informacion_financiera/{financiera_id}/detalle_financiera?empresa_id=1`

```json
{
  "value": {
    "detalle_otros_ingresos": [
      {"concepto": "arriendos", "valor": 600000},
      {"concepto": "freelance", "valor": 400000}
    ],
    "ingresos_fijos_pension": 0,
    "ingresos_por_ventas": 0,
    "ingresos_varios": 0,
    "honorarios": 0,
    "arriendos": 600000,
    "ingresos_actividad_independiente": 0
  }
}
```

---

### Paso 9: Crear Referencia
**POST** `/referencias/?empresa_id=1`

```json
{
  "solicitante_id": {solicitante_id},
  "tipo_referencia": "familiar"
}
```

📋 **Guardar:** `referencia_id` de la respuesta

---

### Paso 10: Llenar Datos de Referencia (JSON)
**PATCH** `/json/referencia/{referencia_id}/detalle_referencia?empresa_id=1`

```json
{
  "value": {
    "nombre_completo": "Ana Pérez",
    "relacion": "Hermana",
    "telefono": "3001112222",
    "departamento": "Antioquia",
    "ciudad": "Medellín",
    "direccion": "Cl 50 # 40-20"
  }
}
```

---

### Paso 11: Crear Solicitud de Crédito
**POST** `/solicitudes/?empresa_id=1`

```json
{
  "solicitante_id": {solicitante_id},
  "created_by_user_id": 10,
  "assigned_to_user_id": 10,
  "estado": "abierta",
  "detalle_credito": {
    "monto": 12000000,
    "plazo_meses": 48,
    "observaciones": "Solicitud de crédito para vivienda",
    "segundo_titular": {
      "nombres": "María González",
      "documento": "987654321"
    }
  }
}
```

---

## Endpoints de Consulta (Opcionales)

### Consultar Esquemas de Campos JSON
**GET** `/json/schema/{entity}/{json_field}?empresa_id=1`

Ejemplos:
- `/json/schema/solicitante/info_extra?empresa_id=1`
- `/json/schema/ubicacion/detalle_direccion?empresa_id=1`
- `/json/schema/actividad_economica/detalle_actividad?empresa_id=1`
- `/json/schema/informacion_financiera/detalle_financiera?empresa_id=1`
- `/json/schema/referencia/detalle_referencia?empresa_id=1`
- `/json/schema/solicitud/detalle_credito?empresa_id=1`

### Validar Campos JSON al Guardar
Agregar `?validate=true` a cualquier PATCH de JSON:

**PATCH** `/json/solicitante/{id}/info_extra?empresa_id=1&validate=true`

### Leer Registros Creados
**GET** `/solicitantes/{id}?empresa_id=1`
**GET** `/ubicaciones/{id}?empresa_id=1`
**GET** `/actividad_economica/{id}?empresa_id=1`
**GET** `/informacion_financiera/{id}?empresa_id=1`
**GET** `/referencias/{id}?empresa_id=1`
**GET** `/solicitudes/{id}?empresa_id=1`

### Leer JSON Específico
**GET** `/json/{entity}/{id}/{json_field}?empresa_id=1`

Ejemplo: `/json/solicitante/1001/info_extra?empresa_id=1`

### Leer Una Clave del JSON
**GET** `/json/{entity}/{id}/{json_field}?empresa_id=1&path=profesion`

---

## Mapeo de Entidades

| **Endpoint CRUD** | **Endpoint JSON** | **Tabla DB** | **Columna JSON** |
|-------------------|-------------------|--------------|------------------|
| `/solicitantes/` | `/json/solicitante/` | `solicitantes` | `info_extra` |
| `/ubicaciones/` | `/json/ubicacion/` | `ubicacion` | `detalle_direccion` |
| `/actividad_economica/` | `/json/actividad_economica/` | `actividad_economica` | `detalle_actividad` |
| `/informacion_financiera/` | `/json/informacion_financiera/` | `informacion_financiera` | `detalle_financiera` |
| `/referencias/` | `/json/referencia/` | `referencias` | `detalle_referencia` |
| `/solicitudes/` | `/json/solicitud/` | `solicitudes` | `detalle_credito` |

---

## Notas Importantes

1. **IDs Dinámicos:** Reemplaza `{solicitante_id}`, `{ubicacion_id}`, etc. con los valores reales que devuelva cada POST.

2. **Multi-tenant:** Todas las peticiones requieren `empresa_id=1` (o el ID de tu empresa).

3. **Campos JSON:** Los campos dinámicos van en columnas JSONB. Puedes agregar/quitar claves sin cambiar la estructura de la tabla.

4. **Validación:** Usa `?validate=true` para verificar que las claves JSON sean permitidas según `json_field_definition`.

5. **Prerrequisitos:** Asegúrate de tener:
   - Tabla `empresa` con `id=1`
   - Tabla `usuarios` con `id=10` (o cambiar en paso 11)
   - Tablas con datos semilla según `json_field_definition`

---

## Ejemplo de Respuesta Exitosa

```json
{
  "ok": true,
  "data": {
    "id": 1001,
    "empresa_id": 1,
    "nombres": "Juan Carlos",
    "primer_apellido": "Pérez",
    "created_at": "2024-01-15T10:30:00Z",
    "info_extra": {
      "profesion": "Analista",
      "estado_civil": "soltero"
    }
  }
}
```

¡Con esta guía puedes simular el llenado completo de formularios usando solo Postman!
