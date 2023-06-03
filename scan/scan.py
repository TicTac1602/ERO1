from datetime import datetime
import heapq
import math
import networkx as nx
import osmnx as ox
import time

# Dictionnaire des correspondances entre les noms de lieux et leurs emplacements
lieux = {
    "montreal" : "Montreal, Canada",
    "outremont": "Outremont, Montreal, Canada",
    "verdun": "Verdun, Montreal, Canada",
    "montRoyal": "Le Plateau-Mont-Royal, Montreal, Canada",
    "riviere": "Rivière-des-Prairies-Pointe-aux-Trembles, Montreal, Canada",
    "saintLeonard": "Saint-Léonard, Montreal, Canada"
}

drone_speed = 70
drone_cost_per_km = 0.01
drone_cost_daily = 100

def scan(place_name, verbose=False):
    """
    Effectue un scan d'une région spécifiée et affiche les informations relatives au parcours.

    @param place_name: Nom de la région à scanner.
    @param verbose: Indicateur pour l'affichage détaillé, par défaut False.
    @return: Tuple contenant le chemin parcouru (liste d'arêtes) et la distance totale parcourue (float).
    """

    #Verification des arguments
    if place_name in lieux:
        place_name = lieux[place_name]
    else:
        print(place_name, " n'est pas un emplacement géré dans ce projet")
        print("Les quartiers gérés sont : [montreal,outremont,verdun,montRoyal,riviere,saintLeonard]")
        return
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Debut du scan de la région :",place_name)
    
    # Télécharger le graphe du réseau de rues du lieu spécifié
    graphique = ox.graph_from_place(place_name, network_type="drive")
    ox.plot_graph(graphique, show=True)
    GU = graphique.to_undirected()
    if not nx.is_connected(GU):
        print("Le graphe n'est pas connexe.")
    
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Graphique de la région",place_name, "chargé !")
    
    #Situation initale
    chemin_parcouru = None
    distance_totale = None
    reel_distance = 0
    for u, v, data in graphique.edges(data=True):
        reel_distance += data["length"]
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Surface réelle du quartier :",round(reel_distance/1000,2), "km")
    
    # Parcours des arêtes et calcul de la distance totale
    start = time.time()
    found, chemin_parcouru, distance_totale = make_it_eulerian(GU,verbose)
    end = time.time()

    # Affichage des informations
    time_travel = (distance_totale/1000)/drone_speed
    daily_cost = math.ceil(time_travel/24)

    print(datetime.now().strftime("[%d/%m %H:%M:%S]"),"Chemin trouvé en",round(end - start,4), "s")
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Distance totale parcourue :",round(distance_totale/1000,2), "km")
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"),"Temps estimé du parcours :",round(time_travel,2) ,"h")
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Cout estimé du scan : ",(daily_cost*100 + math.ceil(distance_totale/1000)*0.01) ,"€")

    if verbose:
        print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Création du plan avec l'itinéraire (Cette opération peut être longue) ETA :",0.08 * len(chemin_parcouru),"secondes")
        # Tracer l'itinéraire sur OSMnx
        ox.plot_graph_routes(GU, chemin_parcouru, route_linewidth=6, node_size=0, bgcolor="w", show=True)

    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Fin du scan")

    return chemin_parcouru, distance_totale

def bfs_min(graph, node, visited):
    """
    Effectue un parcours en largeur (BFS) à partir d'un nœud donné dans le graphe.

    @param graph: Graphe à parcourir.
    @param node: Nœud de départ du parcours.
    @param visited: Ensemble des nœuds visités.
    @return: Tuple contenant le nœud de degré impair le plus proche, la distance pour y arriver et le chemin parcouru.
    """

    # Initialisation des paramètres
    stack = [(node, 0, [node])]
    min_dist = float('inf')
    better = (None, float('inf'), None)
    while stack:
        current_node, distance, path = stack.pop()
        visited.add(current_node)
        if len(visited) > 1 and graph.degree(current_node) % 2 != 0:
            # Sélection du nœud ayant un degré impair le plus proche possible
            if distance < min_dist:
                min_dist = distance
                better = (current_node, distance, path)
        for neighbor in graph.neighbors(current_node):
            if neighbor not in visited:
                edge_length = graph.get_edge_data(current_node, neighbor)[0]["length"]
                stack.append((neighbor, distance + edge_length, path + [neighbor]))
    return better

