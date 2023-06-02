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

deneigeuse_T1 = {
    "vitesse" :  10,
    "cout_jour": 500,
    "cout_kilo": 1.1,
    "cout_horaires_8":1.1,
    "cout_horaires_8p":1.3
}

deneigeuse_T2 = {
    "vitesse" :  20,
    "cout_jour": 800,
    "cout_kilo": 1.3,
    "cout_horaires_8":1.3,
    "cout_horaires_8p":1.5
}

def deneigement_euler(place_name,vehicule):
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
    ox.plot_graph(graph)
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Graphique de la région",place_name, "chargé !")

    # Situation initiale
    chemin_parcouru = None
    distance_totale = None
    reel_distance = 0
    for u, v, data in graph.edges(data=True):
        reel_distance += data["length"]
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Surface réelle du quartier :",round(reel_distance/1000,2), "km")

    start = time.time()
    fix_dead_end(graph)
    fix_source(graph)
    chemin_parcouru, distance_totale = make_it_eulerian(graph)
    end = time.time()

    # Affichage des informations
    time_travel = (distance_totale/1000)/vehicule["vitesse"]
    daily_cost = math.ceil(time_travel/24)

    cout_journalier = daily_cost*vehicule["cout_jour"]
    if time_travel > 8 : 
        cout_journalier += 8*vehicule["cout_horaires_8"]
        time_travel -= 8
        cout_journalier += math.ceil(time_travel)*vehicule["cout_horaires_8p"]
        time_travel +=8
    else : 
        cout_journalier += math.ceil(time_travel)*vehicule["cout_horaires_8"]
    cout_journalier += math.ceil(distance_totale/1000)*vehicule["cout_kilo"]


    print(datetime.now().strftime("[%d/%m %H:%M:%S]"),"Chemin trouvé en",round(end - start,4), "s")
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Distance totale parcourue :",round(distance_totale/1000,2), "km")
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"),"Temps estimé du parcours :",round(time_travel,2) ,"h")
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Cout estimé du déneigement :",cout_journalier  ,"€")
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Fin du déneigement")
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
def dijkstra_reinject(graph, node, visited):
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
        for neighbor in graph.successors(current_node):
            if neighbor not in visited:
                edge_length = graph.get_edge_data(current_node,neighbor,)[0]["length"]
                heapq.heappush(heap, (distance + edge_length, neighbor, path + [neighbor]))
    return res

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
    unbalanced_nodes = [node for node in graph.nodes if graph.in_degree(node) != graph.out_degree(node)]
    nb_todo = len(unbalanced_nodes)

    while len(unbalanced_nodes):

        node= unbalanced_nodes[0]      
        if(graph.in_degree(node)>graph.out_degree(node)):
            distances = dijkstra(graph, node, set())
            if not distances:
                distances = dijkstra_inverted_reinject(graph, node, set())
                graph.add_edge(node, distances[-1][1], directed=True, length=distances[-1][0]) 
            else :
                found = False
                for distance,node_end,path in distances:
                    #link to a bad nodes that will help the situation
                    if node_end in unbalanced_nodes and graph.in_degree(node_end) < graph.out_degree(node_end):
                        found = True
                        # make a path to this node_end
                        add_path(graph,path)
                        break
                if not found: 
                    distances = dijkstra_inverted_reinject(graph, node, set())
                    graph.add_edge(node, distances[-1][1], directed=True, length=distances[-1][0])
        else:
            # ajouter un arc entrant
            distances = dijkstra_inverted(graph, node, set())
            if not distances:
                distances = dijkstra_reinject(graph, node, set())
                graph.add_edge(distances[-1][1], node , directed=True, length=distances[-1][0]) 
            else :
                for distance,node_end,path in distances:
                    if node_end in unbalanced_nodes and graph.in_degree(node_end)>graph.out_degree(node_end):
                        # make a path to this node_end
                        inverted_list = path[::-1]
                        add_path(graph,inverted_list)
                        break
        unbalanced_nodes = [node for node in graph.nodes if graph.in_degree(node) != graph.out_degree(node)]

        if len(unbalanced_nodes) % 1 == 0:
            print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Graph Eulerien :", round(((nb_todo - len(unbalanced_nodes)) / nb_todo) * 100, 2), "%",end='\r')
        if round(((nb_todo - len(unbalanced_nodes)) / nb_todo) * 100, 2) >= 83.8 :
            print("debug")
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Le graphe a été rendu Eulerien")
    chemin,distance_totale = parcourir_aretes_euler(graph)
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Un itinéraire a été trouvé")

    return chemin,distance_totale

def add_path(graph,path):
    for i in range(len(path) - 1):
        source = path[i]
        destination = path[i + 1]
        edge_length = graph.get_edge_data(source, destination)[0]["length"]
        graph.add_edge(source, destination, directed=False, length=edge_length)

def parcourir_aretes_euler(graph):
    """
    Parcourt les arêtes du graphe eulérien pour former un cycle eulérien.

    @param graph: Graphe eulérien à parcourir.
    @param verbose: Indicateur pour l'affichage détaillé.
    @return: Tuple contenant la liste des arêtes parcourues dans le cycle eulérien et la distance totale parcourue (float).
    """

    if not nx.is_eulerian(graph):
        return None, None
    cycle = trouver_cycle_eulerien(graph)
    list = [[cycle[i], cycle[i + 1]] for i in range(len(cycle) - 1)]
    distance_totale = sum(graph.get_edge_data(u, v)[0]["length"] for u, v in list)
    return list, distance_totale

def trouver_cycle_eulerien(graph):
    # Vérifier si le graphe est fortement connexe
    if not nx.is_strongly_connected(graph) and nx.is_eulerian(graph):
        return None
    
    # Trouver le cycle eulerien
    cycle_eulerien = list(nx.eulerian_circuit(graph))
    
    # Créer la liste des sommets visités
    sommets_visites = [cycle_eulerien[0][0]]
    for arc in cycle_eulerien:
        sommets_visites.append(arc[1])
    
    return sommets_visites

deneigement_euler("riviere",deneigeuse_T2)
