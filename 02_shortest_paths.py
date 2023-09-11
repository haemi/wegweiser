import re

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import osmnx as ox
import networkx as nx
import numpy as np
import os
import helpers as myhelpers
import concurrent.futures
import create_gpx_file

max_track_length = 21097


def create_data_model(distance_matrix):
    return {'distance_matrix': distance_matrix}


def process_place(place_name, number_of_vehicles):
    output_file = myhelpers.optimized_route_file(place_name)

    if os.path.isfile(output_file):
        return

    output_file = myhelpers.optimized_route_file(place_name)

    G = ox.graph_from_place(place_name, network_type='all_private', simplify=False)

    pattern = r'Latitude: (\d+\.\d+), Longitude: (\d+\.\d+),.*'

    # read original file content
    with open(myhelpers.guideposts_coordinates_file(place_name)) as f:
        lines = f.readlines()

        print(f"starting with {place_name}")

        gps_coordinates = []

        for line in lines:
            lat = float(re.sub(pattern, r'\1', line))
            lon = float(re.sub(pattern, r'\2', line))
            gps_coordinates.append((lat, lon))

        # Find the nearest nodes to the GPS coordinates
        nodes = ox.distance.nearest_nodes(G, X=[x[1] for x in gps_coordinates], Y=[x[0] for x in gps_coordinates])

        # Calculate the shortest path length between each pair of nodes
        n = len(nodes)
        distance_matrix = np.zeros((n, n), dtype=int)

        lowest_distance = 999999999
        lowest_distance_index = -1

        for i in range(n):
            for j in range(n):
                if i != j:
                    try:
                        distance_matrix[i][j] = int(nx.shortest_path_length(G, nodes[i], nodes[j], weight='length'))
                    except nx.NetworkXNoPath:
                        distance_matrix[i][j] = 999999999
            if sum(distance_matrix[i]) < lowest_distance:
                lowest_distance = sum(distance_matrix[i])
                lowest_distance_index = i

        print(f"trying with {number_of_vehicles} and {lowest_distance_index}")

        # Create and solve the TSP
        data = create_data_model(distance_matrix)
        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), number_of_vehicles, lowest_distance_index)
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data["distance_matrix"][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Distance constraint.
        dimension_name = "Distance"
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            300000,  # vehicle maximum travel distance
            True,  # start cumul to zero
            dimension_name,
        )
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)

        all_optimized_route_coordinates = []

        print(f"Objective: {solution.ObjectiveValue()}")
        max_route_distance = 0
        min_route_distance = 999999999
        for vehicle_id in range(number_of_vehicles):
            index = routing.Start(vehicle_id)
            plan_output = f"Route for vehicle {vehicle_id}:\n"
            route_distance = 0
            optimized_route_nodes = []
            while not routing.IsEnd(index):
                optimized_route_nodes.append(nodes[manager.IndexToNode(index)])
                plan_output += f" {manager.IndexToNode(index)} -> "
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )
            optimized_route_nodes.append(nodes[manager.IndexToNode(index)])

            plan_output += f"{manager.IndexToNode(index)}\n"
            plan_output += f"Distance of the route: {route_distance}m\n"
            print(plan_output)

            max_route_distance = max(route_distance, max_route_distance)
            min_route_distance = min(route_distance, min_route_distance)

            optimized_route_coordinates = []
            for i in range(len(optimized_route_nodes) - 1):
                try:
                    path = nx.shortest_path(G, optimized_route_nodes[i], optimized_route_nodes[i + 1], weight='length')
                    coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in path]
                    optimized_route_coordinates.extend(coords[:-1])
                except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
                    print(
                        f"There is no path between two nodes: {optimized_route_nodes[i]} - {optimized_route_nodes[i + 1]}")

            # Include the coordinates of the last point
            optimized_route_coordinates.append(
                (G.nodes[optimized_route_nodes[-1]]['y'], G.nodes[optimized_route_nodes[-1]]['x']))

            all_optimized_route_coordinates.append(optimized_route_coordinates)

        if max_route_distance > max_track_length and min_route_distance > 1000:
            print(f"Maximum of the route distances: {max_route_distance}m, so let's try again with {number_of_vehicles + 1} vehicles!")
            process_place(place_name, number_of_vehicles + 1)
            return

        print(f"Maximum of the route distances: {max_route_distance}m")

        create_gpx_file.create_gpx_file(all_optimized_route_coordinates, myhelpers.optimized_route_file(place_name))
        print(
            f"Optimized route has been saved to '{myhelpers.optimized_route_file(place_name)}' for {place_name}")


def shortest_paths():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        places = [file_path for file_path in os.listdir(myhelpers.subdirectory) if 'DS_Store' not in file_path]
        for place in places:
            process_place(place, 1)
        # executor.map(process_place, places)

if __name__ == '__main__':
    process_place("Gemeinde Fußach", 1)