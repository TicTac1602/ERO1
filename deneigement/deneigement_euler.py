import osmnx as ox
import networkx as nx
import heapq
import math
import time
from datetime import datetime

# Dictionnaire des correspondances entre les noms de lieux et leurs emplacements
lieux = {
    "outremont": "Outremont, Montreal, Canada",
    "verdun": "Verdun, Montreal, Canada",
    "montRoyal": "Le Plateau-Mont-Royal, Montreal, Canada",
    "riviere": "Rivière-des-Prairies-Pointe-aux-Trembles, Montreal, Canada",
    "saintLeonard": "Saint-Léonard, Montreal, Canada"
}

def deneigement_euler(place_name):
    """
    Effectue le déneigement d'un quartier
    @param place_name: Nom de la région à déneiger
    """

    # Vérification des arguments
    if place_name in lieux:
        place_name = lieux[place_name]
    else:
        print(place_name, " n'est pas un emplacement géré dans ce projet")
        print("Les quartiers gérés sont : [outremont,verdun,montRoyal,riviere,saintLeonard]")
        return

    # Initialisation du graphe
    graph = ox.graph_from_place(place_name, network_type="drive")
    # convert your MultiDiGraph to a DiGraph without parallel edges
    # D = ox.utils_graph.get_digraph(graph)
    # Situation initiale
    chemin_parcouru = None
    distance_totale = None

    start = time.time()
    found, chemin_parcouru, distance_totale = make_it_eulerian(graph)
    end = time.time()

    return chemin_parcouru, distance_totale

def dijkstra(graph, node, visited):
    """
    Effectue l'algorithme de Dijkstra à partir d'un nœud donné dans le graphe.

    @param graph: Graphe à parcourir.
    @param node: Nœud de départ du parcours.
    @param visited: Ensemble des nœuds visités.
    @return: Tuple contenant le nœud de degré impair ayant la plus petite distance, la distance pour y arriver et le chemin parcouru.
    """

    heap = []
    heapq.heappush(heap, (0, node, [node]))
    res = []
    while heap:
        distance, current_node, path = heapq.heappop(heap)
        visited.add(current_node)
        if len(visited) > 1 and graph.in_degree(current_node) != graph.out_degree(current_node):
            # Sélection du nœud de degré impair ayant la plus petite distance
            res.append((distance,current_node,path))
        for neighbor in graph.successors(current_node):
            if neighbor not in visited:
                edge_length = graph.get_edge_data(current_node, neighbor)[0]["length"]
                heapq.heappush(heap, (distance + edge_length, neighbor, path + [neighbor]))
    return res

def make_it_eulerian(graph):
    """
    Transforme le graphe en un graphe eulérien en ajoutant des arêtes supplémentaires.

    @param graph: Graphe à transformer en graphe eulérien.
    @return: Tuple contenant un indicateur si un chemin eulérien a été trouvé, le chemin parcouru (liste d'arêtes) et la distance totale parcourue (float).
    """
    
    odd_nodes = [node for node in graph.nodes if graph.in_degree(node) != graph.out_degree(node)]
    nb_todo = len(odd_nodes)
    while odd_nodes:
        node = odd_nodes[0]
        distances = dijkstra(graph, node, set())
        while (graph.in_degree(node) != graph.out_degree(node)):
            in_node = None
            out_node = None
            if (graph.in_degree(node) > graph.out_degree(node)):
                out_node = node
            else:
                in_node = node
            for distance,node_d,path in distances:
                if (graph.in_degree(node) == graph.out_degree(node)):
                    break
                if in_node is None and graph.out_degree(node_d) > graph.in_degree(node_d): 
                    in_node = node_d
                elif graph.out_degree(node_d) < graph.in_degree(node_d):
                    out_node = node_d
                if in_node != None and out_node != None : 
                    graph.add_edge(out_node, in_node, directed=False, length=distance)
        odd_nodes = [node for node in graph.nodes if graph.in_degree(node) != graph.out_degree(node)]
        if len(odd_nodes) % 100 == 0:
            print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Graph Eulerien :", round(((nb_todo - len(odd_nodes)) / nb_todo) * 100, 2), "%")
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Le graphe a été rendu Eulerien")
    eulerian_cycle, distance = parcourir_aretes_euler(graph)
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Un itinéraire a été trouvé")
    return True, eulerian_cycle, distance

def parcourir_aretes_euler(graph):
    """
    Parcourt les arêtes du graphe eulérien pour former un cycle eulérien.

    @param graph: Graphe eulérien à parcourir.
    @param verbose: Indicateur pour l'affichage détaillé.
    @return: Tuple contenant la liste des arêtes parcourues dans le cycle eulérien et la distance totale parcourue (float).
    """

    if not nx.is_eulerian(graph):
        return None, None
    cycle = find_eulerian_cycle(graph)
    print(cycle)
    list = [[cycle[i], cycle[i + 1]] for i in range(len(cycle) - 1)]
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
    visited_edges = set()
    current_node = curr_path[0]
    while len(curr_path):
        neighbors = list(modified_graph.successors(current_node))
        next_node = None

        # Find the next unvisited neighbor
        for neighbor in neighbors:
            edge = (current_node, neighbor)
            reverse_edge = (neighbor, current_node)
            if edge not in visited_edges and reverse_edge not in visited_edges:
                next_node = neighbor
                visited_edges.add(edge)
                break

        if next_node is not None:
            curr_path.append(current_node)
            modified_graph.remove_edge(current_node, next_node)
            current_node = next_node
        else:
            eulerian_cycle.append(current_node)
            current_node = curr_path[-1]
            curr_path.pop()

    return eulerian_cycle


deneigement_euler("outremont")
