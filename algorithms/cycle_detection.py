"""
Módulo para detectar ciclos en la red de transporte.

Este módulo implementa algoritmos para detectar ciclos en el grafo
dirigido que representa la red de transporte.
"""

from typing import List, Dict, Set, Optional
from transporte.graph.graph import TransportNetwork


def detect_cycles(network: TransportNetwork) -> List[List[str]]:
    """
    Detecta ciclos en la red de transporte utilizando DFS.

    Args:
        network: Red de transporte

    Returns:
        List[List[str]]: Lista de ciclos encontrados. Cada ciclo es una lista de IDs de estaciones.
    """
    cycles = []
    all_stations = set(network.stations.keys())

    # Estados para DFS
    WHITE = 0  # No visitado
    GRAY = 1  # En proceso
    BLACK = 2  # Completado

    # Inicializar estados
    color = {station_id: WHITE for station_id in all_stations}
    parent = {station_id: None for station_id in all_stations}

    # Almacenar el camino actual
    current_path = []

    def dfs_visit(station_id: str) -> None:
        """DFS recursivo para detectar ciclos."""
        nonlocal color, parent, current_path

        color[station_id] = GRAY  # En proceso
        current_path.append(station_id)

        # Explorar vecinos
        for neighbor_id in network.get_neighbors(station_id):
            # Si el vecino no ha sido visitado
            if color[neighbor_id] == WHITE:
                parent[neighbor_id] = station_id
                dfs_visit(neighbor_id)

            # Si el vecino está en proceso, hay un ciclo
            elif color[neighbor_id] == GRAY:
                # Encontrar el inicio del ciclo
                cycle_start_idx = current_path.index(neighbor_id)
                cycle = current_path[cycle_start_idx:] + [neighbor_id]
                cycles.append(cycle)

        color[station_id] = BLACK  # Completado
        current_path.pop()

    # Iniciar DFS desde cada vértice no visitado
    for station_id in all_stations:
        if color[station_id] == WHITE:
            dfs_visit(station_id)

    return cycles


def is_acyclic(network: TransportNetwork) -> bool:
    """
    Verifica si la red de transporte es acíclica.

    Args:
        network: Red de transporte

    Returns:
        bool: True si la red es acíclica, False en caso contrario
    """
    return len(detect_cycles(network)) == 0


def get_cycle_stations(network: TransportNetwork) -> Set[str]:
    """
    Obtiene el conjunto de estaciones que forman parte de algún ciclo.

    Args:
        network: Red de transporte

    Returns:
        Set[str]: Conjunto de IDs de estaciones que forman parte de algún ciclo
    """
    cycles = detect_cycles(network)
    cycle_stations = set()

    for cycle in cycles:
        cycle_stations.update(cycle)

    return cycle_stations


def find_specific_cycle(network: TransportNetwork, station_id: str) -> Optional[List[str]]:
    """
    Encuentra un ciclo que contenga una estación específica.

    Args:
        network: Red de transporte
        station_id: ID de la estación a buscar en ciclos

    Returns:
        Optional[List[str]]: Un ciclo que contiene la estación, o None si no existe
    """
    cycles = detect_cycles(network)

    for cycle in cycles:
        if station_id in cycle:
            return cycle

    return None
