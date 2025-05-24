from src.graph import Grafo

def dfs_ciclos(grafo, nodo, visitados, stack):
    visitados.add(nodo)
    stack.add(nodo)
    for vecino in grafo.rutas.get(nodo, {}):
        if vecino not in visitados:
            if dfs_ciclos(grafo, vecino, visitados, stack):
                return True
        elif vecino in stack:
            return True
    stack.remove(nodo)
    return False

def tiene_ciclos(grafo):
    visitados = set()
    for nodo in grafo.rutas:
        if nodo not in visitados:
            if dfs_ciclos(grafo, nodo, visitados, set()):
                return True
    return False

def actualizar_peso(grafo, origen, destino, nuevo_peso):
    if nuevo_peso < 0:
        return False
    if origen not in grafo.rutas or destino not in grafo.rutas[origen]:
        return False
    grafo.rutas[origen][destino].tiempo_base = nuevo_peso
    return True

def sugerir_conexiones(grafo, presupuesto):
    sugerencias = []
    for origen in grafo.rutas:
        for destino in grafo.rutas:
            if origen != destino and destino not in grafo.rutas.get(origen, {}):
                sugerencias.append((origen, destino, presupuesto))
    return sugerencias[:5]  # por ejemplo, las primeras 5 sugerencias
