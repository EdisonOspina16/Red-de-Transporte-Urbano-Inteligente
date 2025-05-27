from src.graph import Grafo
from src.dijkstra import dijkstra


def dfs_forward(grafo, nodo, visitados, orden):
    """DFS forward pass para Kosaraju's algorithm"""
    visitados.add(nodo)
    for vecino in grafo.rutas.get(nodo, {}):
        if vecino not in visitados:
            dfs_forward(grafo, vecino, visitados, orden)
    orden.append(nodo)


def dfs_reverse(grafo, nodo, visitados, componente):
    """DFS reverse pass para Kosaraju's algorithm"""
    visitados.add(nodo)
    componente.add(nodo)
    for origen, destinos in grafo.rutas.items():
        if nodo in destinos and origen not in visitados:
            dfs_reverse(grafo, origen, visitados, componente)


def es_fuertemente_conexo(grafo):
    """
    Verifica si el grafo es fuertemente conexo usando el algoritmo de Kosaraju.
    Un grafo es fuertemente conexo si existe un camino entre cualquier par de vértices.
    
    Args:
        grafo: Instancia de la clase Grafo
        
    Returns:
        bool: True si el grafo es fuertemente conexo, False en caso contrario
    """
    if not grafo.vertices:
        return True  # Un grafo vacío se considera fuertemente conexo
        
    # Primera pasada DFS
    visitados = set()
    orden = []
    inicio = next(iter(grafo.vertices))  # Tomar cualquier vértice inicial
    dfs_forward(grafo, inicio, visitados, orden)
    
    # Verificar si todos los vértices fueron alcanzados en la primera pasada
    if len(visitados) != len(grafo.vertices):
        return False
        
    # Segunda pasada DFS en orden reverso
    visitados = set()
    componente = set()
    dfs_reverse(grafo, orden[-1], visitados, componente)
    
    # El grafo es fuertemente conexo si todos los vértices están en la misma componente
    return len(componente) == len(grafo.vertices)


def detectar_ciclos(grafo):
    visitados = set()
    en_recursion = set()
    
    def dfs_ciclos(nodo):
        visitados.add(nodo)
        en_recursion.add(nodo)
        
        for vecino in grafo.rutas.get(nodo, {}):
            if vecino not in visitados:
                if dfs_ciclos(vecino):
                    return True
            elif vecino in en_recursion:
                return True
                
        en_recursion.remove(nodo)
        return False
    
    for nodo in grafo.vertices:
        if nodo not in visitados:
            if dfs_ciclos(nodo):
                return True
    return False


def sugerir_nuevas_conexiones(grafo, presupuesto_tiempo):
    """
    Sugiere nuevas conexiones que reduzcan el tiempo promedio entre estaciones,
    respetando un presupuesto de tiempo máximo.
    
    Args:
        grafo: Instancia de la clase Grafo
        presupuesto_tiempo: Tiempo máximo permitido para la nueva conexión
        
    Returns:
        list: Lista de tuplas (origen, destino, tiempo_estimado) con las sugerencias
    """
    # Calcular tiempos actuales entre todas las estaciones
    tiempos_actuales = {}
    for origen in grafo.vertices:
        distancias, _ = dijkstra(grafo, origen)
        for destino, tiempo in distancias.items():
            if tiempo != float('inf'):
                tiempos_actuales[(origen, destino)] = tiempo
    
    # Encontrar pares de estaciones sin conexión directa
    sugerencias = []
    for origen in grafo.vertices:
        for destino in grafo.vertices:
            if origen != destino:
                # Verificar si no hay conexión directa
                if destino not in grafo.rutas.get(origen, {}):
                    # Calcular tiempo actual entre estas estaciones
                    tiempo_actual = tiempos_actuales.get((origen, destino), float('inf'))
                    
                    # Estimar tiempo para nueva conexión (usando tiempo base + factor de congestión promedio)
                    tiempo_estimado = presupuesto_tiempo * 0.8  # 80% del presupuesto como estimación
                    
                    # Si la nueva conexión mejoraría el tiempo actual
                    if tiempo_estimado < tiempo_actual:
                        sugerencias.append((origen, destino, tiempo_estimado))
    
    # Ordenar sugerencias por mejora potencial (diferencia entre tiempo actual y estimado)
    sugerencias.sort(key=lambda x: tiempos_actuales.get((x[0], x[1]), float('inf')) - x[2], reverse=True)
    
    return sugerencias[:5]  # Retornar las 5 mejores sugerencias