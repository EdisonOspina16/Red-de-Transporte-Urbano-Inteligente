import unittest
from src.graph import Grafo
from src.dijkstra import dijkstra

class TestDijkstra(unittest.TestCase):
    def setUp(self):
        self.grafo = Grafo()

        # Agregar estaciones
        self.grafo.agregar_estacion("A", {
            "nombre": "Estación A",
            "tipo": "Metro",
            "linea": "Línea 1",
            "conexiones": []
        })
        self.grafo.agregar_estacion("B", {
            "nombre": "Estación B",
            "tipo": "Metro",
            "linea": "Línea 1",
            "conexiones": []
        })
        self.grafo.agregar_estacion("C", {
            "nombre": "Estación C",
            "tipo": "Metro",
            "linea": "Línea 1",
            "conexiones": []
        })

        # Agregar rutas con tiempos base y factores de congestión normales (sin afectar test)
        self.grafo.agregar_ruta("A", "B", {
            "tipo": "Metro",
            "tiempo": 5,
            "congestion_tipica": {
                "normal": 1.0,
                "hora_pico_manana": 1.0,
                "hora_pico_tarde": 1.0
            }
        })

        self.grafo.agregar_ruta("B", "C", {
            "tipo": "Metro",
            "tiempo": 10,
            "congestion_tipica": {
                "normal": 1.0,
                "hora_pico_manana": 1.0,
                "hora_pico_tarde": 1.0
            }
        })

        self.grafo.agregar_ruta("A", "C", {
            "tipo": "Metro",
            "tiempo": 20,
            "congestion_tipica": {
                "normal": 1.0,
                "hora_pico_manana": 1.0,
                "hora_pico_tarde": 1.0
            }
        })
    def test_dijkstra_distancias_y_caminos(self):
        distancias, caminos = dijkstra(self.grafo, "A")

        self.assertEqual(distancias["A"], 0)
        self.assertEqual(distancias["B"], 5)
        self.assertEqual(distancias["C"], 15)

        self.assertEqual(caminos["A"], ["A"])
        self.assertEqual(caminos["B"], ["A", "B"])
        self.assertEqual(caminos["C"], ["A", "B", "C"])


if __name__ == "__main__":
    unittest.main()
    print("La prueba pasó correctamente")