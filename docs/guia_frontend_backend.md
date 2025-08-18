# Guía Frontend → Backend - API de Solicitudes de Crédito (Campos Dinámicos)

> **Objetivo:** Conectar frontend con la API Flask + Supabase para crear solicitudes completas.
> **Arquitectura:** Frontend consulta esquemas → Genera formularios dinámicos → Backend valida → Guarda en Supabase (multi-tenant)
> **Ventaja clave:** Los campos JSON son totalmente dinámicos y configurables sin cambiar código frontend.

---

## Configuración Inicial

### Headers Obligatorios
```javascript
const headers = {
  'Content-Type': 'application/json',
  // Opcional: si prefieres header en lugar de query param
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

## Catálogo json_field_definition (Endpoints)

Estos endpoints exponen las definiciones configuradas en la tabla `json_field_definition` para que el frontend construya formularios dinámicos.

- GET `/schema/{entidad}?empresa_id={id}`
  - Recomendado. Devuelve esquema completo agrupado por entidad: campos fijos + dinámicos del JSON asociado a esa entidad.
  - Ej.: `/schema/solicitante?empresa_id=1`.

- GET `/json/schema/{entidad}/{json_column}?empresa_id={id}`
  - Legacy/directo a `json_field_definition`. Devuelve solo los campos dinámicos de una columna JSON específica.
  - Ej.: `/json/schema/solicitante/info_extra?empresa_id=1`.

Respuesta típica (resumida):
```json
// /schema/ubicacion?empresa_id=1
{
  "ok": true,
  "data": {
    "entidad": "ubicacion",
    "tabla": "ubicacion",
    "json_column": "detalle_direccion",
    "campos_fijos": [...],
    "campos_dinamicos": [
      {"key":"direccion_residencia","type":"string","required":true},
      {"key":"tipo_vivienda","type":"string","list_values":["propia","familiar","arrendada"]}
    ]
  }
}
```

Notas:
- Debes enviar `empresa_id` en header `X-Empresa-Id` o como query param.
- El endpoint `/schema/{entidad}` usa el mapeo interno entidad→json_column para agrupar automáticamente por entidad.

## Estrategia: Formularios Dinámicos

### 1. Frontend Consulta Esquema Completo (Fijos + Dinámicos)
```javascript
// NUEVO: Obtener esquema completo (recomendado)
const obtenerEsquemaCompleto = async (entidad) => {
  const response = await fetch(`${API_BASE}/schema/${entidad}?empresa_id=${empresaId}`)
  const result = await response.json()

  if (!result.ok) {
    console.error(`Error obteniendo esquema completo ${entidad}:`, result.error)
    return { campos_fijos: [], campos_dinamicos: [] }
  }

  const schema = result.data

  // Validar campos dinámicos
  const camposDinamicosLimpios = validarEsquema(schema.campos_dinamicos || [])

  return {
    entidad: schema.entidad,
    tabla: schema.tabla,
    json_column: schema.json_column,
    campos_fijos: schema.campos_fijos || [],
    campos_dinamicos: camposDinamicosLimpios,
    total_campos: schema.total_campos
  }
}

// LEGACY: Solo campos dinámicos (mantener para compatibilidad)
const obtenerEsquema = async (entidad, campoJson) => {
  const response = await fetch(`${API_BASE}/json/schema/${entidad}/${campoJson}?empresa_id=${empresaId}`)
  const result = await response.json()

  if (!result.ok) {
    console.error(`Error obteniendo esquema ${entidad}/${campoJson}:`, result.error)
    return []
  }

  const esquemaLimpio = validarEsquema(result.data || [])
  return esquemaLimpio
}
```

### 2. Frontend Genera Formularios (Versión Actualizada)
```javascript
const generarFormulario = (esquema) => {
  return esquema.map(campo => {
    const base = {
      name: campo.key,
      type: campo.type,
      required: campo.required,
      description: campo.description,
      defaultValue: campo.default_value
    }

    // Procesar list_values según el tipo
    if (campo.list_values) {
      if (campo.type === 'string' && Array.isArray(campo.list_values)) {
        // Enum simple: ["opcion1", "opcion2"]
        base.options = campo.list_values
      } else if (campo.type === 'object' && Array.isArray(campo.list_values)) {
        // Objeto con estructura: [{"key":"nombre","type":"string",...}]
        base.structure = campo.list_values
      } else if (campo.type === 'array' && campo.list_values.item_structure) {
        // Array de objetos: {"item_structure": [...]}
        base.itemStructure = campo.list_values.item_structure
      }
    }

    return base
  })
}
```

### 3. Frontend Envía Solo Campos Presentes
```javascript
const enviarSoloPresentes = (formData, esquema) => {
  const camposPermitidos = esquema.map(c => c.key)
  const soloPresentes = {}

  Object.keys(formData).forEach(key => {
    if (camposPermitidos.includes(key) && formData[key] !== null && formData[key] !== '') {
      soloPresentes[key] = formData[key]
    }
  })

  return soloPresentes
}

// Helper para manejar campos objeto
const procesarObjetoAnidado = (campo, valores = {}) => {
  if (campo.type !== 'object') return valores[campo.key]

  // Si tiene estructura definida en list_values
  if (campo.list_values && Array.isArray(campo.list_values)) {
    const objetoCompleto = {}
    campo.list_values.forEach(subcampo => {
      const valor = valores[`${campo.key}.${subcampo.key}`]
      if (valor !== undefined && valor !== null && valor !== '') {
        objetoCompleto[subcampo.key] = valor
      }
    })
    return Object.keys(objetoCompleto).length > 0 ? objetoCompleto : undefined
  }

  // Si es objeto libre, retornar como está
  return valores[campo.key]
}

