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


def es_fuertemente_conexo(grafo):
    def dfs(nodo, visitados):
        visitados.add(nodo)
        for vecino in grafo.rutas.get(nodo, {}):
            if vecino not in visitados:
                dfs(vecino, visitados)

    # Verificar conectividad desde cada nodo
    for nodo_inicio in grafo.rutas:
        visitados = set()
        dfs(nodo_inicio, visitados)
        if len(visitados) != len(grafo.rutas):
            return False

        # Verificar que existe camino de vuelta
        for nodo_destino in grafo.rutas:
            if nodo_inicio != nodo_destino:
                camino_vuelta = False
                for intermedio in grafo.rutas:
                    if nodo_destino in grafo.rutas.get(intermedio, {}) and \
                            intermedio in visitados:
                        camino_vuelta = True
                        break
                if not camino_vuelta:
                    return False
    return True

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
