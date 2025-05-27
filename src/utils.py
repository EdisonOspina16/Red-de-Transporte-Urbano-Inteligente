from src.graph import Grafo

def dfs_ciclos(grafo, nodo, visitados, stack):
    """
    Función auxiliar para detectar ciclos en el grafo usando DFS.
    
    Args:
        grafo (Grafo): Grafo a analizar
        nodo (str): Nodo actual en el recorrido
        visitados (set): Conjunto de nodos ya visitados
        stack (set): Conjunto de nodos en el camino actual
        
    Returns:
        bool: True si se encuentra un ciclo, False en caso contrario
    """
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
    """
    Verifica si el grafo contiene ciclos.
    
    Args:
        grafo (Grafo): Grafo a analizar
        
    Returns:
        bool: True si el grafo contiene ciclos, False en caso contrario
    """
    visitados = set()
    for nodo in grafo.rutas:
        if nodo not in visitados:
            if dfs_ciclos(grafo, nodo, visitados, set()):
                return True
    return False


def es_fuertemente_conexo(grafo):
    """
    Verifica si el grafo es fuertemente conexo.
    Un grafo es fuertemente conexo si desde cualquier vértice se puede llegar a cualquier otro.
    
    Args:
        grafo (Grafo): Grafo a analizar
        
    Returns:
        bool: True si el grafo es fuertemente conexo, False en caso contrario
    """
    vertices = list(grafo.vertices.keys())
    if not vertices:
        return True

    def dfs(vertice, visitados):
        """
        Función auxiliar para realizar DFS desde un vértice.
        
        Args:
            vertice (str): Vértice inicial
            visitados (set): Conjunto de vértices visitados
        """
        visitados.add(vertice)
        for destino in grafo.rutas.get(vertice, {}):
            if destino not in visitados:
                dfs(destino, visitados)

    # Verificar desde cada vértice
    for vertice in vertices:
        visitados = set()
        dfs(vertice, visitados)
        if len(visitados) != len(vertices):
            return False
    return True

def actualizar_peso(grafo, origen, destino, nuevo_peso):
    if nuevo_peso < 0:
        return False
    if origen not in grafo.rutas or destino not in grafo.rutas[origen]:
        return False
    grafo.rutas[origen][destino].tiempo_base = nuevo_peso
    return True

def calcular_metrica_impacto(grafo, estacion_id):
    """
    Calcula métricas de impacto para una estación específica.
    """
    # Obtener todas las rutas que pasan por la estación
    rutas_afectadas = []
    for origen, destinos in grafo.rutas.items():
        for destino, ruta in destinos.items():
            if origen == estacion_id or destino == estacion_id:
                rutas_afectadas.append((origen, destino, ruta))

    # Calcular métricas
    total_rutas = len(rutas_afectadas)
    tiempo_total = sum(ruta.tiempo_base for _, _, ruta in rutas_afectadas)
    pasajeros_estimados = sum(ruta.tiempo_base * 10 for _, _, ruta in rutas_afectadas)  # Estimación simple

    return {
        "total_rutas": total_rutas,
        "tiempo_total": tiempo_total,
        "pasajeros_estimados": pasajeros_estimados
    }
