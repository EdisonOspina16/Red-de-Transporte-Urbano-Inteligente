from src.graph import Grafo

def dfs_ciclos(grafo, nodo, visitados, stack):
    visitados.add(nodo)
    stack.add(nodo)
    for vecino in grafo.rutas.get(nodo, {}):
        if vecino not in visitados:
            if dfs_ciclos(grafo, vecino, visitados, stack):
                return True
        elif vecino in stack:
            return True
    stack.remove(nodo)
    return False

def tiene_ciclos(grafo):
    visitados = set()
    for nodo in grafo.rutas:
        if nodo not in visitados:
            if dfs_ciclos(grafo, nodo, visitados, set()):
                return True
    return False


def es_fuertemente_conexo(grafo):
    def dfs(nodo, visitados):
        visitados.add(nodo)
        for vecino in grafo.rutas.get(nodo, {}):
            if vecino not in visitados:
                dfs(vecino, visitados)
    
    # Verificar conectividad desde cada nodo
    for nodo_inicio in grafo.rutas:
        visitados = set()
        dfs(nodo_inicio, visitados)
        if len(visitados) != len(grafo.rutas):
            return False
        
        # Verificar que existe camino de vuelta
        for nodo_destino in grafo.rutas:
            if nodo_inicio != nodo_destino:
                camino_vuelta = False
                for intermedio in grafo.rutas:
                    if nodo_destino in grafo.rutas.get(intermedio, {}) and \
                       intermedio in visitados:
                        camino_vuelta = True
                        break
                if not camino_vuelta:
                    return False
    return True

def actualizar_peso(grafo, origen, destino, nuevo_peso):
    if nuevo_peso < 0:
        return False
    if origen not in grafo.rutas or destino not in grafo.rutas[origen]:
        return False
    grafo.rutas[origen][destino].tiempo_base = nuevo_peso
    return True

def calcular_metrica_impacto(grafo, origen, destino):
    """
    Calcula una métrica de impacto para una nueva conexión basada en:
    - Reducción en tiempo promedio de viaje
    - Mejora en la conectividad de la red
    - Distribución de carga en la red
    """
    # Calcular tiempos actuales entre todos los pares de estaciones
    tiempos_originales = {}
    total_rutas_posibles = 0
    rutas_infinitas = 0
    
    for origen_actual in grafo.vertices:
        distancias, caminos = dijkstra(grafo, origen_actual)
        for destino_actual, tiempo in distancias.items():
            if origen_actual != destino_actual:
                total_rutas_posibles += 1
                tiempos_originales[(origen_actual, destino_actual)] = {
                    'tiempo': tiempo,
                    'camino': caminos.get(destino_actual, [])
                }
                if tiempo == float('inf'):
                    rutas_infinitas += 1

    # Simular la nueva conexión
    grafo_simulado = grafo.copiar()
    tiempo_estimado = max(
        min(grafo.obtener_tiempo(origen, v) for v in grafo.rutas.get(origen, {}) if v != destino),
        min(grafo.obtener_tiempo(v, destino) for v in grafo.rutas.get(destino, {}) if v != origen)
    ) if grafo.rutas.get(origen, {}) and grafo.rutas.get(destino, {}) else 30  # tiempo base estimado

    grafo_simulado.agregar_ruta(origen, destino, {
        "tipo": "propuesta",
        "tiempo": tiempo_estimado,
        "congestion_tipica": {"hora_pico_manana": 1.5, "hora_pico_tarde": 1.5, "normal": 1.0}
    })

    # Calcular nuevos tiempos y rutas alternativas
    mejoras_tiempo = 0
    rutas_mejoradas = 0
    nuevas_conexiones = 0
    rutas_alternativas = []

    # Obtener todas las rutas desde origen a destino
    distancias_nuevas, caminos_nuevos = dijkstra(grafo_simulado, origen)
    
    # Encontrar las tres mejores rutas
    rutas_posibles = []
    for nodo_intermedio in grafo_simulado.vertices:
        if nodo_intermedio != origen and nodo_intermedio != destino:
            # Calcular ruta a través del nodo intermedio
            dist_origen_intermedio, camino_origen = dijkstra(grafo_simulado, origen)
            dist_intermedio_destino, camino_destino = dijkstra(grafo_simulado, nodo_intermedio)
            
            if nodo_intermedio in camino_origen.get(nodo_intermedio, []) and destino in camino_destino.get(destino, []):
                tiempo_total = dist_origen_intermedio.get(nodo_intermedio, float('inf')) + \
                             dist_intermedio_destino.get(destino, float('inf'))
                if tiempo_total != float('inf'):
                    ruta_completa = camino_origen[nodo_intermedio][:-1] + camino_destino[destino]
                    rutas_posibles.append({
                        'tiempo': tiempo_total,
                        'camino': ruta_completa
                    })
    
    # Ordenar rutas por tiempo y tomar las 3 mejores
    rutas_posibles.sort(key=lambda x: x['tiempo'])
    rutas_alternativas = rutas_posibles[:3]

    # Calcular métricas originales
    for origen_actual in grafo.vertices:
        distancias_nuevas, _ = dijkstra(grafo_simulado, origen_actual)
        for destino_actual, tiempo_nuevo in distancias_nuevas.items():
            if origen_actual != destino_actual:
                tiempo_original = tiempos_originales[(origen_actual, destino_actual)]['tiempo']
                if tiempo_original == float('inf') and tiempo_nuevo != float('inf'):
                    nuevas_conexiones += 1
                elif tiempo_nuevo < tiempo_original:
                    mejoras_tiempo += (tiempo_original - tiempo_nuevo)
                    rutas_mejoradas += 1

    # Calcular métricas de impacto
    impacto_conectividad = nuevas_conexiones / max(1, rutas_infinitas) if rutas_infinitas > 0 else 0
    impacto_tiempo = mejoras_tiempo / max(1, rutas_mejoradas) if rutas_mejoradas > 0 else 0
    
    return {
        "impacto_conectividad": impacto_conectividad,
        "impacto_tiempo": impacto_tiempo,
        "rutas_mejoradas": rutas_mejoradas,
        "nuevas_conexiones": nuevas_conexiones,
        "tiempo_estimado": tiempo_estimado,
        "rutas_alternativas": rutas_alternativas
    }

