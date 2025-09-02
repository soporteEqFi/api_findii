# 🔄 Guía: Reordenar Campos Dinámicos

Esta guía explica cómo implementar drag-and-drop para reordenar campos en formularios dinámicos.

## 🎯 Funcionalidad Implementada

### Backend
- **Nuevo endpoint**: `PATCH /json/definitions/{entity}/{json_field}/reorder`
- **Funcionalidad**: Actualiza el `order_index` de múltiples campos dinámicos
- **Integración**: Utiliza el sistema existente de `order_index` en la tabla `json_field_definition`

### Frontend
- **Archivo principal**: `utils/dynamic_form_reorder.js`
- **Clase**: `DynamicFormReorder`
- **Funcionalidad**: Drag-and-drop nativo con actualización automática en BD

## 🚀 Uso Rápido

### 1. Incluir el Script
```html
<script src="utils/dynamic_form_reorder.js"></script>
```

### 2. Inicializar en tu Formulario
```javascript
// Preparar campos existentes
prepareExistingFields('miFormularioContainer');

// Inicializar drag-and-drop
const reorder = initializeDynamicFormReorder(
    'miFormularioContainer',  // ID del contenedor
    'solicitante',           // Entidad
    'info_extra',           // Campo JSON
    'http://localhost:5000', // URL de la API
    1                       // ID de empresa
);
```

### 3. Estructura HTML Requerida
```html
<div id="miFormularioContainer">
    <div class="dynamic-field" data-field-key="campo1">
        <label>Campo 1</label>
        <input name="campo1" type="text">
    </div>
    
    <div class="dynamic-field" data-field-key="campo2">
        <label>Campo 2</label>
        <input name="campo2" type="text">
    </div>
</div>
```

## 📡 API Endpoint

### Reordenar Campos
```
PATCH /json/definitions/{entity}/{json_field}/reorder?empresa_id={id}
```

**Body:**
```json
{
  "field_orders": [
    {"key": "campo1", "order_index": 1},
    {"key": "campo2", "order_index": 2},
    {"key": "campo3", "order_index": 3}
  ]
}
```

**Respuesta:**
```json
{
  "ok": true,
  "data": [...],
  "message": "Reordenados 3 campos para solicitante.info_extra"
}
```

## 🎨 Personalización CSS

Los estilos se inyectan automáticamente, pero puedes personalizarlos:

```css
/* Campo siendo arrastrado */
.draggable-field.dragging {
    opacity: 0.5;
    transform: rotate(2deg);
}

/* Handle de drag */
.drag-handle {
    cursor: grab;
    color: #666;
}

/* Placeholder de drop */
.drag-placeholder {
    border: 2px dashed #007bff;
    background-color: rgba(0, 123, 255, 0.1);
}
```

## 🔧 Funciones Principales

### `DynamicFormReorder`
Clase principal que maneja toda la funcionalidad de drag-and-drop.

### `initializeDynamicFormReorder()`
Función helper para inicialización rápida.

### `prepareExistingFields()`
Prepara campos HTML existentes para ser draggables.

### `injectDragDropStyles()`
Inyecta los estilos CSS necesarios.

## 📋 Requisitos

### HTML
- Contenedor con ID único
- Campos con clase `.dynamic-field` o similar
- Atributo `data-field-key` en cada campo

### Backend
- Campo `order_index` en tabla `json_field_definition`
- Endpoint de reordenamiento implementado

## 🎯 Integración con Formularios Existentes

### Opción 1: Formulario Estático
```javascript
// Para formularios ya renderizados
prepareExistingFields('formularioExistente', '.mi-clase-campo');
const reorder = initializeDynamicFormReorder('formularioExistente', 'entidad', 'campo_json');
```

### Opción 2: Formulario Dinámico
```javascript
// Para formularios generados desde schema
async function generarFormularioConReordenamiento(entity, jsonField) {
    // 1. Obtener schema
    const schema = await obtenerSchema(entity, jsonField);
    
    // 2. Generar HTML
    const formHTML = generarFormularioHTML(schema);
    
    // 3. Insertar en DOM
    document.getElementById('container').innerHTML = formHTML;
    
    // 4. Inicializar drag-and-drop
    prepareExistingFields('container');
    initializeDynamicFormReorder('container', entity, jsonField);
}
```

## 🔄 Flujo Completo

1. **Usuario activa modo reordenamiento**
2. **Campos se vuelven draggables** (con handles visuales)
3. **Usuario arrastra campo** a nueva posición
4. **Frontend calcula nuevos order_index**
5. **Se envía PATCH al backend** con nuevos órdenes
6. **Backend actualiza BD** y confirma cambios
7. **Frontend muestra notificación** de éxito

## ⚠️ Consideraciones

### Performance
- Los estilos se inyectan una sola vez
- Las actualizaciones son incrementales
- Se valida estructura antes de enviar

### Compatibilidad
- Funciona con cualquier estructura de formulario
- Compatible con campos generados dinámicamente
- No requiere librerías externas

### Seguridad
- Validación en backend de `field_orders`
- Verificación de empresa_id
- Manejo de errores robusto

## 🧪 Ejemplo de Prueba

Ver `utils/dynamic_form_example.html` para un ejemplo completo funcional.

```bash
# Abrir ejemplo en navegador
start utils/dynamic_form_example.html
```

## 🎉 ¡Listo!

Tu sistema de formularios dinámicos ahora soporta reordenamiento drag-and-drop, manteniendo la persistencia en la base de datos a través del campo `order_index` existente.
