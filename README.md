# Red de Transporte Urbano Inteligente

Este proyecto modela y analiza una red de transporte urbano inteligente, conectando estaciones de metro, paradas de buses y puntos de integración multimodal mediante un grafo dirigido y ponderado. Se permite calcular rutas más cortas, detectar ciclos, verificar conectividad, simular congestión y visualizar resultados por medio de una interfaz web sencilla.
---
Si la hora actual está entre 7:00-9:00, mostrará "Alta congestión (Hora pico mañana)" en rojo.
Si la hora está entre 17:00-19:00, mostrará "Alta congestión (Hora pico tarde)" en rojo.

---

## Estructura del Proyecto

```
transporte_inteligente/
│
├── main.py                     # Backend FastAPI
├── graph.py                    # Lógica del grafo: estaciones, rutas, algoritmos
├── data/
│   └── red_transporte.json     # Archivo de ejemplo con la red de transporte
├── templates/
│   ├── index.html              # Formulario HTML para calcular ruta
│   └── resultado.html          # Resultado de la ruta más corta
├── static/                     # Archivos estáticos (CSS)
├── requirements.txt            # Dependencias
└── README.md                   # Este archivo

```
---

## Cómo Ejecutar el Proyecto en la Terminal.

### 1. Instala las dependencias
```bash
pip install -r requirements.txt 
```
### 2. ejecuta los test 
```
python -m pytest test/tets_algoritms.py -v
```
### 3. Ejecuta el servidor
```
uvicorn main:app --reload
```


## Tecnologías Usadas
* Python 3.12 +
* FastAPI
* NetworkX
* HTML + Jinja2
* Uvicorn

## Desarrolladores 

* [Edison Ospina Arroyave](https://github.com/EdisonOspina16).
* [Jhon Steven Ceballos](https://github.com/JHONCE79).
* [Ximena Ruiz Arias](https://github.com/ximerza).