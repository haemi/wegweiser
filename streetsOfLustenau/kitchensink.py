"""
kind of working, but streets are interrupted
"""

import osmnx as ox
import networkx as nx
from itertools import combinations
import shapely
import gpxpy.gpx

# Step 1: Create a Street Network Graph
place_name = "Lustenau, Vorarlberg, Austria"
G = ox.graph_from_place(place_name, network_type='drive', simplify=False)
G_proj = G.to_undirected()
stats = ox.basic_stats(G_proj)

lustenau_nodes_df, lustenau_edges_df = ox.graph_to_gdfs(G_proj)

def f(frame):
    xy = frame.geometry.xy
    longs = xy[0].tolist()
    lats = xy[1].tolist()
    return [list(z) for z in zip(lats, longs)]


trying_index = lustenau_edges_df.index
lustenau_edges_df.loc[trying_index, 'coords'] = lustenau_edges_df.loc[trying_index].apply(f, axis=1)

tsp_path = nx.approximation.traveling_salesman_problem(G_proj, cycle=False)

print(f"=>>>>>>>>>>>>>>< after tsp")

waypoints = []

for index, node in enumerate(tsp_path):
    first = node
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

print(gpx.to_xml())
