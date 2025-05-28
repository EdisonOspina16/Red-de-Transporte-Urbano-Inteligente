import unittest
from src.utils import dfs_ciclos, tiene_ciclos, es_fuertemente_conexo
from src.graph import Grafo

class TestUtils(unittest.TestCase):
    def setUp(self):
        # Crear un grafo de prueba
        self.grafo = Grafo()
        # Agregar algunas estaciones
        self.grafo.agregar_estacion("A", {"nombre": "Estacion A", "tipo": "metro", "linea": "M1", "conexiones": []})
        self.grafo.agregar_estacion("B", {"nombre": "Estacion B", "tipo": "metro", "linea": "M1", "conexiones": []})
        self.grafo.agregar_estacion("C", {"nombre": "Estacion C", "tipo": "metro", "linea": "M1", "conexiones": []})
        
        # Agregar algunas rutas
        self.grafo.agregar_ruta("A", "B", {
            "tipo": "metro",
            "tiempo": 5,
            "congestion_tipica": {
                "hora_pico_manana": 1.5,
                "hora_pico_tarde": 1.5,
                "normal": 1.0
            }
        })
        self.grafo.agregar_ruta("B", "C", {
            "tipo": "metro",
            "tiempo": 5,
            "congestion_tipica": {
                "hora_pico_manana": 1.5,
                "hora_pico_tarde": 1.5,
                "normal": 1.0
            }
        })

    def test_dfs_ciclos(self):
        # Grafo sin ciclos
        self.assertFalse(dfs_ciclos(self.grafo, "A", set(), set()))
        
        # Agregar un ciclo
        self.grafo.agregar_ruta("C", "A", {
            "tipo": "metro",
            "tiempo": 5,
            "congestion_tipica": {
                "hora_pico_manana": 1.5,
                "hora_pico_tarde": 1.5,
                "normal": 1.0
            }
        })
        self.assertTrue(dfs_ciclos(self.grafo, "A", set(), set()))

    def test_tiene_ciclos(self):
        # Grafo sin ciclos
        self.assertFalse(tiene_ciclos(self.grafo))
        
        # Agregar un ciclo
        self.grafo.agregar_ruta("C", "A", {
            "tipo": "metro",
            "tiempo": 5,
            "congestion_tipica": {
                "hora_pico_manana": 1.5,
                "hora_pico_tarde": 1.5,
                "normal": 1.0
            }
        })
        self.assertTrue(tiene_ciclos(self.grafo))

    def test_es_fuertemente_conexo(self):
        # Grafo no fuertemente conexo
        self.assertFalse(es_fuertemente_conexo(self.grafo))
        
        # Hacer el grafo fuertemente conexo
        self.grafo.agregar_ruta("C", "A", {
            "tipo": "metro",
            "tiempo": 5,
            "congestion_tipica": {
                "hora_pico_manana": 1.5,
                "hora_pico_tarde": 1.5,
                "normal": 1.0
            }
        })
        self.grafo.agregar_ruta("B", "A", {
            "tipo": "metro",
            "tiempo": 5,
            "congestion_tipica": {
                "hora_pico_manana": 1.5,
                "hora_pico_tarde": 1.5,
                "normal": 1.0
            }
        })
        self.assertTrue(es_fuertemente_conexo(self.grafo))


if __name__ == '__main__':
    unittest.main() 