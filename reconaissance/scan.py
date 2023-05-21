import osmnx as ox
import networkx as nx
import time

# Dictionnaire des correspondances entre les noms de lieux et leurs emplacements
lieux = {
    "outremont": "Outremont, Montreal, Canada",
    "verdun": "Verdun, Montreal, Canada",
    "montRoyal": "Le Plateau-Mont-Royal, Montreal, Canada",
    "riviere": "Rivière-des-Prairies-Pointe-aux-Trembles, Montreal, Canada",
    "saintLeonard": "Saint-Léonard, Montreal, Canada"
}

def scan(place_name, verbose=False):
    if place_name in lieux:
        place_name = lieux[place_name]
    else:
        print(place_name, " n'est pas un emplacement géré dans ce projet")
        print("Les quartiers gérés sont : [outremont,verdun,montRoyal,riviere,saintLeonard]")
        return
    print("Debut du scan de la région : ",place_name)
    # Télécharger le graphe du réseau de rues du lieu spécifié
    graphique = ox.graph_from_place(place_name, network_type="drive")
    ox.plot_graph(graphique, show=verbose)
    GU = graphique.to_undirected()
    if not nx.is_connected(GU):
        print("Le graphe n'est pas connexe.")

    chemin_parcouru = None
    distance_totale = None
    reel_distance = 0
    for u, v, data in graphique.edges(data=True):
        reel_distance += data["length"]
    print("Surface réelle du quartier:", reel_distance, "m")
    start = time.time()
    # Parcours des arêtes et calcul de la distance totale
    found, chemin_parcouru, distance_totale = make_it_eulerian(GU,verbose)
    if not found:
        print("Calcul du chemin en glouton")
        chemin_parcouru, distance_totale = parcourir_aretes(GU)
    end = time.time()

    # Affichage des informations
    print("Chemin trouvé en ", end - start, "s")
    
    print("Distance totale parcourue :", distance_totale, "m")

    if verbose:
        print("Création du plan avec l'itinéraire (Cette opération peut être longue) ETA :", 0.08 * len(chemin_parcouru), " secondes")
        # Tracer l'itinéraire sur OSMnx
        ox.plot_graph_routes(GU, chemin_parcouru, route_linewidth=6, node_size=0, bgcolor="w", show=True)
    print("Fin du scan")
    return chemin_parcouru, distance_totale


def dfs_min(graph, node, visited):
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
    

def make_it_eulerian(graph,verbose):
    odd_nodes = [node for node in graph.nodes if graph.degree(node) % 2 != 0]
    added_edge = 0
    while odd_nodes:
        node = odd_nodes[0]
        neighbors = list(graph.neighbors(node))
        odd_degree_neighbors = [neighbor for neighbor in graph.neighbors(node) if graph.degree(neighbor) % 2 != 0]
        if odd_degree_neighbors and odd_degree_neighbors[0] != node:
            length = graph.get_edge_data(odd_degree_neighbors[0], node)[0]["length"]
            graph.add_edge(node, odd_degree_neighbors[0], directed=False, length=length)
            added_edge += 1
        else:
            # Faire un DFS qui retourne le premier nœud non visité de degré impair et la distance pour y arriver
            visited = set()
            target_node, distance, path = dfs_min(graph, node, visited)
            # Création d'arcs pour atteindre ce nœud
            for i in range(len(path) - 1):
                source = path[i]
                destination = path[i + 1]
                edge_length = graph.get_edge_data(source, destination)[0]["length"]
                graph.add_edge(source, destination, directed=False, length=edge_length)
            added_edge += 1
        # Recalcul des nœuds de degré impair pour voir si on a fini
        odd_nodes = [node for node in graph.nodes if graph.degree(node) % 2 != 0]
    if not odd_nodes:
        eulerian_cycle, distance = parcourir_aretes_euler(graph,verbose)
        return True, eulerian_cycle, distance
    else:
        print("Pas de cycle eulérien après ajout d'arcs")
        return False, None, 0


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


def parcourir_aretes_euler(graph,verbose):
    if not nx.is_eulerian(graph):
        return "Le graphe n'est pas eulérien."
    cycle = find_eulerian_cycle(graph)
    # Pretty print of the cycle
    if (not verbose):
        for i in range(len(cycle) - 1, -1, -1):
            print(cycle[i], end = "")
            if i:
                print(" -> ", end = "")
    list = [[cycle[i], cycle[i+1]] for i in range(len(cycle)-1)]
    distance_totale = sum(graph.get_edge_data(u, v)[0]["length"] for u, v in list)
    return list, distance_totale

def find_eulerian_cycle(graph):

    # Vérifier si le graphe est eulérien
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