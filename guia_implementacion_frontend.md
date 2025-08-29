# Guía de Implementación Frontend - Tablas Dinámicas

## 1. Obtener la configuración desde el backend

### JavaScript/TypeScript - Función para obtener configuración:

```javascript
// Función para obtener la configuración de tablas
async function obtenerConfiguracionTablas(empresaId) {
    try {
        const response = await fetch(`/configuraciones/tablas-frontend?empresa_id=${empresaId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Empresa-Id': empresaId.toString()
            }
        });

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.ok) {
            return data.data.configuracion;
        } else {
            throw new Error(data.error || 'Error desconocido');
        }
    } catch (error) {
        console.error('Error obteniendo configuración de tablas:', error);
        return null;
    }
}
```

## 2. Implementación con React

### Componente de tabla dinámica:

```jsx
import React, { useState, useEffect } from 'react';

const TablaDinamica = ({ nombreTabla, empresaId, datos }) => {
    const [configuracion, setConfiguracion] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const cargarConfiguracion = async () => {
            const config = await obtenerConfiguracionTablas(empresaId);
            if (config && config[nombreTabla]) {
                setConfiguracion(config[nombreTabla]);
            }
            setLoading(false);
        };

        cargarConfiguracion();
    }, [nombreTabla, empresaId]);

    if (loading) return <div>Cargando configuración...</div>;
    if (!configuracion) return <div>No se encontró configuración para esta tabla</div>;

    return (
        <div className="tabla-container">
            <h2>{configuracion.nombre_tabla}</h2>
            {configuracion.descripcion && (
                <p className="descripcion">{configuracion.descripcion}</p>
            )}
            
            {/* Filtros */}
            {configuracion.filtros && (
                <div className="filtros">
                    {configuracion.filtros.map((filtro, index) => (
                        <FiltroComponente key={index} filtro={filtro} />
                    ))}
                </div>
            )}

            {/* Tabla */}
            <table className="tabla-dinamica">
                <thead>
                    <tr>
                        {configuracion.columnas
                            .filter(col => col.visible)
                            .map((columna, index) => (
                                <th 
                                    key={index}
                                    style={{ width: columna.ancho }}
                                    className={columna.ordenable ? 'ordenable' : ''}
                                >
                                    {columna.titulo}
                                </th>
                            ))}
                        {configuracion.acciones && (
                            <th>Acciones</th>
                        )}
                    </tr>
                </thead>
                <tbody>
                    {datos.map((fila, filaIndex) => (
                        <tr key={filaIndex}>
                            {configuracion.columnas
                                .filter(col => col.visible)
                                .map((columna, colIndex) => (
                                    <td key={colIndex}>
                                        <CeldaComponente 
                                            valor={obtenerValorCampo(fila, columna.campo)}
                                            columna={columna}
                                        />
                                    </td>
                                ))}
                            {configuracion.acciones && (
                                <td>
                                    <AccionesComponente 
                                        acciones={configuracion.acciones}
                                        fila={fila}
                                    />
                                </td>
                            )}
                        </tr>
                    ))}
                </tbody>
            </table>

            {/* Paginación */}
            {configuracion.paginacion && (
                <PaginacionComponente configuracion={configuracion.paginacion} />
            )}
        </div>
    );
};

// Componente para renderizar celdas según el tipo
const CeldaComponente = ({ valor, columna }) => {
    switch (columna.tipo) {
        case 'datetime':
            return <span>{formatearFecha(valor, columna.formato)}</span>;
        
        case 'badge':
            const color = columna.colores?.[valor] || 'secondary';
            return <span className={`badge badge-${color}`}>{valor}</span>;
        
        case 'email':
            return <a href={`mailto:${valor}`}>{valor}</a>;
        
        case 'number':
            return <span>{formatearNumero(valor, columna.formato)}</span>;
        
        default:
            return <span>{valor}</span>;
    }
};

// Componente para filtros
const FiltroComponente = ({ filtro }) => {
    const [valor, setValor] = useState('');

    switch (filtro.tipo) {
        case 'select':
            return (
                <select 
                    value={valor} 
                    onChange={(e) => setValor(e.target.value)}
                    className="filtro-select"
                >
                    <option value="">Todos</option>
                    {filtro.opciones.map((opcion, index) => (
                        <option key={index} value={opcion}>{opcion}</option>
                    ))}
                </select>
            );
        
        case 'text':
            return (
                <input
                    type="text"
                    value={valor}
                    onChange={(e) => setValor(e.target.value)}
                    placeholder={`Filtrar por ${filtro.campo}`}
                    className="filtro-text"
                />
            );
        
        default:
            return null;
    }
};

// Componente para acciones
const AccionesComponente = ({ acciones, fila }) => {
    const ejecutarAccion = (accion, fila) => {
        if (accion.confirmacion && accion.tipo === 'eliminar') {
            if (window.confirm('¿Estás seguro de que quieres eliminar este registro?')) {
                // Lógica para eliminar
                console.log('Eliminando:', fila.id);
            }
        } else {
            // Otras acciones
            console.log(`Ejecutando ${accion.tipo} para:`, fila.id);
        }
    };

    return (
        <div className="acciones">
            {acciones.map((accion, index) => (
                <button
                    key={index}
                    className={`btn-accion btn-${accion.tipo}`}
                    onClick={() => ejecutarAccion(accion, fila)}
                    title={accion.tooltip}
                >
                    <i className={`icon-${accion.icono}`}></i>
                </button>
            ))}
        </div>
    );
};

