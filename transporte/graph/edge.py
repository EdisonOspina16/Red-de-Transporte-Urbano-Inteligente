"""
Módulo que define la clase Route para representar las aristas del grafo.

Cada ruta representa una conexión dirigida entre dos estaciones
en la red de transporte urbano.
"""

from .vertex import Station


class Route:
    """
    Clase que representa una ruta (arista) entre dos estaciones.

    Attributes:
        origin (Station): Estación de origen
        destination (Station): Estación de destino
        time (float): Tiempo de viaje en minutos
        distance (float): Distancia en kilómetros (opcional)
        congestion_factor (float): Factor actual de congestión
    """

    def __init__(self, origin: Station, destination: Station, time: float, distance: float = 0.0):
        """
        Inicializa una ruta con sus datos básicos.

        Args:
            origin: Estación de origen
            destination: Estación de destino
            time: Tiempo de viaje en minutos
            distance: Distancia en kilómetros (opcional)
        """
        self.origin = origin
        self.destination = destination
        self.time = time
        self.distance = distance
        self.congestion_factor = 1.0  # Factor de congestión (1.0 = normal)
        self.attributes = {}  # Atributos adicionales (tipo de transporte, frecuencia, etc.)

    def update_congestion(self, factor: float) -> None:
        """
        Actualiza el factor de congestión y recalcula el tiempo.

        Args:
            factor: Nuevo factor de congestión (1.0 = normal, >1.0 = congestionado)
        """
        self.congestion_factor = factor

    def get_effective_time(self) -> float:
        """
        Calcula el tiempo efectivo considerando la congestión actual.

        Returns:
            float: Tiempo de viaje efectivo en minutos
        """
        return self.time * self.congestion_factor

    def add_attribute(self, key: str, value) -> None:
        """
        Agrega un atributo adicional a la ruta.

        Args:
            key: Clave del atributo
            value: Valor del atributo
        """
        self.attributes[key] = value

    def get_attribute(self, key: str, default=None):
        """
        Obtiene un atributo de la ruta.

        Args:
            key: Clave del atributo
            default: Valor por defecto si la clave no existe

        Returns:
            El valor del atributo o el valor por defecto
        """
        return self.attributes.get(key, default)

    def __str__(self) -> str:
        """
        Representación en texto de la ruta.

        Returns:
            str: Representación de la ruta
        """
        return f"{self.origin.id} -> {self.destination.id} ({self.time} min)"
