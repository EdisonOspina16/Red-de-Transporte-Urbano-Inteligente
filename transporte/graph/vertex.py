"""
Módulo que define la clase Station para representar los vértices del grafo.

Cada estación representa un punto de parada en la red de transporte urbano.
"""


class Station:
    """
    Clase que representa una estación (vértice) en la red de transporte.

    Attributes:
        id (str): Identificador único de la estación
        name (str): Nombre descriptivo de la estación
        latitude (float): Coordenada de latitud
        longitude (float): Coordenada de longitud
        metadata (dict): Información adicional de la estación
    """

    def __init__(self, station_id: str, name: str, latitude: float = 0.0, longitude: float = 0.0):
        """
        Inicializa una estación con sus datos básicos.

        Args:
            station_id: Identificador único de la estación
            name: Nombre descriptivo de la estación
            latitude: Coordenada de latitud
            longitude: Coordenada de longitud
        """
        self.id = station_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.metadata = {}  # Información adicional como tipo de estación, servicios, etc.

    def add_metadata(self, key: str, value) -> None:
        """
        Agrega información adicional a la estación.

        Args:
            key: Clave para la información
            value: Valor asociado a la clave
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default=None):
        """
        Obtiene información adicional de la estación.

        Args:
            key: Clave de la información a obtener
            default: Valor por defecto si la clave no existe

        Returns:
            El valor asociado a la clave, o el valor por defecto
        """
        return self.metadata.get(key, default)

    def get_coordinates(self) -> tuple:
        """
        Obtiene las coordenadas geográficas de la estación.

        Returns:
            tuple: Par (latitud, longitud)
        """
        return (self.latitude, self.longitude)

    def __str__(self) -> str:
        """
        Representación en texto de la estación.

        Returns:
            str: Representación de la estación
        """
        return f"{self.id} - {self.name}"

    def __eq__(self, other) -> bool:
        """
        Compara si dos estaciones son iguales basándose en su ID.

        Args:
            other: Otra estación para comparar

        Returns:
            bool: True si son iguales, False en caso contrario
        """
        if not isinstance(other, Station):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """
        Función hash para poder usar estaciones como claves en diccionarios.

        Returns:
            int: Valor hash de la estación
        """
        return hash(self.id)