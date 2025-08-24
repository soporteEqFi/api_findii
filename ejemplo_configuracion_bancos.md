# Ejemplo de Configuración con Order Index

Este documento muestra ejemplos de cómo usar el campo `order_index` para controlar el orden de aparición de campos en arrays y objetos.

## Arrays con Enum

```json
{
  "key": "tipo_empleo",
  "type": "string",
  "required": true,
  "description": "Tipo de empleo",
  "list_values": {
    "enum": ["empleado", "independiente", "pensionado", "empresario"],
    "order_index": 1
  },
  "order_index": 2
}
```

## Arrays de Objetos

```json
{
  "key": "negocios",
  "type": "array",
  "required": false,
  "description": "Lista de negocios del solicitante",
  "list_values": {
    "array_type": "object",
    "object_structure": [
      {
        "key": "nombre_negocio",
        "type": "string",
        "required": true,
        "description": "Nombre del negocio",
        "order_index": 1
      },
      {
        "key": "tipo_negocio",
        "type": "string",
        "required": true,
        "description": "Tipo de negocio",
        "order_index": 2
      },
      {
        "key": "ingresos_mensuales",
        "type": "number",
        "required": false,
        "description": "Ingresos mensuales del negocio",
        "order_index": 3
      }
    ]
  },
  "order_index": 5
}
```

## Objetos Simples

```json
{
  "key": "datos_contacto",
  "type": "object",
  "required": false,
  "description": "Información de contacto",
  "list_values": [
    {
      "key": "telefono_principal",
      "type": "string",
      "required": true,
      "description": "Teléfono principal",
      "order_index": 1
    },
    {
      "key": "telefono_secundario",
      "type": "string",
      "required": false,
      "description": "Teléfono secundario",
      "order_index": 2
    },
    {
      "key": "correo_electronico",
      "type": "string",
      "required": true,
      "description": "Correo electrónico",
      "order_index": 3
    }
  ],
  "order_index": 3
}
```

## Campos Simples con Order Index

```json
{
  "key": "estado_civil",
  "type": "string",
  "required": true,
  "description": "Estado civil",
  "list_values": ["soltero", "casado", "viudo", "divorciado", "union_libre"],
  "order_index": 1
}
```

## Notas Importantes

1. **Order Index en Campos**: El `order_index` en el campo principal controla el orden de aparición del campo completo.

2. **Order Index en Arrays Enum**: El `order_index` en `list_values` controla el orden de los elementos del enum.

3. **Order Index en Objetos**: Cada campo dentro de un objeto puede tener su propio `order_index` para controlar el orden de los campos dentro del objeto.

4. **Valores por Defecto**: Si no se especifica `order_index`, se usa 999 como valor por defecto (aparece al final).

5. **Ordenamiento**: Los campos se ordenan de menor a mayor `order_index` (1, 2, 3, ...).

## Ejemplo de Respuesta del Schema

```json
{
  "entidad": "solicitante",
  "tabla": "solicitantes",
  "json_column": "info_extra",
  "campos_fijos": [...],
  "campos_dinamicos": [
    {
      "key": "estado_civil",
      "type": "string",
      "required": true,
      "description": "Estado civil",
      "list_values": {
        "enum": ["soltero", "casado", "viudo", "divorciado", "union_libre"],
        "order_index": 1
      },
      "order_index": 1
    },
    {
      "key": "datos_contacto",
      "type": "object",
      "required": false,
      "description": "Información de contacto",
      "list_values": [
        {
          "key": "telefono_principal",
          "type": "string",
          "required": true,
          "description": "Teléfono principal",
          "order_index": 1
        },
        {
          "key": "correo_electronico",
          "type": "string",
          "required": true,
          "description": "Correo electrónico",
          "order_index": 2
        }
      ],
      "order_index": 2
    }
  ],
  "total_campos": 10
}
```
