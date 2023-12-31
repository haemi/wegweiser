import osmnx as ox
import re
import helpers
from timeit import default_timer as timer


def nearest_gps_coordinates_for_guidepoints(place_name):

    pattern = r'Latitude: (\d+\.\d+), Longitude: (\d+\.\d+),.*VWW (\d*.\d*)\.*.*\n'

    gps_coordinates = []

    # read original file content
    with open(helpers.guideposts_coordinates_file(place_name)) as f:
        lines = f.readlines()

        for line in lines:
            try:
                lat = float(re.sub(pattern, r'\1', line))
                lon = float(re.sub(pattern, r'\2', line))
                gps_coordinates.append((lat, lon))
            except ValueError:
                pass

    min_lat = min(map(lambda x: x[0], gps_coordinates)) * 0.99
    max_lat = max(map(lambda x: x[0], gps_coordinates)) * 1.01
    min_lon = min(map(lambda x: x[1], gps_coordinates)) * 0.99
    max_lon = max(map(lambda x: x[1], gps_coordinates)) * 1.01

    start = timer()
    print(f"before {start}")
    G = ox.graph_from_bbox(min_lat, max_lat, min_lon, max_lon, network_type='all_private', simplify=False)
    print(f"after {timer() - start}")
    # G = ox.graph_from_place(place_name, network_type='all_private', simplify=False)

    return G, ox.distance.nearest_nodes(G, X=[x[1] for x in gps_coordinates], Y=[x[0] for x in gps_coordinates])
