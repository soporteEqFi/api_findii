# 🚀 Guía Frontend - Campos Dinámicos JSON

> **Objetivo:** Conectar el frontend con la API para manejar campos dinámicos JSON de forma flexible y escalable.
> **Ventaja clave:** Los campos se configuran dinámicamente sin necesidad de cambiar código frontend.

## 🎯 **Diferencia Importante:**

**Hay DOS tipos de operaciones diferentes:**

1. **🛠️ Administrar DEFINICIONES** → Configurar qué campos pueden existir (tabla `json_field_definition`)
2. **📝 Usar DATOS** → Guardar/leer valores en esos campos ya definidos (tablas principales como `solicitantes`, `ubicacion`, etc.)

**Flujo típico:**
```
Admin configura campos → Frontend consulta esquema → Usuario llena datos → Frontend guarda datos
```

---

## 📮 **Ejemplos Rápidos para Postman**

### **🛠️ Configurar Campos (Administrador)**

#### Crear definiciones de campos para solicitantes:
```
Method: POST
URL: http://localhost:5000/json/definitions/solicitante/info_extra?empresa_id=1

Headers:
Content-Type: application/json

Body:
{
  "definitions": [
    {
      "key": "profesion",
      "type": "string",
      "required": true,
      "description": "Profesión del solicitante"
    },
    {
      "key": "experiencia_años",
      "type": "number",
      "required": false,
      "description": "Años de experiencia laboral"
    },
    {
      "key": "nivel_educativo",
      "type": "string",
      "required": true,
      "list_values": ["primaria", "secundaria", "tecnico", "universitario", "posgrado"],
      "description": "Nivel educativo alcanzado"
    }
  ]
}
```

#### Ver campos configurados:
```
Method: GET
URL: http://localhost:5000/json/schema/solicitante/info_extra?empresa_id=1
```

### **📝 Usar Campos (Usuario Final)**

#### Guardar datos en campos configurados:
```
Method: PATCH
URL: http://localhost:5000/json/solicitante/123/info_extra?empresa_id=1&validate=true

Headers:
Content-Type: application/json

Body:
{
  "value": {
    "profesion": "Ingeniero de Software",
    "experiencia_años": 5,
    "nivel_educativo": "universitario"
  }
}
```

#### Leer datos guardados:
```
Method: GET
URL: http://localhost:5000/json/solicitante/123/info_extra?empresa_id=1
```

---

## 📋 Configuración Inicial

### Headers Obligatorios
```javascript
const headers = {
  'Content-Type': 'application/json',
  // Empresa ID puede ir en header o query param
  'X-Empresa-Id': '1'
}
```

### URL Base
```javascript
const API_BASE = 'http://localhost:5000'
```

### Empresa ID (Multi-tenant)
```javascript
// Agregar a TODAS las peticiones como query param
const empresaId = 1
const url = `${API_BASE}/endpoint/?empresa_id=${empresaId}`
```

---

## 📚 **Referencia Rápida de Endpoints**

| **Operación** | **Método** | **Endpoint** | **Propósito** |
|---------------|------------|--------------|---------------|
| **DEFINICIONES (Configuración)** |
| Ver esquema | `GET` | `/json/schema/{entity}/{json_field}` | Obtener campos configurados |
| Crear/actualizar campos | `POST` | `/json/definitions/{entity}/{json_field}` | Configurar qué campos pueden existir |
| Reemplazar todos | `PUT` | `/json/definitions/{entity}/{json_field}` | Reemplazar configuración completa |
| Eliminar campo específico | `DELETE` | `/json/definitions/{entity}/{json_field}/{key}` | Eliminar un campo configurado |
| Eliminar todos | `DELETE` | `/json/definitions/{entity}/{json_field}` | Eliminar toda la configuración |
| **DATOS (Uso)** |
| Leer datos | `GET` | `/json/{entity}/{record_id}/{json_field}` | Obtener datos guardados |
| Guardar datos | `PATCH` | `/json/{entity}/{record_id}/{json_field}` | Guardar/actualizar datos |
| Eliminar datos | `DELETE` | `/json/{entity}/{record_id}/{json_field}?path={key}` | Eliminar datos específicos |

**Nota:** Todos los endpoints requieren `?empresa_id={id}` como query parameter.

---

## 🛠️ 1. Administrar Definiciones de Campos Dinámicos

