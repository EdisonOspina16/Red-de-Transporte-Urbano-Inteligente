import unittest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import patch, MagicMock
from main import app

class TestMain(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_index_route(self):
        """Test the index route returns 200 and contains expected elements"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        # Check for station names in the select options
        self.assertIn("Biblioteca", response.text)
        self.assertIn("Universidad", response.text)
        # Check for status panel elements
        self.assertIn("Estado del Sistema", response.text)
        self.assertIn("Tráfico fluido", response.text)

    @patch('main.red')
    def test_ruta_route_valid_stations(self, mock_red):
        """Test the ruta route with valid stations"""
        # Mock the red object and its methods
        mock_red.obtener_id_por_nombre.side_effect = lambda x: "A" if x == "Estación A" else "B"
        mock_red.obtener_nombre_por_id.side_effect = lambda x: "Estación A" if x == "A" else "Estación B"
        
        # Mock dijkstra results
        mock_distancias = {"B": 10}
        mock_caminos = {"B": ["A", "B"]}
        
        with patch('main.dijkstra', return_value=(mock_distancias, mock_caminos)):
            response = self.client.post(
                "/ruta",
                data={"origen": "Estación A", "destino": "Estación B"}
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn("Estación A", response.text)
            self.assertIn("Estación B", response.text)

    @patch('main.red')
    def test_ruta_route_invalid_origin(self, mock_red):
        """Test the ruta route with invalid origin station"""
        mock_red.obtener_id_por_nombre.return_value = None
        
        response = self.client.post(
            "/ruta",
            data={"origen": "Estación Inexistente", "destino": "Estación B"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Estación de origen", response.text)

    @patch('main.red')
    def test_ruta_route_invalid_destination(self, mock_red):
        """Test the ruta route with invalid destination station"""
        mock_red.obtener_id_por_nombre.side_effect = lambda x: "A" if x == "Estación A" else None
        
        response = self.client.post(
            "/ruta",
            data={"origen": "Estación A", "destino": "Estación Inexistente"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Estación de destino", response.text)

    @patch('main.red')
    def test_ruta_route_no_path(self, mock_red):
        """Test the ruta route when no path exists between stations"""
        mock_red.obtener_id_por_nombre.side_effect = lambda x: "A" if x == "Estación A" else "B"
        mock_red.obtener_nombre_por_id.side_effect = lambda x: "Estación A" if x == "A" else "Estación B"
        
        # Mock dijkstra results with no path
        mock_distancias = {"B": float('inf')}
        mock_caminos = {}
        
        with patch('main.dijkstra', return_value=(mock_distancias, mock_caminos)):
            response = self.client.post(
                "/ruta",
                data={"origen": "Estación A", "destino": "Estación B"}
            )
            self.assertEqual(response.status_code, 500)
            self.assertIn("No existe una ruta disponible", response.text)

    @patch('main.red')
    def test_ruta_route_with_alternative_path(self, mock_red):
        """Test the ruta route with alternative path calculation"""
        # Mock the red object and its methods
        mock_red.obtener_id_por_nombre.side_effect = lambda x: "A" if x == "Estación A" else "B"
        mock_red.obtener_nombre_por_id.side_effect = lambda x: "Estación A" if x == "A" else "Estación B"
        mock_red.copia_sin_estacion.return_value = mock_red
        
        # Mock dijkstra results for main path
        mock_distancias = {"B": 10}
        mock_caminos = {"B": ["A", "B"]}
        
        # Mock dijkstra results for alternative path
        mock_distancias_alt = {"B": 15}
        mock_caminos_alt = {"B": ["A", "C", "B"]}
        
        with patch('main.dijkstra', side_effect=[(mock_distancias, mock_caminos), (mock_distancias_alt, mock_caminos_alt)]):
            response = self.client.post(
                "/ruta",
                data={"origen": "Estación A", "destino": "Estación B"}
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn("Estación A", response.text)
            self.assertIn("Estación B", response.text)

if __name__ == '__main__':
    unittest.main()
