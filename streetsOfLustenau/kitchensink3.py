import osmnx as ox
import networkx as nx
import gpxpy.gpx


place_name = "Röns, Vorarlberg, Austria"
custom_filter = '["highway"!~"motorway|motorway_link"]["access"!~"private"]'

G = ox.graph_from_place(place_name, network_type='drive', simplify=False)
G = G.to_undirected()

# Step 1: Create a new graph where each edge in G is a node
edge_graph = nx.Graph()
edge_map = {}  # Map to keep track of edge to new node mapping
for i, edge in enumerate(G.edges()):
    # Sort the tuple to handle undirected nature and ensure uniqueness
    sorted_edge = tuple(sorted(edge))
    if sorted_edge not in edge_map:
        edge_map[sorted_edge] = i
        edge_graph.add_node(i)

# Step 2: Add edges between these new nodes
for edge1 in edge_graph.nodes():
    for edge2 in edge_graph.nodes():
        if edge1 != edge2:
            # Check if original edges have a node in common
            original_edge1 = next(key for key, value in edge_map.items() if value == edge1)
            original_edge2 = next(key for key, value in edge_map.items() if value == edge2)
            if set(original_edge1).intersection(set(original_edge2)):
                edge_graph.add_edge(edge1, edge2)

# Step 3: Solve the TSP on the transformed graph
# Since the graph is now significantly different, use a TSP solver like Christofides
tsp_solution = nx.approximation.traveling_salesman_problem(edge_graph, cycle=True)


# Step 4: Map the TSP solution back to the original graph
original_graph_solution = [next(key for key, value in edge_map.items() if value == node) for node in tsp_solution]

print(original_graph_solution)
flattened = [item for sublist in original_graph_solution for item in sublist]
tsp_path = flattened

waypoints = []

for index, node in enumerate(tsp_path):
    first = tsp_path[index]
    waypoints.append(
        gpxpy.gpx.GPXWaypoint(latitude=G.nodes[first]['x'], longitude=G.nodes[first]['y'],
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

with open(f"111unmodified-track-{place_name}.gpx", "w") as mod_file:
    mod_file.write(gpx.to_xml())

#
# def add_waypoints_to_gpx(file_path, distance_interval_km):
#     # Load GPX file
#     with open(file_path, 'r') as gpx_file:
#         gpx = gpxpy.parse(gpx_file)
#
#     yard = 1
#
#     for track in gpx.tracks:
#         for segment in track.segments:
#             total_distance = 0
#             previous_point = None
#             for pointIndex, point in enumerate(segment.points):
#                 if previous_point is not None:
#                     # Calculate distance from the previous point
#                     total_distance += point.distance_2d(previous_point)
#
#                     # Check if the distance interval is reached or exceeded
#                     if total_distance >= distance_interval_km * 1000:  # convert km to meters
#                         # Add a new waypoint
#                         waypoint = gpxpy.gpx.GPXWaypoint(latitude=point.latitude, longitude=point.longitude, name=f"{yard}")
#                         gpx.waypoints.append(waypoint)
#
#                         # Reset the total distance
#                         total_distance = 0
#                         yard += 1
#
#                 previous_point = point
#
#     # Save the modified GPX file
#     with open(f"modified-track-{place_name}.gpx", "w") as mod_file:
#         mod_file.write(gpx.to_xml())
#
#
# # Path to your GPX file
# gpx_file_path = f"unmodified-track-{place_name}.gpx"
#
# # Interval distance in kilometers
# kilometers_per_mile = 1.609344
# interval_distance_km = 100 * kilometers_per_mile / 24
#
# add_waypoints_to_gpx(gpx_file_path, interval_distance_km)