// Componente para arrays dinámicos
const DynamicArrayEditor = ({ name, itemStructure, valores = [] }) => {
  const [items, setItems] = useState(valores)

  const agregarItem = () => {
    const nuevoItem = {}
    itemStructure.forEach(field => {
      nuevoItem[field.key] = field.type === 'number' ? 0 : ''
    })
    setItems([...items, nuevoItem])
  }

  const eliminarItem = (index) => {
    setItems(items.filter((_, i) => i !== index))
  }

  const actualizarItem = (index, key, valor) => {
    const nuevosItems = [...items]
    nuevosItems[index][key] = valor
    setItems(nuevosItems)
  }

  return (
    <div className="array-editor">
      <label>{name}:</label>
      {items.map((item, index) => (
        <div key={index} className="array-item">
          {itemStructure.map(field => (
            <input
              key={field.key}
              type={field.type === 'number' ? 'number' : 'text'}
              placeholder={field.description || field.key}
              value={item[field.key] || ''}
              onChange={(e) => actualizarItem(index, field.key, e.target.value)}
              required={field.required}
            />
          ))}
          <button type="button" onClick={() => eliminarItem(index)}>Eliminar</button>
        </div>
      ))}
      <button type="button" onClick={agregarItem}>Agregar {name}</button>
      <input type="hidden" name={name} value={JSON.stringify(items)} />
    </div>
  )
}

// Helper para procesar arrays anidados
const procesarArrayAnidado = (campo, valores = {}) => {
  if (campo.type !== 'array') return valores[campo.key]

  const valorString = valores[campo.key]
  if (!valorString) return undefined

  try {
    const array = JSON.parse(valorString)
    return Array.isArray(array) && array.length > 0 ? array : undefined
  } catch {
    return undefined
  }
}
```

---

## 1. SOLICITANTE (Datos Personales)

> **Estrategia:** Campos de BD fijos + JSON dinámico consultado al cargar formulario

### Campos de Base de Datos (Obligatorios)
```javascript
const solicitanteBase = {
  nombres: "Juan Carlos",                    // string, requerido
  primer_apellido: "Pérez",                  // string, requerido
  segundo_apellido: "García",                // string, requerido
  tipo_identificacion: "cc",                 // string, requerido
  numero_documento: "123456789",             // string, requerido
  fecha_nacimiento: "1990-05-15",           // string YYYY-MM-DD, requerido
  genero: "M",                              // string (M/F), requerido
  correo: "juan@email.com"                  // string, requerido
}
```

### Frontend → Backend
```javascript
// Paso 1: Crear solicitante base
const crearSolicitante = async (datos) => {
  const response = await fetch(`${API_BASE}/solicitantes/?empresa_id=${empresaId}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(datos)
  })
  const result = await response.json()
  return result.data.id // Guardar este ID para siguientes pasos
}
```

### Campos JSON Dinámicos (Consultados Dinámicamente)
```javascript
// Paso 2A: Consultar qué campos están disponibles
const esquemaSolicitante = await obtenerEsquema('solicitante', 'info_extra')
/*
Ejemplo de respuesta:
[
  { key: "fecha_expedicion", type: "string", required: false, description: "Fecha YYYY-MM-DD" },
  { key: "estado_civil", type: "string", required: false, list_values: ["soltero","casado","viudo","divorciado","union_libre"] },
  { key: "nivel_estudio", type: "string", required: false, list_values: ["primaria","secundaria","tecnico","tecnologo","profesional","posgrado"] },
  { key: "personas_a_cargo", type: "integer", required: false },
  // ... más campos que se puedan agregar en el futuro sin cambiar frontend
]
*/

// Paso 2B: Generar formulario dinámico
const camposSolicitante = generarFormulario(esquemaSolicitante)

// Paso 2C: Usuario llena formulario, frontend envía solo campos con valor
const datosLlenados = {
  fecha_expedicion: "2021-03-10",
  estado_civil: "soltero",
  nivel_estudio: "tecnico",
  profesion: "Analista"
  // Nota: solo campos que el usuario llenó, no todos los posibles
}

const datosLimpios = enviarSoloPresentes(datosLlenados, esquemaSolicitante)

// Paso 2D: Enviar con validación automática
const llenarDatosAdicionales = async (solicitanteId, datos) => {
  await fetch(`${API_BASE}/json/solicitante/${solicitanteId}/info_extra?empresa_id=${empresaId}&validate=true`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify({ value: datos })
  })
}
```

---

## 2. UBICACIÓN (Residencia)

### Campos de Base de Datos (Obligatorios)
```javascript
const ubicacionBase = {
  solicitante_id: solicitanteId,             // number, requerido
  ciudad_residencia: "Medellín",             // string, requerido
  departamento_residencia: "Antioquia"       // string, requerido
}
```

### Frontend → Backend
```javascript
// Paso 3: Crear ubicación base
const crearUbicacion = async (datos) => {
  const response = await fetch(`${API_BASE}/ubicaciones/?empresa_id=${empresaId}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(datos)
  })
  const result = await response.json()
  return result.data.id
}
```

### Campos JSON Dinámicos (Direcciones y Contacto)
```javascript
const ubicacionJSON = {
  direccion_residencia: "Cra 50 # 12-34",   // string, requerido
  telefono: "6041234567",                    // string
  celular: "3001234567",                     // string
  correo_personal: "juan@correo.com",        // string
  tipo_vivienda: "arrendada",                // enum: propia|familiar|arrendada
  arrendador: {                              // object (si tipo_vivienda = "arrendada")
    nombre: "Carlos Pérez",
    telefono: "3009998888",
    ciudad: "Medellín",
    departamento: "Antioquia"
  },
  valor_mensual_arriendo: 1200000,           // number (si arrendada)
  id_autenticacion: "abc-123",               // string
  recibir_correspondencia: "personal"        // enum: personal|laboral
}

