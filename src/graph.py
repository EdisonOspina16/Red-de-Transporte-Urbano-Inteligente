import json
from datetime import datetime


class Estacion:
    def __init__(self, id, nombre, tipo, linea, conexiones):
        self.id = id
        self.nombre = nombre
        self.tipo = tipo
        self.linea = linea
        self.conexiones = conexiones


class Ruta:
    def __init__(self, origen, destino, tipo, tiempo, congestion_tipica):
        self.origen = origen
        self.destino = destino
        self.tipo = tipo
        self.tiempo_base = tiempo
        self.congestion_tipica = congestion_tipica

    def calcular_tiempo_actual(self, hora=None):
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
    def __init__(self):
        self.vertices = {}  # id -> Estacion
        self.rutas = {}  # origen -> {destino -> Ruta}
        self.nombres_a_ids = {}  # nombre -> id

    def agregar_estacion(self, id, datos):
        print(f"Agregando estación: {id} - {datos['nombre']}")  # Debug log
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
        print(f"Agregando ruta: {origen} -> {destino}")  # Debug log
        # Crear ruta de ida
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
        if origen in self.rutas and destino in self.rutas[origen]:
            return self.rutas[origen][destino].calcular_tiempo_actual()
        return float('inf')

    def obtener_adyacentes(self, estacion):
        print(f"Obteniendo adyacentes para: {estacion}")  # Debug log
        if estacion not in self.rutas:
            print(f"No se encontraron rutas para: {estacion}")  # Debug log
            return {}
        adyacentes = {destino: ruta.calcular_tiempo_actual() for destino, ruta in self.rutas[estacion].items()}
        print(f"Adyacentes encontrados: {adyacentes}")  # Debug log
        return adyacentes

    def obtener_id_por_nombre(self, nombre):
        print(f"Buscando ID para nombre: {nombre}")  # Debug log
        id_encontrado = self.nombres_a_ids.get(nombre)
        print(f"ID encontrado: {id_encontrado}")  # Debug log
        return id_encontrado

    def obtener_nombre_por_id(self, id):
        if id in self.vertices:
            return self.vertices[id].nombre
        return None

    def cargar_desde_json(self, archivo):
        print(f"Cargando datos desde: {archivo}")  # Debug log
        with open(archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # Cargar estaciones
        for id, datos_estacion in datos["vertices"].items():
            self.agregar_estacion(id, datos_estacion)
        
        # Cargar rutas
        for ruta in datos["rutas"]:
            self.agregar_ruta(ruta["origen"], ruta["destino"], ruta)
        
        print(f"Total de estaciones cargadas: {len(self.vertices)}")  # Debug log
        print(f"Total de rutas cargadas: {sum(len(rutas) for rutas in self.rutas.values())}")  # Debug log

    def obtener_info_estacion(self, id):
        if id in self.vertices:
            estacion = self.vertices[id]
            return {
                "nombre": estacion.nombre,
                "tipo": estacion.tipo,
                "linea": estacion.linea,
                "conexiones": estacion.conexiones
            }
        return None
