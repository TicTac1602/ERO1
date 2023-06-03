import osmnx as ox
import networkx as nx

import matplotlib.pyplot as plt

place_name = "Outremont, Montreal, Canada"
graph = ox.graph_from_place(place_name, network_type="drive")

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
    component_mapping = {}  # Dictionnaire des composantes vers les identifiants numériques

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

def find_path_macro(condensation_graph,graph, source):
    path = []
    current_node = source
    copy_condensation = condensation_graph.copy()
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

        path.append(current_node)
        condensation_graph.remove_edge(current_node, next_node )
        current_node = next_node  
    path_micro = find_path_micro(copy_condensation,graph,path)
    return path,path_micro

def find_path_micro(condensation_graph,graph,path):
    path_micro = []
    first = True
    for scc in path:
        if first:
            source = None
        else : 
            prev_scc = path[path.index(scc) - 1]
            source = None
            out = False
            for out_node in condensation_graph.nodes[prev_scc]['out']:
                if out:
                    break
                for in_node in condensation_graph.nodes[scc]['go']:
                    if graph.has_edge(out_node, in_node):
                        source = in_node
                        out = True
                        break
            
        if scc == path[-1]:
            destination = None
        else:
            next_scc = path[path.index(scc) + 1]
            destination = None
            out = False
            for out_node in condensation_graph.nodes[scc]['out']:
                if out:
                    break
                for in_node in condensation_graph.nodes[next_scc]['go']:
                    if graph.has_edge(out_node, in_node):
                        destination = out_node
                        out = True
                        break
        path_micro.extend(explore_scc(condensation_graph,graph,scc,source,destination))
        first = False
    return path_micro

def explore_scc(condensation_graph, graph, scc, source, destination):
    path_scc = []

    if scc in condensation_graph.nodes:
        print('ouii')

    # Recuperation des infos de chemin
    if not source:
        start_node = condensation_graph.nodes[scc]['go']
        if start_node:
            start_node = start_node[0]
        else:
            start_node = condensation_graph.nodes[scc]['component'][0]
    else:
        start_node = source
    if not destination:
        end_node = condensation_graph.nodes[scc]['out'][-1]
    else:
        end_node = destination
    
    # Explore la SCC
    # TODO faire le chemin de source a destination
    return path_scc


def deneigement_macro(sources,condensation,graph):
    cpy_graph = condensation.copy()
    paths = []
    while sources:
        path,path_micro = find_path_macro(cpy_graph,graph,sources[0])
        paths.append(path_micro)
        sources, sinks = find_sources_and_sinks(cpy_graph)
    return paths

scc = tarjan_scc(graph)
print(f"Nombres de composantes fortement connexes : {len(scc)}")

condensation = create_condensation_graph(graph, scc)

# visualize_condensation_graph(condensation)

sources, sinks = find_sources_and_sinks(condensation)
print("Sources :", sources)
print("Puits :", sinks)

paths = deneigement_macro(sources, condensation,graph)
print("Chemin :", paths)

pos = nx.spring_layout(condensation)
nx.draw(condensation, pos, with_labels=True, node_size=50, node_color='lightblue', edge_color='gray', arrows=True)

ox.plot_graph_routes(graph, paths)
plt.show()
 