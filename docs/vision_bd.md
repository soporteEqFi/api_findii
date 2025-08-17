# Visión General de la Base de Datos

> **Contexto:** Aplicación multi-empresa (tenant) para gestión de solicitantes y solicitudes de crédito.  
> **Punto clave:** Todas las tablas de negocio filtran por `empresa_id`. Campos variables/optativos viven en **JSONB**.

---

## Mapa de Entidades

- **EMPRESAS** (catálogo de tenants)  
- **USUARIOS** (cuentas del sistema)  
- **SOLICITANTES** (personas que piden crédito)  
- **UBICACION** (dirección del solicitante)  
- **ACTIVIDAD_ECONOMICA** (empleado/independiente, etc.)  
- **INFORMACION_FINANCIERA** (totales + detalle)  
- **REFERENCIAS** (familiar/personal/comercial)  
- **DOCUMENTOS** (archivos del solicitante)  
- **SOLICITUDES** (casos de crédito)  
- **TIPOS_CREDITOS** (catálogo configurable por empresa)

---

## Diagrama (ER, simplificado)

```
EMPRESAS (1) ──< SOLICITANTES (N) ──< UBICACION (N)
     │                    │ ├──< ACTIVIDAD_ECONOMICA (N)
     │                    │ ├──< INFORMACION_FINANCIERA (N)
     │                    │ ├──< REFERENCIAS (N)
     │                    │ └──< DOCUMENTOS (N)
     │
     ├──< SOLICITUDES (N) >── USUARIOS (creador/asignado)
     │
     └──< TIPOS_CREDITOS (N)
```

> Regla multi-tenant: `empresa_id` en SOLICITANTES, UBICACION, ACTIVIDAD_ECONOMICA, INFORMACION_FINANCIERA, REFERENCIAS, SOLICITUDES y TIPOS_CREDITOS (recomendado también para DOCUMENTOS).

---

## Esquema por Tabla (contrato de datos)

### EMPRESAS
- **PK:** `id`
- `nombre`, `imagen`, `created_at`

### USUARIOS
- **PK:** `id`
- `nombre`, `cedula`, `correo`, `password_hash` _(en tu DB aparece `contraseña`)_  
- `rol`, `created_at`

### SOLICITANTES *(tenant)*
- **PK:** `id` • **FK tenant:** `empresa_id → EMPRESAS.id`
- Datos base: `nombres`, `primer_apellido`, `segundo_apellido`, `tipo_identificacion`, `numero_documento` (TEXT), `fecha_nacimiento`, `genero`, `correo`, `created_at`
- **JSONB:** `info_extra`
  ```json
  {
    "estado_civil": "soltero|casado|...",
    "nivel_estudio": "tecnico|profesional|...",
    "profesion": "string",
    "personas_a_cargo": 0
  }
  ```

### UBICACION *(tenant)*
- **PK:** `id` • **FKs:** `solicitante_id → SOLICITANTES.id`, `empresa_id → EMPRESAS.id`
- Base: `ciudad_residencia`, `departamento_residencia`, `created_at`
- **JSONB:** `detalle_direccion`
  ```json
  {
    "direccion": "string",
    "tipo_vivienda": "propia|familiar|arrendada",
    "arrendador": { "nombre": "string", "telefono": "string" },
    "valor_arriendo": 0
  }
  ```

### ACTIVIDAD_ECONOMICA *(tenant)*
- **PK:** `id` • **FKs:** `solicitante_id`, `empresa_id`
- Base: `tipo_actividad` (empleado|independiente|pensionado|socio), `sector_economico`, `created_at`
- **JSONB (recomendado)** `detalle_actividad`
  ```json
  {
    "empresa": "string",
    "nit": "string",
    "fecha_ingreso": "YYYY-MM-DD",
    "tipo_contrato": "fijo|indefinido|prestación",
    "ciudad": "string",
    "telefono": "string",
    "ingresos": 0
  }
  ```

### INFORMACION_FINANCIERA *(tenant)*
- **PK:** `id` • **FKs:** `solicitante_id`, `empresa_id`
- Totales: `total_ingresos_mensuales`, `total_egresos_mensuales`, `total_activos`, `total_pasivos`, `created_at`
- **JSONB:** `detalle_financiera`
  ```json
  {
    "ingresos_fijos": 0,
    "ingresos_variables": 0,
    "otros_ingresos": [{"concepto":"arriendo","valor":0}],
    "gastos_financieros": 0,
    "gastos_personales": 0
  }
  ```

### REFERENCIAS *(tenant)*
- **PK:** `id` • **FKs:** `solicitante_id`, `empresa_id`
- Base: `tipo_referencia` (familiar|personal|comercial), `created_at`
- **JSONB:** `detalle_referencia`
  ```json
  {
    "nombre_completo": "string",
    "relacion": "string",
    "telefono": "string",
    "ciudad": "string",
    "direccion": "string"
  }
  ```

### DOCUMENTOS
- **PK:** `id` • **FK:** `solicitante_id`
- Base: `nombre`, `documento_url`, `created_at`, `updated_at`
- **Sugerido:** agregar `empresa_id` para filtrar por tenant.

### SOLICITUDES *(tenant)*
- **PK:** `id` • **FKs:** `empresa_id`, `solicitante_id`, `created_by_user_id → USUARIOS.id`, `assigned_to_user_id → USUARIOS.id`
- Base: `estado`, `created_at`, `updated_at`
- **Sugerido:** `detalle_credito JSONB`
  ```json
  {
    "tipo_credito_id": "uuid",
    "monto": 12000000,
    "plazo_meses": 48,
    "observaciones": "string",
    "segundo_titular": { "nombres": "...", "documento": "..." }
  }
  ```

### TIPOS_CREDITOS *(tenant recomendado)*
- **PK:** `id (uuid)`
- **Sugerido:** `empresa_id bigint NOT NULL` + **FK a EMPRESAS**
- Base: `name`, `display_name`, `description`, `is_activate` (DEFAULT true), `created_at`, `updated_at (timestamptz)`
- **JSONB:** `fields` (schema de campos dinámicos)
  ```json
  {
    "schema": [
      {"key":"monto","type":"number","label":"Monto","required":true},
      {"key":"plazo_meses","type":"integer","label":"Plazo (meses)","required":true}
    ]
  }
  ```

---

## Reglas Clave (multi-tenant, integridad, rendimiento)

- **Tenant:** `empresa_id` requerido en todas las tablas de negocio.  
- **Coherencia hijo-padre:** `empresa_id(hijo) = empresa_id(padre)` (ideal con trigger).  
- **Unicidad sugerida:** `SOLICITANTES(empresa_id, tipo_identificacion, numero_documento)`  
- **Índices:**
  - Por tenant: `... ON <tabla>(empresa_id)`
  - JSONB (si filtras por claves): `USING GIN(<campo_jsonb>)`
- **Timestamps:** usar `timestamptz` y `updated_at` con trigger de auto-update.
