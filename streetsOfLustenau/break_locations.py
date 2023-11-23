import gpxpy.gpx
import osmnx as ox
import networkx as nx
import gpxpy.gpx
from geopy.geocoders import Nominatim
from pprint import pprint

# Step 1: Create a Street Network Graph
place_name = "Lustenau, Vorarlberg, Austria"
G = ox.graph_from_place(place_name, network_type='drive', simplify=False)
lustenau_nodes_df, lustenau_edges_df = ox.graph_to_gdfs(G)

gpx_file = open('modified-track-Lustenau, Vorarlberg, Austria.gpx', 'r')

gpx = gpxpy.parse(gpx_file)
geolocator = Nominatim(user_agent="StefanWalknerLustenauMarathon")

for waypoint in gpx.waypoints:
    pprint(f'waypoint {waypoint.name} -> ({waypoint.latitude},{waypoint.longitude})')
    print(f'waypoint {waypoint.name} -> ({waypoint.latitude},{waypoint.longitude})')
    # nodes = ox.distance.nearest_nodes(G, X=[waypoint.latitude], Y=[waypoint.longitude])
    # node_id = nodes[0]
    # node_latlon = G.nodes[node_id]
    # latitude, longitude = node_latlon['y'], node_latlon['x']
    location = geolocator.reverse((waypoint.latitude, waypoint.longitude))

    pprint(f"The address of node {waypoint} is: {location}")
    print(f"The address of node {waypoint} is: {location}")
