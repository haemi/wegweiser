import gpxpy.gpx
import os
import helpers as myhelpers
import re
import gpxpy


def add_waypoints_to_gpx(gpx_filename, waypoints, output_gpx_filename):
    with open(gpx_filename, 'r') as gpx_file:
        gpx_content = gpx_file.read()

    gpx = gpxpy.parse(gpx_content)

    for lat, lon, name in waypoints:
        waypoint = gpxpy.gpx.GPXWaypoint(latitude=lat, longitude=lon, name=name)
        gpx.waypoints.append(waypoint)

    with open(output_gpx_filename, 'w') as modified_gpx_file:
        modified_gpx_file.write(gpx.to_xml())


def overlay_hiking_route_with_guideposts(file_path):
    place_name = file_path
    output_gpx_filename = myhelpers.final_hiking_guideposts_file(place_name)

    if os.path.isfile(output_gpx_filename):
        return

    input_gpx_filename = myhelpers.optimized_enrich_file(place_name)

    new_waypoints = []

    pattern = r'Latitude: (\d+\.\d+), Longitude: (\d+\.\d+),.*VWW (\d*.\d*)\.*.*\n'

    # read original file content
    with open(myhelpers.guideposts_coordinates_file(place_name)) as f:
        lines = f.readlines()

        for line in lines:
            try:
                lat = float(re.sub(pattern, r'\1', line))
                lon = float(re.sub(pattern, r'\2', line))
                name = re.sub(pattern, r'\3', line)
                new_waypoints.append((lat, lon, name))
            except ValueError:
                pass

    add_waypoints_to_gpx(input_gpx_filename, new_waypoints, output_gpx_filename)

    print(f"hiking route created for {output_gpx_filename}")
