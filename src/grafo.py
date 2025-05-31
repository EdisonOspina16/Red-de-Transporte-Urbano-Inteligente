class Grafo:
    def __init__(self):
        self.nodos = []

    def mostrar_grafo(self):
        """Muestra la estructura del grafo."""
        for nodo in self.nodos:
            print(f"\nNodo: {nodo.nombre}")
            print("Conexiones:")
            for conexion in nodo.conexiones:
                print(f"  -> {conexion.destino.nombre} (distancia: {conexion.distancia}, tiempo: {conexion.tiempo})") 