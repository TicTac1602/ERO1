import osmnx as ox
import networkx as nx
import time


def scan(place_name, verbose=False):
    if place_name == "outremont":
        place_name = "Outremont, Montreal, Canada"
        pass
    elif place_name == "verdun":
        place_name = "Verdun, Montreal, Canada"
        pass
    elif place_name == "montRoyal":
        place_name = "Le Plateau-Mont-Royal, Montreal, Canada"
        pass
    elif place_name == "riviere":
        place_name = "Rivière-des-Prairies-Pointe-aux-Trembles, Montreal, Canada"
        pass
    elif place_name == "saintLeonard":
        place_name = "Rivière-des-Prairies-Pointe-aux-Trembles, Montreal, Canada"
        pass
    else:
        print(place_name, "n'est pas un emplacement gerer dans ce projet")
        print("Les quartiers gerer sont : [outremont,verdun,montRoyal,riviere,saintLeonard]")
        return
    # Télécharger le graphe du réseau de rues du lieu spécifié
    graph = ox.graph_from_place(place_name, network_type="drive")
    G = ox.plot_graph(graph, show=verbose)
    GU = graph.to_undirected()
    if not nx.is_weakly_connected(graph):
        print("Le graphe n'est pas connexe.")

    chemin_parcouru = None
    distance_totale = None

    # Parcours des arêtes et calcul de la distance totale
    found, chemin_parcouru, distance_totale = make_it_eulerian(GU)

    if not found:
        print("Calcul du chemin en glouton")
        chemin_parcouru, distance_totale = parcourir_aretes(GU)

    if verbose:
        print("Chemin calculer")
        for u, v,data in graph.edges(data=True):
            print(data['length'])

        print("Taille du réseau routier : ", real_distance, "m")
        print("Distance totale parcourue :", distance_totale, "m")
        print("Creation du plan avec l'itineraire (Cette operation peut etre longue) ETA :" , 0.08 * len(chemin_parcouru), " secondes")

        # Tracer l'itinéraire sur OSMnx
        start_time = time.time() 
        ox.plot_graph_routes(GU, chemin_parcouru, route_linewidth=6, node_size=0, bgcolor='w', show=True)
        end_time = time.time()
        execution_time = end_time - start_time  # Calcul du temps d'exécution
        print("Temps d'exécution : ", execution_time, " secondes avec ", len(chemin_parcouru), " arretes")
    print("Fin du scan")
    return chemin_parcouru, distance_totale

def make_it_eulerian(graph):
    odd_nodes = [node for node in graph.nodes if graph.degree(node) % 2 != 0]
    
    # Transformer le graph pour ajouter les arcs pour que ce soit un graphe avec que des degres pair
    
    odd_nodes = [node for node in graph.nodes if graph.degree(node) % 2 != 0]
    if not odd_nodes:
        eulerian_cycle = find_eulerian_circuit(len(graph.nodes()),graph.edges(data=True))
        distance = sum(graph[u][v]['length'] for u, v in eulerian_cycle)
        return True, eulerian_cycle, distance
    else:
        print("Pas de cycle eulerien apres ajout d'arc")
        return False, None, 0

def odd_vertices(n, edges):
    deg = [0] * n
    for (a,b) in edges:
        deg[a] += 1
        deg[b] += 1
    return [a for a in range(n) if deg[a] % 2]

def is_edge_connected(n, edges):
    if n == 0 or len(edges) == 0:
        return True
    # Convert to adjacency list
    succ = [[] for a in range(n)]
    for (a,b) in edges:
        succ[a].append(b)
        succ[b].append(a)
    # BFS over the graph, starting from one extremity of the first edge
    touched = [False] * n
    init = edges[0][0]
    touched[init] = True
    todo = [init]
    while todo:
        s = todo.pop()
        for d in succ[s]:
            if touched[d]:
                continue
            touched[d] = True
            todo.append(d)
    for a in range(n):
        if succ[a] and not touched[a]:
            return False
    return True

def is_eulerian(n, edges):
    return is_edge_connected(n, edges) and not odd_vertices(n, edges)

def find_eulerian_circuit(n, edges):
    assert is_eulerian(n, edges)
    if len(edges) == 0:
        return []
    cycle = [edges[0][0]] # start somewhere
    while True:
        rest = []
        for (a, b) in edges:
            if cycle[-1] == a:
                cycle.append(b)
            elif cycle[-1] == b:
                cycle.append(a)
            else:
                rest.append((a,b))
        if not rest:
            assert cycle[0] == cycle[-1]
            return cycle[0:-1]
        edges = rest
        if cycle[0] == cycle[-1]:
            # Rotate the cycle so that the last state
            # has some outgoing edge in EDGES.
            for (a, b) in edges:
                if a in cycle:
                    idx = cycle.index(a)
                    cycle = cycle[idx:-1] + cycle[0:idx+1]
                    break

# Parcours de toutes les arêtes du graphe
def parcourir_aretes(graph):
    chemin = []
    distance_totale = 0  # Variable pour stocker la distance totale parcourue
    for u, v, k, data in graph.edges(keys=True, data=True):
        chemin.append([u, v])
        distance = data["length"]
        distance_totale += distance  # Ajouter la distance
        chemin.append([v, u])

    return chemin, distance_totale

