# 🏦 Configuración de Campos Dinámicos para Bancos

## 📋 **Paso 1: Configurar Campo Dinámico de Bancos**

### Configurar en `solicitud.detalle_credito` con clave "banco"

```bash
# POST /json/definitions/solicitud/detalle_credito?empresa_id=1
curl -X POST "http://localhost:5000/json/definitions/solicitud/detalle_credito?empresa_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "definitions": [
      {
        "key": "banco",
        "type": "string",
        "required": true,
        "description": "Banco donde se solicita el crédito",
        "list_values": [
          "Banco de Bogotá",
          "Banco Popular",
          "Bancolombia",
          "BBVA Colombia",
          "Banco AV Villas",
          "Banco Caja Social",
          "Banco Colpatria",
          "Banco Davivienda",
          "Banco Falabella",
          "Banco Pichincha",
          "Banco Santander",
          "Scotiabank Colpatria",
          "Banco Agrario",
          "Banco de Occidente",
          "Banco Itaú"
        ]
      }
    ]
  }'
```

## 📋 **Paso 2: Obtener Bancos Disponibles**

```bash
# GET /solicitudes/bancos-disponibles?empresa_id=1
curl -X GET "http://localhost:5000/solicitudes/bancos-disponibles?empresa_id=1" \
  -H "Content-Type: application/json"
```

**Respuesta esperada:**
```json
{
  "ok": true,
  "data": {
    "bancos": [
      "Banco Agrario",
      "Banco AV Villas",
      "Banco Caja Social",
      "Banco Colpatria",
      "Banco de Bogotá",
      "Banco de Occidente",
      "Banco Davivienda",
      "Banco Falabella",
      "Banco Itaú",
      "Banco Pichincha",
      "Banco Popular",
      "Banco Santander",
      "Bancolombia",
      "BBVA Colombia",
      "Scotiabank Colpatria"
    ],
    "total": 15
  },
  "message": "Se encontraron 15 bancos disponibles"
}
```

## 📋 **Paso 3: Crear Solicitud con Banco Válido**

```bash
# POST /solicitudes/?empresa_id=1
curl -X POST "http://localhost:5000/solicitudes/?empresa_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "solicitante_id": 123,
    "created_by_user_id": 1,
    "estado": "pendiente",
    "detalle_credito": {
      "banco": "Bancolombia",
      "monto_solicitado": 50000000,
      "plazo_meses": 60,
      "destino_credito": "vivienda"
    }
  }'
```

**Nota importante:** El banco se envía dentro de `detalle_credito.banco` (campo dinámico) y el backend automáticamente lo extrae y lo asigna a la columna `banco_nombre` de la tabla `SOLICITUDES`.

## 🎯 **Ventajas de este Enfoque**

### ✅ **Consistencia**
- Los bancos se definen una sola vez en `solicitud.detalle_credito.banco`
- Se reutilizan automáticamente en todas las solicitudes

### ✅ **Flexibilidad**
- Fácil agregar/quitar bancos sin cambiar código
- Diferentes listas por empresa si es necesario

### ✅ **Validación Automática**
- El backend valida que el banco existe en la lista
- Previene errores de tipeo o bancos inexistentes

### ✅ **Frontend Dinámico**
- El frontend puede obtener la lista de bancos y crear dropdowns automáticamente
- No necesita hardcodear la lista de bancos

## 🔧 **Uso en Frontend**

```javascript
// 1. Obtener bancos disponibles
const obtenerBancos = async () => {
  const response = await fetch('/solicitudes/bancos-disponibles?empresa_id=1')
  const { data } = await response.json()
  return data.bancos
}

// 2. Crear dropdown dinámico
const crearDropdownBancos = (bancos) => {
  const select = document.createElement('select')
  select.name = 'banco_nombre'

  bancos.forEach(banco => {
    const option = document.createElement('option')
    option.value = banco
    option.textContent = banco
    select.appendChild(option)
  })

  return select
}

// 3. Usar en formulario
const bancos = await obtenerBancos()
const dropdownBancos = crearDropdownBancos(bancos)
document.getElementById('formulario').appendChild(dropdownBancos)
```

## 🚀 **Flujo Completo**

1. **Admin configura** bancos en `solicitud.detalle_credito.banco`
2. **Frontend consulta** `/solicitudes/bancos-disponibles`
3. **Frontend genera** dropdown con bancos disponibles
4. **Usuario selecciona** banco del dropdown
5. **Frontend envía** solicitud con `detalle_credito.banco`
6. **Backend extrae** el banco de `detalle_credito.banco` y lo asigna a `banco_nombre`
7. **Backend valida** que el banco existe en la lista de campos dinámicos
8. **Backend guarda** la solicitud con el banco asignado en ambas ubicaciones:
   - Columna `banco_nombre` (para consultas rápidas)
   - Campo dinámico `detalle_credito.banco` (para consistencia)

## 📍 **Ubicación Específica**

Los bancos se almacenan en:
- **Entidad:** `solicitud`
- **Campo JSON:** `detalle_credito`
- **Clave:** `banco`
- **Tipo:** `string` con `list_values`

¡Listo! Ahora tienes un sistema completo y dinámico para manejar bancos usando los campos dinámicos. 🎉
