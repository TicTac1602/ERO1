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

deneigeuse_T1 = {
    "nom" : "deneigeuse Type1",
    "vitesse" :  10,
    "cout_jour": 500,
    "cout_kilo": 1.1,
    "cout_horaires_8":1.1,
    "cout_horaires_8p":1.3
}

deneigeuse_T2 = {
    "nom" : "deneigeuse Type2",
    "vitesse" :  20,
    "cout_jour": 800,
    "cout_kilo": 1.3,
    "cout_horaires_8":1.3,
    "cout_horaires_8p":1.5
}

def deneigement_euler(place_name,vehicule = None):
    """
    Effectue le déneigement d'un quartier
    @param place_name: Nom de la région à déneiger
    @param vehicule: Véhicule qui va deneiger
    """

    # Vérification des arguments
    if place_name in lieux:
        place_name = lieux[place_name]
    else:
        print(place_name, " n'est pas un emplacement géré dans le deneigement")
        print("Les quartiers gérés sont : [outremont,verdun,montRoyal,riviere,saintLeonard]")
        return

    # Initialisation du graphe
    graph = ox.graph_from_place(place_name, network_type="drive")
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "\033[0;36mGraphique de la région",place_name, "chargé !\033[0m")

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

    #Affichage des stats
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"),"Chemin trouvé en",round(end - start,4), "s")
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Distance totale parcourue :",round(distance_totale/1000,2), "km")
    # Calcul du prix
    if vehicule is not None : 
        cout_journalier,time_travel = calculer_prix(vehicule, distance_totale)
        print(datetime.now().strftime("[%d/%m %H:%M:%S]"),"Temps estimé du parcours :",round(time_travel,2) ,"h")
        print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Cout estimé du déneigement :",round(cout_journalier,2)  ,"€")
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "\033[0;36mFin du déneigement\033[0m")
    return chemin_parcouru, distance_totale,graph

def calculer_meilleur_choix(vehicules, quartiers):
    """
    Trouve le meilleur vehicule pour chaque quartiers

    @param vehicule: Le type de deneigeuse.
    @param quarties: Les quartiers que ont souahite etudier.
    @return: Les meilleurs choix pour chaque quartiers
    """
    meilleur_choix = {}  # Utiliser un dictionnaire pour stocker les résultats
    for quartier in quartiers:
        meilleur_vehicule = None
        meilleur_prix = float('inf')  # initialiser à une valeur élevée pour trouver le prix minimum

        chemin_parcouru, distance_totale =  deneigement_euler(quartier)
        for vehicule in vehicules:
            prix,time_travel= calculer_prix(vehicule, distance_totale)

            if prix < meilleur_prix:
                meilleur_prix = prix
                meilleur_vehicule = vehicule

        meilleur_choix[quartier] = {"Vehicule": meilleur_vehicule["nom"],"Itinéraire":chemin_parcouru,"Distance du trajet":distance_totale,"prix" : meilleur_prix}
    for choix in meilleur_choix:
        print(f"{datetime.now().strftime('[%d/%m %H:%M:%S]')} \033[0;32mLe meilleur choix pour {choix} : {meilleur_choix[choix]['Vehicule']} pour {round(meilleur_choix[choix]['prix'],2)} €\033[0m")
    return meilleur_choix