### Crear/Actualizar Definiciones de Campos
```javascript
// POST /json/definitions/{entidad}/{json_field}?empresa_id={id}
async function crearDefinicionesCampos(entidad, campoJson, definiciones) {
  const response = await fetch(`${API_BASE}/json/definitions/${entidad}/${campoJson}?empresa_id=${empresaId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      definitions: definiciones
    })
  })
  return await response.json()
}

// Ejemplo de uso
await crearDefinicionesCampos('solicitante', 'info_extra', [
  {
    key: 'profesion',
    type: 'string',
    required: true,
    description: 'Profesión del solicitante'
  },
  {
    key: 'experiencia_años',
    type: 'number',
    required: false,
    description: 'Años de experiencia laboral'
  },
  {
    key: 'nivel_educativo',
    type: 'string',
    required: true,
    list_values: ['primaria', 'secundaria', 'tecnico', 'universitario', 'posgrado'],
    description: 'Nivel educativo alcanzado'
  }
])
```

### Reemplazar Todas las Definiciones
```javascript
// PUT /json/definitions/{entidad}/{json_field}?empresa_id={id}
async function reemplazarDefinicionesCampos(entidad, campoJson, definiciones) {
  const response = await fetch(`${API_BASE}/json/definitions/${entidad}/${campoJson}?empresa_id=${empresaId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      definitions: definiciones
    })
  })
  return await response.json()
}

// Ejemplo: reemplazar completamente las definiciones
await reemplazarDefinicionesCampos('solicitante', 'info_extra', [
  {
    key: 'nuevo_campo',
    type: 'string',
    required: false,
    description: 'Campo completamente nuevo'
  }
])
```

### Eliminar Definición Específica
```javascript
// DELETE /json/definitions/{entidad}/{json_field}/{key}?empresa_id={id}
async function eliminarDefinicionCampo(entidad, campoJson, clave) {
  const response = await fetch(`${API_BASE}/json/definitions/${entidad}/${campoJson}/${clave}?empresa_id=${empresaId}`, {
    method: 'DELETE'
  })
  return await response.json()
}

// Ejemplo
await eliminarDefinicionCampo('solicitante', 'info_extra', 'profesion')
```

### Eliminar Todas las Definiciones
```javascript
// DELETE /json/definitions/{entidad}/{json_field}?empresa_id={id}
async function eliminarTodasDefiniciones(entidad, campoJson) {
  const response = await fetch(`${API_BASE}/json/definitions/${entidad}/${campoJson}?empresa_id=${empresaId}`, {
    method: 'DELETE'
  })
  return await response.json()
}

// Ejemplo
await eliminarTodasDefiniciones('solicitante', 'info_extra')
```

---

## 🔍 2. Obtener Esquemas de Campos

### Esquema Completo por Entidad (⭐ Recomendado)
```javascript
// GET /schema/{entidad}?empresa_id={id}
async function obtenerEsquemaCompleto(entidad) {
  const response = await fetch(`${API_BASE}/schema/${entidad}?empresa_id=${empresaId}`)
  return await response.json()
}

// Ejemplo de uso
const esquema = await obtenerEsquemaCompleto('solicitante')
```

**Respuesta:**
```json
{
  "ok": true,
  "data": {
    "entidad": "solicitante",
    "tabla": "solicitantes",
    "json_column": "info_extra",
    "campos_fijos": [
      {
        "name": "nombre",
        "type": "string",
        "required": true,
        "description": "Nombre completo"
      }
    ],
    "campos_dinamicos": [
      {
        "key": "profesion",
        "type": "string",
        "required": true,
        "description": "Profesión del solicitante"
      },
      {
        "key": "experiencia_años",
        "type": "number",
        "required": false,
        "description": "Años de experiencia"
      },
      {
        "key": "nivel_educativo",
        "type": "string",
        "required": true,
        "list_values": ["primaria", "secundaria", "tecnico", "universitario", "posgrado"],
        "description": "Nivel educativo alcanzado"
      }
    ]
  }
}
```

### Esquema Solo de Campos JSON
```javascript
// GET /json/schema/{entidad}/{json_field}?empresa_id={id}
async function obtenerEsquemaJSON(entidad, campoJson) {
  const response = await fetch(`${API_BASE}/json/schema/${entidad}/${campoJson}?empresa_id=${empresaId}`)
  return await response.json()
}

// Ejemplo
const esquemaJSON = await obtenerEsquemaJSON('solicitante', 'info_extra')
```

---

## 📖 3. Leer Datos JSON

### Leer Campo JSON Completo
```javascript
// GET /json/{entidad}/{record_id}/{json_field}?empresa_id={id}
async function leerCampoJSON(entidad, recordId, campoJson) {
  const response = await fetch(`${API_BASE}/json/${entidad}/${recordId}/${campoJson}?empresa_id=${empresaId}`)
  return await response.json()
}

// Ejemplo
const datos = await leerCampoJSON('solicitante', 123, 'info_extra')
// Respuesta: { "ok": true, "data": { "profesion": "Ingeniero", "experiencia_años": 5 } }
```

### Leer Clave Específica del JSON
```javascript
// GET /json/{entidad}/{record_id}/{json_field}?empresa_id={id}&path={clave}
async function leerClaveJSON(entidad, recordId, campoJson, clave) {
  const response = await fetch(`${API_BASE}/json/${entidad}/${recordId}/${campoJson}?empresa_id=${empresaId}&path=${clave}`)
  return await response.json()
}

// Ejemplo
const profesion = await leerClaveJSON('solicitante', 123, 'info_extra', 'profesion')
// Respuesta: { "ok": true, "data": "Ingeniero" }
```

---

## ✏️ 4. Actualizar Datos JSON

### Actualizar Una Clave Específica
```javascript
// PATCH /json/{entidad}/{record_id}/{json_field}?empresa_id={id}
async function actualizarClaveJSON(entidad, recordId, campoJson, clave, valor, validar = true) {
  const response = await fetch(`${API_BASE}/json/${entidad}/${recordId}/${campoJson}?empresa_id=${empresaId}&validate=${validar}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      path: clave,
      value: valor
    })
  })
  return await response.json()
}

