import unittest
from src.dijkstra import dijkstra
from src.graph import Grafo

class TestDijkstra(unittest.TestCase):
    def setUp(self):
        # Crear un grafo de prueba
        self.grafo = Grafo()
        
        # Agregar estaciones
        self.grafo.agregar_estacion("A", {"nombre": "Estacion A", "tipo": "metro", "linea": "M1", "conexiones": []})
        self.grafo.agregar_estacion("B", {"nombre": "Estacion B", "tipo": "metro", "linea": "M1", "conexiones": []})
        self.grafo.agregar_estacion("C", {"nombre": "Estacion C", "tipo": "metro", "linea": "M1", "conexiones": []})
        self.grafo.agregar_estacion("D", {"nombre": "Estacion D", "tipo": "metro", "linea": "M1", "conexiones": []})
        
        # Agregar rutas con diferentes tiempos
        self.grafo.agregar_ruta("A", "B", {
            "tipo": "metro",
            "tiempo": 5,
            "congestion_tipica": {
                "hora_pico_manana": 1.0,
                "hora_pico_tarde": 1.0,
                "normal": 1.0
            }
        })
        self.grafo.agregar_ruta("B", "C", {
            "tipo": "metro",
            "tiempo": 3,
            "congestion_tipica": {
                "hora_pico_manana": 1.0,
                "hora_pico_tarde": 1.0,
                "normal": 1.0
            }
        })
        self.grafo.agregar_ruta("A", "C", {
            "tipo": "metro",
            "tiempo": 10,
            "congestion_tipica": {
                "hora_pico_manana": 1.0,
                "hora_pico_tarde": 1.0,
                "normal": 1.0
            }
        })
        self.grafo.agregar_ruta("C", "D", {
            "tipo": "metro",
            "tiempo": 4,
            "congestion_tipica": {
                "hora_pico_manana": 1.0,
                "hora_pico_tarde": 1.0,
                "normal": 1.0
            }
        })

    def test_dijkstra_camino_mas_corto(self):
        distancias, caminos = dijkstra(self.grafo, "A")
        
        # Verificar distancias
        self.assertEqual(distancias["A"], 0)
        self.assertEqual(distancias["B"], 5)
        self.assertEqual(distancias["C"], 8)  # A -> B -> C (5 + 3)
        self.assertEqual(distancias["D"], 12)  # A -> B -> C -> D (5 + 3 + 4)
        
        # Verificar caminos
        self.assertEqual(caminos["A"], ["A"])
        self.assertEqual(caminos["B"], ["A", "B"])
        self.assertEqual(caminos["C"], ["A", "B", "C"])
        self.assertEqual(caminos["D"], ["A", "B", "C", "D"])

    def test_dijkstra_nodo_aislado(self):
        # Agregar un nodo aislado
        self.grafo.agregar_estacion("E", {"nombre": "Estacion E", "tipo": "metro", "linea": "M1", "conexiones": []})
        
        distancias, caminos = dijkstra(self.grafo, "A")
        
        # Verificar que el nodo aislado tiene distancia infinita
        self.assertEqual(distancias["E"], float('inf'))
        self.assertEqual(caminos["E"], [])

    def test_dijkstra_desde_nodo_sin_salidas(self):
        # Agregar un nodo sin salidas
        self.grafo.agregar_estacion("F", {"nombre": "Estacion F", "tipo": "metro", "linea": "M1", "conexiones": []})
        self.grafo.agregar_ruta("D", "F", {
            "tipo": "metro",
            "tiempo": 2,
            "congestion_tipica": {
                "hora_pico_manana": 1.0,
                "hora_pico_tarde": 1.0,
                "normal": 1.0
            }
        })
        
        distancias, caminos = dijkstra(self.grafo, "F")
        
        # Verificar que desde F solo se puede llegar a F
        self.assertEqual(distancias["F"], 0)
        self.assertEqual(caminos["F"], ["F"])
        for nodo in ["A", "B", "C", "D"]:
            self.assertEqual(distancias[nodo], float('inf'))
            self.assertEqual(caminos[nodo], [])

if __name__ == '__main__':
    unittest.main() 