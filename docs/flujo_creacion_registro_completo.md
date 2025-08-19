# 📋 Flujo Completo - Crear Registro desde Frontend

> **Objetivo:** Guía paso a paso para crear un registro completo desde solicitante hasta referencias usando la API.
> **Orden:** Sigue este flujo exacto para crear todos los registros relacionados correctamente.

---

## 🎯 **Configuración Inicial**

```javascript
// Configuración base
const API_BASE = 'http://localhost:5000'
const empresaId = 1

// Headers para todas las requests
const headers = {
  'Content-Type': 'application/json',
  'X-Empresa-Id': empresaId.toString()
}
```

---

## 1️⃣ **CREAR SOLICITANTE**

### **Endpoint Base**
```
POST /solicitantes/?empresa_id=1
```

### **JSON a Enviar**
```json
{
  "nombre": "Juan",
  "apellido": "Pérez",
  "cedula": "12345678",
  "email": "juan@email.com",
  "telefono": "3001234567",
  "fecha_nacimiento": "1990-05-15",
  "empresa_id": 1
}
```

### **Respuesta Esperada**
```json
{
  "ok": true,
  "data": {
    "id": 123,
    "nombre": "Juan",
    "apellido": "Pérez",
    "cedula": "12345678",
    ...
  }
}
```

### **💾 Campos Dinámicos del Solicitante**
```
PATCH /json/solicitante/123/info_extra?empresa_id=1&validate=true
```

**JSON:**
```json
{
  "value": {
    "profesion": "Ingeniero de Software",
    "experiencia_años": 5,
    "nivel_educativo": "universitario",
    "salario": 4500000,
    "fecha_graduacion": "2018-06-15",
    "estado_civil": "soltero"
  }
}
```

---

## 2️⃣ **CREAR UBICACIÓN RESIDENCIA**

### **Endpoint Base**
```
POST /ubicacion/?empresa_id=1
```

### **JSON a Enviar**
```json
{
  "solicitante_id": 123,
  "direccion": "Calle 123 #45-67",
  "ciudad": "Bogotá",
  "departamento": "Cundinamarca",
  "tipo_direccion": "residencia",
  "empresa_id": 1
}
```

### **Respuesta Esperada**
```json
{
  "ok": true,
  "data": {
    "id": 456,
    "solicitante_id": 123,
    "direccion": "Calle 123 #45-67",
    ...
  }
}
```

### **💾 Campos Dinámicos Ubicación Residencia**
```
PATCH /json/ubicacion/456/detalle_direccion?empresa_id=1&validate=true
```

**JSON:**
```json
{
  "value": {
    "tipo_vivienda": "propia",
    "tiempo_residencia": "5 años",
    "valor_arriendo": null,
    "servicios_publicos": ["agua", "luz", "gas", "internet"],
    "contacto_emergencia": "María Pérez - 3009876543"
  }
}
```

---

## 3️⃣ **CREAR UBICACIÓN TRABAJO**

### **Endpoint Base**
```
POST /ubicacion/?empresa_id=1
```

### **JSON a Enviar**
```json
{
  "solicitante_id": 123,
  "direccion": "Carrera 7 #32-16",
  "ciudad": "Bogotá",
  "departamento": "Cundinamarca",
  "tipo_direccion": "trabajo",
  "empresa_id": 1
}
```

### **💾 Campos Dinámicos Ubicación Trabajo**
```
PATCH /json/ubicacion/789/detalle_direccion?empresa_id=1&validate=true
```

**JSON:**
```json
{
  "value": {
    "nombre_empresa": "TechCorp SAS",
    "piso_oficina": "5",
    "extension": "1234",
    "horario_trabajo": "8:00 AM - 6:00 PM",
    "modalidad": "presencial"
  }
}
```

---

## 4️⃣ **CREAR ACTIVIDAD ECONÓMICA**

### **Endpoint Base**
```
POST /actividad_economica/?empresa_id=1
```

### **JSON a Enviar**
```json
{
  "solicitante_id": 123,
  "empresa": "TechCorp SAS",
  "cargo": "Desarrollador Senior",
  "tipo_contrato": "indefinido",
  "salario_base": 4500000,
  "fecha_ingreso": "2020-03-15",
  "empresa_id": 1
}
```