// Ejemplo
await actualizarClaveJSON('solicitante', 123, 'info_extra', 'profesion', 'Ingeniero de Software')
```

### Actualizar Múltiples Campos (Merge)
```javascript
async function actualizarVariasClavesJSON(entidad, recordId, campoJson, datos, validar = true) {
  const response = await fetch(`${API_BASE}/json/${entidad}/${recordId}/${campoJson}?empresa_id=${empresaId}&validate=${validar}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      value: datos
    })
  })
  return await response.json()
}

// Ejemplo
await actualizarVariasClavesJSON('solicitante', 123, 'info_extra', {
  profesion: 'Ingeniero de Software',
  experiencia_años: 8,
  nivel_educativo: 'universitario'
})
```

---

## 🗑️ 5. Eliminar Datos JSON

### Eliminar Una Clave
```javascript
// DELETE /json/{entidad}/{record_id}/{json_field}?empresa_id={id}&path={clave}
async function eliminarClaveJSON(entidad, recordId, campoJson, clave) {
  const response = await fetch(`${API_BASE}/json/${entidad}/${recordId}/${campoJson}?empresa_id=${empresaId}&path=${clave}`, {
    method: 'DELETE'
  })
  return await response.json()
}

// Ejemplo
await eliminarClaveJSON('solicitante', 123, 'info_extra', 'experiencia_años')
```

---

## 🏗️ 6. Entidades y Campos Disponibles

| **Entidad** | **JSON Field** | **Descripción** | **Ejemplo de Uso** |
|-------------|----------------|-----------------|-------------------|
| `solicitante` | `info_extra` | Información adicional del solicitante | Profesión, experiencia, educación |
| `ubicacion` | `detalle_direccion` | Detalles de dirección | Tipo vivienda, arrendador, servicios |
| `actividad_economica` | `detalle_actividad` | Detalles de actividad económica | Sector, cargo, empresa, ingresos |
| `informacion_financiera` | `detalle_financiera` | Información financiera detallada | Otros ingresos, gastos, patrimonio |
| `referencia` | `detalle_referencia` | Detalles de referencias | Relación, conoce desde, comentarios |
| `solicitud` | `detalle_credito` | Detalles del crédito solicitado | Destino, garantías, observaciones |
| `tipo_credito` | `fields` | Campos del tipo de crédito | Configuración dinámica por tipo |

---

## 🛠️ 7. Utilidades y Helpers

### Clase Helper para Campos Dinámicos
```javascript
class CamposDinamicosAPI {
  constructor(baseUrl, empresaId) {
    this.baseUrl = baseUrl
    this.empresaId = empresaId
  }

  async obtenerEsquema(entidad) {
    const response = await fetch(`${this.baseUrl}/schema/${entidad}?empresa_id=${this.empresaId}`)
    const result = await response.json()
    if (!result.ok) throw new Error(result.error)
    return result.data
  }

  async leerDatos(entidad, recordId, campoJson, clave = null) {
    const pathParam = clave ? `&path=${clave}` : ''
    const response = await fetch(`${this.baseUrl}/json/${entidad}/${recordId}/${campoJson}?empresa_id=${this.empresaId}${pathParam}`)
    const result = await response.json()
    if (!result.ok) throw new Error(result.error)
    return result.data
  }

  async guardarDatos(entidad, recordId, campoJson, datos, clave = null, validar = true) {
    const body = clave
      ? { path: clave, value: datos }
      : { value: datos }

    const response = await fetch(`${this.baseUrl}/json/${entidad}/${recordId}/${campoJson}?empresa_id=${this.empresaId}&validate=${validar}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })

    const result = await response.json()
    if (!result.ok) throw new Error(result.error)
    return result.data
  }

  async eliminarClave(entidad, recordId, campoJson, clave) {
    const response = await fetch(`${this.baseUrl}/json/${entidad}/${recordId}/${campoJson}?empresa_id=${this.empresaId}&path=${clave}`, {
      method: 'DELETE'
    })

    const result = await response.json()
    if (!result.ok) throw new Error(result.error)
    return result.data
  }
}