// Paso 4: Llenar detalles de dirección
const llenarDireccion = async (ubicacionId, datos) => {
  await fetch(`${API_BASE}/json/ubicacion/${ubicacionId}/detalle_direccion?empresa_id=${empresaId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify({ value: datos })
  })
}
```

---

## 3. ACTIVIDAD ECONÓMICA (Laboral)

### Campos de Base de Datos (Obligatorios)
```javascript
const actividadBase = {
  solicitante_id: solicitanteId,             // number, requerido
  tipo_actividad: "empleado",                // string, requerido
  sector_economico: "servicios"              // string, requerido
}
```

### Frontend → Backend
```javascript
// Paso 5: Crear actividad económica base
const crearActividad = async (datos) => {
  const response = await fetch(`${API_BASE}/actividad_economica/?empresa_id=${empresaId}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(datos)
  })
  const result = await response.json()
  return result.data.id
}
```

### Campos JSON Dinámicos (Detalles Laborales)
```javascript
const actividadJSON = {
  empresa: "ACME S.A.",                      // string, requerido
  ciudad_empresa: "Bogotá",                  // string
  direccion_empresa: "Calle 10 # 5-20",     // string
  fecha_ingreso: "2022-01-15",              // string YYYY-MM-DD
  tipo_contrato: "indefinido",               // enum: fijo|indefinido|prestacion
  telefono_empresa: "6013334444",           // string
  correo_oficina: "juan@acme.com",          // string
  tiene_negocio_propio: false,              // boolean
  nit: "900123456",                         // string
  actividad_economica_principal: "Servicios", // string
  declara_renta: true,                      // boolean
  paga_impuestos_fuera: { aplica: false },  // object
  empresa_pagadora_pension: null,           // string
  fecha_pension: null                       // string YYYY-MM-DD
}

// Paso 6: Llenar detalles laborales
const llenarLaboral = async (actividadId, datos) => {
  await fetch(`${API_BASE}/json/actividad_economica/${actividadId}/detalle_actividad?empresa_id=${empresaId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify({ value: datos })
  })
}
```

---

## 4. INFORMACIÓN FINANCIERA (Ingresos/Egresos)

### Campos de Base de Datos (Obligatorios - Totales)
```javascript
const financieraBase = {
  solicitante_id: solicitanteId,             // number, requerido
  total_ingresos_mensuales: 3000000,         // number, requerido
  total_egresos_mensuales: 1500000,          // number, requerido
  total_activos: 50000000,                   // number, requerido
  total_pasivos: 20000000                    // number, requerido
}
```

### Frontend → Backend
```javascript
// Paso 7: Crear información financiera base
const crearFinanciera = async (datos) => {
  const response = await fetch(`${API_BASE}/informacion_financiera/?empresa_id=${empresaId}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(datos)
  })
  const result = await response.json()
  return result.data.id
}
```

### Campos JSON Dinámicos (Detalles Financieros)
```javascript
const financieraJSON = {
  detalle_otros_ingresos: [                  // array de objects
    { concepto: "arriendos", valor: 600000 },
    { concepto: "freelance", valor: 400000 }
  ],
  ingresos_fijos_pension: 0,                 // number
  ingresos_por_ventas: 0,                    // number
  ingresos_varios: 0,                        // number
  honorarios: 0,                             // number
  arriendos: 600000,                         // number
  ingresos_actividad_independiente: 0        // number
}

// Paso 8: Llenar detalles financieros
const llenarFinanciera = async (financieraId, datos) => {
  await fetch(`${API_BASE}/json/informacion_financiera/${financieraId}/detalle_financiera?empresa_id=${empresaId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify({ value: datos })
  })
}
```

---

## 5. REFERENCIAS (Contactos)

### Campos de Base de Datos (Obligatorios)
```javascript
const referenciaBase = {
  solicitante_id: solicitanteId,             // number, requerido
  tipo_referencia: "familiar"                // string, requerido
}
```

### Frontend → Backend
```javascript
// Paso 9: Crear referencia base
const crearReferencia = async (datos) => {
  const response = await fetch(`${API_BASE}/referencias/?empresa_id=${empresaId}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(datos)
  })
  const result = await response.json()
  return result.data.id
}
```

### Campos JSON Dinámicos (Datos de Contacto)
```javascript
const referenciaJSON = {
  nombre_completo: "Ana Pérez",              // string, requerido
  relacion: "Hermana",                       // string, requerido
  telefono: "3001112222",                    // string, requerido
  departamento: "Antioquia",                 // string
  ciudad: "Medellín",                        // string
  direccion: "Cl 50 # 40-20"                // string
}

