import unittest
from datetime import datetime
from src.graph import Grafo, Estacion, Ruta
import json
import os
import tempfile
from unittest.mock import patch

class TestGrafo(unittest.TestCase):
    def setUp(self):
        self.grafo = Grafo()
        self.datos_estacion = {
            "nombre": "Estación Central",
            "tipo": "metro",
            "linea": "L1",
            "conexiones": ["L2", "L3"]
        }
        self.datos_ruta = {
            "tipo": "metro",
            "tiempo": 10,
            "congestion_tipica": {
                "hora_pico_manana": 1.5,
                "hora_pico_tarde": 1.3,
                "normal": 1.0
            }
        }
        # Create a temporary test data file
        self.test_data = {
            "vertices": {
                "E1": {
                    "nombre": "Estación Central",
                    "tipo": "metro",
                    "linea": "L1",
                    "conexiones": ["L2", "L3"]
                },
                "E2": {
                    "nombre": "Estación Sur",
                    "tipo": "metro",
                    "linea": "L2",
                    "conexiones": ["L1"]
                }
            },
            "rutas": [
                {
                    "origen": "E1",
                    "destino": "E2",
                    "tipo": "metro",
                    "tiempo": 10,
                    "congestion_tipica": {
                        "hora_pico_manana": 1.5,
                        "hora_pico_tarde": 1.3,
                        "normal": 1.0
                    }
                }
            ]
        }
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "test_red.json")
        with open(self.temp_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_data, f)

    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_agregar_estacion(self):
        self.grafo.agregar_estacion("E1", self.datos_estacion)
        self.assertIn("E1", self.grafo.vertices)
        self.assertEqual(self.grafo.vertices["E1"].nombre, "Estación Central")
        self.assertEqual(self.grafo.vertices["E1"].tipo, "metro")
        self.assertEqual(self.grafo.vertices["E1"].linea, "L1")
        self.assertEqual(self.grafo.vertices["E1"].conexiones, ["L2", "L3"])
        self.assertIn("Estación Central", self.grafo.nombres_a_ids)

    def test_agregar_ruta(self):
        self.grafo.agregar_estacion("E1", self.datos_estacion)
        self.grafo.agregar_estacion("E2", {
            "nombre": "Estación Sur",
            "tipo": "metro",
            "linea": "L2",
            "conexiones": ["L1"]
        })
        self.grafo.agregar_ruta("E1", "E2", self.datos_ruta)
        
        self.assertIn("E2", self.grafo.rutas["E1"])
        self.assertEqual(self.grafo.rutas["E1"]["E2"].tiempo_base, 10)
        self.assertEqual(self.grafo.rutas["E1"]["E2"].tipo, "metro")

    @patch('src.graph.datetime')
    def test_obtener_tiempo(self, mock_datetime):
        # Mock datetime to return a non-peak hour (e.g., 14:00)
        mock_datetime.now.return_value.hour = 14
        
        self.grafo.agregar_estacion("E1", self.datos_estacion)
        self.grafo.agregar_estacion("E2", {
            "nombre": "Estación Sur",
            "tipo": "metro",
            "linea": "L2",
            "conexiones": ["L1"]
        })
        self.grafo.agregar_ruta("E1", "E2", self.datos_ruta)
        
        # Test tiempo normal (factor 1.0)
        tiempo = self.grafo.obtener_tiempo("E1", "E2")
        self.assertEqual(tiempo, 10)  # tiempo base * factor normal (1.0)
        
        # Test hora pico mañana (factor 1.5)
        mock_datetime.now.return_value.hour = 8
        tiempo_pico = self.grafo.obtener_tiempo("E1", "E2")
        self.assertEqual(tiempo_pico, 15)  # tiempo base * factor pico mañana (1.5)
        
        # Test ruta inexistente
        tiempo_inf = self.grafo.obtener_tiempo("E2", "E1")
        self.assertEqual(tiempo_inf, float('inf'))

    @patch('src.graph.datetime')
    def test_obtener_adyacentes(self, mock_datetime):
        # Mock datetime to return a non-peak hour (e.g., 14:00)
        mock_datetime.now.return_value.hour = 14
        
        self.grafo.agregar_estacion("E1", self.datos_estacion)
        self.grafo.agregar_estacion("E2", {
            "nombre": "Estación Sur",
            "tipo": "metro",
            "linea": "L2",
            "conexiones": ["L1"]
        })
        self.grafo.agregar_ruta("E1", "E2", self.datos_ruta)
        
        adyacentes = self.grafo.obtener_adyacentes("E1")
        self.assertIn("E2", adyacentes)
        self.assertEqual(adyacentes["E2"], 10)  # tiempo base * factor normal (1.0)
        
        # Test estación sin adyacentes
        adyacentes_vacios = self.grafo.obtener_adyacentes("E2")
        self.assertEqual(adyacentes_vacios, {})

    def test_obtener_id_por_nombre(self):
        self.grafo.agregar_estacion("E1", self.datos_estacion)
        id_encontrado = self.grafo.obtener_id_por_nombre("Estación Central")
        self.assertEqual(id_encontrado, "E1")
        
        # Test nombre inexistente
        id_no_encontrado = self.grafo.obtener_id_por_nombre("Estación Inexistente")
        self.assertIsNone(id_no_encontrado)

    def test_obtener_nombre_por_id(self):
        self.grafo.agregar_estacion("E1", self.datos_estacion)
        nombre = self.grafo.obtener_nombre_por_id("E1")
        self.assertEqual(nombre, "Estación Central")
        
        # Test ID inexistente
        nombre_no_encontrado = self.grafo.obtener_nombre_por_id("E999")
        self.assertIsNone(nombre_no_encontrado)

    def test_obtener_info_estacion(self):
        self.grafo.agregar_estacion("E1", self.datos_estacion)
        info = self.grafo.obtener_info_estacion("E1")
        self.assertEqual(info["nombre"], "Estación Central")
        self.assertEqual(info["tipo"], "metro")
        self.assertEqual(info["linea"], "L1")
        self.assertEqual(info["conexiones"], ["L2", "L3"])
        
        # Test ID inexistente
        info_no_encontrada = self.grafo.obtener_info_estacion("E999")
        self.assertIsNone(info_no_encontrada)

    def test_cargar_desde_json(self):
        grafo = Grafo()
        grafo.cargar_desde_json(self.temp_file)
        
        # Verify stations were loaded
        self.assertEqual(len(grafo.vertices), 2)
        self.assertIn("E1", grafo.vertices)
        self.assertIn("E2", grafo.vertices)
        
        # Verify station properties
        self.assertEqual(grafo.vertices["E1"].nombre, "Estación Central")
        self.assertEqual(grafo.vertices["E2"].nombre, "Estación Sur")
        
        # Verify routes were loaded
        self.assertIn("E1", grafo.rutas)
        self.assertIn("E2", grafo.rutas["E1"])
        self.assertEqual(grafo.rutas["E1"]["E2"].tiempo_base, 10)
        
        # Test loading non-existent file
        with self.assertRaises(FileNotFoundError):
            grafo.cargar_desde_json("non_existent_file.json")

