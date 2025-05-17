"""
Módulo para optimizar la red de transporte.

Este módulo implementa algoritmos para sugerir mejoras en la red,
como nuevas conexiones que reduzcan los tiempos de viaje.
"""

from typing import List, Tuple, Dict, Set
import heapq
from transporte.graph.graph import TransportNetwork
from transporte.algorithms.shortest_path import find_all_shortest_paths


def calculate_average_travel_time(network: TransportNetwork) -> float:
    """
    Calcula el tiempo promedio de viaje entre todas las estaciones.

    Args:
        network: Red de transporte

    Returns:
        float: Tiempo promedio de viaje en minutos
    """
    all_paths = find_all_shortest_paths(network)

    total_time = 0.0
    count = 0

    for origin_id in network.stations:
        for dest_id in network.stations:
            if origin_id != dest_id:
                path, time = all_paths[origin_id][dest_id]
                if path is not None:  # Si existe un camino
                    total_time += time
                    count += 1

    if count == 0:
        return float('inf')

    return total_time / count


def suggest_new_connections(network: TransportNetwork, budget: float, max_suggestions: int = 5) -> List[
    Tuple[str, str, float]]:
    """
    Sugiere nuevas conexiones que podrían reducir el tiempo promedio de viaje.

    Args:
        network: Red de transporte
        budget: Presupuesto de tiempo máximo para nuevas conexiones (minutos)
        max_suggestions: Número máximo de sugerencias a devolver

    Returns:
        List[Tuple[str, str, float]]: Lista de tuples (origen, destino, tiempo estimado)
    """
    # Calcular el tiempo promedio de viaje actual
    current_avg_time = calculate_average_travel_time(network)

    # Calcular todas las rutas más cortas actuales
    all_paths = find_all_shortest_paths(network)

    # Crear una copia del grafo para simular cambios
    # (En una implementación real, clonaríamos el grafo)

    # Encontrar pares de estaciones sin conexión directa
    potential_connections = []

    for origin_id in network.stations:
        for dest_id in network.stations:
            # Saltar si es la misma estación o ya existe una conexión directa
            if origin_id == dest_id or dest_id in network.get_neighbors(origin_id):
                continue

            # Estimar el tiempo de la nueva conexión
            # Podríamos usar la distancia euclídea entre las coordenadas,
            # pero para simplificar usaremos un valor basado en la ruta actual
            path, current_time = all_paths[origin_id][dest_id]

            if path is None:
                # No hay ruta actual, asignamos un tiempo proporcional a la red
                estimated_time = budget  # Como máximo, usamos todo el presupuesto
            else:
                # Estimamos que una conexión directa tomaría ~70% del tiempo actual
                estimated_time = current_time * 0.7

            # Verificar si está dentro del presupuesto
            if estimated_time <= budget:
                # Calcular el impacto potencial
                impact = estimate_connection_impact(network, all_paths, origin_id, dest_id, estimated_time)
                potential_connections.append((impact, origin_id, dest_id, estimated_time))

    # Ordenar por impacto (mayor primero)
    potential_connections.sort(reverse=True)

    # Devolver las mejores sugerencias
    suggestions = []
    for _, origin_id, dest_id, time in potential_connections[:max_suggestions]:
        suggestions.append((origin_id, dest_id, time))

    return suggestions


