from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.graph import Grafo
from src.dijkstra import dijkstra
from src.utils import es_fuertemente_conexo
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

<<<<<<< HEAD
@app.get("/simulacion", response_class=HTMLResponse)
def simulacion(request: Request):
    estaciones = sorted([estacion.nombre for estacion in red.vertices.values()])
    return templates.TemplateResponse("simulacion.html", {
        "request": request,
        "estaciones": estaciones,
        "red_original": red
    })
=======
>>>>>>> 970da7ff453ca3af322cfad65b0ff6fc73745067

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
        
        # Obtener la ruta principal y alternativas
        rutas_alternativas = []
        tiempos_alternativos = []
        camino_principal = caminos[destino_id]
        camino_principal_nombres = [red.obtener_nombre_por_id(estacion_id) for estacion_id in camino_principal]
        
        # Calcular ruta alternativa excluyendo estaciones de la ruta principal
        estaciones_intermedias = camino_principal[1:-1]
        for estacion_excluida in estaciones_intermedias:
            logger.info(f"Intentando encontrar ruta alternativa excluyendo: {estacion_excluida}")
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
                        
                        logger.info(f"Ruta alternativa encontrada: {' -> '.join(camino_alt_nombres)}")
                        rutas_alternativas.append(camino_alt_nombres)
                        tiempos_alternativos.append(tiempo_alt)
                        break  # Solo necesitamos una ruta alternativa
            except Exception as e:
                logger.warning(f"Error al calcular ruta alternativa: {str(e)}")
                continue
        
        # Calcular hora actual y estimada de llegada
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        # Calcular hora estimada de llegada para la ruta principal
        minutos_totales = now.hour * 60 + now.minute + int(tiempo)
        hora_llegada = f"{minutos_totales // 60:02d}:{minutos_totales % 60:02d}"
        
        # Calcular hora estimada de llegada para la ruta alternativa
        hora_llegada_alt = []
        if tiempos_alternativos:
            minutos_alt = now.hour * 60 + now.minute + int(tiempos_alternativos[0])
            hora_llegada_alt = [f"{minutos_alt // 60:02d}:{minutos_alt % 60:02d}"]
        
        logger.info(f"Ruta encontrada con {len(camino_principal_nombres)} estaciones y tiempo {tiempo}")
        logger.info(f"Se encontró {len(rutas_alternativas)} ruta alternativa")
        if tiempos_alternativos:
            logger.info(f"Ruta alternativa: {tiempos_alternativos[0]} minutos")

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
            "horas_llegada_alt": hora_llegada_alt
        })
    except Exception as e:
        logger.error(f"Error al calcular la ruta: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al calcular la ruta: {str(e)}"
<<<<<<< HEAD
        )

@app.post("/simular", response_class=HTMLResponse)
def simular_cambios(
    request: Request,
    estacion: str = Form(...),
    tipo_cambio: str = Form(...),
    valor: float = Form(...)
):
    try:
        # Hacer una copia de la red original para simular
        red_simulada = red.copiar()
        
        mensaje = ""
        if tipo_cambio == "congestion":
            # Aumentar tiempo en todas las conexiones desde/hacia la estación
            estacion_id = red.obtener_id_por_nombre(estacion)
            if estacion_id is None:
                raise HTTPException(status_code=400, detail=f"Estación '{estacion}' no encontrada")
            
            # Ajustar los tiempos de las rutas
            for origen, rutas in red_simulada.rutas.items():
                for destino, ruta in rutas.items():
                    if origen == estacion_id or destino == estacion_id:
                        # Aumentar el tiempo base según el porcentaje de congestión
                        factor = 1 + (valor / 100)
                        ruta.tiempo_base *= factor
            
            mensaje = f"Simulando congestión del {valor}% en {estacion}"
            
        elif tipo_cambio == "cierre":
            # Remover temporalmente la estación
            estacion_id = red.obtener_id_por_nombre(estacion)
            if estacion_id is None:
                raise HTTPException(status_code=400, detail=f"Estación '{estacion}' no encontrada")
            
            # Remover la estación y sus conexiones
            if estacion_id in red_simulada.vertices:
                del red_simulada.vertices[estacion_id]
            if estacion_id in red_simulada.rutas:
                del red_simulada.rutas[estacion_id]
            for origen in red_simulada.rutas:
                if estacion_id in red_simulada.rutas[origen]:
                    del red_simulada.rutas[origen][estacion_id]
            
            mensaje = f"Simulando cierre de la estación {estacion}"
        
        # Verificar que la red sigue siendo conexa
        if not es_fuertemente_conexo(red_simulada):
            return templates.TemplateResponse("simulacion.html", {
                "request": request,
                "mensaje": "¡Advertencia! El cambio desconectaría partes de la red",
                "estaciones": sorted([estacion.nombre for estacion in red.vertices.values()]),
                "red_original": red,
                "red_simulada": None
            })
        
        return templates.TemplateResponse("simulacion.html", {
            "request": request,
            "mensaje": mensaje,
            "estaciones": sorted([estacion.nombre for estacion in red.vertices.values()]),
            "red_original": red_simulada if tipo_cambio == "congestion" else red,
            "red_simulada": red_simulada
        })
        
    except Exception as e:
        logger.error(f"Error en la simulación: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en la simulación: {str(e)}"
        )
=======
        )
>>>>>>> 970da7ff453ca3af322cfad65b0ff6fc73745067
