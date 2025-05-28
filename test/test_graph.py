import unittest
import json
import os
from src.graph import Grafo, Estacion, Ruta

class TestGrafo(unittest.TestCase):
    def setUp(self):
        self.grafo = Grafo()
        
        # Datos de prueba para estaciones
        self.datos_estacion = {
            "nombre": "Estacion Test",
            "tipo": "metro",
            "linea": "M1",
            "conexiones": ["M2", "B1"]
        }
        
        # Datos de prueba para rutas
        self.datos_ruta = {
            "tipo": "metro",
            "tiempo": 5,
            "congestion_tipica": {
                "hora_pico_manana": 1.5,
                "hora_pico_tarde": 1.5,
                "normal": 1.0
            }
        }

    def test_agregar_estacion(self):
        # Agregar estación válida
        self.grafo.agregar_estacion("TEST1", self.datos_estacion)
        self.assertIn("TEST1", self.grafo.vertices)
        self.assertEqual(self.grafo.vertices["TEST1"].nombre, "Estacion Test")
        self.assertEqual(self.grafo.vertices["TEST1"].tipo, "metro")
        self.assertEqual(self.grafo.vertices["TEST1"].linea, "M1")
        self.assertEqual(self.grafo.vertices["TEST1"].conexiones, ["M2", "B1"])
        
        # Verificar mapeo de nombre a ID
        self.assertEqual(self.grafo.nombres_a_ids["Estacion Test"], "TEST1")

    def test_agregar_ruta(self):
        # Agregar estaciones primero
        self.grafo.agregar_estacion("A", self.datos_estacion)
        self.grafo.agregar_estacion("B", self.datos_estacion)
        
        # Agregar ruta válida
        self.grafo.agregar_ruta("A", "B", self.datos_ruta)
        self.assertIn("A", self.grafo.rutas)
        self.assertIn("B", self.grafo.rutas["A"])
        self.assertEqual(self.grafo.rutas["A"]["B"].tiempo_base, 5)
        self.assertEqual(self.grafo.rutas["A"]["B"].tipo, "metro")

    def test_obtener_tiempo(self):
        # Configurar grafo con una ruta
        self.grafo.agregar_estacion("A", self.datos_estacion)
        self.grafo.agregar_estacion("B", self.datos_estacion)
        self.grafo.agregar_ruta("A", "B", self.datos_ruta)
        
        # Verificar tiempo de ruta existente
        self.assertEqual(self.grafo.obtener_tiempo("A", "B"), 5)
        
        # Verificar tiempo de ruta inexistente
        self.assertEqual(self.grafo.obtener_tiempo("A", "C"), float('inf'))

    def test_obtener_adyacentes(self):
        # Configurar grafo con múltiples rutas
        self.grafo.agregar_estacion("A", self.datos_estacion)
        self.grafo.agregar_estacion("B", self.datos_estacion)
        self.grafo.agregar_estacion("C", self.datos_estacion)
        
        self.grafo.agregar_ruta("A", "B", self.datos_ruta)
        self.grafo.agregar_ruta("A", "C", self.datos_ruta)
        
        # Verificar adyacentes
        adyacentes = self.grafo.obtener_adyacentes("A")
        self.assertEqual(len(adyacentes), 2)
        self.assertIn("B", adyacentes)
        self.assertIn("C", adyacentes)
        
        # Verificar adyacentes de nodo sin salidas
        self.assertEqual(len(self.grafo.obtener_adyacentes("B")), 0)

    def test_obtener_id_por_nombre(self):
        self.grafo.agregar_estacion("TEST1", self.datos_estacion)
        
        # Verificar ID existente
        self.assertEqual(self.grafo.obtener_id_por_nombre("Estacion Test"), "TEST1")
        
        # Verificar nombre inexistente
        self.assertIsNone(self.grafo.obtener_id_por_nombre("Estacion Inexistente"))

    def test_obtener_nombre_por_id(self):
        self.grafo.agregar_estacion("TEST1", self.datos_estacion)
        
        # Verificar ID existente
        self.assertEqual(self.grafo.obtener_nombre_por_id("TEST1"), "Estacion Test")
        
        # Verificar ID inexistente
        self.assertIsNone(self.grafo.obtener_nombre_por_id("TEST2"))

    def test_cargar_desde_json(self):
        # Crear archivo JSON de prueba
        datos_json = {
            "vertices": {
                "TEST1": {
                    "nombre": "Estacion Test 1",
                    "tipo": "metro",
                    "linea": "M1",
                    "conexiones": []
                },
                "TEST2": {
                    "nombre": "Estacion Test 2",
                    "tipo": "metro",
                    "linea": "M1",
                    "conexiones": []
                }
            },
            "rutas": [
                {
                    "origen": "TEST1",
                    "destino": "TEST2",
                    "tipo": "metro",
                    "tiempo": 5,
                    "congestion_tipica": {
                        "hora_pico_manana": 1.5,
                        "hora_pico_tarde": 1.5,
                        "normal": 1.0
                    }
                }
            ]
        }
        
        # Guardar archivo temporal
        with open("test_network.json", "w", encoding="utf-8") as f:
            json.dump(datos_json, f)
        
        # Cargar desde JSON
        self.grafo.cargar_desde_json("test_network.json")
        
        # Verificar carga
        self.assertIn("TEST1", self.grafo.vertices)
        self.assertIn("TEST2", self.grafo.vertices)
        self.assertIn("TEST1", self.grafo.rutas)
        self.assertIn("TEST2", self.grafo.rutas["TEST1"])
        
        # Limpiar archivo temporal
        os.remove("test_network.json")

    def test_copia_sin_estacion(self):
        # Configurar grafo con múltiples estaciones y rutas
        self.grafo.agregar_estacion("A", self.datos_estacion)
        self.grafo.agregar_estacion("B", self.datos_estacion)
        self.grafo.agregar_estacion("C", self.datos_estacion)
        
        self.grafo.agregar_ruta("A", "B", self.datos_ruta)
        self.grafo.agregar_ruta("B", "C", self.datos_ruta)
        
        # Crear copia sin estación B
        copia = self.grafo.copia_sin_estacion("B")
        
        # Verificar que B no está en la copia
        self.assertNotIn("B", copia.vertices)
        self.assertNotIn("B", copia.rutas)
        
        # Verificar que A y C están en la copia
        self.assertIn("A", copia.vertices)
        self.assertIn("C", copia.vertices)
        
        # Verificar que las rutas que involucran B no están en la copia
        self.assertNotIn("B", copia.rutas.get("A", {}))
        self.assertNotIn("B", copia.rutas.get("C", {}))

if __name__ == '__main__':
    unittest.main() 