def estimate_connection_impact(
        network: TransportNetwork,
        all_paths: Dict[str, Dict[str, Tuple[List[str], float]]],
        origin_id: str,
        dest_id: str,
        connection_time: float
) -> float:
    """
    Estima el impacto de agregar una nueva conexión en el tiempo promedio de viaje.

    Args:
        network: Red de transporte
        all_paths: Diccionario con todas las rutas más cortas actuales
        origin_id: ID de la estación de origen para la nueva conexión
        dest_id: ID de la estación de destino para la nueva conexión
        connection_time: Tiempo estimado para la nueva conexión

    Returns:
        float: Reducción estimada en el tiempo promedio de viaje (valor positivo)
    """
    total_improvement = 0.0
    pairs_affected = 0

    # Para cada par de estaciones
    for start_id in network.stations:
        for end_id in network.stations:
            if start_id == end_id:
                continue

            # Obtener el tiempo actual
            _, current_time = all_paths[start_id][end_id]

            # Si no hay ruta actual, ignoramos este par
            if current_time == float('inf'):
                continue

            # Calcular el nuevo tiempo considerando la conexión propuesta
            # (empíricamente, comprobando si usar la nueva conexión mejora)

            # Ruta: start -> origin -> dest -> end
            path1_time = float('inf')
            if start_id != origin_id and end_id != dest_id:
                _, time_to_origin = all_paths[start_id][origin_id]
                _, time_from_dest = all_paths[dest_id][end_id]
                if time_to_origin != float('inf') and time_from_dest != float('inf'):
                    path1_time = time_to_origin + connection_time + time_from_dest

            # Ruta: start -> dest -> origin -> end
            path2_time = float('inf')
            if start_id != dest_id and end_id != origin_id:
                _, time_to_dest = all_paths[start_id][dest_id]
                _, time_from_origin = all_paths[origin_id][end_id]
                if time_to_dest != float('inf') and time_from_origin != float('inf'):
                    path2_time = time_to_dest + connection_time + time_from_origin

            # El nuevo tiempo sería el mínimo entre el actual y los dos nuevos caminos
            new_time = min(current_time, path1_time, path2_time)

            # Si hay mejora, la acumulamos
            improvement = current_time - new_time
            if improvement > 0.001:  # Umbral pequeño para evitar errores de punto flotante
                total_improvement += improvement
                pairs_affected += 1

    # Normalizar por el número de pares afectados
    if pairs_affected == 0:
        return 0.0

    return total_improvement / pairs_affected


def optimize_congestion(network: TransportNetwork) -> Dict[Tuple[str, str], float]:
    """
    Optimiza los factores de congestión para distribuir mejor el tráfico.

    Args:
        network: Red de transporte

    Returns:
        Dict[Tuple[str, str], float]: Diccionario con las rutas y sus factores de congestión sugeridos
    """
    # Este es un algoritmo simplificado para redistribuir la congestión
    # En un sistema real, se usarían datos históricos y predicciones

    # Encontrar rutas alternativas para las rutas más congestionadas
    congested_routes = []

    # Identificar rutas congestionadas (factor > 1.2)
    for origin_id, destinations in network.routes.items():
        for dest_id, route in destinations.items():
            if route.congestion_factor > 1.2:
                congested_routes.append((origin_id, dest_id, route))

    # Ordenar por nivel de congestión (mayor primero)
    congested_routes.sort(key=lambda x: x[2].congestion_factor, reverse=True)

    # Buscar rutas alternativas para cada ruta congestionada
    suggestions = {}

    for origin_id, dest_id, route in congested_routes:
        # Encontrar rutas alternativas
        alternative_paths = find_alternative_paths(network, origin_id, dest_id)

        # Si hay alternativas, sugerir redistribución
        if alternative_paths:
            # Calcular factor de redistribución
            redistribution_factor = 0.9  # Reducir congestión un 10%
            suggestions[(origin_id, dest_id)] = route.congestion_factor * redistribution_factor

    return suggestions


def find_alternative_paths(network: TransportNetwork, origin_id: str, dest_id: str, max_alternatives: int = 2) -> List[
    List[str]]:
    """
    Encuentra caminos alternativos entre dos estaciones.

    Args:
        network: Red de transporte
        origin_id: ID de la estación de origen
        dest_id: ID de la estación de destino
        max_alternatives: Número máximo de alternativas a buscar

    Returns:
        List[List[str]]: Lista de caminos alternativos
    """
    # Implementación simple para encontrar caminos que no usen el enlace directo

    # Crear una copia del grafo sin el enlace directo
    # (En una implementación real, clonaríamos el grafo)

    # Para simplificar, usaremos un enfoque de BFS modificado
    visited = {origin_id: []}
    queue = [(origin_id, [origin_id])]
    alternatives = []

    while queue and len(alternatives) < max_alternatives:
        current_id, path = queue.pop(0)

        # Si llegamos al destino y el camino no usa el enlace directo
        if current_id == dest_id and len(path) > 2:
            alternatives.append(path)
            continue

        # Explorar vecinos
        for neighbor_id in network.get_neighbors(current_id):
            # Evitar ciclos
            if neighbor_id in path:
                continue

            # Evitar el enlace directo
            if current_id == origin_id and neighbor_id == dest_id:
                continue

            # Agregar a la cola
            new_path = path + [neighbor_id]
            queue.append((neighbor_id, new_path))

    return alternatives
