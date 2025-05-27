from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.graph import Grafo
from src.dijkstra import dijkstra
from src.utils import es_fuertemente_conexo, calcular_metrica_impacto
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Montar los archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

red = Grafo()
try:
    red.cargar_desde_json("src/data/red.json")
    logger.info("Red de transporte cargada exitosamente")
except Exception as e:
    logger.error(f"Error al cargar la red de transporte: {str(e)}")
    raise

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    estaciones = sorted([estacion.nombre for estacion in red.vertices.values()])
    logger.info(f"Mostrando {len(estaciones)} estaciones en el índice")
    current_time = datetime.now().strftime("%H:%M:%S")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "estaciones": estaciones,
        "current_time": current_time
    })

@app.post("/ruta", response_class=HTMLResponse)
def calcular_ruta(request: Request, origen: str = Form(...), destino: str = Form(...)):
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
    
    try:
        logger.info(f"Ejecutando Dijkstra desde {origen_id}")
        distancias, caminos = dijkstra(red, origen_id)
        
        tiempo = distancias.get(destino_id, float('inf'))
        if tiempo == float('inf') or destino_id not in caminos:
            logger.error(f"No se encontró ruta entre {origen_id} y {destino_id}")
            raise HTTPException(
                status_code=404,
                detail=f"No existe una ruta disponible entre {origen} y {destino}"
            )
        
        # Convertir IDs de estaciones en el camino a nombres
        camino_ids = caminos[destino_id]
        camino_nombres = [red.obtener_nombre_por_id(estacion_id) for estacion_id in camino_ids]
        
        # Calcular hora actual y estimada de llegada
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        # Calcular hora estimada de llegada
        minutos_totales = now.hour * 60 + now.minute + int(tiempo)
        hora_llegada = f"{minutos_totales // 60:02d}:{minutos_totales % 60:02d}"
        
        logger.info(f"Ruta encontrada con {len(camino_nombres)} estaciones y tiempo {tiempo}")

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
        for i in range(len(camino_ids) - 1):
            rutas_camino.append((camino_ids[i], camino_ids[i + 1]))

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
            "camino": camino_nombres,
            "camino_ids": camino_ids,
            "tiempo": tiempo,
            "current_time": current_time,
            "hora_llegada": hora_llegada,
            "todas_estaciones": todas_estaciones,
            "todas_rutas": todas_rutas,
            "rutas_camino": rutas_camino
        })
    except Exception as e:
        logger.error(f"Error al calcular la ruta: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al calcular la ruta: {str(e)}"
        )

@app.post("/simular", response_class=HTMLResponse)
def simular_cambios(
    request: Request,
    estacion: str = Form(...),
    tipo_cambio: str = Form(...),
    valor: float = Form(...)
):
    # Hacer una copia de la red original para simular
    red_simulada = red.copiar()
    
    mensaje = ""
    if tipo_cambio == "congestion":
        # Aumentar tiempo en todas las conexiones desde/hacia la estación
        red_simulada.ajustar_tiempos(estacion, valor)
        mensaje = f"Simulando congestión del {valor}% en {estacion}"
    elif tipo_cambio == "cierre":
        # Remover temporalmente la estación
        red_simulada.remover_estacion(estacion)
        mensaje = f"Simulando cierre de la estación {estacion}"
    
    # Verificar que la red sigue siendo conexa
    if not es_fuertemente_conexo(red_simulada):
        return templates.TemplateResponse("simulacion.html", {
            "request": request,
            "mensaje": "¡Advertencia! El cambio desconectaría partes de la red",
            "estaciones": list(red.vertices.keys()),
            "red_original": red,
            "red_simulada": None
        })
        
    return templates.TemplateResponse("simulacion.html", {
        "request": request,
        "mensaje": mensaje,
        "estaciones": list(red.vertices.keys()),
        "red_original": red,
        "red_simulada": red_simulada
    })

@app.post("/sugerencias", response_class=HTMLResponse) 
def obtener_sugerencias(
    request: Request,
    presupuesto: float = Form(...),
    origen: str = Form(...),
    destino: str = Form(...)
):
    # Analizar rutas actuales
    distancias_original, _ = dijkstra(red, origen)
    tiempo_actual = distancias_original.get(destino, float('inf'))
    
    sugerencias = []
    
    # Identificar cuellos de botella
    cuellos_botella = red.identificar_cuellos_botella()
    
    for estacion, metricas in cuellos_botella.items():
        costo_mejora = metricas['costo_estimado']
        if costo_mejora <= presupuesto:
            # Simular mejora
            red_mejorada = red.copiar()
            red_mejorada.mejorar_estacion(estacion)
            distancias_mejorada, _ = dijkstra(red_mejorada, origen)
            tiempo_mejorado = distancias_mejorada.get(destino, float('inf'))
            
            if tiempo_mejorado < tiempo_actual:
                mejora_porcentual = ((tiempo_actual - tiempo_mejorado) / tiempo_actual) * 100
                sugerencias.append({
                    'estacion': estacion,
                    'costo': costo_mejora,
                    'mejora_tiempo': mejora_porcentual,
                    'justificacion': metricas['justificacion']
                })
    
    # Ordenar sugerencias por mejor relación costo-beneficio
    sugerencias.sort(key=lambda x: x['mejora_tiempo'] / x['costo'], reverse=True)
    
    return templates.TemplateResponse("sugerencias.html", {
        "request": request,
        "presupuesto": presupuesto,
        "sugerencias": sugerencias,
        "origen": origen,
        "destino": destino
    })
