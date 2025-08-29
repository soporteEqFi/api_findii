# Configuración de Tablas Frontend

## Estructura de la configuración en la tabla `configuraciones`

Para definir qué tablas y columnas mostrar en el frontend, debes insertar una fila en la tabla `configuraciones` con la siguiente estructura:

### Ejemplo de inserción SQL:

```sql
INSERT INTO configuraciones (empresa_id, categoria, configuracion, descripcion, activo) 
VALUES (
    1, -- Tu empresa_id
    'tablas_frontend',
    '{
        "solicitantes": {
            "nombre_tabla": "Solicitantes",
            "descripcion": "Lista de personas que han solicitado créditos",
            "columnas": [
                {
                    "campo": "id",
                    "titulo": "ID",
                    "tipo": "number",
                    "visible": true,
                    "ordenable": true,
                    "ancho": "80px"
                },
                {
                    "campo": "nombres",
                    "titulo": "Nombres",
                    "tipo": "text",
                    "visible": true,
                    "ordenable": true,
                    "ancho": "150px"
                },
                {
                    "campo": "primer_apellido",
                    "titulo": "Primer Apellido",
                    "tipo": "text",
                    "visible": true,
                    "ordenable": true,
                    "ancho": "150px"
                },
                {
                    "campo": "numero_documento",
                    "titulo": "Documento",
                    "tipo": "text",
                    "visible": true,
                    "ordenable": true,
                    "ancho": "120px"
                },
                {
                    "campo": "correo",
                    "titulo": "Email",
                    "tipo": "email",
                    "visible": true,
                    "ordenable": true,
                    "ancho": "200px"
                },
                {
                    "campo": "created_at",
                    "titulo": "Fecha Creación",
                    "tipo": "datetime",
                    "visible": true,
                    "ordenable": true,
                    "ancho": "150px",
                    "formato": "DD/MM/YYYY HH:mm"
                }
            ],
            "acciones": [
                {
                    "tipo": "ver",
                    "icono": "eye",
                    "tooltip": "Ver detalles"
                },
                {
                    "tipo": "editar",
                    "icono": "edit",
                    "tooltip": "Editar solicitante"
                },
                {
                    "tipo": "eliminar",
                    "icono": "trash",
                    "tooltip": "Eliminar solicitante",
                    "confirmacion": true
                }
            ],
            "filtros": [
                {
                    "campo": "tipo_identificacion",
                    "tipo": "select",
                    "opciones": ["CC", "CE", "NIT", "Pasaporte"]
                },
                {
                    "campo": "genero",
                    "tipo": "select",
                    "opciones": ["Masculino", "Femenino", "Otro"]
                }
            ],
            "paginacion": {
                "items_por_pagina": 20,
                "mostrar_selector": true
            }
        },
        "solicitudes": {
            "nombre_tabla": "Solicitudes",
            "descripcion": "Lista de solicitudes de crédito",
            "columnas": [
                {
                    "campo": "id",
                    "titulo": "ID",
                    "tipo": "number",
                    "visible": true,
                    "ordenable": true,
                    "ancho": "80px"
                },
                {
                    "campo": "solicitante.nombres",
                    "titulo": "Solicitante",
                    "tipo": "text",
                    "visible": true,
                    "ordenable": true,
                    "ancho": "200px"
                },
                {
                    "campo": "estado",
                    "titulo": "Estado",
                    "tipo": "badge",
                    "visible": true,
                    "ordenable": true,
                    "ancho": "120px",
                    "colores": {
                        "pendiente": "warning",
                        "aprobado": "success",
                        "rechazado": "danger",
                        "en_revision": "info"
                    }
                },
                {
                    "campo": "banco_nombre",
                    "titulo": "Banco",
                    "tipo": "text",
                    "visible": true,
                    "ordenable": true,
                    "ancho": "150px"
                },
                {
                    "campo": "created_at",
                    "titulo": "Fecha Solicitud",
                    "tipo": "datetime",
                    "visible": true,
                    "ordenable": true,
                    "ancho": "150px",
                    "formato": "DD/MM/YYYY"
                }
            ],
            "acciones": [
                {
                    "tipo": "ver",
                    "icono": "eye",
                    "tooltip": "Ver solicitud"
                },
                {
                    "tipo": "procesar",
                    "icono": "cog",
                    "tooltip": "Procesar solicitud"
                }
            ],
            "filtros": [
                {
                    "campo": "estado",
                    "tipo": "select",
                    "opciones": ["pendiente", "aprobado", "rechazado", "en_revision"]
                },
                {
                    "campo": "banco_nombre",
                    "tipo": "select_dinamico",
                    "endpoint": "/configuraciones/bancos"
                }
            ]
        }
    }',
    'Configuración de tablas y columnas para mostrar en el frontend',
    true
);
```

## Estructura del JSON de configuración

### Propiedades principales por tabla:

- **`nombre_tabla`**: Nombre que se mostrará como título de la tabla
- **`descripcion`**: Descripción opcional de la tabla
- **`columnas`**: Array de objetos que definen cada columna
- **`acciones`**: Array de botones de acción por fila
- **`filtros`**: Array de filtros disponibles
- **`paginacion`**: Configuración de paginación

### Propiedades de columnas:

- **`campo`**: Nombre del campo en la base de datos (soporta notación punto para relaciones)
- **`titulo`**: Texto que se mostrará en el header de la columna
- **`tipo`**: Tipo de dato (`text`, `number`, `datetime`, `email`, `badge`, etc.)
- **`visible`**: Si la columna se muestra por defecto
- **`ordenable`**: Si se puede ordenar por esta columna
- **`ancho`**: Ancho de la columna en CSS
- **`formato`**: Formato específico para fechas o números
- **`colores`**: Para tipo `badge`, mapeo de valores a colores

### Tipos de acciones disponibles:

- **`ver`**: Navegar a vista de detalle
- **`editar`**: Abrir formulario de edición
- **`eliminar`**: Eliminar registro (con confirmación opcional)
- **`procesar`**: Acción personalizada
- **`descargar`**: Descargar archivo relacionado

### Tipos de filtros:

- **`select`**: Lista desplegable con opciones fijas
- **`select_dinamico`**: Lista desplegable que obtiene opciones de un endpoint
- **`text`**: Campo de texto libre
- **`date_range`**: Selector de rango de fechas
- **`number_range`**: Selector de rango numérico

## Endpoint disponible

Una vez configurado, puedes obtener la configuración desde:

```
GET /configuraciones/tablas-frontend?empresa_id=1
```

Respuesta esperada:
```json
{
    "ok": true,
    "data": {
        "id": 123,
        "categoria": "tablas_frontend",
        "configuracion": { /* objeto con la configuración */ },
        "descripcion": "Configuración de tablas y columnas para mostrar en el frontend",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    "message": "Configuración de tablas obtenida exitosamente"
}
```
