from fastapi import FastAPI, Request, Form, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.graph import Grafo
from src.dijkstra import dijkstra_k_rutas
from src.utils import es_fuertemente_conexo, tiene_ciclos
import logging
from datetime import datetime
from dotenv import load_dotenv
import os
import copy

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

load_dotenv()
ORS_API_KEY = os.getenv("ORS_API_KEY")

def nombre_completo_estacion(estacion):
    tipo = estacion.tipo.capitalize()
    linea = estacion.linea
    return f"{estacion.nombre} ({tipo} {linea})"

def agrupar_estaciones_por_tipo_y_linea(red):
    grupos = {}
    for est in red.vertices.values():
        if est.tipo == "metro":
            grupo = f"Metro Línea {est.linea}"
        elif est.tipo == "cable":
            grupo = f"Cable Línea {est.linea}"
        elif est.tipo == "tranvia":
            grupo = "Tranvía"
        else:
            grupo = est.tipo.capitalize()
        if grupo not in grupos:
            grupos[grupo] = []
        grupos[grupo].append((est.id, nombre_completo_estacion(est)))
    return grupos

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    estaciones_agrupadas = agrupar_estaciones_por_tipo_y_linea(red)
    print(f"Total de estaciones: {len(red.vertices)}")
    print(f"Total de rutas: {sum(len(destinos) for destinos in red.rutas.values())}")
    estaciones_mapa = [
        {
            "id": est.id,
            "nombre": est.nombre,
            "linea": est.linea,
            "tipo": est.tipo,
            "coordenadas": est.coordenadas
        }
        for est in red.vertices.values()
        if hasattr(est, "coordenadas") and est.coordenadas
    ]
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

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "estaciones_agrupadas": estaciones_agrupadas, "estaciones_mapa": estaciones_mapa, "ors_api_key": ORS_API_KEY, "current_time": current_time, "estado_congestion": estado_congestion, "clase_congestion": clase_congestion}
    )

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

    # Usar directamente el ID recibido
    origen_id = origen
    destino_id = destino

    if origen_id not in red.vertices:
        logger.error(f"Estación de origen no encontrada: {origen_id}")
        raise HTTPException(status_code=400, detail=f"Estación de origen '{origen_id}' no encontrada")
    if destino_id not in red.vertices:
        logger.error(f"Estación de destino no encontrada: {destino_id}")
        raise HTTPException(status_code=400, detail=f"Estación de destino '{destino_id}' no encontrada")
    
    # Verificar conectividad fuerte y ciclos antes de calcular la ruta
    es_conexa = es_fuertemente_conexo(red)
    tiene_ciclos_red = tiene_ciclos(red)
    
    try:
        # Usar dijkstra_k_rutas para obtener las 3 rutas más cortas
        distancias, caminos = dijkstra_k_rutas(red, origen_id, K=3)
        
        # Verificar si hay rutas disponibles
        if not distancias[destino_id] or not caminos[destino_id]:
            logger.error(f"No se encontró ruta entre {origen_id} y {destino_id}")
            raise HTTPException(
                status_code=404,
                detail=f"No existe una ruta disponible entre {origen} y {destino}"
            )
        
        # Obtener la ruta principal (la más corta)
        tiempo = distancias[destino_id][0]
        camino_principal = caminos[destino_id][0]
        camino_principal_nombres = [nombre_completo_estacion(red.vertices[estacion_id]) for estacion_id in camino_principal]
        
        # Obtener rutas alternativas usando ambas estrategias
        rutas_alternativas = []
        tiempos_alternativos = []
        
        # 1. Usar las rutas K más cortas del algoritmo dijkstra_k_rutas
        for i in range(1, len(caminos[destino_id])):
            ruta_alt = caminos[destino_id][i]
            tiempo_alt = distancias[destino_id][i]
            if tiempo_alt < tiempo * 1.5:  # Solo incluir si no es más del 50% más larga
                rutas_alternativas.append([nombre_completo_estacion(red.vertices[est_id]) for est_id in ruta_alt])
                tiempos_alternativos.append(tiempo_alt)
        
        # 2. Buscar rutas alternativas excluyendo combinaciones de estaciones intermedias
        estaciones_intermedias = camino_principal[1:-1]
        if len(estaciones_intermedias) >= 2:  # Solo si hay al menos 2 estaciones intermedias
            for i in range(len(estaciones_intermedias)):
                for j in range(i + 1, len(estaciones_intermedias)):
                    # Crear una copia temporal de la red
                    red_temp = copy.deepcopy(red)
                    # Eliminar dos estaciones de la red temporal
                    red_temp.eliminar_estacion(estaciones_intermedias[i])
                    red_temp.eliminar_estacion(estaciones_intermedias[j])
                    try:
                        dist_alt, caminos_alt = dijkstra_k_rutas(red_temp, origen_id, K=1)
                        if destino_id in caminos_alt and caminos_alt[destino_id][0] != camino_principal:
                            ruta_alt = caminos_alt[destino_id][0]
                            tiempo_alt = dist_alt[destino_id][0]
                            if tiempo_alt < tiempo * 2:  # Permitir rutas hasta 2 veces más largas
                                rutas_alternativas.append([nombre_completo_estacion(red.vertices[est_id]) for est_id in ruta_alt])
                                tiempos_alternativos.append(tiempo_alt)
                    except Exception as e:
                        logger.warning(f"No se pudo calcular ruta alternativa excluyendo {estaciones_intermedias[i]} y {estaciones_intermedias[j]}: {str(e)}")
                        continue

        # Obtener la hora actual
        now = datetime.now()
        
        # Calcular hora estimada de llegada para la ruta principal
        minutos_totales = now.hour * 60 + now.minute + int(tiempo)
        hora_llegada = f"{minutos_totales // 60:02d}:{minutos_totales % 60:02d}"
        
        # Calcular hora estimada de llegada para las rutas alternativas
        hora_llegada_alt = []
        for tiempo_alt in tiempos_alternativos:
            minutos_alt = now.hour * 60 + now.minute + int(tiempo_alt)
            hora_llegada_alt.append(f"{minutos_alt // 60:02d}:{minutos_alt % 60:02d}")

        # Preparar datos para la visualización
        todas_estaciones = []
        for id, estacion in red.vertices.items():
            todas_estaciones.append({
                'id': id,
                'nombre': estacion.nombre,
                'tipo': estacion.tipo,
                'linea': estacion.linea,
                'coordenadas': estacion.coordenadas
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

        # Preparar datos para el mapa
        estaciones_mapa = []
        for id, estacion in red.vertices.items():
            if estacion.coordenadas:
                estaciones_mapa.append({
                    'id': id,
                    'nombre': estacion.nombre,
                    'tipo': estacion.tipo,
                    'linea': estacion.linea,
                    'coordenadas': estacion.coordenadas
                })

        return templates.TemplateResponse(
            "resultado.html",
            {
                "request": request,
                "origen": nombre_completo_estacion(red.vertices[origen_id]),
                "destino": nombre_completo_estacion(red.vertices[destino_id]),
                "tiempo": int(tiempo),
                "camino": camino_principal_nombres,
                "camino_ids": camino_principal,
                "rutas_alternativas": rutas_alternativas,
                "tiempos_alternativos": tiempos_alternativos,
                "hora_llegada": hora_llegada,
                "horas_llegada_alt": hora_llegada_alt,
                "es_conexa": es_conexa,
                "tiene_ciclos": tiene_ciclos_red,
                "estado_congestion": "Hora pico" if (7 <= now.hour < 9) or (17 <= now.hour < 19) else "Normal",
                "clase_congestion": "congestion-warning" if (7 <= now.hour < 9) or (17 <= now.hour < 19) else "congestion-ok",
                "todas_estaciones": todas_estaciones,
                "todas_rutas": todas_rutas,
                "rutas_camino": rutas_camino,
                "estaciones_mapa": estaciones_mapa
            }
        )
    except Exception as e:
        logger.error(f"Error al calcular la ruta: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al calcular la ruta: {str(e)}"
        )

@app.post("/api/ruta-corta")
def api_ruta_corta(origen: str = Body(...), destino: str = Body(...)):
    """
    Devuelve el camino más corto entre dos estaciones como lista de estaciones (con coordenadas).
    """
    if origen not in red.vertices or destino not in red.vertices:
        return JSONResponse(status_code=400, content={"error": "Estación no encontrada"})
    try:
        distancias, caminos = dijkstra_k_rutas(red, origen, K=1)
        if destino not in caminos:
            return JSONResponse(status_code=404, content={"error": "No existe ruta"})
        
        camino_ids = caminos[destino][0]
        camino_estaciones = []
        
        for est_id in camino_ids:
            estacion = red.vertices[est_id]
            if estacion.coordenadas:
                camino_estaciones.append({
                    'id': est_id,
                    'nombre': estacion.nombre,
                    'tipo': estacion.tipo,
                    'linea': estacion.linea,
                    'coordenadas': estacion.coordenadas
                })
        
        return JSONResponse(content={"camino": camino_estaciones})
    except Exception as e:
        logger.error(f"Error al calcular ruta corta: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})
