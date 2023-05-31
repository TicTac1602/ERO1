import osmnx as ox
import networkx as nx

import matplotlib.pyplot as plt

place_name = "Rivière-des-Prairies-Pointe-aux-Trembles, Montreal, Canada"
graph = ox.graph_from_place(place_name, network_type="drive")

ox.plot_graph(graph, node_size=4)

def tarjan_scc(graph):
    index = 0
    stack = []
    scc_list = []

    def strongconnect(v):
        nonlocal index
        graph.nodes[v]['index'] = index
        graph.nodes[v]['lowlink'] = index
        index += 1
        stack.append(v)

        for neighbor in graph.neighbors(v):
            if 'index' not in graph.nodes[neighbor]:
                strongconnect(neighbor)
                graph.nodes[v]['lowlink'] = min(graph.nodes[v]['lowlink'], graph.nodes[neighbor]['lowlink'])
            elif neighbor in stack:
                graph.nodes[v]['lowlink'] = min(graph.nodes[v]['lowlink'], graph.nodes[neighbor]['index'])

        if graph.nodes[v]['lowlink'] == graph.nodes[v]['index']:
            scc = []
            while True:
                w = stack.pop()
                scc.append(w)
                if w == v:
                    break
            scc_list.append(scc)

    for node in graph.nodes:
        if 'index' not in graph.nodes[node]:
            strongconnect(node)

    return scc_list

def create_condensation_graph(graph, scc):
    condensation_graph = nx.DiGraph()
    component_mapping = {}  # Dictionnaire de mapping des composantes vers les identifiants numériques

    for i, component in enumerate(scc):
        component_mapping[i] = component
        condensation_graph.add_node(i, component=component,go=[],out=[])

    for u, v, data in graph.edges(data=True):
        u_component = None
        v_component = None

        for i, component in component_mapping.items():
            if u in component:
                u_component = i
            if v in component:
                v_component = i

        if u_component is not None and v_component is not None and u_component != v_component:
            if condensation_graph.has_edge(u_component, v_component):
                condensation_graph[u_component][v_component]['distance'] += data['length']
            else:
                condensation_graph.add_edge(u_component, v_component, distance=data['length'])
                condensation_graph.nodes[u_component]['out'] += [u]
                condensation_graph.nodes[v_component]['go'] += [v]

    return condensation_graph

def visualize_condensation_graph(condensation_graph):
    pos = nx.spring_layout(condensation_graph)
    edge_labels = {(u, v): round(d['distance'],3) for u, v, d in condensation_graph.edges(data=True)}

    nx.draw(condensation_graph, pos, with_labels=True, node_size=50, node_color='lightblue', edge_color='gray', arrows=True)
    nx.draw_networkx_edge_labels(condensation_graph, pos, edge_labels=edge_labels)

    plt.title("Graphe de condensation")
    plt.show()

def find_sources_and_sinks(condensation_graph):
    sources = []
    sinks = []

    for node in condensation_graph.nodes:
        out_degree = condensation_graph.out_degree(node)
        in_degree = condensation_graph.in_degree(node)

        if out_degree == 0 and in_degree != 0:
            sinks.append(node)
        if in_degree == 0 and out_degree != 0:
            sources.append(node)
    return sources, sinks

def find_path_macro(condensation_graph, source):
    path = []
    current_node = source

    while True:
        neighbors = list(condensation_graph.neighbors(current_node))

        if len(neighbors) == 0:
            break

        max_component_size = float('inf')
        next_node = None

        for neighbor in neighbors:
            component = condensation_graph.nodes[neighbor]['component']
            component_size = len(component)

            if component_size < max_component_size:
                max_component_size = component_size
                next_node = neighbor

        path.append((current_node, next_node))
        condensation_graph.remove_edge(current_node, next_node )
        current_node = next_node  
    if condensation_graph.out_degree(source) == 0: 
        condensation_graph.remove_node(source)
    u,v = path[-1]
    if condensation_graph.in_degree(v) == 0:
        condensation_graph.remove_node(v)
    return path

def deneigement_macro(sources,condensation):
    cpy_graph = condensation.copy()
    paths = []
    while sources:
        path = find_path_macro(cpy_graph,sources[0])
        paths.append(path)
        sources, sinks = find_sources_and_sinks(cpy_graph)
    return paths

scc = tarjan_scc(graph)
print(f"Nombres de composantes fortement connexes : {len(scc)}")

condensation = create_condensation_graph(graph, scc)

visualize_condensation_graph(condensation)

sources, sinks = find_sources_and_sinks(condensation)
print("Sources :", sources)
print("Puits :", sinks)

paths = deneigement_macro(sources, condensation)
print("Chemin :", paths)

pos = nx.spring_layout(condensation)
nx.draw(condensation, pos, with_labels=True, node_size=50, node_color='lightblue', edge_color='gray', arrows=True)
for path in paths :
    nx.draw_networkx_edges(condensation, pos, edgelist=path, edge_color='red', arrows=True)
plt.show()
 