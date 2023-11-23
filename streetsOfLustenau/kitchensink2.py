"""
now trying to calculate route from first to last waypoint of each linepoint
"""
import gpxpy.gpx
import osmnx as ox
import networkx as nx
import gpxpy.gpx

# Step 1: Create a Street Network Graph
place_name = "Lustenau, Vorarlberg, Austria"
custom_filter = '["highway"!~"motorway|motorway_link"]["access"!~"private"]'

# 4 = {str} 'unclassified'

# Create the graph using the custom filter
# G = ox.graph_from_place(place_name, network_type='drive', custom_filter=custom_filter, simplify=False)
G = ox.graph_from_place(place_name, network_type='drive', simplify=False)
G_proj = G.to_undirected()
G = G_proj
stats = ox.basic_stats(G_proj)

nodes_to_add = []
edges_to_add = []

for u, v, k, data in G.edges(keys=True, data=True):
    sidewalk = data.get('sidewalk', 'unknown')
    foot = data.get('foot', 'unknown')
    highway = data.get('highway', 'unknown')
    maxspeed = int(data.get('maxspeed', '0'))
    length = int(data.get('maxspeed', '0'))
    if length < 100:
        continue

    avg_x = (G.nodes[u]['x'] + G.nodes[v]['x']) / 2
    avg_y = (G.nodes[u]['y'] + G.nodes[v]['y']) / 2
    end = G.nodes[v]
    nearest_node = ox.nearest_nodes(G, avg_x, avg_y)
    if nearest_node != u and nearest_node != v:
        nodes_to_add.append(nearest_node)
        if nearest_node != u:
            edges_to_add.append((u, nearest_node, data))
        else:
            edges_to_add.append((nearest_node, v, data))


for node_to_add in nodes_to_add:
    G_proj.add_node(node_to_add)

for edge_to_add in edges_to_add:
    G_proj.add_edge(edge_to_add[0], edge_to_add[1], **{**edge_to_add[2]})

lustenau_nodes_df, lustenau_edges_df = ox.graph_to_gdfs(G_proj)

foo = lustenau_edges_df[lustenau_edges_df['highway'].isnull()]

motorway_df = lustenau_edges_df[
    lustenau_edges_df['highway'].str.contains("motor")]

G_proj.remove_edges_from(motorway_df.highway.keys())

ox.config(use_cache=True, log_console=True)

isolated_nodes = list(nx.isolates(G_proj))

# Remove isolated nodes
G_proj.remove_nodes_from(isolated_nodes)

isolated_nodes = list(nx.isolates(G_proj))

i = 0

while not nx.is_connected(G_proj):

    components = list(nx.connected_components(G))
    print(f"we have {len(components)} components")

    # Function to find the nearest nodes between two components
    def calculate_geographic_distance(G, node1, node2):
        point1 = G.nodes[node1]['y'], G.nodes[node1]['x']
        point2 = G.nodes[node2]['y'], G.nodes[node2]['x']
        return ox.distance.great_circle_vec(*point1, *point2)


    # Connect each component to its nearest component
    for comp1 in components:
        print("comp 1 oben")
        nearest_component = None
        nearest_nodes = None
        min_distance = float('inf')
        adding_from = []

        for comp2 in components:
            if comp1 is not comp2:
                for node1 in comp1:
                    for node2 in comp2:
                        distance = calculate_geographic_distance(G_proj, node1, node2)
                        if distance < min_distance:
                            min_distance = distance
                            adding_from = [len(comp1), len(comp2)]
                            nearest_nodes = (node1, node2)
            else:
                print("comparing the same")

        print("we have a nearest node")
        # Add an edge between the nearest nodes of the nearest components
        if nearest_nodes:
            print(f"adding nodes {adding_from}")
            G_proj.add_edge(*nearest_nodes, length=min_distance)

print(nx.is_connected(G_proj))
print("Starting with TSP")

tsp_path = nx.approximation.traveling_salesman_problem(G_proj, cycle=False)

waypoints = []

for index, node in enumerate(tsp_path):
    first = tsp_path[index]
    waypoints.append(
        gpxpy.gpx.GPXWaypoint(latitude=G_proj.nodes[first]['x'], longitude=G_proj.nodes[first]['y'],
                              name=""))

gpx = gpxpy.gpx.GPX()

# Create first track in our GPX:
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)

# Create first segment in our GPX track:
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

for waypoint in waypoints:
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(waypoint.longitude, waypoint.latitude))

with open(f"unmodified-track-{place_name}.gpx", "w") as mod_file:
    mod_file.write(gpx.to_xml())


def add_waypoints_to_gpx(file_path, distance_interval_km):
    # Load GPX file
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    yard = 1

    for track in gpx.tracks:
        for segment in track.segments:
            total_distance = 0
            previous_point = None
            for pointIndex, point in enumerate(segment.points):
                if previous_point is not None:
                    # Calculate distance from the previous point
                    total_distance += point.distance_2d(previous_point)

                    # Check if the distance interval is reached or exceeded
                    if total_distance >= distance_interval_km * 1000:  # convert km to meters
                        # Add a new waypoint
                        waypoint = gpxpy.gpx.GPXWaypoint(latitude=point.latitude, longitude=point.longitude, name=f"{yard}")
                        gpx.waypoints.append(waypoint)

                        # Reset the total distance
                        total_distance = 0
                        yard += 1

                previous_point = point

    # Save the modified GPX file
    with open(f"modified-track-{place_name}.gpx", "w") as mod_file:
        mod_file.write(gpx.to_xml())


# Path to your GPX file
gpx_file_path = f"unmodified-track-{place_name}.gpx"

# Interval distance in kilometers
kilometers_per_mile = 1.609344
interval_distance_km = 100 * kilometers_per_mile / 24

add_waypoints_to_gpx(gpx_file_path, interval_distance_km)


# get mid point of linepoint coordinates

# check if midpoint is in gpx
