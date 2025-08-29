# Ejemplo Frontend - Configuración Simple de Columnas

## URL para verificar columnas

```
GET /configuraciones/columnas-tabla?empresa_id=1
```

**Respuesta esperada:**
```json
{
    "ok": true,
    "data": {
        "id": 5,
        "categoria": "columnas_tabla",
        "columnas": ["Nombre", "Ciudad", "Correo", "Teléfono"],
        "descripcion": "Columnas de la tabla principal",
        "created_at": "2025-08-29T15:55:11.759036+00:00",
        "updated_at": "2025-08-29T15:55:11.759036+00:00"
    },
    "message": "Configuración de columnas obtenida exitosamente"
}
```

## Implementación Frontend - React

```jsx
import React, { useState, useEffect } from 'react';

const TablaConColumnasConfigurables = ({ empresaId, datos }) => {
    const [columnas, setColumnas] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        cargarConfiguracionColumnas();
    }, [empresaId]);

    const cargarConfiguracionColumnas = async () => {
        try {
            const response = await fetch(`/configuraciones/columnas-tabla?empresa_id=${empresaId}`, {
                headers: {
                    'X-Empresa-Id': empresaId.toString()
                }
            });

            const result = await response.json();
            
            if (result.ok) {
                setColumnas(result.data.columnas);
            } else {
                console.error('Error:', result.error);
                // Columnas por defecto si no hay configuración
                setColumnas(['Nombre', 'Ciudad', 'Correo', 'Teléfono']);
            }
        } catch (error) {
            console.error('Error cargando configuración:', error);
            setColumnas(['Nombre', 'Ciudad', 'Correo', 'Teléfono']);
        } finally {
            setLoading(false);
        }
    };

    const obtenerValorColumna = (fila, nombreColumna) => {
        // Mapeo de nombres de columnas a campos de la base de datos
        const mapeoColumnas = {
            'Nombre': fila.nombres ? `${fila.nombres} ${fila.primer_apellido || ''}`.trim() : '',
            'Ciudad': fila.ciudad_residencia,
            'Correo': fila.correo,
            'Teléfono': fila.celular,
            'Celular': fila.celular,
            'Tipo Credito': fila.tipo_credito,
            'Tipo Crédito': fila.tipo_credito,
            'Ciudad Residencia': fila.ciudad_residencia,
            'Documento': fila.numero_documento,
            'Estado': fila.estado_solicitud,
            'Banco': fila.banco_nombre
        };

        return mapeoColumnas[nombreColumna] || '';
    };

    if (loading) {
        return <div>Cargando configuración de columnas...</div>;
    }

    return (
        <div className="tabla-container">
            <h2>Tabla Principal</h2>
            
            <table className="tabla-configurable">
                <thead>
                    <tr>
                        {columnas.map((columna, index) => (
                            <th key={index}>{columna}</th>
                        ))}
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {datos.map((fila, filaIndex) => (
                        <tr key={filaIndex}>
                            {columnas.map((columna, colIndex) => (
                                <td key={colIndex}>
                                    {obtenerValorColumna(fila, columna)}
                                </td>
                            ))}
                            <td>
                                <button onClick={() => verDetalle(fila.id)}>Ver</button>
                                <button onClick={() => editarFila(fila.id)}>Editar</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );

    function verDetalle(id) {
        console.log('Ver detalle:', id);
    }

    function editarFila(id) {
        console.log('Editar:', id);
    }
};

export default TablaConColumnasConfigurables;
```

## Implementación Frontend - Vue.js

```vue
<template>
  <div class="tabla-container">
    <h2>Tabla Principal</h2>
    
    <div v-if="loading">Cargando configuración de columnas...</div>
    
    <table v-else class="tabla-configurable">
      <thead>
        <tr>
          <th v-for="(columna, index) in columnas" :key="index">
            {{ columna }}
          </th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(fila, filaIndex) in datos" :key="filaIndex">
          <td v-for="(columna, colIndex) in columnas" :key="colIndex">
            {{ obtenerValorColumna(fila, columna) }}
          </td>
          <td>
            <button @click="verDetalle(fila.id)">Ver</button>
            <button @click="editarFila(fila.id)">Editar</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'TablaConColumnasConfigurables',
  props: {
    empresaId: Number,
    datos: Array
  },
  data() {
    return {
      columnas: [],
      loading: true
    };
  },
  mounted() {
    this.cargarConfiguracionColumnas();
  },
  methods: {
    async cargarConfiguracionColumnas() {
      try {
        const response = await fetch(`/configuraciones/columnas-tabla?empresa_id=${this.empresaId}`, {
          headers: {
            'X-Empresa-Id': this.empresaId.toString()
          }
        });

        const result = await response.json();
        
        if (result.ok) {
          this.columnas = result.data.columnas;
        } else {
          console.error('Error:', result.error);
          // Columnas por defecto
          this.columnas = ['Nombre', 'Ciudad', 'Correo', 'Teléfono'];
        }
      } catch (error) {
        console.error('Error cargando configuración:', error);
        this.columnas = ['Nombre', 'Ciudad', 'Correo', 'Teléfono'];
      } finally {
        this.loading = false;
      }
    },

    obtenerValorColumna(fila, nombreColumna) {
      const mapeoColumnas = {
        'Nombre': fila.nombres ? `${fila.nombres} ${fila.primer_apellido || ''}`.trim() : '',
        'Ciudad': fila.ciudad_residencia,
        'Correo': fila.correo,
        'Teléfono': fila.celular,
        'Celular': fila.celular,
        'Tipo Credito': fila.tipo_credito,
        'Tipo Crédito': fila.tipo_credito,
        'Ciudad Residencia': fila.ciudad_residencia,
        'Documento': fila.numero_documento,
        'Estado': fila.estado_solicitud,
        'Banco': fila.banco_nombre
      };

      return mapeoColumnas[nombreColumna] || '';
    },

    verDetalle(id) {
      console.log('Ver detalle:', id);
    },

    editarFila(id) {
      console.log('Editar:', id);
    }
  }
};
</script>
```