// Uso
const api = new CamposDinamicosAPI('http://localhost:5000', 1)
```

### Generador de Formularios Dinámicos
```javascript
function generarFormularioDinamico(esquema) {
  const { campos_dinamicos } = esquema

  return campos_dinamicos.map(campo => {
    const input = {
      key: campo.key,
      label: campo.description || campo.key,
      type: campo.type,
      required: campo.required,
      defaultValue: campo.default_value
    }

    // Si tiene lista de valores, es un select
    if (campo.list_values && Array.isArray(campo.list_values)) {
      input.type = 'select'
      input.options = campo.list_values
    }

    return input
  })
}

// Ejemplo de uso
const esquema = await api.obtenerEsquema('solicitante')
const formulario = generarFormularioDinamico(esquema)
```

---

## 🔧 8. Validación y Manejo de Errores

### Validación Automática
```javascript
// Activar validación con validate=true
try {
  await api.guardarDatos('solicitante', 123, 'info_extra', {
    profesion: 'Ingeniero',
    campo_no_permitido: 'valor'  // Esto generará error
  }, null, true)  // validar = true
} catch (error) {
  console.error('Error de validación:', error.message)
  // "Clave no permitida: campo_no_permitido"
}
```

### Manejo de Errores Comunes
```javascript
async function manejarErroresComunes(operacion) {
  try {
    return await operacion()
  } catch (error) {
    if (error.message.includes('empresa_id es requerido')) {
      alert('Error: ID de empresa no configurado')
    } else if (error.message.includes('Clave no permitida')) {
      alert('Error: Campo no permitido en el esquema')
    } else if (error.message.includes('Entidad no soportada')) {
      alert('Error: Entidad no válida')
    } else {
      alert(`Error: ${error.message}`)
    }
  }
}
```

---

## 📝 9. Ejemplos Prácticos

### Formulario de Solicitante
```javascript
async function configurarFormularioSolicitante(recordId) {
  const api = new CamposDinamicosAPI('http://localhost:5000', 1)

  // 1. Obtener esquema
  const esquema = await api.obtenerEsquema('solicitante')

  // 2. Obtener datos existentes
  const datosActuales = await api.leerDatos('solicitante', recordId, 'info_extra')

  // 3. Generar formulario
  const formulario = generarFormularioDinamico(esquema)

  // 4. Prellenar con datos existentes
  formulario.forEach(campo => {
    campo.value = datosActuales[campo.key] || campo.defaultValue
  })

  return formulario
}
```

### Guardar Formulario
```javascript
async function guardarFormularioSolicitante(recordId, datosFormulario) {
  const api = new CamposDinamicosAPI('http://localhost:5000', 1)

  try {
    await api.guardarDatos('solicitante', recordId, 'info_extra', datosFormulario, null, true)
    alert('Datos guardados correctamente')
  } catch (error) {
    alert(`Error al guardar: ${error.message}`)
  }
}
```

---

## ⚠️ 10. Limitaciones y Consideraciones

### Limitaciones Técnicas
- **Solo primer nivel:** Los campos JSON solo soportan claves de primer nivel (sin anidación con puntos)
- **Empresa ID obligatorio:** Todas las requests requieren `empresa_id`
- **Validación opcional:** Se debe activar explícitamente con `validate=true`

### Buenas Prácticas
1. **Siempre usar validación** en producción (`validate=true`)
2. **Cachear esquemas** para evitar múltiples requests
3. **Manejar errores** apropiadamente en el UI
4. **Usar headers** para empresa_id cuando sea posible
5. **Validar datos** en frontend antes de enviar

### Consideraciones de Performance
```javascript
// ✅ Cachear esquemas
const schemaCache = new Map()

