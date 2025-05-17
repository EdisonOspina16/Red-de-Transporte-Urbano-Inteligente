"""
Módulo para el grafo dirigido y ponderado que representa la red de transporte.

Este módulo contiene la implementación de la estructura principal del grafo
que modela la red de transporte urbano.
"""

from collections import defaultdict
from typing import Dict, List, Tuple, Set, Optional
from .vertex import Station
from .edge import Route


class TransportNetwork:
    """
    Clase que representa la red de transporte como un grafo dirigido y ponderado.
    Implementa operaciones básicas sobre el grafo y sirve como estructura principal
    para el sistema de transporte urbano inteligente.
    """

    def __init__(self):
        """Inicializa una red de transporte vacía."""
        self.stations: Dict[str, Station] = {}  # Diccionario de estaciones (vértices)
        self.routes: Dict[str, Dict[str, Route]] = defaultdict(dict)  # Lista de adyacencia para rutas
        self.station_count = 0
        self.route_count = 0

    def add_station(self, station_id: str, name: str, lat: float = 0.0, lon: float = 0.0) -> bool:
        """
        Agrega una estación (vértice) a la red.

        Args:
            station_id: Identificador único de la estación
            name: Nombre descriptivo de la estación
            lat: Latitud geográfica de la estación
            lon: Longitud geográfica de la estación

        Returns:
            bool: True si la estación se agregó correctamente, False si ya existía
        """
        if station_id in self.stations:
            return False

        self.stations[station_id] = Station(station_id, name, lat, lon)
        self.station_count += 1
        return True

    def remove_station(self, station_id: str) -> bool:
        """
        Elimina una estación y todas sus rutas asociadas.

        Args:
            station_id: Identificador de la estación a eliminar

        Returns:
            bool: True si la estación se eliminó correctamente, False si no existía
        """
        if station_id not in self.stations:
            return False

        # Eliminar rutas donde esta estación es origen
        if station_id in self.routes:
            self.route_count -= len(self.routes[station_id])
            del self.routes[station_id]

        # Eliminar rutas donde esta estación es destino
        for origin, destinations in self.routes.items():
            if station_id in destinations:
                del destinations[station_id]
                self.route_count -= 1

        # Eliminar la estación
        del self.stations[station_id]
        self.station_count -= 1
        return True

    def add_route(self, origin_id: str, dest_id: str, time: float) -> bool:
        """
        Agrega una ruta (arista) entre dos estaciones.

        Args:
            origin_id: Identificador de la estación de origen
            dest_id: Identificador de la estación de destino
            time: Tiempo de viaje en minutos

        Returns:
            bool: True si la ruta se agregó correctamente, False en caso contrario
        """
        if origin_id not in self.stations or dest_id not in self.stations:
            return False

        # Si ya existe la ruta, actualizar su tiempo
        if dest_id in self.routes[origin_id]:
            self.routes[origin_id][dest_id].time = time
            return True

        # Agregar nueva ruta
        self.routes[origin_id][dest_id] = Route(
            self.stations[origin_id],
            self.stations[dest_id],
            time
        )
        self.route_count += 1
        return True

    def remove_route(self, origin_id: str, dest_id: str) -> bool:
        """
        Elimina una ruta entre dos estaciones.

        Args:
            origin_id: Identificador de la estación de origen
            dest_id: Identificador de la estación de destino

        Returns:
            bool: True si la ruta se eliminó correctamente, False si no existía
        """
        if origin_id not in self.routes or dest_id not in self.routes[origin_id]:
            return False

        del self.routes[origin_id][dest_id]
        self.route_count -= 1
        return True

    def get_route(self, origin_id: str, dest_id: str) -> Optional[Route]:
        """
        Obtiene la ruta entre dos estaciones.

        Args:
            origin_id: Identificador de la estación de origen
            dest_id: Identificador de la estación de destino

        Returns:
            Route: Objeto ruta si existe, None en caso contrario
        """
        if origin_id in self.routes and dest_id in self.routes[origin_id]:
            return self.routes[origin_id][dest_id]
        return None

    def update_route_time(self, origin_id: str, dest_id: str, new_time: float) -> bool:
        """
        Actualiza el tiempo de una ruta para simular condiciones de tráfico.

        Args:
            origin_id: Identificador de la estación de origen
            dest_id: Identificador de la estación de destino
            new_time: Nuevo tiempo de viaje en minutos

        Returns:
            bool: True si se actualizó correctamente, False si la ruta no existe
        """
        route = self.get_route(origin_id, dest_id)
        if route:
            route.time = new_time
            return True
        return False

    def get_neighbors(self, station_id: str) -> Dict[str, Route]:
        """
        Obtiene todas las estaciones adyacentes a una estación dada.

        Args:
            station_id: Identificador de la estación

        Returns:
            Dict[str, Route]: Diccionario de rutas salientes de la estación
        """
        if station_id in self.routes:
            return self.routes[station_id]
        return {}

    def get_all_stations(self) -> List[Station]:
        """
        Obtiene todas las estaciones de la red.

        Returns:
            List[Station]: Lista de todas las estaciones
        """
        return list(self.stations.values())

    def get_all_routes(self) -> List[Tuple[str, str, Route]]:
        """
        Obtiene todas las rutas de la red.

        Returns:
            List[Tuple[str, str, Route]]: Lista de tuplas (origen_id, destino_id, ruta)
        """
        all_routes = []
        for origin_id, destinations in self.routes.items():
            for dest_id, route in destinations.items():
                all_routes.append((origin_id, dest_id, route))
        return all_routes

    def __str__(self) -> str:
        """Representación en texto de la red de transporte."""
        result = f"Red de Transporte: {self.station_count} estaciones, {self.route_count} rutas\n"

        for station_id, station in self.stations.items():
            result += f"Estación: {station}\n"
            if station_id in self.routes:
                for dest_id, route in self.routes[station_id].items():
                    result += f"  -> {dest_id}: {route.time} min\n"

        return result