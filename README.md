# Red de Transporte Urbano Inteligente

Este proyecto implementa un sistema inteligente de gestión y análisis de redes de transporte urbano. Utiliza un grafo dirigido y ponderado para modelar la red de transporte, permitiendo calcular rutas óptimas, analizar la conectividad y simular condiciones de tráfico en tiempo real.

## Características Principales

- 🚇 Modelado de red multimodal (metro, buses, puntos de integración)
- 🗺️ Cálculo de rutas más cortas usando el algoritmo de Dijkstra
- 🔄 Detección de ciclos y análisis de conectividad
- ⏰ Simulación de congestión basada en horarios
- 📊 Visualización interactiva de rutas y estaciones
- 🔍 Cálculo de rutas alternativas
- 🕒 Estimación de tiempos de llegada en tiempo real

## Estado de Congestión

El sistema monitorea automáticamente el estado de la red:
- 7:00-9:00: Alta congestión (Hora pico mañana)
- 17:00-19:00: Alta congestión (Hora pico tarde)
- Resto del día: Tráfico fluido

## Estructura del Proyecto

```
Red-de-Transporte-Urbano-Inteligente/
│
├── main.py                     # Backend FastAPI
├── src/
│   ├── __init__.py            # Inicializador del paquete
│   ├── graph.py               # Implementación del grafo
│   ├── dijkstra.py            # Algoritmo de Dijkstra
│   ├── utils.py               # Utilidades y funciones auxiliares
│   └── data/                  # Directorio de datos
│       └── red.json           # Datos de la red de transporte
├── templates/                 # Plantillas HTML
│   ├── index.html            # Página principal
│   └── resultado.html        # Visualización de rutas
├── static/                    # Archivos estáticos (CSS, JS)
├── test/                     # Pruebas unitarias
│   ├── __init__.py           # Inicializador del paquete de pruebas
│   ├── test_graph.py         # Pruebas del grafo
│   ├── test_dijkstra.py      # Pruebas del algoritmo Dijkstra
│   ├── test_utils.py         # Pruebas de utilidades
│   └── test_main.py          # Pruebas de la API
├── requirements.txt          # Dependencias del proyecto
├── .gitignore               # Archivos ignorados por git
└── README.md                # Documentación del proyecto
```

## Requisitos Previos

- Python 3.12 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clona el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd Red-de-Transporte-Urbano-Inteligente
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución

1. Ejecuta las pruebas unitarias:
```bash
python -m pytest test/ -v
```

2. Inicia el servidor:
```bash
uvicorn main:app --reload
```

3. Abre tu navegador y visita:
```
http://localhost:8000
```

## Tecnologías Utilizadas

- **Backend:**
  - Python 3.12+
  - FastAPI (Framework web)
  - NetworkX (Análisis de grafos)
  - Uvicorn (Servidor ASGI)

- **Frontend:**
  - HTML5
  - CSS3
  - Jinja2 (Templating)
  - JavaScript

## Características Técnicas

- Implementación de grafo dirigido y ponderado
- Algoritmo de Dijkstra para rutas más cortas
- Análisis de conectividad fuerte
- Detección de ciclos
- Simulación de congestión basada en horarios
- Cálculo de rutas alternativas
- Visualización interactiva de la red

## Desarrolladores

* [Edison Ospina Arroyave](https://github.com/EdisonOspina16)
* [Jhon Steven Ceballos](https://github.com/JHONCE79)
* [Ximena Ruiz Arias](https://github.com/ximerza)

## Contribuir

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.