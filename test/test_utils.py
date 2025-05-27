import unittest
from src.graph import Grafo
from src.utils import sugerir_nuevas_conexiones

class TestSugerirNuevasConexiones(unittest.TestCase):
    def setUp(self):
        self.grafo = Grafo()
        
        # Crear una red simple de 4 estaciones
        self.grafo.agregar_estacion("A", {
            "nombre": "Estación A",
            "tipo": "metro",
            "linea": "L1",
            "conexiones": []
        })
        self.grafo.agregar_estacion("B", {
            "nombre": "Estación B",
            "tipo": "metro",
            "linea": "L1",
            "conexiones": []
        })
        self.grafo.agregar_estacion("C", {
            "nombre": "Estación C",
            "tipo": "metro",
            "linea": "L2",
            "conexiones": []
        })
        self.grafo.agregar_estacion("D", {
            "nombre": "Estación D",
            "tipo": "metro",
            "linea": "L2",
            "conexiones": []
        })
        
        # Agregar algunas rutas existentes
        self.grafo.agregar_ruta("A", "B", {
            "tipo": "metro",
            "tiempo": 10,
            "congestion_tipica": {
                "normal": 1.0,
                "hora_pico_manana": 1.5,
                "hora_pico_tarde": 1.3
            }
        })
        self.grafo.agregar_ruta("C", "D", {
            "tipo": "metro",
            "tiempo": 10,
            "congestion_tipica": {
                "normal": 1.0,
                "hora_pico_manana": 1.5,
                "hora_pico_tarde": 1.3
            }
        })
        
    def test_sugerir_nuevas_conexiones(self):
        # Probar con un presupuesto de tiempo de 15 minutos
        sugerencias = sugerir_nuevas_conexiones(self.grafo, 15)
        
        # Verificar que hay sugerencias
        self.assertTrue(len(sugerencias) > 0)
        
        # Verificar que cada sugerencia es una tupla de 3 elementos
        for sugerencia in sugerencias:
            self.assertEqual(len(sugerencia), 3)
            origen, destino, tiempo = sugerencia
            
            # Verificar que los tiempos estimados son menores al presupuesto
            self.assertLessEqual(tiempo, 15)
            
            # Verificar que no hay conexión directa entre origen y destino
            self.assertNotIn(destino, self.grafo.rutas.get(origen, {}))
            
        # Verificar que hay máximo 5 sugerencias
        self.assertLessEqual(len(sugerencias), 5) 