async function obtenerEsquemaCacheado(entidad) {
  if (!schemaCache.has(entidad)) {
    const esquema = await api.obtenerEsquema(entidad)
    schemaCache.set(entidad, esquema)
  }
  return schemaCache.get(entidad)
}
```

---

## 🎯 11. Configuración Recomendada

### Variables de Entorno
```javascript
// config.js
export const CONFIG = {
  API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  EMPRESA_ID: process.env.REACT_APP_EMPRESA_ID || '1',
  VALIDAR_JSON: process.env.NODE_ENV === 'production'
}
```

### Instancia Global
```javascript
// api.js
import { CONFIG } from './config'

export const camposDinamicosAPI = new CamposDinamicosAPI(
  CONFIG.API_BASE_URL,
  CONFIG.EMPRESA_ID
)
```

---

## 🎯 **Casos de Uso Prácticos**

### **Caso 1: Administrador configurando nuevos campos**
```javascript
// 1. El admin quiere agregar un campo "salario" a solicitantes
await fetch('http://localhost:5000/json/definitions/solicitante/info_extra?empresa_id=1', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    definitions: [{
      key: 'salario',
      type: 'number',
      required: true,
      description: 'Salario mensual en pesos'
    }]
  })
})

// 2. El frontend detecta automáticamente el nuevo campo
const esquema = await fetch('/json/schema/solicitante/info_extra?empresa_id=1')
// Ahora incluye el campo "salario" automáticamente
```

### **Caso 2: Usuario llenando formulario dinámico**
```javascript
// 1. Frontend consulta qué campos mostrar
const response = await fetch('/json/schema/solicitante/info_extra?empresa_id=1')
const { data: campos } = await response.json()

// 2. Genera formulario dinámicamente
campos.forEach(campo => {
  // Crear input según campo.type, campo.required, etc.
})

// 3. Usuario llena y guarda
await fetch('/json/solicitante/123/info_extra?empresa_id=1&validate=true', {
  method: 'PATCH',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    value: {
      profesion: 'Ingeniero',
      salario: 5000000,
      experiencia_años: 3
    }
  })
})
```

### **Caso 3: Modificar configuración existente**
```javascript
// Eliminar un campo que ya no se usa
await fetch('/json/definitions/solicitante/info_extra/campo_obsoleto?empresa_id=1', {
  method: 'DELETE'
})

