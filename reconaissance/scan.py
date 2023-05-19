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
    # Parcours des arêtes et calcul de la distance totale
    chemin_parcouru, distance_totale = parcourir_aretes(GU)

    # Affichage du chemin parcouru
    if verbose:
        print("Chemin calculer")

    # Affichage de la distance totale parcourue
    if verbose:
        print("Distance totale parcourue :", distance_totale, "m")
        print("Creation du plan avec l'itineraire (Cette operation peut etre longue) ETA :" , 0.09* len(chemin_parcouru), " secondes")

    # Tracer l'itinéraire sur OSMnx
    start_time = time.time() 
    fig, ax = ox.plot_graph_routes(GU, chemin_parcouru, route_linewidth=6, node_size=0, bgcolor='w', show=verbose)
    end_time = time.time()
    execution_time = end_time - start_time  # Calcul du temps d'exécution

    print("Temps d'exécution : ", execution_time, " secondes avec ", len(chemin_parcouru), " arretes")
    return chemin_parcouru, distance_totale


# Parcours de toutes les arêtes du graphe
def parcourir_aretes(graph):
    chemin = []
    distance_totale = 0  # Variable pour stocker la distance totale parcourue
    for u, v, k, data in graph.edges(keys=True, data=True):
        chemin.append([u, v])
        distance = data["length"]
        distance_totale += distance * 2  # Ajouter la distance à la distance totale allez et retour
        chemin.append([v, u])

    return chemin, distance_totale

