import gpxpy
import uuid


def create_gpx_file(coordinates_tracks, filename):
    gpx = gpxpy.gpx.GPX()

    for coordinates in coordinates_tracks:
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx_track.name = str(uuid.uuid4())
        gpx.tracks.append(gpx_track)
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        for coord in coordinates:
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(coord[0], coord[1]))

    with open(filename, 'w') as f:
        f.write(gpx.to_xml())