def estimar_costo_conexion(grafo, origen, destino):
    """
    Estima el costo de implementar una nueva conexión basado en:
    - Distancia entre estaciones
    - Tipo de estaciones
    - Infraestructura existente
    """
    # Factores de costo base según tipo de estación
    costos_tipo = {
        "metro": 1000,
        "bus": 500,
        "intermodal": 750
    }
    
    # Obtener tipos de estaciones
    tipo_origen = grafo.vertices[origen].tipo
    tipo_destino = grafo.vertices[destino].tipo
    
    # Costo base según tipos de estaciones
    costo_base = (costos_tipo.get(tipo_origen, 500) + costos_tipo.get(tipo_destino, 500)) / 2
    
    # Factor de complejidad basado en conexiones existentes
    factor_complejidad = 1.0
    if len(grafo.rutas.get(origen, {})) > 3:
        factor_complejidad *= 1.2  # Estación origen muy conectada
    if len(grafo.rutas.get(destino, {})) > 3:
        factor_complejidad *= 1.2  # Estación destino muy conectada
        
    return costo_base * factor_complejidad

def sugerir_conexiones(grafo, presupuesto):
    """
    Sugiere nuevas conexiones optimizando el presupuesto disponible.
    Retorna una lista de sugerencias ordenadas por relación costo-beneficio.
    """
    sugerencias = []
    
    # Analizar todas las posibles conexiones nuevas
    for origen in grafo.vertices:
        for destino in grafo.vertices:
            if origen != destino and destino not in grafo.rutas.get(origen, {}):
                # Calcular métricas de impacto
                metricas = calcular_metrica_impacto(grafo, origen, destino)
                
                # Estimar costo
                costo = estimar_costo_conexion(grafo, origen, destino)
                
                if costo <= presupuesto:
                    # Calcular score de beneficio
                    beneficio = (
                        metricas["impacto_conectividad"] * 0.4 +  # 40% peso a mejora en conectividad
                        metricas["impacto_tiempo"] * 0.3 +        # 30% peso a reducción de tiempo
                        (metricas["rutas_mejoradas"] / len(grafo.vertices)) * 0.2 +  # 20% peso a rutas mejoradas
                        (metricas["nuevas_conexiones"] / len(grafo.vertices)) * 0.1   # 10% peso a nuevas conexiones
                    )
                    
                    # Calcular ROI (Return on Investment)
                    roi = beneficio / costo if costo > 0 else 0
                    
                    sugerencias.append({
                        "origen": origen,
                        "destino": destino,
                        "costo": costo,
                        "beneficio": beneficio,
                        "roi": roi,
                        "metricas": metricas,
                        "justificacion": {
                            "mejora_conectividad": f"Conecta {metricas['nuevas_conexiones']} nuevos pares de estaciones",
                            "ahorro_tiempo": f"Mejora {metricas['rutas_mejoradas']} rutas existentes",
                            "tiempo_promedio": f"Reduce en promedio {metricas['impacto_tiempo']:.1f} minutos por ruta",
                            "costo_beneficio": f"ROI estimado: {roi:.2f}"
                        }
                    })
    
    # Ordenar por ROI (mayor a menor)
    sugerencias.sort(key=lambda x: x["roi"], reverse=True)
    
    # Retornar las mejores sugerencias dentro del presupuesto
    sugerencias_filtradas = []
    presupuesto_restante = presupuesto
    
    for sugerencia in sugerencias:
        if presupuesto_restante >= sugerencia["costo"]:
            sugerencias_filtradas.append(sugerencia)
            presupuesto_restante -= sugerencia["costo"]
            
        if len(sugerencias_filtradas) >= 5:  # Limitar a las 5 mejores sugerencias
            break
    
    return sugerencias_filtradas
