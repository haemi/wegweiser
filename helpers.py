subdirectory = 'data'


def area_directory(area_name):
    return subdirectory + '/' + area_name


def guideposts_coordinates_file(area_name):
    return area_directory(area_name) + '/' + 'guideposts_coordinates.txt'


def optimized_route_file(area_name):
    return area_directory(area_name) + '/' + 'optimized_route.gpx'


def optimized_enrich_file(area_name):
    return 'data' + '/' + area_name + '/' + 'optimized_route_enriched.gpx'


def final_hiking_guideposts_file(area_name):
    return 'data' + '/' + area_name + '/' + area_name + '_final.gpx'