def dijkstra(graph, node,visited):
    """
    Effectue l'algorithme de Dijkstra à partir d'un nœud donné dans le graphe.

    @param graph: Graphe à parcourir.
    @param node: Nœud de départ du parcours.
    @param visited: Ensemble des nœuds visités.
    @return: Tuple contenant le nœud de degré impair ayant la plus petite distance, la distance pour y arriver et le chemin parcouru.
    """

    heap = []
    heapq.heappush(heap, (0, node, [node]))
    min_dist = float('inf')
    better = (None, float('inf'), None)
    while heap:
        distance, current_node, path = heapq.heappop(heap)
        if(current_node in visited):
            continue
        visited.add(current_node)
        if len(visited) > 1 and graph.degree(current_node) % 2 != 0:
            # Sélection du nœud de degré impair ayant la plus petite distance
            if distance < min_dist:
                min_dist = distance
                better = (current_node, distance, path)
        for neighbor in graph.neighbors(current_node):
            if neighbor not in visited:
                edge_length = graph.get_edge_data(current_node, neighbor)[0]["length"]
                heapq.heappush(heap, (distance + edge_length, neighbor, path + [neighbor]))
    return better    

def make_it_eulerian(graph,verbose):
    """
    Transforme le graphe en un graphe eulérien en ajoutant des arêtes supplémentaires.

    @param graph: Graphe à transformer en graphe eulérien.
    @param verbose: Indicateur pour l'affichage détaillé.
    @return: Tuple contenant un indicateur si un chemin eulérien a été trouvé, le chemin parcouru (liste d'arêtes) et la distance totale parcourue (float).
    """

    odd_nodes = [node for node in graph.nodes if graph.degree(node) % 2 != 0]
    nb_todo = len(odd_nodes)
    while odd_nodes:
        node = odd_nodes[0]
        odd_degree_neighbors = [neighbor for neighbor in graph.neighbors(node) if graph.degree(neighbor) % 2 != 0]
        if odd_degree_neighbors and odd_degree_neighbors[0] != node:
            length = graph.get_edge_data(odd_degree_neighbors[0], node)[0]["length"]
            graph.add_edge(node, odd_degree_neighbors[0], directed=False, length=length)
        else:
            visited = set()
            # - opti mais fonctionne : target_node, distance, path = bfs_min(graph, node, visited)
            target_node,distance,path = dijkstra(graph, node,visited)
            # Création d'arcs pour atteindre ce nœud
            for i in range(len(path) - 1):
                source = path[i]
                destination = path[i + 1]
                edge_length = graph.get_edge_data(source, destination)[0]["length"]
                graph.add_edge(source, destination, directed=False, length=edge_length)
        # Recalcul des nœuds de degré impair pour voir si on a fini
        odd_nodes = [node for node in graph.nodes if graph.degree(node) % 2 != 0]
        if (len(odd_nodes)%100 == 0):
            print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Graph Eulerien :",round(((nb_todo -len(odd_nodes))/nb_todo)*100,2),"%",end='\r')
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Le graphe a été rendu Eulerien")
    eulerian_cycle, distance = parcourir_aretes_euler(graph,verbose)
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Un itinéraire a été trouvé")
    return True, eulerian_cycle, distance

def parcourir_aretes_euler(graph,verbose):
    """
    Parcourt les arêtes du graphe eulérien pour former un cycle eulérien.

    @param graph: Graphe eulérien à parcourir.
    @param verbose: Indicateur pour l'affichage détaillé.
    @return: Tuple contenant la liste des arêtes parcourues dans le cycle eulérien et la distance totale parcourue (float).
    """

    if not nx.is_eulerian(graph):
        return None,None
    cycle = find_eulerian_cycle(graph)
    list = [[cycle[i], cycle[i+1]] for i in range(len(cycle)-1)]
    distance_totale = sum(graph.get_edge_data(u, v)[0]["length"] for u, v in list)
    return list, distance_totale

def find_eulerian_cycle(graph):
    """
    Trouve un cycle eulérien dans le graphe.

    @param graph: Graphe dans lequel chercher un cycle eulérien.
    @return: Liste des nœuds parcourus dans le cycle eulérien.
    """

    if not nx.is_eulerian(graph):
        return None

    # Copier le graphe pour effectuer les modifications
    modified_graph = graph.copy()
    
    # Liste pour stocker le cycle eulérien
    curr_path = [list(modified_graph.nodes())[0]]
    eulerian_cycle = []
    current_node = curr_path[0]
    while len(curr_path):
        neighbors = list(modified_graph.neighbors(current_node))
        if (neighbors):
            curr_path.append(current_node)
            next_node = neighbors[-1]
            modified_graph.remove_edge(current_node, next_node)
            current_node = next_node
        else:   
            eulerian_cycle.append(current_node)
            current_node = curr_path[-1]
            curr_path.pop()
    return eulerian_cycle