// Paso 10: Llenar datos de referencia
const llenarReferencia = async (referenciaId, datos) => {
  await fetch(`${API_BASE}/json/referencia/${referenciaId}/detalle_referencia?empresa_id=${empresaId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify({ value: datos })
  })
}
```

---

## 6. SOLICITUD DE CRÉDITO (Final)

### Campos Completos (Base + JSON)
```javascript
const solicitudCompleta = {
  // Campos de BD (obligatorios)
  solicitante_id: solicitanteId,             // number, requerido
  created_by_user_id: 10,                   // number, requerido (debe existir en tabla usuarios)
  assigned_to_user_id: 10,                  // number, requerido
  estado: "abierta",                        // string, requerido

  // JSON dinámico
  detalle_credito: {
    monto: 12000000,                        // number, requerido
    plazo_meses: 48,                        // number, requerido
    observaciones: "Solicitud de crédito para vivienda", // string
    segundo_titular: {                      // object (opcional)
      nombres: "María González",
      documento: "987654321"
    },
    tipo_credito_id: "uuid-aqui",          // string UUID (opcional)
    garantia: "hipotecaria",               // enum: hipotecaria|prendaria|personal|libranza
    destino_credito: "vivienda",           // enum: vivienda|vehiculo|libre_inversion|educacion|consolidacion
    tasa_interes: 12.5,                    // number
    valor_cuota: 250000                    // number
  }
}
```

### Frontend → Backend
```javascript
// Paso 11: Crear solicitud completa
const crearSolicitud = async (datos) => {
  const response = await fetch(`${API_BASE}/solicitudes/?empresa_id=${empresaId}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(datos)
  })
  const result = await response.json()
  return result.data.id
}
```

---

## Flujo Dinámico Completo (Recomendado)

### 1. Cargar Esquemas Completos al Inicializar App
```javascript
const cargarEsquemas = async () => {
  const esquemas = {
    solicitante: await obtenerEsquemaCompleto('solicitante'),
    ubicacion: await obtenerEsquemaCompleto('ubicacion'),
    actividad: await obtenerEsquemaCompleto('actividad_economica'),
    financiera: await obtenerEsquemaCompleto('informacion_financiera'),
    referencia: await obtenerEsquemaCompleto('referencia'),
    solicitud: await obtenerEsquemaCompleto('solicitud')
  }

  // Debug: verificar esquemas cargados
  Object.keys(esquemas).forEach(key => {
    const schema = esquemas[key]
    console.log(`=== ${key.toUpperCase()} SCHEMA ===`)
    console.log(`Total campos: ${schema.total_campos} (${schema.campos_fijos.length} fijos + ${schema.campos_dinamicos.length} dinámicos)`)

    console.log('CAMPOS FIJOS:')
    schema.campos_fijos.forEach(campo => {
      console.log(`  ${campo.key} (${campo.type}) - ${campo.required ? 'requerido' : 'opcional'}`)
    })

    console.log('CAMPOS DINÁMICOS:')
    schema.campos_dinamicos.forEach(campo => {
      console.log(`  ${campo.key} (${campo.type}):`, campo.list_values)
      if (campo.type === 'object' && campo.list_values) {
        console.log('    → Structure:', Array.isArray(campo.list_values) ? 'Array' : 'Object')
      }
      if (campo.type === 'array' && campo.list_values) {
        console.log('    → Item structure:', campo.list_values.item_structure ? 'Defined' : 'Free')
      }
    })
  })

  // Guardar en estado global/context
  return esquemas
}

// Función para validar y limpiar esquemas problemáticos
const validarEsquema = (esquema) => {
  return esquema.map(campo => {
    // Verificar si list_values está correctamente estructurado
    if (campo.list_values) {
      try {
        // Si es string, intentar parsear como JSON
        if (typeof campo.list_values === 'string') {
          campo.list_values = JSON.parse(campo.list_values)
        }

        // Validar estructura según tipo
        if (campo.type === 'array') {
          // Para arrays, debe tener item_structure
          if (!campo.list_values.item_structure) {
            console.warn(`Campo ${campo.key}: array sin item_structure`, campo.list_values)
            campo.list_values = null // Tratar como array libre
          }
        } else if (campo.type === 'object') {
          // Para objetos, debe ser array de definiciones
          if (!Array.isArray(campo.list_values)) {
            console.warn(`Campo ${campo.key}: object sin array structure`, campo.list_values)
            campo.list_values = null // Tratar como objeto libre
          }
        } else if (campo.type === 'string') {
          // Para strings, debe ser array simple
          if (!Array.isArray(campo.list_values)) {
            console.warn(`Campo ${campo.key}: string sin array options`, campo.list_values)
            campo.list_values = null // Tratar como input libre
          }
        }
      } catch (e) {
        console.error(`Error parsing list_values for ${campo.key}:`, e)
        campo.list_values = null
      }
    }

    return campo
  })
}
```

### 2. Generar Formularios Completos (Fijos + Dinámicos)
```javascript
const FormularioCompleto = ({ schemaCompleto, onSubmit, valores = {} }) => {
  return (
    <form onSubmit={onSubmit}>
      {/* SECCIÓN: CAMPOS FIJOS */}
      <div className="campos-fijos">
        <h3>Información Básica</h3>
        {schemaCompleto.campos_fijos.map(campo => (
          <CampoFijo key={campo.key} campo={campo} valor={valores[campo.key]} />
        ))}
      </div>

      {/* SECCIÓN: CAMPOS DINÁMICOS */}
      <div className="campos-dinamicos">
        <h3>Información Adicional</h3>
        {schemaCompleto.campos_dinamicos.map(campo => (
          <CampoDinamico key={campo.key} campo={campo} valor={valores[schemaCompleto.json_column]?.[campo.key]} />
        ))}
      </div>

      <button type="submit">Guardar</button>
    </form>
  )
}

