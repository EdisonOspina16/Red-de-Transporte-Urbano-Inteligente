import json
from datetime import datetime


class Estacion:
    """
    Representa una estación en la red de transporte.
    
    Attributes:
        id (str): Identificador único de la estación
        nombre (str): Nombre de la estación
        tipo (str): Tipo de estación ('metro' o 'bus')
        linea (str): Línea a la que pertenece (ej: 'M1', 'M2', 'B1', 'B2')
        conexiones (list): Lista de conexiones con otras estaciones
        es_intercambiador (bool): Indica si la estación es un punto de intercambio entre líneas
    """
    def __init__(self, id, nombre, tipo, linea, conexiones):
        self.id = id
        self.nombre = nombre
        self.tipo = tipo  # 'metro' o 'bus'
        self.linea = linea  # 'M1', 'M2', 'B1', 'B2', etc.
        self.conexiones = conexiones
        self.es_intercambiador = '-' in linea  # Si la línea contiene un guión, es un intercambiador (ej: M1-M2)


class Ruta:
    """
    Representa una ruta entre dos estaciones.
    
    Attributes:
        origen (str): ID de la estación de origen
        destino (str): ID de la estación de destino
        tipo (str): Tipo de ruta
        tiempo_base (float): Tiempo base de recorrido en minutos
        congestion_tipica (dict): Factores de congestión para diferentes horarios
    """
    def __init__(self, origen, destino, tipo, tiempo, congestion_tipica):
        self.origen = origen
        self.destino = destino
        self.tipo = tipo
        self.tiempo_base = tiempo
        self.congestion_tipica = congestion_tipica

    def calcular_tiempo_actual(self, hora=None):
        """
        Calcula el tiempo actual de recorrido considerando la congestión.
        
        Args:
            hora (int, optional): Hora del día (0-23). Si es None, usa la hora actual.
            
        Returns:
            float: Tiempo de recorrido ajustado por la congestión
        """
        if hora is None:
            hora = datetime.now().hour
        
        if 7 <= hora < 9:
            factor = self.congestion_tipica["hora_pico_manana"]
        elif 17 <= hora < 19:
            factor = self.congestion_tipica["hora_pico_tarde"]
        else:
            factor = self.congestion_tipica["normal"]
        
        return self.tiempo_base * factor


class Grafo:
    """
    Representa la red de transporte como un grafo dirigido.
    
    Attributes:
        vertices (dict): Diccionario de estaciones (id -> Estacion)
        rutas (dict): Diccionario de rutas (origen -> {destino -> Ruta})
        nombres_a_ids (dict): Mapeo de nombres de estaciones a sus IDs
    """
    def __init__(self):
        self.vertices = {}  # id -> Estacion
        self.rutas = {}  # origen -> {destino -> Ruta}
        self.nombres_a_ids = {}  # nombre -> id

    def agregar_estacion(self, id, datos):
        """
        Agrega una nueva estación al grafo.
        
        Args:
            id (str): Identificador único de la estación
            datos (dict): Diccionario con los datos de la estación
                {
                    "nombre": str,
                    "tipo": str,
                    "linea": str,
                    "conexiones": list
                }
        """
        estacion = Estacion(
            id=id,
            nombre=datos["nombre"],
            tipo=datos["tipo"],
            linea=datos["linea"],
            conexiones=datos["conexiones"]
        )
        self.vertices[id] = estacion
        self.nombres_a_ids[datos["nombre"]] = id
        if id not in self.rutas:
            self.rutas[id] = {}

    def agregar_ruta(self, origen, destino, datos):
        """
        Agrega una nueva ruta entre dos estaciones.
        
        Args:
            origen (str): ID de la estación de origen
            destino (str): ID de la estación de destino
            datos (dict): Diccionario con los datos de la ruta
                {
                    "tipo": str,
                    "tiempo": float,
                    "congestion_tipica": dict
                }
        """
        ruta_ida = Ruta(
            origen=origen,
            destino=destino,
            tipo=datos["tipo"],
            tiempo=datos["tiempo"],
            congestion_tipica=datos["congestion_tipica"]
        )
        if origen not in self.rutas:
            self.rutas[origen] = {}
        self.rutas[origen][destino] = ruta_ida

    def obtener_tiempo(self, origen, destino):
        """
        Obtiene el tiempo de recorrido entre dos estaciones.
        
        Args:
            origen (str): ID de la estación de origen
            destino (str): ID de la estación de destino
            
        Returns:
            float: Tiempo de recorrido o float('inf') si no hay ruta
        """
        if origen in self.rutas and destino in self.rutas[origen]:
            return self.rutas[origen][destino].calcular_tiempo_actual()
        return float('inf')

    def obtener_adyacentes(self, estacion):
        """
        Obtiene las estaciones adyacentes y sus tiempos de recorrido.
        
        Args:
            estacion (str): ID de la estación
            
        Returns:
            dict: Diccionario {destino: tiempo} para cada estación adyacente
        """
        if estacion not in self.rutas:
            return {}
        return {destino: ruta.calcular_tiempo_actual() for destino, ruta in self.rutas[estacion].items()}

    def obtener_id_por_nombre(self, nombre):
        """
        Obtiene el ID de una estación por su nombre.
        
        Args:
            nombre (str): Nombre de la estación
            
        Returns:
            str: ID de la estación o None si no se encuentra
        """
        return self.nombres_a_ids.get(nombre)

    def obtener_nombre_por_id(self, id):
        """
        Obtiene el nombre de una estación por su ID.
        
        Args:
            id (str): ID de la estación
            
        Returns:
            str: Nombre de la estación o None si no se encuentra
        """
        if id in self.vertices:
            return self.vertices[id].nombre
        return None


    def cargar_desde_json(self, archivo):
        """
        Carga la red de transporte desde un archivo JSON.
        
        Args:
            archivo (str): Ruta al archivo JSON con los datos de la red
        """
        with open(archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # Cargar estaciones
        for id, datos_estacion in datos["vertices"].items():
            self.agregar_estacion(id, datos_estacion)
        
        # Cargar rutas
        for ruta in datos["rutas"]:
            self.agregar_ruta(ruta["origen"], ruta["destino"], ruta)

    def copia_sin_estacion(self, estacion_id):
        """
        Crea una copia del grafo excluyendo una estación específica y sus rutas.
        
        Args:
            estacion_id (str): ID de la estación a excluir
            
        Returns:
            Grafo: Nueva instancia de Grafo sin la estación especificada
        """
        nuevo_grafo = Grafo()
        
        # Copiar todas las estaciones excepto la excluida
        for id, estacion in self.vertices.items():
            if id != estacion_id:
                datos_estacion = {
                    "nombre": estacion.nombre,
                    "tipo": estacion.tipo,
                    "linea": estacion.linea,
                    "conexiones": estacion.conexiones.copy() if estacion.conexiones else []
                }
                nuevo_grafo.agregar_estacion(id, datos_estacion)
                nuevo_grafo.nombres_a_ids[estacion.nombre] = id
        
        # Copiar todas las rutas que no involucren la estación excluida
        for origen, destinos in self.rutas.items():
            if origen != estacion_id:
                for destino, ruta in destinos.items():
                    if destino != estacion_id:
                        datos_ruta = {
                            "tipo": ruta.tipo,
                            "tiempo": ruta.tiempo_base,
                            "congestion_tipica": ruta.congestion_tipica.copy()
                        }
                        nuevo_grafo.agregar_ruta(origen, destino, datos_ruta)
        
        return nuevo_grafo


