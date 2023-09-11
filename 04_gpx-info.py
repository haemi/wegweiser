from math import radians, sin, cos, sqrt, atan2
import gpxpy
import gpxpy.gpx
import os
import helpers


def read_gpx_file(file_path):
    with open(file_path, 'r') as f:
        gpx = gpxpy.parse(f)
    return gpx


def extract_track_points(gpx_filename):
    with open(gpx_filename, 'r') as gpx_file:
        gpx_content = gpx_file.read()

    gpx = gpxpy.parse(gpx_content)

    track_points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                track_points.append({
                    'lat': point.latitude,
                    'lon': point.longitude,
                    'ele': point.elevation
                })

    return track_points


def extract_elevation_gain_loss(track_points):
    elevation_gain = 0
    elevation_loss = 0

    for i in range(len(track_points) - 1):
        ele_diff = track_points[i + 1]['ele'] - track_points[i]['ele']
        if ele_diff > 0:
            elevation_gain += ele_diff
        elif ele_diff < 0:
            elevation_loss += abs(ele_diff)

    return elevation_gain, elevation_loss


def haversine_distance(point1, point2):
    # Radius of the Earth in meters
    R = 6371000

    lat1, lon1 = map(radians, point1)
    lat2, lon2 = map(radians, point2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


def calculate_track_length(track_points):
    total_distance = 0

    for i in range(len(track_points) - 1):
        point1 = (float(track_points[i]['lat']), float(track_points[i]['lon']))
        point2 = (float(track_points[i + 1]['lat']), float(track_points[i + 1]['lon']))
        total_distance += haversine_distance(point1, point2)

    return total_distance


def gpx_info():
    for file_path in os.listdir('data'):
        if 'DS_Store' in file_path:
            continue

        # Fetch the road network
        place_name = file_path

        gpx_file_path = helpers.optimized_enrich_file(place_name)

        gpx = read_gpx_file(gpx_file_path)
        uphill_down = gpx.get_uphill_downhill()

        # Sample track points from the provided GPX data
        track_points = extract_track_points(gpx_file_path)

        track_length = calculate_track_length(track_points)
        elevation_gain = uphill_down.uphill.real
        elevation_loss = uphill_down.downhill.real
        print(f"{place_name}, {track_length}, {elevation_gain}, {elevation_loss}")