// Componente para campos fijos
const CampoFijo = ({ campo, valor }) => {
  switch (campo.type) {
    case 'string':
      return (
        <div className="field">
          <label>{campo.description}:</label>
          <input
            type="text"
            name={campo.key}
            defaultValue={valor}
            required={campo.required}
            placeholder={campo.description}
          />
        </div>
      )
    case 'number':
    case 'integer':
      return (
        <div className="field">
          <label>{campo.description}:</label>
          <input
            type="number"
            name={campo.key}
            defaultValue={valor}
            required={campo.required}
            placeholder={campo.description}
          />
        </div>
      )
    default:
      return (
        <div className="field">
          <label>{campo.description}:</label>
          <input
            type="text"
            name={campo.key}
            defaultValue={valor}
            required={campo.required}
          />
        </div>
      )
  }
}

// Componente para campos dinámicos (reutilizar lógica anterior)
const CampoDinamico = ({ campo, valor }) => {
  const formularioProcesado = generarFormulario([campo])

  return formularioProcesado.map(campoProcessed => {
    switch (campo.type) {
      case 'string':
        if (campo.options) {
          // Select/dropdown para enums
          return (
            <select name={campo.name} required={campo.required} key={campo.name}>
              <option value="">Seleccionar...</option>
              {campo.options.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          )
        }
        // Input text
        return <input type="text" name={campo.name} required={campo.required} key={campo.name} />

      case 'integer':
      case 'number':
        return <input type="number" name={campo.name} required={campo.required} key={campo.name} />

      case 'boolean':
        return <input type="checkbox" name={campo.name} key={campo.name} />

      case 'object':
        if (campo.structure) {
          // Objeto con estructura definida - crear sub-formulario
          return (
            <ObjectField
              key={campo.name}
              name={campo.name}
              structure={campo.structure}
              required={campo.required}
              description={campo.description}
            />
          )
        }
        // Objeto libre - JSON editor
        return <JsonEditor name={campo.name} description={campo.description} key={campo.name} />

      case 'array':
        if (campo.itemStructure) {
          // Array con estructura de items definida
          return (
            <DynamicArrayEditor
              key={campo.name}
              name={campo.name}
              itemStructure={campo.itemStructure}
              description={campo.description}
            />
          )
        }
        // Array libre
        return <ArrayEditor name={campo.name} key={campo.name} />

      default:
        return <input type="text" name={campo.name} key={campo.name} />
    }
  })
}

// Componente para campos objeto estructurados
const ObjectField = ({ name, structure, required, description }) => {
  return (
    <div className="object-field" key={name}>
      <label>{name}: {description && <small>({description})</small>}</label>
      <div className="object-inputs">
        {structure.map(subcampo => (
          <div key={subcampo.key} className="sub-field">
            <label>{subcampo.description || subcampo.key}:</label>
            <input
              name={`${name}.${subcampo.key}`}
              type={subcampo.type === 'number' ? 'number' : 'text'}
              placeholder={subcampo.description || subcampo.key}
              required={subcampo.required || false}
            />
          </div>
        ))}
      </div>
    </div>
  )
}
```

### 3. Envío Inteligente
```javascript
const enviarInteligente = async (entidad, id, campoJson, formData, esquema) => {
  // Filtrar solo campos que tienen valor
  const datosLimpios = enviarSoloPresentes(formData, esquema)

  // Validar tipos antes de enviar
  const datosValidados = validarTipos(datosLimpios, esquema)

  // Enviar con validación del backend
  return await fetch(`${API_BASE}/json/${entidad}/${id}/${campoJson}?empresa_id=${empresaId}&validate=true`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify({ value: datosValidados })
  })
}

const validarTipos = (datos, esquema) => {
  const validados = {}

  Object.keys(datos).forEach(key => {
    const campo = esquema.find(c => c.key === key)
    if (!campo) return

    let valor = datos[key]

    // Convertir tipos
    switch (campo.type) {
      case 'integer':
        valor = parseInt(valor, 10)
        break
      case 'number':
        valor = parseFloat(valor)
        break
      case 'boolean':
        valor = Boolean(valor)
        break
      case 'object':
      case 'array':
        if (typeof valor === 'string') {
          valor = JSON.parse(valor)
        }
        break
    }

    validados[key] = valor
  })

  return validados
}
```

### 4. Gestión de Cambios en Esquemas
```javascript
const manejarCambiosEsquema = async (entidadCambiada) => {
  // Re-cargar solo el esquema que cambió
  const nuevoEsquema = await obtenerEsquema(entidadCambiada.entidad, entidadCambiada.campo)

  // Actualizar estado/context
  updateEsquema(entidadCambiada.entidad, nuevoEsquema)

  // Re-renderizar formulario afectado
  reRenderFormulario(entidadCambiada.entidad)
}

// Cache con TTL para evitar consultas innecesarias
const esquemaCache = new Map()
const CACHE_TTL = 5 * 60 * 1000 // 5 minutos

