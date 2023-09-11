from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import re
import helpers
import calculate_distance_matrix
import osmnx as ox
import networkx as nx
import multiprocessing
import itertools
import gpxpy
import create_gpx_file
from timeit import default_timer as timer

place_name = "Marktgemeinde Lustenau"
max_track_length = 21097

G, distance_matrix = calculate_distance_matrix.calculate_distance_matrix(place_name)


def add_waypoints_to_gpx(gpx_filename: object, waypoints: object, output_gpx_filename: object) -> object:
    gpx_file = open(gpx_filename, 'r')
    gpx_content = gpx_file.read()
    gpx_file.close()

    gpx = gpxpy.parse(gpx_content)

    for lat, lon, name in waypoints:
        waypoint = gpxpy.gpx.GPXWaypoint(latitude=lat, longitude=lon, name=name)
        gpx.waypoints.append(waypoint)

    modified_gpx_file = open(output_gpx_filename, 'w')
    modified_gpx_file.write(gpx.to_xml())


def solve_vrp(starting_points, number_of_vehicles):
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), number_of_vehicles, starting_points,
                                           starting_points)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)

        return distance_matrix[from_node][to_node]

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

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    solution = routing.SolveWithParameters(search_parameters)
    # here we have the solution with ids like [0, 29, 1, 5, 33...]

    all_optimized_route_coordinates = []

    new_waypoints = []

    pattern = r'Latitude: (\d+\.\d+), Longitude: (\d+\.\d+),.*VWW (\d*.\d*)\.*.*\n'

    f = open(helpers.guideposts_coordinates_file(place_name))
    lines = f.readlines()

    for line in lines:
        try:
            lat = float(re.sub(pattern, r'\1', line))
            lon = float(re.sub(pattern, r'\2', line))
            name = re.sub(pattern, r'\3', line)
            new_waypoints.append((lat, lon, name))
        except ValueError:
            pass

    nodes = ox.distance.nearest_nodes(G, X=[x[1] for x in new_waypoints],
                                      Y=[x[0] for x in new_waypoints])

    total_distance = 0
    routes = []
    routes_distance_mapping = []

    for vehicle_id in range(number_of_vehicles):
        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        route = []
        route_distance = 0
        optimized_route_nodes = []
        while not routing.IsEnd(index):
            next_index = solution.Value(routing.NextVar(index))
            total_distance += routing.GetArcCostForVehicle(index, next_index, vehicle_id)
            optimized_route_nodes.append(nodes[manager.IndexToNode(index)])
            route.append(manager.IndexToNode(index))
            plan_output += f" {manager.IndexToNode(index)} -> "
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
        routes.append(route)
        optimized_route_nodes.append(nodes[manager.IndexToNode(index)])

        plan_output += f"{manager.IndexToNode(index)}\n"
        plan_output += f"Distance of the route: {route_distance}m\n"

        optimized_route_coordinates = []
        for i in range(len(optimized_route_nodes) - 1):
            try:
                path = nx.shortest_path(G, optimized_route_nodes[i], optimized_route_nodes[i + 1], weight='length')
                coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in path]
                optimized_route_coordinates.extend(coords[:-1])
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                print(
                    f"There is no path between two nodes: {optimized_route_nodes[i]} - {optimized_route_nodes[i + 1]}")

        # Include the coordinates of the last point
        optimized_route_coordinates.append(
            (G.nodes[optimized_route_nodes[-1]]['y'], G.nodes[optimized_route_nodes[-1]]['x']))

        all_optimized_route_coordinates.append(optimized_route_coordinates)
        routes_distance_mapping.append((route_distance, routes, optimized_route_coordinates))

    return routes_distance_mapping


def parallel_solve_vrp(starting_points_chunk):
    routes_distances_mapping = []

    print(f"number of chunks {len(starting_points_chunk)}")
    i = 0
    for starting_points in starting_points_chunk:
        print(f"before trying {i}/{len(starting_points_chunk)}")
        routes_distances_mapping.append((starting_points_chunk, solve_vrp(starting_points, len(starting_points))))
        print(f"after trying {i}/{len(starting_points_chunk)}")
        i += len(starting_points)

    return routes_distances_mapping


def chunk_data(data, num_chunks):
    avg_len = len(data) // num_chunks
    chunks = [data[i:i + avg_len] for i in range(0, len(data), avg_len)]
    return chunks


if __name__ == '__main__':
    start = timer()
    multiprocessing.set_start_method('fork')

    # create distance matrix for coordinates
    print(f"before calculating distance matrix {timer() - start}")
    # G, distance_matrix = calculate_distance_matrix.calculate_distance_matrix(place_name)
    print(f"after calculating distance matrix {timer() - start}")
    num_locations = len(distance_matrix)
    number_of_vehicles = 0
    solution_found = False

    best_distance = float('inf')
    best_routes = None
    best_starting_points = None

    while not solution_found:
        number_of_vehicles = number_of_vehicles + 1
        starting_point_combinations = list(itertools.combinations(range(num_locations), number_of_vehicles))

        num_cores = multiprocessing.cpu_count() - 2

        if number_of_vehicles == 1:
            chunks = [(0,)]
            results = [parallel_solve_vrp(chunks)]
        else:
            print(f"let's try another one after {timer() - start}")
            chunks = chunk_data(starting_point_combinations, num_cores)

            with multiprocessing.Pool(num_cores) as pool:
                results = pool.map(parallel_solve_vrp, chunks)

        for result in results:
            routes = map(lambda x: x[2], result[0][1])
            distance = sum(map(lambda x: x[0], result[0][1]))

            print(f" {best_distance}")
            if distance < best_distance and all(y < max_track_length for y in map(lambda x: x[0], result[0][1])):
                best_distance = distance
                best_routes = routes

        if number_of_vehicles > 1:
            print(f"=======> {best_distance} ======= {max_track_length}")
        solution_found = best_distance < float('inf')

    new_waypoints = []

    pattern = r'Latitude: (\d+\.\d+), Longitude: (\d+\.\d+),.*VWW (\d*.\d*)\.*.*\n'

    create_gpx_file.create_gpx_file(list(best_routes), helpers.optimized_route_file(place_name))

    enrich_gpx = __import__('03_enrich_gpx')
    gpx_info = __import__('04_gpx-info')
    overlay_hiking_route_with_guideposts = __import__('05_overlay_hiking_route_with_guideposts')

    enrich_gpx.enrich_gpx(place_name)

    overlay_hiking_route_with_guideposts.overlay_hiking_route_with_guideposts(place_name)


    # f = open(helpers.guideposts_coordinates_file(place_name))
    # lines = f.readlines()
    # f.close()
    #
    # for line in lines:
    #     try:
    #         lat = float(re.sub(pattern, r'\1', line))
    #         lon = float(re.sub(pattern, r'\2', line))
    #         name = re.sub(pattern, r'\3', line)
    #         new_waypoints.append((lat, lon, name))
    #     except ValueError:
    #         pass
    #
    # add_waypoints_to_gpx(f"/Users/stefan/Downloads/{place_name}.gpx", new_waypoints,
    #                      f"/Users/stefan/Downloads/{place_name}_2.gpx")
    # print(list(best_routes))
    print("without GPU:", timer() - start)
    print("---")
