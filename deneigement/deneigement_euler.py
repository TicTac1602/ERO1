import osmnx as ox
import networkx as nx
import heapq
import math
import time
from datetime import datetime
import matplotlib.pyplot as plt
import random
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
    visualize_condensation_graph(graph,[3691019539, 5412399379])
    fix_dead_end(graph)
    fix_source(graph)
    print(nx.is_strongly_connected(graph))
    found, chemin_parcouru, distance_totale = make_it_eulerian(graph)
    print(chemin_parcouru,distance_totale)
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
def dijkstra_inverted(graph, node, visited):
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
        for neighbor in graph.predecessors(current_node):
            if neighbor not in visited:
                edge_length = graph.get_edge_data(neighbor, current_node)[0]["length"]
                heapq.heappush(heap, (distance + edge_length, neighbor, path + [neighbor]))
    return res
def dijkstra_inverted_reinject(graph, node, visited):
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
        if len(visited) > 1 and graph.out_degree(current_node) == graph.in_degree(current_node):
            # Sélection du nœud de degré impair ayant la plus petite distance
            res.append((distance,current_node,path))
        for neighbor in graph.predecessors(current_node):
            if neighbor not in visited:
                edge_length = graph.get_edge_data(neighbor, current_node)[0]["length"]
                heapq.heappush(heap, (distance + edge_length, neighbor, path + [neighbor]))
    return res

def visualize_condensation_graph(condensation_graph,node_to_find=[209387103]):
    pos = nx.spring_layout(condensation_graph)
    # edge_labels = {(u, v): round(d['distance'],3) for u, v, d in condensation_graph.edges(data=True)}

    nx.draw(condensation_graph, pos, with_labels=False, node_size=50, node_color='lightblue', edge_color='gray', arrows=True)
    # nx.draw_networkx_edge_labels(condensation_graph, pos, edge_labels="test")
    nx.draw_networkx_nodes(condensation_graph, pos, nodelist=node_to_find, node_color='red', node_size=100)
    plt.title("Graphe de condensation")
    plt.show()

def fix_source(graph):
    node_todo=[element for element in graph.nodes if graph.in_degree(element)==0]
    for u in node_todo:
            for v in (graph.successors(u)):
                data = graph.get_edge_data(u,v)
                graph.add_edge(v, u, directed=True, length=data[0]["length"])

def fix_dead_end(graph):
    node_todo=[element for element in graph.nodes if graph.out_degree(element)==0]
    for u in node_todo:
            v=list(graph.predecessors(u))[0]
            data = graph.get_edge_data(v,u)
            graph.add_edge(u, v, directed=True, length=data[0]["length"])
            while(graph.out_degree(v)<2):
                preds=list(graph.predecessors(v))
                for pred in preds:
                    if pred!=u:
                        data = graph.get_edge_data(pred,v)
                        graph.add_edge(v, pred,directed=True, length=data[0]["length"])
                        v=pred
                        break

def make_it_eulerian(graph):
    """
    Transforme le graphe en un graphe eulérien en ajoutant des arêtes supplémentaires.

    @param graph: Graphe à transformer en graphe eulérien.
    @return: Tuple contenant un indicateur si un chemin eulérien a été trouvé, le chemin parcouru (liste d'arêtes) et la distance totale parcourue (float).
    """
    unbalanced_nodes = []

    for node in graph:
            in_degree = graph.in_degree(node)
            out_degree = graph.out_degree(node)
            if in_degree != out_degree:
                unbalanced_nodes.append(node)
    nb_todo = len(unbalanced_nodes)

    first=True
    while(first or len(unbalanced_nodes)>2):

        first=False

        node= unbalanced_nodes[0]
        if(graph.out_degree(node)==0):
            edge_length = graph.get_edge_data(list(graph.predecessors(node))[0], node)[0]["length"]
            graph.add_edge(node, list(graph.predecessors(node))[0], directed=True, length=edge_length)
            continue

        if(graph.in_degree(node)>graph.out_degree(node)):
            distances = dijkstra(graph, node, set())
            if not distances:
                distances = dijkstra_inverted_reinject(graph, node, set())
                graph.add_edge(node, distances[-1][1], directed=True, length=distances[0][0]) 
                continue
            for distance,node_end,path in distances:
                if(node_end  in unbalanced_nodes):
                    # make a path to this node_end
                    add_path(graph,path)
                    break

        else:
            # ajouter un arc entrant
            distances = dijkstra_inverted(graph, node, set())
            if not distances:
                distances = dijkstra_inverted_reinject(graph, node, set())
                graph.add_edge(node, distances[-1][1], directed=True, length=distances[0][0]) 
                continue
            for distance,node_end,path in distances:
                if(node_end  in unbalanced_nodes):
                    # make a path to this node_end
                    inverted_list = path[::-1]
                    add_path(graph,inverted_list)
                    break
        unbalanced_nodes = []
        for node in graph:
            in_degree = graph.in_degree(node)
            out_degree = graph.out_degree(node)
            if in_degree != out_degree:
                unbalanced_nodes.append(node)
        if len(unbalanced_nodes) % 1 == 0:
            print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Graph Eulerien :", round(((nb_todo - len(unbalanced_nodes)) / nb_todo) * 100, 2), "%",end='\r')

    visualize_condensation_graph(graph,unbalanced_nodes)
    chemin,distance_total=parcourir_aretes_euler(graph,unbalanced_nodes)

    return True,chemin,distance_total

def add_path(graph,path):
    while(len(path)>1):
        edge_length = graph.get_edge_data(path[0], path[1])[0]["length"]
        graph.add_edge(path[0], path[1], directed=True, length=edge_length)
        path.pop(0)
    return

def parcourir_aretes_euler(graph,sources):
    """
    Parcourt les arêtes du graphe eulérien pour former un cycle eulérien.

    @param graph: Graphe eulérien à parcourir.
    @param verbose: Indicateur pour l'affichage détaillé.
    @return: Tuple contenant la liste des arêtes parcourues dans le cycle eulérien et la distance totale parcourue (float).
    """

    if not nx.has_eulerian_path(graph,sources[0]):
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
