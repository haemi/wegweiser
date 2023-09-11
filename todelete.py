import json
import gpxpy
import uuid

# Opening JSON file
f = open('/Users/stefan/Downloads/lustenau-graphhopper.json')

# returns JSON object as
# a dictionary
data = json.load(f)

# Iterating through the json
# list
gpx = gpxpy.gpx.GPX()

for i in data['solution']['routes']:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx_track.name = str(uuid.uuid4())
    gpx.tracks.append(gpx_track)

    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    optimized_route_coordinates = []

    optimized_route_notes = i['activities']

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

    for activity in i['activities']:
        address = activity['address']
        print(activity)

        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(address['lat'], address['lon']))

with open("/Users/stefan/Downloads/lustenau.gpx", 'w') as f:
    f.write(gpx.to_xml())

# Closing file
f.close()