// Agregar nuevos campos manteniendo los existentes
await fetch('/json/definitions/solicitante/info_extra?empresa_id=1', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    definitions: [{
      key: 'telefono_emergencia',
      type: 'string',
      required: false,
      description: 'Teléfono de contacto de emergencia'
    }]
  })
})
```

---

## 🚀 **¡Listo para usar!**

Esta guía te permitirá implementar completamente el manejo de campos dinámicos en tu frontend. Los campos se configuran desde la base de datos y aparecen automáticamente en tu interfaz sin necesidad de cambiar código!

**Ventajas:**
- ✅ **Sin deployments** para agregar campos
- ✅ **Configuración por empresa** (multi-tenant)
- ✅ **Validación automática** de datos
- ✅ **Formularios dinámicos** que se adaptan automáticamente

🚀

## 🚀 Creación de Registro Completo (Recomendado)

### Endpoint Principal
```
POST /solicitantes/crear-registro-completo
```

Este endpoint permite crear **todo el registro en una sola request**, evitando la complejidad de manejar IDs entre requests.

### Estructura de Datos
```javascript
{
  "solicitante": {
    "nombres": "Juan Carlos",
    "primer_apellido": "Pérez",
    "segundo_apellido": "García",
    "tipo_documento": "CC",
    "numero_documento": "12345678",
    "fecha_nacimiento": "1990-05-15",
    "genero": "M",
    "estado_civil": "Soltero",
    "info_extra": {
      "campo_dinamico_1": "valor1",
      "campo_dinamico_2": "valor2"
    }
  },
  "ubicaciones": [
    {
      "ciudad_residencia": "Bogotá",
      "departamento_residencia": "Cundinamarca",
      "detalle_direccion": "Calle 123 # 45-67",
      "info_extra": {
        "tiempo_residencia": "5 años"
      }
    }
  ],
  "actividad_economica": {
    "tipo_actividad": "Empleado",
    "empresa": "TechCorp",
    "cargo": "Desarrollador",
    "ingresos_mensuales": 5000000,
    "info_extra": {
      "antiguedad": "3 años"
    }
  },
  "informacion_financiera": {
    "ingresos_mensuales": 5000000,
    "gastos_mensuales": 3000000,
    "ahorros": 10000000,
    "info_extra": {
      "fuente_ingresos": "Salario"
    }
  },
  "referencias": [
    {
      "nombre": "María López",
      "telefono": "3001234567",
      "tipo_relacion": "Familiar",
      "info_extra": {
        "tiempo_conocido": "10 años"
      }
    }
  ],
  "solicitudes": [
    {
      "tipo_credito": "Personal",
      "monto_solicitado": 20000000,
      "plazo_meses": 24,
      "info_extra": {
        "destino_credito": "Educación"
      }
    }
  ]
}
```

### Ejemplo de Uso (JavaScript)
```javascript
async function crearRegistroCompleto(datosCompletos) {
  try {
    const response = await fetch('/solicitantes/crear-registro-completo?empresa_id=1', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Empresa-Id': '1'
      },
      body: JSON.stringify(datosCompletos)
    });

    const resultado = await response.json();

    if (resultado.ok) {
      console.log('✅ Registro completo creado:', resultado.data);
      console.log('📊 Resumen:', resultado.data.resumen);
      return resultado.data;
    } else {
      console.error('❌ Error:', resultado.error);
      throw new Error(resultado.error);
    }
  } catch (error) {
    console.error('💥 Error en la request:', error);
    throw error;
  }
}

// Uso
const datosCompletos = {
  solicitante: {
    nombres: "Juan Carlos",
    primer_apellido: "Pérez",
    // ... más campos
  },
  ubicaciones: [
    {
      ciudad_residencia: "Bogotá",
      departamento_residencia: "Cundinamarca"
    }
  ],
  // ... otras entidades
};

crearRegistroCompleto(datosCompletos)
  .then(data => {
    console.log('Registro creado con ID:', data.solicitante.id);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

### Ventajas de este Enfoque
1. **Una sola request** - No necesitas manejar IDs entre requests
2. **Transaccional** - Si falla algo, nada se guarda
3. **Más simple** - El frontend solo envía todos los datos de una vez
4. **Mejor UX** - El usuario ve el resultado completo inmediatamente
5. **Menos errores** - No hay problemas de sincronización

### Respuesta del Servidor
```javascript
{
  "ok": true,
  "data": {
    "solicitante": {
      "id": 123,
      "nombres": "Juan Carlos",
      // ... todos los campos
    },
    "ubicaciones": [
      {
        "id": 456,
        "solicitante_id": 123,
        // ... todos los campos
      }
    ],
    "actividad_economica": {
      "id": 789,
      "solicitante_id": 123,
      // ... todos los campos
    },
    "informacion_financiera": {
      "id": 101,
      "solicitante_id": 123,
      // ... todos los campos
    },
    "referencias": [
      {
        "id": 202,
        "solicitante_id": 123,
        // ... todos los campos
      }
    ],
    "solicitudes": [
      {
        "id": 303,
        "solicitante_id": 123,
        // ... todos los campos
      }
    ],
    "resumen": {
      "solicitante_id": 123,
      "total_ubicaciones": 1,
      "tiene_actividad_economica": true,
      "tiene_informacion_financiera": true,
      "total_referencias": 1,
      "total_solicitudes": 1
    }
  },
  "message": "Registro completo creado exitosamente. Solicitante ID: 123"
}
```

### Campos Opcionales
- **Ubicaciones**: Si no envías `ubicaciones` o es un array vacío, no se crean ubicaciones
- **Actividad económica**: Si no envías `actividad_economica` o es un objeto vacío, no se crea
- **Información financiera**: Si no envías `informacion_financiera` o es un objeto vacío, no se crea
- **Referencias**: Si no envías `referencias` o es un array vacío, no se crean referencias
- **Solicitudes**: Si no envías `solicitudes` o es un array vacío, no se crean solicitudes

**Solo el solicitante es obligatorio.**