def calculer_prix(vehicule,distance_totale):
    """
    Calcul le prix d'un vehicule pour une certaines distance

    @param vehicule: Le type de deneigeuse.
    @param distance_totale: La distance totale couverte par ce vehicule .
    @return: Le prix du deneigement
    """
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
    return cout_journalier,time_travel

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
    Transforme le graphe en un graphe eulérien en ajoutant des arêtes supplémentaires. Et trouve un cycle dans ce graphe modifier

    @param graph: Graphe à transformer en graphe eulérien.
    @return: Tuple contenant un indicateur si un chemin eulérien a été trouvé, le chemin parcouru (liste d'arêtes) et la distance totale parcourue (float).
    """
    unbalanced_nodes = [node for node in graph.nodes if graph.in_degree(node) != graph.out_degree(node)]
    nb_todo = len(unbalanced_nodes)
    count=0
    while len(unbalanced_nodes):
        node= unbalanced_nodes[0] 
        if( len(unbalanced_nodes)==2):
            count+=1
            if(count>1):
                unbalanced_nodes.reverse()
                node= unbalanced_nodes[0] 
        if(graph.in_degree(node)>graph.out_degree(node)):
            distances = dijkstra(graph, node, set())
            if not distances:
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
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Le graphe a été rendu Eulerien")
    chemin,distance_totale = parcourir_aretes_euler(graph)
    print(datetime.now().strftime("[%d/%m %H:%M:%S]"), "Un itinéraire a été trouvé")

    return chemin,distance_totale

def add_path(graph,path):
    """
    Ajoute dans le graph le chemin renseigné

    @param graph: Graphe eulérien à parcourir.
    @param path: Chemin a suivre
    """
    for i in range(len(path) - 1):
        source = path[i]
        destination = path[i + 1]
        edge_length = graph.get_edge_data(source, destination)[0]["length"]
        graph.add_edge(source, destination, directed=False, length=edge_length)

def parcourir_aretes_euler(graph):
    """
    Parcourt les arêtes du graphe eulérien pour former un cycle eulérien.

    @param graph: Graphe eulérien à parcourir.
    @return: Tuple contenant la liste des arêtes parcourues dans le cycle eulérien et la distance totale parcourue (float).
    """

    if not nx.is_eulerian(graph):
        return None, None
    cycle = trouver_cycle_eulerien(graph)
    list = [[cycle[i], cycle[i + 1]] for i in range(len(cycle) - 1)]
    distance_totale = sum(graph.get_edge_data(u, v)[0]["length"] for u, v in list)
    return list, distance_totale

def trouver_cycle_eulerien(graph):
    """
    Parcourt les arêtes du graphe eulérien pour trouver le cycle eulérien.

    @param graph: Graphe eulérien à parcourir.
    @return: la liste des arêtes parcourues.
    """

    if not nx.is_strongly_connected(graph) and nx.is_eulerian(graph):
        return None
    
    # Trouver le cycle eulerien
    cycle_eulerien = list(nx.eulerian_circuit(graph))
    
    # Créer la liste des sommets visités
    sommets_visites = [cycle_eulerien[0][0]]
    for arc in cycle_eulerien:
        sommets_visites.append(arc[1])
    
    return sommets_visites

def splitDeneigeuse(place,type1,type2):
    print(f"{datetime.now().strftime('[%d/%m %H:%M:%S]')} \033[0;36mLancement du deneigement avec {type1} deneigeuse de type 1 et {type2} deneigeuse de type 2\033[0;00m")
    chemin_parcouru, distance_totale,graph =  deneigement_euler(place)
    result = []
    curr = 0
    next_step = distance_totale / (type1+type2)
    curr_path = []
    for u,v in chemin_parcouru:
        if next_step < curr:
            result.append([curr_path,curr])
            curr = 0
            e = []
        curr_path.append((u,v))
        curr += graph.get_edge_data(u,v)[0]['length']
    if len(curr_path) != 0:
        result.append([curr_path,curr])
    prix = 0
    max_time = 0
    for res in result: 
        if (type2 > 0):
            cout, time_travel = calculer_prix(deneigeuse_T2, res[1])
            type2-=1
        else:
            cout, time_travel = calculer_prix(deneigeuse_T1, res[1])
        if time_travel > max_time:
            max_time = time_travel
        prix += cout
    print(f"{datetime.now().strftime('[%d/%m %H:%M:%S]')} \033[32mFaire tourner ces deneigeuses coutera : {prix} € et prendra {round(max_time,2)} h\033[0m")
    return result
