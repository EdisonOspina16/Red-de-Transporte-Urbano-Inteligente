import heapq


def dijkstra(grafo, inicio):
    distancias = {v: float('inf') for v in grafo.vertices}
    distancias[inicio] = 0
    camino = {v: [] for v in grafo.vertices}
    camino[inicio] = [inicio]
    cola = [(0, inicio)]

    while cola:
        actual_dist, actual_vert = heapq.heappop(cola)
        if actual_dist > distancias[actual_vert]:
            continue
        for vecino, peso in grafo.obtener_adyacentes(actual_vert).items():
            nueva_dist = actual_dist + peso
            if nueva_dist < distancias[vecino]:
                distancias[vecino] = nueva_dist
                camino[vecino] = camino[actual_vert] + [vecino]
                heapq.heappush(cola, (nueva_dist, vecino))
    return distancias, camino