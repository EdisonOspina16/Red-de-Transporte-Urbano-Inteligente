import heapq


def dijkstra_k_rutas(grafo, inicio, K=3):
    """
    Dijkstra para encontrar las K rutas más cortas
    desde un nodo inicial a todos los demás nodos en el grafo.
    
    Args:
        grafo (Grafo): Grafo que representa la red de transporte
        inicio (str): ID del nodo inicial
        K (int): Número de rutas más cortas a encontrar para cada nodo
        
    Returns:
        tuple: (distancias, caminos) donde:
            - distancias (dict): Diccionario con listas de las K distancias mínimas desde el inicio a cada nodo
            - caminos (dict): Diccionario con listas de las K rutas mínimas desde el inicio a cada nodo
    """
    # Inicializamos distancias y caminos como listas de K elementos
    distancias = {v: [] for v in grafo.vertices}
    caminos = {v: [] for v in grafo.vertices}
    
    # La distancia/camino inicial tiene 1 entrada (ruta trivial: [inicio] con distancia 0)
    distancias[inicio] = [0]
    caminos[inicio] = [[inicio]]
    
    # La cola prioritaria almacena tuplas (distancia, nodo, ruta)
    cola = [(0, inicio, [inicio])]
    
    while cola:
        actual_dist, actual_vert, actual_camino = heapq.heappop(cola)
        
        # Si ya tenemos K rutas para este nodo y la actual es peor que la K-ésima, la ignoramos
        if len(distancias[actual_vert]) >= K and actual_dist > distancias[actual_vert][-1]:
            continue
            
        for vecino, peso in grafo.obtener_adyacentes(actual_vert).items():
            nueva_dist = actual_dist + peso
            nuevo_camino = actual_camino + [vecino]
            
            # Si el vecino no tiene K rutas aún, o la nueva es mejor que la peor de sus K rutas
            if len(distancias[vecino]) < K or nueva_dist < distancias[vecino][-1]:
                # Insertamos la nueva ruta de manera ordenada
                insertar_ordenado(distancias[vecino], caminos[vecino], nueva_dist, nuevo_camino, K)
                heapq.heappush(cola, (nueva_dist, vecino, nuevo_camino))
    
    return distancias, caminos

def insertar_ordenado(lista_distancias, lista_caminos, nueva_dist, nuevo_camino, K):
    """
    Inserta una nueva distancia y camino en las listas manteniendo el orden ascendente
    y limitando el tamaño a K elementos.
    
    Args:
        lista_distancias (list): Lista de distancias ordenadas
        lista_caminos (list): Lista de caminos correspondientes a las distancias
        nueva_dist (float): Nueva distancia a insertar
        nuevo_camino (list): Nuevo camino a insertar
        K (int): Número máximo de elementos a mantener
    """
    # Encuentra la posición donde insertar la nueva distancia (manteniendo orden ascendente)
    i = 0
    while i < len(lista_distancias) and lista_distancias[i] < nueva_dist:
        i += 1
    
    # Insertamos en la posición correcta
    lista_distancias.insert(i, nueva_dist)
    lista_caminos.insert(i, nuevo_camino)
    
    # Truncamos a K elementos si es necesario
    if len(lista_distancias) > K:
        lista_distancias.pop()
        lista_caminos.pop()