const obtenerEsquemaConCache = async (entidad, campo) => {
  const key = `${entidad}_${campo}`
  const cached = esquemaCache.get(key)

  if (cached && (Date.now() - cached.timestamp) < CACHE_TTL) {
    return cached.data
  }

  const esquema = await obtenerEsquema(entidad, campo)
  esquemaCache.set(key, { data: esquema, timestamp: Date.now() })

  return esquema
}
```

---

## Flujo Estático (Para Referencia)

```javascript
const crearSolicitudCompleta = async (formulario) => {
  try {
    // 1-2. Solicitante
    const solicitanteId = await crearSolicitante(formulario.solicitante.base)
    await llenarDatosAdicionales(solicitanteId, formulario.solicitante.adicional)

    // 3-4. Ubicación
    const ubicacionData = { ...formulario.ubicacion.base, solicitante_id: solicitanteId }
    const ubicacionId = await crearUbicacion(ubicacionData)
    await llenarDireccion(ubicacionId, formulario.ubicacion.direccion)

    // 5-6. Actividad Económica
    const actividadData = { ...formulario.actividad.base, solicitante_id: solicitanteId }
    const actividadId = await crearActividad(actividadData)
    await llenarLaboral(actividadId, formulario.actividad.laboral)

    // 7-8. Información Financiera
    const financieraData = { ...formulario.financiera.base, solicitante_id: solicitanteId }
    const financieraId = await crearFinanciera(financieraData)
    await llenarFinanciera(financieraId, formulario.financiera.detalles)

    // 9-10. Referencias (múltiples)
    for (const ref of formulario.referencias) {
      const refData = { ...ref.base, solicitante_id: solicitanteId }
      const refId = await crearReferencia(refData)
      await llenarReferencia(refId, ref.contacto)
    }

    // 11. Solicitud Final
    const solicitudData = { ...formulario.solicitud, solicitante_id: solicitanteId }
    const solicitudId = await crearSolicitud(solicitudData)

    return { success: true, solicitudId }

  } catch (error) {
    console.error('Error creando solicitud:', error)
    return { success: false, error: error.message }
  }
}
```

---

## Ejemplo: Array de Objetos Anidados

### Configuración en BD
```sql
-- Campo: detalle_otros_ingresos (array de objetos)
UPDATE json_field_definition
SET type = 'array',
    required = false,
    list_values = '{
      "item_structure": [
        {"key":"concepto","type":"string","required":true,"description":"Tipo de ingreso (arriendos, freelance, etc.)"},
        {"key":"valor","type":"number","required":true,"description":"Valor mensual en pesos"}
      ]
    }'::jsonb,
    description = 'Lista de otros ingresos mensuales'
WHERE entity = 'informacion_financiera'
  AND json_column = 'detalle_financiera'
  AND key = 'detalle_otros_ingresos';
```

### Respuesta del Esquema
```javascript
// GET /json/schema/informacion_financiera/detalle_financiera?empresa_id=1
{
  key: "detalle_otros_ingresos",
  type: "array",
  required: false,
  list_values: {
    item_structure: [
      {key: "concepto", type: "string", required: true, description: "Tipo de ingreso (arriendos, freelance, etc.)"},
      {key: "valor", type: "number", required: true, description: "Valor mensual en pesos"}
    ]
  },
  description: "Lista de otros ingresos mensuales"
}
```

### Frontend Generado
```jsx
// El formulario genera automáticamente:
<DynamicArrayEditor
  name="detalle_otros_ingresos"
  itemStructure={[
    {key: "concepto", type: "string", required: true, description: "Tipo de ingreso"},
    {key: "valor", type: "number", required: true, description: "Valor mensual"}
  ]}
/>

// Que se renderiza como:
<div className="array-editor">
  <label>detalle_otros_ingresos:</label>

  {/* Item 1 */}
  <div className="array-item">
    <input type="text" placeholder="Tipo de ingreso" value="arriendos" required />
    <input type="number" placeholder="Valor mensual" value="600000" required />
    <button type="button">Eliminar</button>
  </div>

  {/* Item 2 */}
  <div className="array-item">
    <input type="text" placeholder="Tipo de ingreso" value="freelance" required />
    <input type="number" placeholder="Valor mensual" value="400000" required />
    <button type="button">Eliminar</button>
  </div>

  <button type="button">Agregar detalle_otros_ingresos</button>
  <input type="hidden" name="detalle_otros_ingresos" value='[{"concepto":"arriendos","valor":600000},{"concepto":"freelance","valor":400000}]' />
</div>
```

### Datos Enviados al Backend
```javascript
// El usuario llena el formulario y se envía:
{
  "detalle_otros_ingresos": [
    {"concepto": "arriendos", "valor": 600000},
    {"concepto": "freelance", "valor": 400000}
  ],
  "ingresos_fijos_pension": 0,
  "arriendos": 600000
}
```

---

## Ventajas del Enfoque Dinámico

### ✅ **Sin Cambios en Frontend**
```javascript
// ❌ Antes: campos hardcodeados
const camposEstaticos = {
  estado_civil: "soltero",
  profesion: "Analista"
  // Si agregas campo nuevo → tienes que cambiar frontend
}

// ✅ Ahora: campos consultados dinámicamente
const esquema = await obtenerEsquema('solicitante', 'info_extra')
const formulario = generarFormulario(esquema)
// Si agregas campo nuevo → aparece automáticamente en frontend
```

### ✅ **Configuración por Empresa**
```javascript
// Empresa 1 puede tener campos diferentes a Empresa 2
const esquemaEmpresa1 = await obtenerEsquema('solicitante', 'info_extra') // empresa_id=1
const esquemaEmpresa2 = await obtenerEsquema('solicitante', 'info_extra') // empresa_id=2
// Cada una ve solo sus campos configurados
```

### ✅ **Agregar Campos Sin Deploy**
```sql
-- Admin agrega un campo nuevo desde SQL
INSERT INTO json_field_definition (empresa_id, entity, json_column, key, type, required, description)
VALUES (1, 'solicitante', 'info_extra', 'categoria_cliente', 'string', false, 'VIP|Normal|Básico');