// Funciones auxiliares
const obtenerValorCampo = (objeto, campo) => {
    return campo.split('.').reduce((obj, key) => obj?.[key], objeto);
};

const formatearFecha = (fecha, formato = 'DD/MM/YYYY') => {
    if (!fecha) return '';
    const date = new Date(fecha);
    // Implementar formateo según el formato especificado
    return date.toLocaleDateString('es-ES');
};

const formatearNumero = (numero, formato) => {
    if (!numero) return '';
    return new Intl.NumberFormat('es-ES').format(numero);
};

export default TablaDinamica;
```

## 3. Implementación con Vue.js

```vue
<template>
  <div class="tabla-container">
    <h2 v-if="configuracion">{{ configuracion.nombre_tabla }}</h2>
    <p v-if="configuracion?.descripcion" class="descripcion">
      {{ configuracion.descripcion }}
    </p>

    <!-- Filtros -->
    <div v-if="configuracion?.filtros" class="filtros">
      <div v-for="(filtro, index) in configuracion.filtros" :key="index">
        <select v-if="filtro.tipo === 'select'" v-model="filtros[filtro.campo]">
          <option value="">Todos</option>
          <option v-for="opcion in filtro.opciones" :key="opcion" :value="opcion">
            {{ opcion }}
          </option>
        </select>
      </div>
    </div>

    <!-- Tabla -->
    <table v-if="configuracion" class="tabla-dinamica">
      <thead>
        <tr>
          <th 
            v-for="columna in columnasVisibles" 
            :key="columna.campo"
            :style="{ width: columna.ancho }"
          >
            {{ columna.titulo }}
          </th>
          <th v-if="configuracion.acciones">Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(fila, index) in datosFiltrados" :key="index">
          <td v-for="columna in columnasVisibles" :key="columna.campo">
            <component 
              :is="obtenerComponenteCelda(columna.tipo)"
              :valor="obtenerValorCampo(fila, columna.campo)"
              :columna="columna"
            />
          </td>
          <td v-if="configuracion.acciones">
            <button
              v-for="accion in configuracion.acciones"
              :key="accion.tipo"
              @click="ejecutarAccion(accion, fila)"
              :title="accion.tooltip"
              class="btn-accion"
            >
              <i :class="`icon-${accion.icono}`"></i>
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'TablaDinamica',
  props: {
    nombreTabla: String,
    empresaId: Number,
    datos: Array
  },
  data() {
    return {
      configuracion: null,
      filtros: {}
    };
  },
  computed: {
    columnasVisibles() {
      return this.configuracion?.columnas?.filter(col => col.visible) || [];
    },
    datosFiltrados() {
      // Implementar lógica de filtrado
      return this.datos;
    }
  },
  async mounted() {
    await this.cargarConfiguracion();
  },
  methods: {
    async cargarConfiguracion() {
      const config = await obtenerConfiguracionTablas(this.empresaId);
      if (config && config[this.nombreTabla]) {
        this.configuracion = config[this.nombreTabla];
      }
    },
    obtenerValorCampo(objeto, campo) {
      return campo.split('.').reduce((obj, key) => obj?.[key], objeto);
    },
    ejecutarAccion(accion, fila) {
      this.$emit('accion', { tipo: accion.tipo, fila });
    }
  }
};
</script>
```

## 4. CSS para estilos

```css
.tabla-container {
  margin: 20px 0;
}

.tabla-dinamica {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.tabla-dinamica th,
.tabla-dinamica td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.tabla-dinamica th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.tabla-dinamica th.ordenable {
  cursor: pointer;
}

.tabla-dinamica th.ordenable:hover {
  background-color: #e9e9e9;
}

.filtros {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filtro-select,
.filtro-text {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.acciones {
  display: flex;
  gap: 8px;
}

.btn-accion {
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-accion.btn-ver {
  background-color: #007bff;
  color: white;
}

.btn-accion.btn-editar {
  background-color: #28a745;
  color: white;
}

.btn-accion.btn-eliminar {
  background-color: #dc3545;
  color: white;
}

.badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.badge-success { background-color: #28a745; color: white; }
.badge-warning { background-color: #ffc107; color: black; }
.badge-danger { background-color: #dc3545; color: white; }
.badge-info { background-color: #17a2b8; color: white; }
.badge-secondary { background-color: #6c757d; color: white; }
```

## 5. Uso del componente

```jsx
// En tu componente principal
function PaginaSolicitantes() {
    const [solicitantes, setSolicitantes] = useState([]);
    const empresaId = 1; // Obtener del contexto o props

    useEffect(() => {
        // Cargar datos de solicitantes
        cargarSolicitantes();
    }, []);

    return (
        <div>
            <TablaDinamica 
                nombreTabla="solicitantes"
                empresaId={empresaId}
                datos={solicitantes}
            />
        </div>
    );
}
```

Esta implementación te permite:

1. **Configurar tablas dinámicamente** desde la base de datos
2. **Mostrar/ocultar columnas** según configuración
3. **Aplicar diferentes tipos de renderizado** (badges, fechas, etc.)
4. **Agregar acciones personalizadas** por fila
5. **Implementar filtros** dinámicos
6. **Mantener consistencia** en toda la aplicación