class TestRuta(unittest.TestCase):
    def setUp(self):
        self.ruta = Ruta(
            origen="E1",
            destino="E2",
            tipo="metro",
            tiempo=10,
            congestion_tipica={
                "hora_pico_manana": 1.5,
                "hora_pico_tarde": 1.3,
                "normal": 1.0
            }
        )

    def test_calcular_tiempo_actual(self):
        # Test hora pico mañana (7-9)
        tiempo_manana = self.ruta.calcular_tiempo_actual(8)
        self.assertEqual(tiempo_manana, 15)  # 10 * 1.5
        
        # Test hora pico tarde (17-19)
        tiempo_tarde = self.ruta.calcular_tiempo_actual(18)
        self.assertEqual(tiempo_tarde, 13)  # 10 * 1.3
        
        # Test hora normal
        tiempo_normal = self.ruta.calcular_tiempo_actual(14)
        self.assertEqual(tiempo_normal, 10)  # 10 * 1.0

class TestEstacion(unittest.TestCase):
    def test_creacion_estacion(self):
        estacion = Estacion(
            id="E1",
            nombre="Estación Central",
            tipo="metro",
            linea="L1",
            conexiones=["L2", "L3"]
        )
        
        self.assertEqual(estacion.id, "E1")
        self.assertEqual(estacion.nombre, "Estación Central")
        self.assertEqual(estacion.tipo, "metro")
        self.assertEqual(estacion.linea, "L1")
        self.assertEqual(estacion.conexiones, ["L2", "L3"])

if __name__ == '__main__':
    unittest.main()
