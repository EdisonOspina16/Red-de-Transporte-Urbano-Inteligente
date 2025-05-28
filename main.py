from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.graph import Grafo
from src.dijkstra import dijkstra
from src.utils import es_fuertemente_conexo, tiene_ciclos
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Montar los archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inicializar la red de transporte
red = Grafo()
try:
    red.cargar_desde_json("src/data/red.json")
    logger.info("Red de transporte cargada exitosamente")
    
    # Verificar conectividad fuerte
    if es_fuertemente_conexo(red):
        logger.info("La red es fuertemente conexa")
    else:
        logger.warning("La red NO es fuertemente conexa - algunas rutas pueden no ser posibles")
    
    # Verificar ciclos
    if tiene_ciclos(red):
        logger.info("La red contiene ciclos - existen rutas circulares")
    else:
        logger.info("La red no contiene ciclos - todas las rutas son lineales")
except Exception as e:
    logger.error(f"Error al cargar la red de transporte: {str(e)}")
    raise


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """
    Ruta principal que muestra la página de inicio.
    
    Args:
        request (Request): Objeto de solicitud de FastAPI
        
    Returns:
        TemplateResponse: Página de inicio con la lista de estaciones
    """
    estaciones = sorted([estacion.nombre for estacion in red.vertices.values()])
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    hora = now.hour

    # Determinar el estado de congestión
    if 7 <= hora < 9:
        estado_congestion = "Alta congestión (Hora pico mañana)"
        clase_congestion = "congestion-high"
    elif 17 <= hora < 19:
        estado_congestion = "Alta congestión (Hora pico tarde)"
        clase_congestion = "congestion-high"
    else:
        estado_congestion = "Tráfico fluido"
        clase_congestion = "congestion-low"

    return templates.TemplateResponse("index.html", {
        "request": request,
        "estaciones": estaciones,
        "current_time": current_time,
        "estado_congestion": estado_congestion,
        "clase_congestion": clase_congestion
    })

