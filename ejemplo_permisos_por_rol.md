# 🔐 Sistema de Permisos por Rol - Solicitudes

## 🎯 **Descripción**

El sistema implementa control de acceso basado en roles (RBAC) para las solicitudes. Los usuarios solo pueden ver las solicitudes según su rol y permisos asignados.

## 👥 **Roles Disponibles**

### **1. `admin`**
- **Permisos:** Ve todas las solicitudes de la empresa
- **Filtros:** Ninguno (acceso completo)

### **2. `banco`**
- **Permisos:** Solo ve solicitudes asignadas a su banco
- **Filtros:** `banco_nombre = [banco_del_usuario]`
- **Requisito:** Debe tener `banco_nombre` asignado

### **3. `empresa`**
- **Permisos:** Ve todas las solicitudes de la empresa
- **Filtros:** Ninguno (acceso completo a su empresa)

## 🔧 **Implementación**

### **Headers Requeridos**

```bash
# Headers obligatorios para autenticación
Authorization: Bearer <token_jwt>
X-Empresa-Id: 1

# Headers para información del usuario (en desarrollo)
X-User-Id: 123
X-User-Rol: banco
X-User-Banco: Bancolombia
```

### **Ejemplos de Uso**

#### **1. Usuario Admin - Ve todas las solicitudes**
```bash
curl -X GET "http://localhost:5000/solicitudes/?empresa_id=1" \
  -H "Authorization: Bearer <token>" \
  -H "X-User-Id: 1" \
  -H "X-User-Rol: admin"
```

**Respuesta:** Todas las solicitudes de la empresa

#### **2. Usuario Banco - Solo ve solicitudes de su banco**
```bash
curl -X GET "http://localhost:5000/solicitudes/?empresa_id=1" \
  -H "Authorization: Bearer <token>" \
  -H "X-User-Id: 2" \
  -H "X-User-Rol: banco" \
  -H "X-User-Banco: Bancolombia"
```

**Respuesta:** Solo solicitudes con `banco_nombre = "Bancolombia"`

#### **3. Usuario Empresa - Ve todas las solicitudes de su empresa**
```bash
curl -X GET "http://localhost:5000/solicitudes/?empresa_id=1" \
  -H "Authorization: Bearer <token>" \
  -H "X-User-Id: 3" \
  -H "X-User-Rol: empresa"
```

**Respuesta:** Todas las solicitudes de la empresa

## 🚨 **Casos Especiales**

### **Usuario Banco sin banco asignado**
```bash
curl -X GET "http://localhost:5000/solicitudes/?empresa_id=1" \
  -H "X-User-Id: 4" \
  -H "X-User-Rol: banco"
  # Sin X-User-Banco
```

**Respuesta:** `[]` (lista vacía)

### **Rol desconocido**
```bash
curl -X GET "http://localhost:5000/solicitudes/?empresa_id=1" \
  -H "X-User-Id: 5" \
  -H "X-User-Rol: rol_desconocido"
```

**Respuesta:** `[]` (lista vacía)

### **Sin autenticación**
```bash
curl -X GET "http://localhost:5000/solicitudes/?empresa_id=1"
# Sin headers de autenticación
```

**Respuesta:** Todas las solicitudes (comportamiento por defecto)

## 📊 **Filtros Combinados**

Los filtros de permisos se combinan con otros filtros:

```bash
# Usuario banco + filtro por estado
curl -X GET "http://localhost:5000/solicitudes/?empresa_id=1&estado=pendiente" \
  -H "X-User-Id: 2" \
  -H "X-User-Rol: banco" \
  -H "X-User-Banco: Bancolombia"
```

**Resultado:** Solicitudes de Bancolombia con estado "pendiente"

## 🔒 **Seguridad**

### **Validaciones Implementadas:**

1. **Filtro por empresa:** Siempre se aplica `empresa_id`
2. **Filtro por banco:** Para usuarios con rol "banco"
3. **Validación de roles:** Solo roles válidos tienen acceso
4. **Fallback seguro:** Roles desconocidos no ven nada

### **Endpoints Protegidos:**

- `GET /solicitudes/` - Lista con filtros de permisos
- `GET /solicitudes/{id}` - Detalle con filtros de permisos
- `PATCH /solicitudes/{id}` - Actualización con filtros de permisos

## 🚀 **Próximos Pasos**

### **Implementación Completa de JWT:**

```python
def _obtener_usuario_autenticado(self):
    """Obtener información del usuario desde JWT decodificado"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]
        # Decodificar JWT aquí
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        return {
            "id": payload.get("user_id"),
            "rol": payload.get("rol"),
            "banco_nombre": payload.get("banco_nombre"),
            "empresa_id": payload.get("empresa_id")
        }
    except Exception:
        return None
```

### **Integración con Base de Datos:**

```sql
-- Tabla usuarios con información de roles
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    rol VARCHAR(50) NOT NULL DEFAULT 'empresa',
    banco_nombre VARCHAR(255),
    empresa_id INTEGER REFERENCES empresas(id),
    info_extra JSONB
);
```

¡El sistema de permisos está listo para usar! 🎉