### **Respuesta Esperada**
```json
{
  "ok": true,
  "data": {
    "id": 101,
    "solicitante_id": 123,
    "empresa": "TechCorp SAS",
    ...
  }
}
```

### **💾 Campos Dinámicos Actividad Económica**
```
PATCH /json/actividad_economica/101/detalle_actividad?empresa_id=1&validate=true
```

**JSON:**
```json
{
  "value": {
    "sector_economico": "tecnologia",
    "antiguedad_laboral": "4 años",
    "jefe_inmediato": "María García",
    "telefono_empresa": "6015551234",
    "beneficios": ["seguro médico", "prima técnica", "bonos"],
    "fecha_ultimo_aumento": "2023-01-15"
  }
}
```

---

## 5️⃣ **CREAR INFORMACIÓN FINANCIERA**

### **Endpoint Base**
```
POST /informacion_financiera/?empresa_id=1
```

### **JSON a Enviar**
```json
{
  "solicitante_id": 123,
  "ingresos_mensuales": 4500000,
  "gastos_mensuales": 2800000,
  "otros_ingresos": 500000,
  "empresa_id": 1
}
```

### **Respuesta Esperada**
```json
{
  "ok": true,
  "data": {
    "id": 202,
    "solicitante_id": 123,
    "ingresos_mensuales": 4500000,
    ...
  }
}
```

### **💾 Campos Dinámicos Información Financiera**
```
PATCH /json/informacion_financiera/202/detalle_financiera?empresa_id=1&validate=true
```

**JSON:**
```json
{
  "value": {
    "detalle_otros_ingresos": [
      {
        "concepto": "Freelance",
        "valor": 300000,
        "frecuencia": "mensual"
      },
      {
        "concepto": "Alquiler",
        "valor": 200000,
        "frecuencia": "mensual"
      }
    ],
    "gastos_detallados": {
      "vivienda": 1200000,
      "alimentacion": 600000,
      "transporte": 400000,
      "servicios": 300000,
      "entretenimiento": 200000,
      "otros": 100000
    },
    "patrimonio": {
      "vehiculo": "Honda Civic 2018",
      "valor_vehiculo": 45000000,
      "propiedades": [],
      "inversiones": "CDT por $10,000,000"
    },
    "obligaciones_financieras": [
      {
        "entidad": "Banco ABC",
        "tipo": "tarjeta_credito",
        "saldo": 2500000,
        "cuota_mensual": 250000
      }
    ]
  }
}
```

---

## 6️⃣ **CREAR REFERENCIAS**

### **Referencia Personal**

#### **Endpoint Base**
```
POST /referencias/?empresa_id=1
```

#### **JSON a Enviar**
```json
{
  "solicitante_id": 123,
  "nombre_completo": "Carlos Rodríguez",
  "telefono": "3009876543",
  "tipo_referencia": "personal",
  "empresa_id": 1
}
```

#### **💾 Campos Dinámicos Referencia Personal**
```
PATCH /json/referencia/301/detalle_referencia?empresa_id=1&validate=true
```

**JSON:**
```json
{
  "value": {
    "relacion": "amigo",
    "tiempo_conoce": "10 años",
    "frecuencia_contacto": "semanal",
    "comentarios": "Persona muy responsable y confiable",
    "direccion": "Calle 45 #12-34",
    "ciudad": "Bogotá"
  }
}
```

### **Referencia Laboral**

#### **Endpoint Base**
```
POST /referencias/?empresa_id=1
```

#### **JSON a Enviar**
```json
{
  "solicitante_id": 123,
  "nombre_completo": "Ana Martínez",
  "telefono": "6015551234",
  "tipo_referencia": "laboral",
  "empresa_id": 1
}
```

#### **💾 Campos Dinámicos Referencia Laboral**
```
PATCH /json/referencia/302/detalle_referencia?empresa_id=1&validate=true
```

**JSON:**
```json
{
  "value": {
    "cargo_referencia": "Gerente de Desarrollo",
    "empresa": "TechCorp SAS",
    "tiempo_conoce": "4 años",
    "relacion_laboral": "jefe directo",
    "calificacion_desempeño": "excelente",
    "email": "ana.martinez@techcorp.com",
    "extension": "1001"
  }
}
```

### **Referencia Comercial (Opcional)**

#### **Endpoint Base**
```
POST /referencias/?empresa_id=1
```

