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
        print(place_name, " n'est pas un emplacement gerer dans ce projet")
        print("Les quartiers gerer sont : [outremont,verdun,montRoyal,riviere,saintLeonard]")
        return
    # Télécharger le graphe du réseau de rues du lieu spécifié
    graph = ox.graph_from_place(place_name, network_type="drive")
    ox.plot_graph(graph, show=verbose)
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
        reel_distance = 0
        for u,v,data in graph.edges(data=True):
            reel_distance += data['length']
        print("Surface reel du quartier:", reel_distance, 'm')
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

def dfs(graph, node, visited):
    stack = [(node, 0, [node])]  
    while stack:
        current_node, distance, path = stack.pop()  
        visited.add(current_node)  # Marquer le nœud comme visité
        if len(visited) > 1 and graph.degree(current_node) % 2 != 0:
            return current_node, distance, path  # Retourner le nœud, la distance et le chemin
        for neighbor in graph.neighbors(current_node):
            if neighbor not in visited:
                edge_length = graph.get_edge_data(current_node, neighbor)[0]['length']
                stack.append((neighbor, distance + edge_length, path + [neighbor]))

def make_it_eulerian(graph):
    odd_nodes = [node for node in graph.nodes if graph.degree(node) % 2 != 0]
    added_edge = 0
    while(odd_nodes):
        node = odd_nodes[0]
        neighbors = list(graph.neighbors(node))
        odd_degree_neighbors = [neighbor for neighbor in graph.neighbors(node) if graph.degree(neighbor) % 2 != 0]
        if(odd_degree_neighbors):
            length = graph.get_edge_data(odd_degree_neighbors[0], node)[0]['length']
            graph.add_edge(node, odd_degree_neighbors[0],length=length)
            odd_nodes = [node for node in graph.nodes if graph.degree(node) % 2 != 0]
            added_edge +=1
        else :
            # faire un DFS qui retourne le premier noeud pas visiter de degres imp et la distance pour aller a ce point
            visited = set()
            target_node, distance, path = dfs(graph, node, visited)
            for i in range(len(path) - 1):
                source = path[i]
                destination = path[i + 1]
                edge_length = graph.get_edge_data(source, destination)[0]['length']
                graph.add_edge(source, destination, length=edge_length)
            odd_nodes = [node for node in graph.nodes if graph.degree(node) % 2 != 0]
            added_edge +=1
    odd_nodes = [node for node in graph.nodes if graph.degree(node) % 2 != 0]
    if not odd_nodes:
        eulerian_cycle, distance = parcourir_aretes_euler(graph)
        return True, eulerian_cycle, distance
    else:
        print("Pas de cycle eulerien apres ajout d'arc")
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

def parcourir_aretes_euler(graph):
    if not nx.is_eulerian(graph):
        return "Le graphe n'est pas eulérien."
    cycle = nx.eulerian_circuit(graph)
    cycle_arretes = [[u, v] for u, v in cycle]
    distance_totale = sum(graph.get_edge_data(u, v)[0]['length'] for u, v in cycle_arretes)
    return cycle_arretes,distance_totale
