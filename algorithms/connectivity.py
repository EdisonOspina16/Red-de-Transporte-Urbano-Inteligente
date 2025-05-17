"""
Módulo para analizar la conectividad de la red de transporte.

Este módulo implementa algoritmos para verificar si la red es fuertemente conexa
y para identificar componentes conexas.
"""

from typing import List, Set, Dict
from collections import deque
from transporte.graph.graph import TransportNetwork


def is_strongly_connected(network: TransportNetwork) -> bool:
    """
    Verifica si el grafo es fuertemente conexo, es decir, si existe un camino
    desde cualquier estación a cualquier otra estación.

    Args:
        network: Red de transporte

    Returns:
        bool: True si la red es fuertemente conexa, False en caso contrario
    """
    if len(network.stations) <= 1:
        return True

    # Elegir una estación arbitraria para comenzar
    start_id = next(iter(network.stations.keys()))

    # Verificar si se puede llegar a todas las estaciones desde start_id
    if not can_reach_all(network, start_id):
        return False

    # Crear el grafo transpuesto (invirtiendo todas las aristas)
    transpose = create_transpose(network)

    # Verificar si se puede llegar a todas las estaciones desde start_id en el grafo transpuesto
    # Esto equivale a verificar si todas las estaciones pueden llegar a start_id en el grafo original
    return can_reach_all(transpose, start_id)


def can_reach_all(network: TransportNetwork, start_id: str) -> bool:
    """
    Verifica si desde una estación se puede alcanzar a todas las demás.

    Args:
        network: Red de transporte
        start_id: ID de la estación de inicio

    Returns:
        bool: True si se pueden alcanzar todas las estaciones, False en caso contrario
    """
    # Implementación usando BFS
    visited = set()
    queue = deque([start_id])
    visited.add(start_id)

    while queue:
        current_id = queue.popleft()

        for neighbor_id in network.get_neighbors(current_id):
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                queue.append(neighbor_id)

    # Verificar si se visitaron todas las estaciones
    return len(visited) == len(network.stations)


def create_transpose(network: TransportNetwork) -> Dict[str, Set[str]]:
    """
    Crea el grafo transpuesto (invirtiendo las aristas).

    Args:
        network: Red de transporte

    Returns:
        Dict[str, Set[str]]: Grafo transpuesto como listas de adyacencia
    """
    transpose = {station_id: set() for station_id in network.stations}

    # Invertir cada arista
    for origin_id, destinations in network.routes.items():
        for dest_id in destinations:
            transpose[dest_id].add(origin_id)

    return transpose


def find_strongly_connected_components(network: TransportNetwork) -> List[Set[str]]:
    """
    Encuentra los componentes fuertemente conexos del grafo utilizando
    el algoritmo de Kosaraju.

    Args:
        network: Red de transporte

    Returns:
        List[Set[str]]: Lista de componentes fuertemente conexos
    """
    # Fase 1: Realizar DFS en el grafo original y obtener el orden de finalización
    visited = set()
    finish_order = []

    def dfs_finish_time(station_id: str) -> None:
        visited.add(station_id)

        for neighbor_id in network.get_neighbors(station_id):
            if neighbor_id not in visited:
                dfs_finish_time(neighbor_id)

        finish_order.append(station_id)

    # Ejecutar DFS para cada estación no visitada
    for station_id in network.stations:
        if station_id not in visited:
            dfs_finish_time(station_id)

    # Fase 2: Crear el grafo transpuesto
    transpose = create_transpose(network)

    # Fase 3: Realizar DFS en el grafo transpuesto siguiendo el orden de finalización inverso
    visited.clear()
    components = []

    def dfs_component(station_id: str, component: Set[str]) -> None:
        visited.add(station_id)
        component.add(station_id)

        for neighbor_id in transpose.get(station_id, set()):
            if neighbor_id not in visited:
                dfs_component(neighbor_id, component)

    # Procesar estaciones en orden de finalización inverso
    for station_id in reversed(finish_order):
        if station_id not in visited:
            component = set()
            dfs_component(station_id, component)
            components.append(component)

    return components


def find_articulation_points(network: TransportNetwork) -> Set[str]:
    """
    Encuentra los puntos de articulación en la red (estaciones cuya eliminación
    aumentaría el número de componentes desconectados).

    Args:
        network: Red de transporte

    Returns:
        Set[str]: Conjunto de IDs de estaciones que son puntos de articulación
    """
    # Implementación usando el algoritmo de Tarjan
    if len(network.stations) <= 1:
        return set()

    articulation_points = set()
    visited = set()
    discovery_time = {}  # Tiempo de descubrimiento
    low_link = {}  # Valor low-link
    parent = {}  # Padre en el árbol DFS
    time = [0]  # Tiempo actual (lista para poder modificarlo en la función recursiva)

    def dfs(station_id: str, is_root: bool = False) -> None:
        visited.add(station_id)
        children = 0
        time[0] += 1
        discovery_time[station_id] = low_link[station_id] = time[0]

        for neighbor_id in network.get_neighbors(station_id):
            if neighbor_id not in visited:
                children += 1
                parent[neighbor_id] = station_id

                dfs(neighbor_id)

                # Actualizar low-link
                low_link[station_id] = min(low_link[station_id], low_link[neighbor_id])

                # Condición 1: No es raíz y low-link del hijo >= discovery time
                if not is_root and low_link[neighbor_id] >= discovery_time[station_id]:
                    articulation_points.add(station_id)

            elif neighbor_id != parent.get(station_id):
                low_link[station_id] = min(low_link[station_id], discovery_time[neighbor_id])

        # Condición 2: Es raíz y tiene más de un hijo
        if is_root and children > 1:
            articulation_points.add(station_id)

    # Ejecutar DFS desde cada estación no visitada
    for station_id in network.stations:
        if station_id not in visited:
            dfs(station_id, True)

    return articulation_points
