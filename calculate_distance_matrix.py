import numpy as np
import networkx as nx
import nearest_gps_coordinates_for_guidepoints


def calculate_distance_matrix(place_name):
    print("before calculating distance matrix")
    G, nodes = nearest_gps_coordinates_for_guidepoints.nearest_gps_coordinates_for_guidepoints(place_name)

    # Calculate the shortest path length between each pair of nodes
    n = len(nodes)
    distance_matrix = np.zeros((n, n), dtype=int)

    for i in range(n):
        for j in range(n):
            if i != j:
                try:
                    distance_matrix[i][j] = int(nx.shortest_path_length(G, nodes[i], nodes[j], weight='length'))
                except nx.NetworkXNoPath:
                    distance_matrix[i][j] = 999999999

    print("finished calculating distance matrix")
    return G, distance_matrix
