from src.graph import Grafo
from src.utils import tiene_ciclos, es_fuertemente_conexo, actualizar_peso, sugerir_conexiones

def test_tiene_ciclos():
    # Test 1: Grafo con ciclo simple
    grafo_con_ciclo = Grafo()
    datos_ruta = {
        "tipo": "metro",
        "tiempo": 1,
        "congestion_tipica": {
            "hora_pico_manana": 1.5,
            "hora_pico_tarde": 1.3,
            "normal": 1.0
        }
    }
    grafo_con_ciclo.agregar_ruta("A", "B", datos_ruta)
    grafo_con_ciclo.agregar_ruta("B", "C", datos_ruta)
    grafo_con_ciclo.agregar_ruta("C", "A", datos_ruta)
    assert tiene_ciclos(grafo_con_ciclo) == True

    # Test 2: Grafo sin ciclos
    grafo_sin_ciclo = Grafo()
    grafo_sin_ciclo.agregar_ruta("A", "B", datos_ruta)
    grafo_sin_ciclo.agregar_ruta("B", "C", datos_ruta)
    assert tiene_ciclos(grafo_sin_ciclo) == False

    # Test 3: Grafo vacío
    grafo_vacio = Grafo()
    assert tiene_ciclos(grafo_vacio) == False

    # Test 4: Grafo con ciclo más complejo
    grafo_ciclo_complejo = Grafo()
    grafo_ciclo_complejo.agregar_ruta("A", "B", datos_ruta)
    grafo_ciclo_complejo.agregar_ruta("B", "C", datos_ruta)
    grafo_ciclo_complejo.agregar_ruta("C", "D", datos_ruta)
    grafo_ciclo_complejo.agregar_ruta("D", "B", datos_ruta)
    assert tiene_ciclos(grafo_ciclo_complejo) == True

    # Test 5: Grafo con múltiples componentes, uno con ciclo
    grafo_multi_componentes = Grafo()
    grafo_multi_componentes.agregar_ruta("A", "B", datos_ruta)
    grafo_multi_componentes.agregar_ruta("C", "D", datos_ruta)
    grafo_multi_componentes.agregar_ruta("D", "E", datos_ruta)
    grafo_multi_componentes.agregar_ruta("E", "C", datos_ruta)
    assert tiene_ciclos(grafo_multi_componentes) == True

def test_es_fuertemente_conexo():
    # Test 1: Grafo fuertemente conexo simple
    grafo_conexo = Grafo()
    datos_ruta = {
        "tipo": "metro",
        "tiempo": 1,
        "congestion_tipica": {
            "hora_pico_manana": 1.5,
            "hora_pico_tarde": 1.3,
            "normal": 1.0
        }
    }
    grafo_conexo.agregar_ruta("A", "B", datos_ruta)
    grafo_conexo.agregar_ruta("B", "C", datos_ruta)
    grafo_conexo.agregar_ruta("C", "A", datos_ruta)
    grafo_conexo.agregar_ruta("B", "A", datos_ruta)
    grafo_conexo.agregar_ruta("C", "B", datos_ruta)
    grafo_conexo.agregar_ruta("A", "C", datos_ruta)
    assert es_fuertemente_conexo(grafo_conexo) == True

    # Test 2: Grafo no conexo
    grafo_no_conexo = Grafo()
    grafo_no_conexo.agregar_ruta("A", "B", datos_ruta)
    grafo_no_conexo.agregar_ruta("B", "C", datos_ruta)
    assert es_fuertemente_conexo(grafo_no_conexo) == False

    # Test 3: Grafo vacío (considerado fuertemente conexo por definición)
    grafo_vacio = Grafo()
    assert es_fuertemente_conexo(grafo_vacio) == True

    # Test 4: Grafo con un solo nodo (fuertemente conexo por definición)
    grafo_un_nodo = Grafo()
    grafo_un_nodo.agregar_ruta("A", "A", datos_ruta)
    assert es_fuertemente_conexo(grafo_un_nodo) == True

    # Test 5: Grafo con conexiones en un solo sentido
    grafo_unidireccional = Grafo()
    grafo_unidireccional.agregar_ruta("A", "B", datos_ruta)
    grafo_unidireccional.agregar_ruta("B", "C", datos_ruta)
    grafo_unidireccional.agregar_ruta("C", "D", datos_ruta)
    assert es_fuertemente_conexo(grafo_unidireccional) == False

def test_actualizar_peso():
    grafo = Grafo()
    datos_ruta = {
        "tipo": "metro",
        "tiempo": 5,
        "congestion_tipica": {
            "hora_pico_manana": 1.5,
            "hora_pico_tarde": 1.3,
            "normal": 1.0
        }
    }
    grafo.agregar_ruta("A", "B", datos_ruta)

    # Test 1: Actualización exitosa
    assert actualizar_peso(grafo, "A", "B", 10) == True
    assert grafo.rutas["A"]["B"].tiempo_base == 10

    # Test 2: Peso negativo
    assert actualizar_peso(grafo, "A", "B", -5) == False
    assert grafo.rutas["A"]["B"].tiempo_base == 10  # El peso no debería cambiar

    # Test 3: Ruta inexistente
    assert actualizar_peso(grafo, "A", "C", 15) == False

    # Test 4: Nodo origen inexistente
    assert actualizar_peso(grafo, "X", "B", 20) == False

    # Test 5: Actualizar a peso cero
    assert actualizar_peso(grafo, "A", "B", 0) == True
    assert grafo.rutas["A"]["B"].tiempo_base == 0

def test_sugerir_conexiones():
    grafo = Grafo()
    # Crear una red más compleja para probar sugerencias
    datos_ruta = {
        "tipo": "metro",
        "tiempo": 2,
        "congestion_tipica": {
            "hora_pico_manana": 1.5,
            "hora_pico_tarde": 1.3,
            "normal": 1.0
        }
    }
    grafo.agregar_ruta("A", "B", datos_ruta)
    grafo.agregar_ruta("B", "C", datos_ruta)
    grafo.agregar_ruta("C", "D", datos_ruta)
    grafo.agregar_ruta("D", "E", datos_ruta)

    # Test 1: Verificar número de sugerencias
    sugerencias = sugerir_conexiones(grafo, presupuesto=6)
    assert len(sugerencias) <= 5  # No debe exceder 5 sugerencias

    # Test 2: Verificar que no se sugieren conexiones existentes
    for origen, destino, peso in sugerencias:
        assert destino not in grafo.rutas.get(origen, {})

    # Test 3: Verificar que los pesos sugeridos no exceden el presupuesto
    for origen, destino, peso in sugerencias:
        assert peso <= 6

    # Test 4: Grafo vacío
    grafo_vacio = Grafo()
    sugerencias_vacio = sugerir_conexiones(grafo_vacio, presupuesto=5)
    assert len(sugerencias_vacio) == 0

    # Test 5: Grafo completamente conectado
    grafo_completo = Grafo()
    grafo_completo.agregar_ruta("A", "B", datos_ruta)
    grafo_completo.agregar_ruta("B", "A", datos_ruta)
    sugerencias_completo = sugerir_conexiones(grafo_completo, presupuesto=5)
    assert len(sugerencias_completo) == 0

if __name__ == "__main__":
    test_tiene_ciclos()
    test_es_fuertemente_conexo()
    test_actualizar_peso()
    test_sugerir_conexiones()
    print("Todas las pruebas pasaron correctamente.")
