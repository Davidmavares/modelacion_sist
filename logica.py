
import heapq
import math

def encontrar_ruta_simple(grafo_adj, nodo_inicio, destino, nodos_prohibidos=None):
    """
    Dijkstra estándar que ignora los nodos presentes en nodos_prohibidos.
    """
    if nodos_prohibidos is None: 
        nodos_prohibidos = set()

    if nodo_inicio not in grafo_adj or destino not in grafo_adj: 
        return math.inf, []


    cola = [(0, nodo_inicio, [nodo_inicio])]
    tiempos = {nodo: math.inf for nodo in grafo_adj}
    tiempos[nodo_inicio] = 0
    visitados = set()

    while cola:
        t_act, n_act, ruta = heapq.heappop(cola)
        
        if n_act in visitados: 
            continue
        visitados.add(n_act)

        if n_act == destino: 
            return t_act, ruta

        for vecino, peso in grafo_adj[n_act].items():
            
            if vecino in nodos_prohibidos and vecino != destino: 
                continue
            
            nuevo_t = t_act + peso
            if nuevo_t < tiempos[vecino]:
                tiempos[vecino] = nuevo_t
                heapq.heappush(cola, (nuevo_t, vecino, ruta + [vecino]))
                    
    return math.inf, []

def calcular_itinerario_sincronizado(grafo, casa_j, casa_a, destino):
    """
    Calcula rutas evitando que Javier y Andreína ocupen el mismo espacio (nodos/aristas).
    Se consideran las casas de inicio como obstáculos físicos.
    """
    
 
    bloqueo_inicial_a = {casa_j} - {destino}
    ta1, ra1 = encontrar_ruta_simple(grafo, casa_a, destino, bloqueo_inicial_a)
    
    
    bloqueo_j1 = set(ra1) | {casa_a}
    bloqueo_j1 = bloqueo_j1 - {destino} 
    tj1, rj1 = encontrar_ruta_simple(grafo, casa_j, destino, bloqueo_j1)
    

    bloqueo_inicial_j = {casa_a} - {destino}
    tj2, rj2 = encontrar_ruta_simple(grafo, casa_j, destino, bloqueo_inicial_j)
    

    bloqueo_a2 = set(rj2) | {casa_j}
    bloqueo_a2 = bloqueo_a2 - {destino}
    ta2, ra2 = encontrar_ruta_simple(grafo, casa_a, destino, bloqueo_a2)
    
   
    total1 = ta1 + tj1
    total2 = tj2 + ta2
    
    
    posible1 = (ta1 != math.inf and tj1 != math.inf)
    posible2 = (tj2 != math.inf and ta2 != math.inf)
    
    if not posible1 and not posible2:
        return None 
        

    if posible1 and (not posible2 or total1 <= total2):
        estrategia = "Prioridad Andreína (Ella elige ruta)"
        path_j, time_j = rj1, tj1
        path_a, time_a = ra1, ta1
    else:
        estrategia = "Prioridad Javier (Él elige ruta)"
        path_j, time_j = rj2, tj2
        path_a, time_a = ra2, ta2
        
    # --- SINCRONIZACIÓN ---
    diferencia = abs(time_j - time_a)
    if time_j > time_a:
        msg_orden = f"Javier sale {diferencia} min ANTES."
    elif time_a > time_j:
        msg_orden = f"Andreína sale {diferencia} min ANTES."
    else:
        msg_orden = "Salida SIMULTÁNEA."
        
    return {
        "exito": True,
        "estrategia": estrategia,
        "javier": {"ruta": path_j, "tiempo": time_j},
        "andreina": {"ruta": path_a, "tiempo": time_a},
        "mensaje_sincronia": msg_orden
    }