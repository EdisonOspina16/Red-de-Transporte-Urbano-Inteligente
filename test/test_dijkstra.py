import unittest
from src.graph import Grafo
from src.dijkstra import dijkstra
from src.utils import es_fuertemente_conexo

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

    def test_es_fuertemente_conexo(self):
        # Caso 1: Grafo fuertemente conexo
        self.grafo.agregar_ruta("B", "A", {
            "tipo": "Metro",
            "tiempo": 5,
            "congestion_tipica": {
                "normal": 1.0,
                "hora_pico_manana": 1.0,
                "hora_pico_tarde": 1.0
            }
        })
        self.grafo.agregar_ruta("C", "B", {
            "tipo": "Metro",
            "tiempo": 10,
            "congestion_tipica": {
                "normal": 1.0,
                "hora_pico_manana": 1.0,
                "hora_pico_tarde": 1.0
            }
        })
        
        self.assertTrue(es_fuertemente_conexo(self.grafo))
        
        # Caso 2: Grafo no fuertemente conexo
        grafo_no_conexo = Grafo()
        grafo_no_conexo.agregar_estacion("X", {
            "nombre": "Estación X",
            "tipo": "Metro",
            "linea": "Línea 1",
            "conexiones": []
        })
        grafo_no_conexo.agregar_estacion("Y", {
            "nombre": "Estación Y",
            "tipo": "Metro",
            "linea": "Línea 1",
            "conexiones": []
        })
        grafo_no_conexo.agregar_ruta("X", "Y", {
            "tipo": "Metro",
            "tiempo": 5,
            "congestion_tipica": {
                "normal": 1.0,
                "hora_pico_manana": 1.0,
                "hora_pico_tarde": 1.0
            }
        })
        self.assertFalse(es_fuertemente_conexo(grafo_no_conexo))

if __name__ == "__main__":
    unittest.main()
    print("La prueba pasó correctamente")