## JavaScript Vanilla

```javascript
class TablaConfigurable {
    constructor(containerId, empresaId) {
        this.container = document.getElementById(containerId);
        this.empresaId = empresaId;
        this.columnas = [];
        this.datos = [];
        
        this.init();
    }

    async init() {
        await this.cargarConfiguracionColumnas();
        this.render();
    }

    async cargarConfiguracionColumnas() {
        try {
            const response = await fetch(`/configuraciones/columnas-tabla?empresa_id=${this.empresaId}`, {
                headers: {
                    'X-Empresa-Id': this.empresaId.toString()
                }
            });

            const result = await response.json();
            
            if (result.ok) {
                this.columnas = result.data.columnas;
            } else {
                console.error('Error:', result.error);
                this.columnas = ['Nombre', 'Ciudad', 'Correo', 'Teléfono'];
            }
        } catch (error) {
            console.error('Error cargando configuración:', error);
            this.columnas = ['Nombre', 'Ciudad', 'Correo', 'Teléfono'];
        }
    }

    setDatos(datos) {
        this.datos = datos;
        this.render();
    }

    obtenerValorColumna(objeto, campo) {
      const mapeoColumnas = {
        'Nombre': objeto.nombres ? `${objeto.nombres} ${objeto.primer_apellido || ''}`.trim() : '',
        'Ciudad': objeto.ciudad_residencia,
        'Correo': objeto.correo,
        'Teléfono': objeto.celular,
        'Celular': objeto.celular,
        'Tipo Credito': objeto.tipo_credito,
        'Tipo Crédito': objeto.tipo_credito,
        'Ciudad Residencia': objeto.ciudad_residencia,
        'Documento': objeto.numero_documento,
        'Estado': objeto.estado_solicitud,
        'Banco': objeto.banco_nombre
      };

      return mapeoColumnas[campo] || '';
    }

    render() {
        const html = `
            <h2>Tabla Principal</h2>
            <table class="tabla-configurable">
                <thead>
                    <tr>
                        ${this.columnas.map(col => `<th>${col}</th>`).join('')}
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    ${this.datos.map((fila, index) => `
                        <tr>
                            ${this.columnas.map(col => `
                                <td>${this.obtenerValorColumna(fila, col)}</td>
                            `).join('')}
                            <td>
                                <button onclick="verDetalle(${fila.id})">Ver</button>
                                <button onclick="editarFila(${fila.id})">Editar</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        this.container.innerHTML = html;
    }
}

// Uso
const tabla = new TablaConfigurable('tabla-container', 1);

// Cuando tengas los datos
tabla.setDatos(misDatos);
```

## CSS

```css
.tabla-configurable {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

.tabla-configurable th,
.tabla-configurable td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

.tabla-configurable th {
    background-color: #f5f5f5;
    font-weight: bold;
}

.tabla-configurable button {
    margin-right: 5px;
    padding: 5px 10px;
    border: none;
    border-radius: 3px;
    cursor: pointer;
}

.tabla-configurable button:first-child {
    background-color: #007bff;
    color: white;
}

.tabla-configurable button:last-child {
    background-color: #28a745;
    color: white;
}
```

## Uso del componente

```jsx
// En tu componente principal
function PaginaPrincipal() {
    const [datos, setDatos] = useState([]);
    const empresaId = 1;

    useEffect(() => {
        // Cargar tus datos desde el backend
        cargarDatos();
    }, []);

    const cargarDatos = async () => {
        // Tu lógica para cargar datos
        const response = await fetch(`/solicitantes?empresa_id=${empresaId}`);
        const result = await response.json();
        setDatos(result.data);
    };

    return (
        <div>
            <TablaConColumnasConfigurables 
                empresaId={empresaId}
                datos={datos}
            />
        </div>
    );
}
```