@app.post("/ruta", response_class=HTMLResponse)
def calcular_ruta(request: Request, origen: str = Form(...), destino: str = Form(...)):
    """
    Calcula la ruta óptima entre dos estaciones y sus alternativas.
    
    Args:
        request (Request): Objeto de solicitud de FastAPI
        origen (str): Nombre de la estación de origen
        destino (str): Nombre de la estación de destino
        
    Returns:
        TemplateResponse: Página de resultados con la ruta calculada
        
    Raises:
        HTTPException: Si no se encuentran las estaciones o no hay ruta disponible
    """
    logger.info(f"Calculando ruta desde '{origen}' hasta '{destino}'")
    
    # Obtener IDs de las estaciones
    origen_id = red.obtener_id_por_nombre(origen)
    destino_id = red.obtener_id_por_nombre(destino)
    
    if origen_id is None:
        logger.error(f"Estación de origen no encontrada: {origen}")
        raise HTTPException(status_code=400, detail=f"Estación de origen '{origen}' no encontrada")
    
    if destino_id is None:
        logger.error(f"Estación de destino no encontrada: {destino}")
        raise HTTPException(status_code=400, detail=f"Estación de destino '{destino}' no encontrada")
    
    # Verificar conectividad fuerte y ciclos antes de calcular la ruta
    es_conexa = es_fuertemente_conexo(red)
    tiene_ciclos_red = tiene_ciclos(red)
    
    try:
        distancias, caminos = dijkstra(red, origen_id)
        
        tiempo = distancias.get(destino_id, float('inf'))
        if tiempo == float('inf') or destino_id not in caminos:
            logger.error(f"No se encontró ruta entre {origen_id} y {destino_id}")
            raise HTTPException(
                status_code=404,
                detail=f"No existe una ruta disponible entre {origen} y {destino}"
            )
        
        # Obtener la ruta principal y alternativas
        rutas_alternativas = []
        tiempos_alternativos = []
        camino_principal = caminos[destino_id]
        camino_principal_nombres = [red.obtener_nombre_por_id(estacion_id) for estacion_id in camino_principal]
        
        # Calcular ruta alternativa excluyendo estaciones de la ruta principal
        estaciones_intermedias = camino_principal[1:-1]
        for estacion_excluida in estaciones_intermedias:
            red_temp = red.copia_sin_estacion(estacion_excluida)
            
            try:
                distancias_alt, caminos_alt = dijkstra(red_temp, origen_id)
                if destino_id in caminos_alt and distancias_alt[destino_id] < float('inf'):
                    camino_alt = caminos_alt[destino_id]
                    camino_alt_nombres = [red.obtener_nombre_por_id(estacion_id) for estacion_id in camino_alt]
                    tiempo_alt = distancias_alt[destino_id]
                    
                    # Verificar que la ruta alternativa es diferente y válida
                    if (camino_alt_nombres != camino_principal_nombres and 
                        len(camino_alt_nombres) > 0 and 
                        camino_alt_nombres[0] == origen and 
                        camino_alt_nombres[-1] == destino):
                        
                        rutas_alternativas.append(camino_alt_nombres)
                        tiempos_alternativos.append(tiempo_alt)
                        break  # Solo necesitamos una ruta alternativa
            except Exception as e:
                logger.warning(f"Error al calcular ruta alternativa: {str(e)}")
                continue
        
        # Calcular hora actual y estimada de llegada
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        hora = now.hour

        # Determinar el estado de congestión (igual que en index)
        if 7 <= hora < 9:
            estado_congestion = "Alta congestión (Hora pico mañana)"
            clase_congestion = "congestion-high"
        elif 17 <= hora < 19:
            estado_congestion = "Alta congestión (Hora pico tarde)"
            clase_congestion = "congestion-high"
        else:
            estado_congestion = "Tráfico fluido"
            clase_congestion = "congestion-low"
        
        # Calcular hora estimada de llegada para la ruta principal
        minutos_totales = now.hour * 60 + now.minute + int(tiempo)
        hora_llegada = f"{minutos_totales // 60:02d}:{minutos_totales % 60:02d}"
        
        # Calcular hora estimada de llegada para la ruta alternativa
        hora_llegada_alt = []
        if tiempos_alternativos:
            minutos_alt = now.hour * 60 + now.minute + int(tiempos_alternativos[0])
            hora_llegada_alt = [f"{minutos_alt // 60:02d}:{minutos_alt % 60:02d}"]

        # Preparar datos para la visualización
        todas_estaciones = []
        for id, estacion in red.vertices.items():
            todas_estaciones.append({
                'id': id,
                'nombre': estacion.nombre,
                'tipo': estacion.tipo
            })

        todas_rutas = []
        rutas_camino = []
        for i in range(len(camino_principal) - 1):
            rutas_camino.append((camino_principal[i], camino_principal[i + 1]))

        for origen_est, rutas_dest in red.rutas.items():
            for destino_est, ruta in rutas_dest.items():
                todas_rutas.append({
                    'origen': origen_est,
                    'destino': destino_est,
                    'tipo': ruta.tipo,
                    'tiempo': ruta.tiempo_base
                })
        
        return templates.TemplateResponse("resultado.html", {
            "request": request,
            "origen": origen,
            "destino": destino,
            "camino": camino_principal_nombres,
            "camino_ids": camino_principal,
            "tiempo": tiempo,
            "current_time": current_time,
            "hora_llegada": hora_llegada,
            "todas_estaciones": todas_estaciones,
            "todas_rutas": todas_rutas,
            "rutas_camino": rutas_camino,
            "rutas_alternativas": rutas_alternativas,
            "tiempos_alternativos": tiempos_alternativos,
            "horas_llegada_alt": hora_llegada_alt,
            "estado_congestion": estado_congestion,
            "clase_congestion": clase_congestion,
            "es_conexa": es_conexa,
            "tiene_ciclos": tiene_ciclos_red
        })
    except Exception as e:
        logger.error(f"Error al calcular la ruta: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al calcular la ruta: {str(e)}"
        )