#### **JSON a Enviar**
```json
{
  "solicitante_id": 123,
  "nombre_completo": "Banco XYZ - Luis Gómez",
  "telefono": "6015559999",
  "tipo_referencia": "comercial",
  "empresa_id": 1
}
```

#### **💾 Campos Dinámicos Referencia Comercial**
```
PATCH /json/referencia/303/detalle_referencia?empresa_id=1&validate=true
```

**JSON:**
```json
{
  "value": {
    "entidad_financiera": "Banco XYZ",
    "tipo_producto": "cuenta_ahorros",
    "tiempo_cliente": "6 años",
    "calificacion_riesgo": "A",
    "observaciones": "Cliente cumplido sin reportes negativos"
  }
}
```

---

## 7️⃣ **CREAR SOLICITUD DE CRÉDITO**

### **Endpoint Base**
```
POST /solicitudes/?empresa_id=1
```

### **JSON a Enviar**
```json
{
  "solicitante_id": 123,
  "monto_solicitado": 15000000,
  "plazo_meses": 36,
  "tipo_credito_id": 2,
  "destino_credito": "vehiculo",
  "empresa_id": 1
}
```

### **Respuesta Esperada**
```json
{
  "ok": true,
  "data": {
    "id": 401,
    "solicitante_id": 123,
    "monto_solicitado": 15000000,
    "estado": "pendiente",
    ...
  }
}
```

### **💾 Campos Dinámicos Solicitud**
```
PATCH /json/solicitud/401/detalle_credito?empresa_id=1&validate=true
```

**JSON:**
```json
{
  "value": {
    "vehiculo_interes": {
      "marca": "Honda",
      "modelo": "Civic",
      "año": 2022,
      "valor_comercial": 85000000,
      "concesionario": "Honda Bogotá"
    },
    "valor_cuota_inicial": 20000000,
    "garantias": [
      {
        "tipo": "vehiculo_actual",
        "descripcion": "Honda Civic 2018",
        "valor": 45000000,
        "estado": "excelente"
      }
    ],
    "observaciones": "Cliente con excelente historial crediticio y capacidad de pago comprobada",
    "scoring_interno": 850,
    "fecha_solicitud": "2024-01-15",
    "asesor_asignado": "Patricia López"
  }
}
```

---

## 📋 **Resumen del Flujo Completo**

### **Orden de Creación:**
```
1. POST /solicitantes/ → ID: 123
   ↳ PATCH /json/solicitante/123/info_extra

2. POST /ubicacion/ (residencia) → ID: 456
   ↳ PATCH /json/ubicacion/456/detalle_direccion

3. POST /ubicacion/ (trabajo) → ID: 789
   ↳ PATCH /json/ubicacion/789/detalle_direccion

4. POST /actividad_economica/ → ID: 101
   ↳ PATCH /json/actividad_economica/101/detalle_actividad

5. POST /informacion_financiera/ → ID: 202
   ↳ PATCH /json/informacion_financiera/202/detalle_financiera

6. POST /referencias/ (personal) → ID: 301
   ↳ PATCH /json/referencia/301/detalle_referencia

7. POST /referencias/ (laboral) → ID: 302
   ↳ PATCH /json/referencia/302/detalle_referencia

8. POST /referencias/ (comercial) → ID: 303 [OPCIONAL]
   ↳ PATCH /json/referencia/303/detalle_referencia

9. POST /solicitudes/ → ID: 401
   ↳ PATCH /json/solicitud/401/detalle_credito
```

### **⚠️ Notas Importantes:**

1. **Empresa ID obligatorio:** Todos los endpoints requieren `?empresa_id=1`
2. **Validación recomendada:** Usar `&validate=true` en todos los PATCH de campos dinámicos
3. **Orden importante:** Sigue el orden exacto porque hay dependencias entre entidades
4. **IDs dinámicos:** Guarda los IDs de respuesta para usar en siguientes requests
5. **Manejo de errores:** Verifica que cada paso sea exitoso antes del siguiente
6. **Campos opcionales:** Los campos dinámicos pueden ser opcionales según configuración

### **🎯 Headers Requeridos:**
```javascript
{
  'Content-Type': 'application/json',
  'X-Empresa-Id': '1'  // Opcional, puede ir en query param
}
```

---

Esta guía te permite crear un registro completo paso a paso con toda la información necesaria para solicitudes de crédito! 🚀
