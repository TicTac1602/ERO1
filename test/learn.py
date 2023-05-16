import osmnx as ox
import networkx as nx

##########################
# Manipulation classique #
##########################

place_name = "Outremont, Montreal, Canada"
# Recuperation des donées Géo
graph = ox.graph_from_place(place_name, network_type="all")
# Creation de graph a partir des donées
G = ox.plot_graph(graph, show=False, close=False)
# Analyse des réseaux routiers
shortest_path = nx.shortest_path(graph, source=source_node, target=target_node)
# Visualisation des données cartographiques:
ox.plot_graph(ox.graph_from_place(place_name, network_type="all"), show=True)
# Extraction de données spécifiques
streets = ox.graph_to_gdfs(graph, nodes=False, edges=True)["name"]

########################################
# Récuperer la distance entre 2 points #
########################################

# Définition des points de départ et d'arrivée (exemple)
start_point = (45.523, -73.603)  # Coordonnées du point de départ
end_point = (45.517, -73.582)  # Coordonnées du point d'arrivée

# Recherche des nœuds les plus proches dans le graphe
start_node = ox.distance.nearest_nodes(graph, start_point[1], start_point[0], method='haversine')
end_node = ox.distance.nearest_nodes(graph, end_point[1], end_point[0], method='haversine')

# Calcul du chemin le plus court (par distance) entre les deux nœuds
shortest_path = nx.shortest_path(graph, source=start_node, target=end_node, weight='length')

# Récupération de la distance totale du chemin le plus court
total_distance = sum(nx.get_edge_attributes(graph, 'length')[edge] for edge in zip(shortest_path[:-1], shortest_path[1:]))

# Attribution de la distance comme valeur d'arc pour chaque segment de route
edge_attributes = {(u, v): graph.edges[u, v]['length'] for u, v in zip(shortest_path[:-1], shortest_path[1:])}
nx.set_edge_attributes(graph, edge_attributes, 'distance')

# Accès à la valeur d'arc pour un segment de route spécifique
distance_of_edge = graph.edges[start_node, shortest_path[1]]['distance']
