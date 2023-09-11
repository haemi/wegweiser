import time

# get the start time
st = time.time()
sum_x = 0

fetch_guideposts = __import__('01_fetch_guideposts')
shortest_paths = __import__('02_shortest_paths')
enrich_gpx = __import__('03_enrich_gpx')
gpx_info = __import__('04_gpx-info')
overlay_hiking_route_with_guideposts = __import__('05_overlay_hiking_route_with_guideposts')

print(f'current time (started): {time.time() - st}')

fetch_guideposts.fetch_guideposts()

print(f'current time (fetched guideposts): {time.time() - st}')

shortest_paths.shortest_paths()

print(f'current time (found shortest paths): {time.time() - st}')

enrich_gpx.enrich_gpx()

print(f'current time (finished enriching gpx): {time.time() - st}')

# gpx_info.gpx_info()

print(f'current time (printed out gpx info): {time.time() - st}')

overlay_hiking_route_with_guideposts.overlay_hiking_route_with_guideposts()

print(f'current time (overlayed hiking routes with guideposts): {time.time() - st}')