-- Frontend lo detecta automáticamente en la siguiente carga
```

### ✅ **Definir Objetos Anidados**
```sql
-- Opción 1: Estructura fija del objeto en list_values
UPDATE json_field_definition
SET list_values = '[
  {"key":"nombre","type":"string","required":true,"description":"Nombre del arrendador"},
  {"key":"telefono","type":"string","required":true,"description":"Teléfono de contacto"},
  {"key":"ciudad","type":"string","required":false,"description":"Ciudad"},
  {"key":"departamento","type":"string","required":false,"description":"Departamento"}
]'::jsonb
WHERE entity = 'ubicacion' AND json_column = 'detalle_direccion' AND key = 'arrendador';

-- Opción 2: Descripción textual simple (para objetos libres)
UPDATE json_field_definition
SET description = 'Objeto con: nombre (string), telefono (string), ciudad (string), departamento (string)',
    list_values = null
WHERE entity = 'ubicacion' AND json_column = 'detalle_direccion' AND key = 'arrendador';

-- Opción 3: Array de objetos con estructura definida
UPDATE json_field_definition
SET list_values = '{
  "item_structure": [
    {"key":"concepto","type":"string","required":true,"description":"Tipo de ingreso"},
    {"key":"valor","type":"number","required":true,"description":"Valor mensual"}
  ]
}'::jsonb
WHERE entity = 'informacion_financiera' AND json_column = 'detalle_financiera' AND key = 'detalle_otros_ingresos';
```

### ✅ **Validación Automática**
```javascript
// Backend valida automáticamente según json_field_definition
const response = await enviarInteligente('solicitante', id, 'info_extra', formData, esquema)
// Si el admin cambió reglas de validación → se aplican inmediatamente
```

---

## Validación de Campos JSON (Método Dinámico)

### Consultar Esquema Antes de Enviar
```javascript
const obtenerEsquema = async (entidad, campoJson) => {
  const response = await fetch(`${API_BASE}/json/schema/${entidad}/${campoJson}?empresa_id=${empresaId}`)
  const result = await response.json()
  return result.data // Array con definiciones de campos
}

// Ejemplo
const esquemaSolicitante = await obtenerEsquema('solicitante', 'info_extra')
/*
Retorna:
[
  { key: "estado_civil", type: "string", required: false, list_values: ["soltero","casado",...] },
  { key: "profesion", type: "string", required: false, list_values: null },
  ...
]
*/
```

### Validar al Enviar
```javascript
const enviarConValidacion = async (entidad, id, campo, datos) => {
  const url = `${API_BASE}/json/${entidad}/${id}/${campo}?empresa_id=${empresaId}&validate=true`
  const response = await fetch(url, {
    method: 'PATCH',
    headers,
    body: JSON.stringify({ value: datos })
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error) // "Clave no permitida: campo_invalido"
  }

  return response.json()
}
```

---

## Estructura de Formulario Sugerida

```javascript
const formularioCompleto = {
  solicitante: {
    base: {
      nombres: "",
      primer_apellido: "",
      segundo_apellido: "",
      tipo_identificacion: "",
      numero_documento: "",
      fecha_nacimiento: "",
      genero: "",
      correo: ""
    },
    adicional: {
      fecha_expedicion: "",
      nacionalidad: "",
      lugar_nacimiento: "",
      estado_civil: "",
      personas_a_cargo: 0,
      nivel_estudio: "",
      profesion: ""
    }
  },

  ubicacion: {
    base: {
      ciudad_residencia: "",
      departamento_residencia: ""
    },
    direccion: {
      direccion_residencia: "",
      telefono: "",
      celular: "",
      correo_personal: "",
      tipo_vivienda: "",
      arrendador: {},
      valor_mensual_arriendo: 0
    }
  },

  actividad: {
    base: {
      tipo_actividad: "",
      sector_economico: ""
    },
    laboral: {
      empresa: "",
      fecha_ingreso: "",
      tipo_contrato: "",
      // ... más campos
    }
  },

  financiera: {
    base: {
      total_ingresos_mensuales: 0,
      total_egresos_mensuales: 0,
      total_activos: 0,
      total_pasivos: 0
    },
    detalles: {
      detalle_otros_ingresos: [],
      ingresos_fijos_pension: 0,
      // ... más campos
    }
  },

  referencias: [
    {
      base: { tipo_referencia: "familiar" },
      contacto: { nombre_completo: "", relacion: "", telefono: "" }
    }
  ],

  solicitud: {
    created_by_user_id: 10,
    assigned_to_user_id: 10,
    estado: "abierta",
    detalle_credito: {
      monto: 0,
      plazo_meses: 0,
      observaciones: ""
    }
  }
}
```

---

## Manejo de Errores

```javascript
const manejarRespuesta = async (response) => {
  const data = await response.json()

  if (!data.ok) {
    // Errores comunes
    if (data.error.includes('foreign key')) {
      throw new Error('ID de usuario no válido')
    }
    if (data.error.includes('not found')) {
      throw new Error('Registro no encontrado')
    }
    if (data.error.includes('Clave no permitida')) {
      throw new Error(`Campo no válido: ${data.error}`)
    }

    throw new Error(data.error)
  }

  return data.data
}
```

---

---

## 🚀 Nuevas Rutas para Schemas Completos

### **Endpoint Principal (Recomendado):**
```
GET http://localhost:5000/schema/{entidad}?empresa_id={empresa_id}
```

### **Ejemplos para Postman:**

1. **Solicitante completo:**
```
GET http://localhost:5000/schema/solicitante?empresa_id=1
```

2. **Ubicación completa:**
```
GET http://localhost:5000/schema/ubicacion?empresa_id=1
```

3. **Actividad económica completa:**
```
GET http://localhost:5000/schema/actividad_economica?empresa_id=1
```

4. **Información financiera completa:**
```
GET http://localhost:5000/schema/informacion_financiera?empresa_id=1
```

5. **Referencias completas:**
```
GET http://localhost:5000/schema/referencia?empresa_id=1
```

6. **Solicitudes completas:**
```
GET http://localhost:5000/schema/solicitud?empresa_id=1
```

### **Respuesta del Nuevo Endpoint:**
```json
{
  "ok": true,
  "data": {
    "entidad": "ubicacion",
    "tabla": "ubicacion",
    "json_column": "detalle_direccion",
    "total_campos": 8,
    "campos_fijos": [
      {"key": "direccion", "type": "string", "required": true, "description": "Dirección principal"},
      {"key": "ciudad", "type": "string", "required": true, "description": "Ciudad"},
      {"key": "departamento", "type": "string", "required": true, "description": "Departamento"}
    ],
    "campos_dinamicos": [
      {"key": "direccion_residencia", "type": "string", "required": true, "description": "Dirección completa"},
      {"key": "tipo_vivienda", "type": "string", "required": true, "list_values": ["propia", "familiar", "arrendada"]},
      {"key": "arrendador", "type": "object", "required": false, "list_values": [
        {"key": "nombre", "type": "string", "required": true, "description": "Nombre del arrendador"},
        {"key": "telefono", "type": "string", "required": true, "description": "Teléfono contacto"}
      ]}
    ]
  }
}
```

### **Ventajas del Nuevo Endpoint:**
✅ **Un solo request** para obtener todo
✅ **Campos fijos + dinámicos** combinados
✅ **Metadata completa** (tabla, json_column, totales)
✅ **Información estructurada** para el frontend
✅ **Solo campos editables** (excluye IDs automáticos)

### **Campos Excluidos (Manejados por Backend):**
❌ `id` - Primary key autoincremental
❌ `empresa_id` - Se obtiene del query param
❌ `solicitante_id` - Foreign key (se maneja en contexto)
❌ `created_by_user_id` - Se obtiene del JWT
❌ `assigned_to_user_id` - Se maneja por lógica de negocio
❌ `created_at` / `updated_at` - Timestamps automáticos

---

## 🔧 Troubleshooting: Campos JSON Anidados

### Problema: Campos con `list_values` no se renderizan correctamente

**Síntomas:**
- Campos `object` aparecen como input simple en lugar de sub-formulario
- Campos `array` no muestran editor dinámico
- Console errors sobre JSON parsing

**Diagnóstico:**
```javascript
// Ejecutar en consola del navegador
const diagnosticar = async () => {
  const esquema = await obtenerEsquema('ubicacion', 'detalle_direccion')
  console.log('=== DIAGNÓSTICO ===')

  esquema.forEach(campo => {
    console.log(`\n${campo.key} (${campo.type}):`)
    console.log('  list_values:', campo.list_values)
    console.log('  tipo de list_values:', typeof campo.list_values)

    if (campo.type === 'object' && campo.list_values) {
      console.log('  ✓ Es array?', Array.isArray(campo.list_values))
      if (Array.isArray(campo.list_values)) {
        console.log('  ✓ Primer item:', campo.list_values[0])
      }
    }

    if (campo.type === 'array' && campo.list_values) {
      console.log('  ✓ Tiene item_structure?', !!campo.list_values.item_structure)
      if (campo.list_values.item_structure) {
        console.log('  ✓ Item structure:', campo.list_values.item_structure)
      }
    }
  })
}

