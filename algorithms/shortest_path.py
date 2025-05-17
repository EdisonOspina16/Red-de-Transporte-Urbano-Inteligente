"""
Módulo que implementa algoritmos para encontrar caminos más cortos en la red.

Este módulo contiene la implementación del algoritmo de Dijkstra y otras
funciones relacionadas con la búsqueda de rutas óptimas.
"""

from queue import PriorityQueue
from typing import Dict, List, Tuple, Optional
from transporte.graph.graph import TransportNetwork


def find_shortest_path(network: TransportNetwork, origin_id: str, destination_id: str) -> Tuple[
    Optional[List[str]], float]:
    """
    Implementa el algoritmo de Dijkstra para encontrar el camino más corto.

    Args:
        network: Red de transporte
        origin_id: ID de la estación de origen
        destination_id: ID de la estación de destino

    Returns:
        Tuple[List[str], float]: Tupla con la lista de IDs de estaciones en la ruta y el tiempo total
        Si no hay ruta, devuelve (None, float('inf'))
    """
    # Verificar que las estaciones existan
    if origin_id not in network.stations or destination_id not in network.stations:
        return None, float('inf')

    # Caso especial: origen y destino son iguales
    if origin_id == destination_id:
        return [origin_id], 0

    # Inicialización
    distances = {station_id: float('inf') for station_id in network.stations}
    distances[origin_id] = 0
    previous = {station_id: None for station_id in network.stations}
    visited = set()
    pq = PriorityQueue()
    pq.put((0, origin_id))

    # Bucle principal del algoritmo de Dijkstra
    while not pq.empty():
        current_distance, current_id = pq.get()

        # Si ya procesamos esta estación o encontramos distancias más cortas, saltamos
        if current_id in visited or current_distance > distances[current_id]:
            continue

        # Marcar como visitado
        visited.add(current_id)

        # Si llegamos al destino, terminamos
        if current_id == destination_id:
            break

        # Explorar vecinos
        for neighbor_id, route in network.get_neighbors(current_id).items():
            if neighbor_id in visited:
                continue

            # Calcular nueva distancia
            new_distance = distances[current_id] + route.get_effective_time()

            # Si encontramos un camino más corto
            if new_distance < distances[neighbor_id]:
                distances[neighbor_id] = new_distance
                previous[neighbor_id] = current_id
                pq.put((new_distance, neighbor_id))

    # Reconstruir el camino
    if distances[destination_id] == float('inf'):
        return None, float('inf')  # No hay camino

    path = []
    current_id = destination_id
    while current_id is not None:
        path.append(current_id)
        current_id = previous[current_id]

    path.reverse()  # El camino debe ir desde el origen al destino

    return path, distances[destination_id]


def find_all_shortest_paths(network: TransportNetwork) -> Dict[str, Dict[str, Tuple[List[str], float]]]:
    """
    Encuentra todos los caminos más cortos entre todas las estaciones usando Floyd-Warshall.

    Args:
        network: Red de transporte

    Returns:
        Dict[str, Dict[str, Tuple[List[str], float]]]: Diccionario de caminos y tiempos
    """
    # Inicializar matrices de distancias y caminos
    stations = list(network.stations.keys())
    n = len(stations)

    # Mapear índices a IDs de estaciones
    idx_to_id = {i: stations[i] for i in range(n)}
    id_to_idx = {stations[i]: i for i in range(n)}

    # Inicializar matrices
    dist = [[float('inf') for _ in range(n)] for _ in range(n)]
    next_hop = [[None for _ in range(n)] for _ in range(n)]

    # Configurar distancias iniciales
    for i in range(n):
        dist[i][i] = 0  # Distancia a sí mismo

    # Añadir aristas conocidas
    for origin_id, destinations in network.routes.items():
        for dest_id, route in destinations.items():
            i = id_to_idx[origin_id]
            j = id_to_idx[dest_id]
            dist[i][j] = route.get_effective_time()
            next_hop[i][j] = j

    # Algoritmo Floyd-Warshall
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next_hop[i][j] = next_hop[i][k]

    # Construir resultado
    result = {}
    for i in range(n):
        origin_id = idx_to_id[i]
        result[origin_id] = {}

        for j in range(n):
            dest_id = idx_to_id[j]

            # Si no hay camino
            if dist[i][j] == float('inf') or next_hop[i][j] is None and i != j:
                result[origin_id][dest_id] = (None, float('inf'))
                continue

            # Reconstruir camino
            path = [origin_id]
            current = i

            while current != j and next_hop[current][j] is not None:
                current = next_hop[current][j]
                path.append(idx_to_id[current])

            result[origin_id][dest_id] = (path, dist[i][j])

    return result


def find_k_shortest_paths(network: TransportNetwork, origin_id: str, destination_id: str, k: int = 3) -> List[
    Tuple[List[str], float]]:
    """
    Encuentra los K caminos más cortos entre dos estaciones usando el algoritmo de Yen.

    Args:
        network: Red de transporte
        origin_id: ID de la estación de origen
        destination_id: ID de la estación de destino
        k: Número de caminos a encontrar

    Returns:
        List[Tuple[List[str], float]]: Lista de tuplas (camino, tiempo) ordenadas por tiempo
    """
    # Implementación básica por ahora
    # Esta función se puede ampliar con un algoritmo más sofisticado como Yen
    shortest_path, time = find_shortest_path(network, origin_id, destination_id)
    if shortest_path is None:
        return []

    return [(shortest_path, time)]
