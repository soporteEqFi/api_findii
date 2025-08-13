# 🧪 Pruebas de Actualización de info_segundo_titular

Este documento describe cómo probar que la actualización del campo `info_segundo_titular` funcione correctamente en el sistema CRM FINDII.

## 📋 Resumen de Cambios Implementados

### ✅ **Mejoras en el Correo Electrónico**
- Se agregó la función `format_second_holder_info()` para formatear mejor la información
- Ahora se muestra la información detallada del segundo titular cuando existe
- La información se presenta de manera legible tanto para JSON como para texto

### ✅ **Mejoras en el PDF**
- Se agregó el campo `info_segundo_titular` en la generación del PDF
- Se incluye en el template HTML del PDF

### ✅ **Logs de Debug Agregados**
- Se agregaron logs detallados en la función `edit_record()` para rastrear la actualización
- Se puede ver exactamente qué datos se reciben y procesan

## 🚀 Cómo Probar la Actualización

### 1. **Preparar el Entorno**
```bash
# Asegúrate de que la API esté ejecutándose
python app.py
```

### 2. **Ejecutar el Script de Prueba**
```bash
# Instalar dependencias si es necesario
pip install requests

# Ejecutar el script de prueba
python test_update_info_segundo_titular.py
```

### 3. **Verificar los Logs del Servidor**
Los logs de debug mostrarán:
- Datos recibidos para la actualización
- Campos disponibles en PRODUCTO_SOLICITADO
- Valor y tipo de `info_segundo_titular`
- Datos que se van a actualizar en cada tabla
- Resultado de cada actualización

## 📊 Estructura de Datos de Prueba

### **Prueba 1: JSON Completo**
```json
{
  "solicitante_id": 1,
  "PRODUCTO_SOLICITADO": {
    "info_segundo_titular": {
      "nombre": "María García",
      "tipo_documento": "CC",
      "numero_documento": "98765432",
      "fecha_nacimiento": "1985-05-15",
      "numero_celular": "3009876543",
      "correo_electronico": "maria@email.com",
      "nivel_estudio": "Universitario",
      "profesion": "Ingeniera",
      "estado_civil": "Casada",
      "personas_a_cargo": "2"
    }
  }
}
```

### **Prueba 2: String Simple**
```json
{
  "solicitante_id": 1,
  "PRODUCTO_SOLICITADO": {
    "info_segundo_titular": "Información del segundo titular como string simple"
  }
}
```

### **Prueba 3: Valor Vacío**
```json
{
  "solicitante_id": 1,
  "PRODUCTO_SOLICITADO": {
    "info_segundo_titular": ""
  }
}
```

## 🔍 Qué Verificar

### **En los Logs del Servidor:**
1. ✅ Los datos se reciben correctamente
2. ✅ El campo `info_segundo_titular` está presente
3. ✅ Se procesa correctamente según su tipo (JSON o string)
4. ✅ Se actualiza en la base de datos
5. ✅ No hay errores en la actualización

### **En la Base de Datos:**
1. ✅ El campo se actualiza en la tabla `PRODUCTO_SOLICITADO`
2. ✅ El valor se guarda correctamente (JSON o string)
3. ✅ Se puede consultar posteriormente

### **En el Correo Electrónico:**
1. ✅ Se muestra la información del segundo titular cuando existe
2. ✅ Se formatea correctamente (JSON estructurado o texto simple)
3. ✅ Solo aparece cuando `segundo_titular` es "si"

### **En el PDF:**
1. ✅ Se incluye el campo `info_segundo_titular`
2. ✅ Se muestra correctamente en el template

## 🐛 Solución de Problemas

### **Problema: Campo no se actualiza**
- Verificar que el `solicitante_id` sea válido
- Revisar los logs de debug para identificar el problema
- Verificar que la estructura de datos sea correcta

### **Problema: Error en la base de datos**
- Verificar que la tabla `PRODUCTO_SOLICITADO` tenga la columna `info_segundo_titular`
- Verificar permisos de escritura en la base de datos
- Revisar restricciones de clave foránea

### **Problema: No se muestra en el correo/PDF**
- Verificar que los datos se estén enviando correctamente
- Revisar la función de formateo
- Verificar que el template esté actualizado

## 📝 Notas Importantes

1. **Cambiar el ID**: Modifica el `solicitante_id` en el script de prueba por un ID válido de tu base de datos
2. **Revisar Logs**: Los logs de debug te mostrarán exactamente qué está pasando
3. **Probar Diferentes Tipos**: El sistema debe manejar tanto JSON como strings simples
4. **Verificar Base de Datos**: Confirma que los cambios se guarden correctamente

## 🔗 Endpoints Relevantes

- **PUT** `/edit-record/` - Actualizar registros existentes
- **GET** `/get-all-data/` - Obtener todos los registros
- **POST** `/filtrar-tabla/` - Filtrar registros por criterios

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs de debug en la consola del servidor
2. Verifica que la estructura de datos sea correcta
3. Confirma que la base de datos tenga la columna `info_segundo_titular`
4. Prueba con diferentes tipos de datos (JSON, string, vacío)