diagnosticar()
```

**Soluciones Comunes:**

1. **Array mal estructurado (como `detalle_otros_ingresos`):**
```sql
-- Corregir en BD:
UPDATE json_field_definition
SET list_values = '{
  "item_structure": [
    {"key":"concepto","type":"string","required":true,"description":"Tipo de ingreso"},
    {"key":"valor","type":"number","required":true,"description":"Valor mensual"}
  ]
}'::jsonb
WHERE entity = 'informacion_financiera' AND key = 'detalle_otros_ingresos';
```

2. **Objeto con estructura incorrecta:**
```sql
-- Verificar que sea array de objetos:
UPDATE json_field_definition
SET list_values = '[
  {"key":"nombres","type":"string","required":true,"description":"Nombres completos"},
  {"key":"numero_documento","type":"string","required":true,"description":"Número de documento"}
]'::jsonb
WHERE entity = 'solicitud' AND key = 'segundo_titular';
```

3. **String con opciones malformadas:**
```sql
-- Asegurar que sea array simple:
UPDATE json_field_definition
SET list_values = '["soltero","casado","viudo","divorciado","union_libre"]'::jsonb
WHERE entity = 'solicitante' AND key = 'estado_civil';
```

### Debug Frontend en Vivo:
```javascript
// Agregar al componente para debug en tiempo real
const DebugFormulario = ({ esquema }) => {
  return (
    <div style={{background: '#f0f0f0', padding: '10px', margin: '10px'}}>
      <h4>🔍 Debug Esquema:</h4>
      {esquema.map(campo => (
        <div key={campo.key} style={{marginBottom: '5px'}}>
          <strong>{campo.key}</strong> ({campo.type})
          {campo.list_values && (
            <div style={{fontSize: '12px', marginLeft: '20px'}}>
              list_values: {JSON.stringify(campo.list_values, null, 2)}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
```

¡Con esta guía actualizada el frontend manejará correctamente todos los tipos de campos JSON anidados de tu BD!
