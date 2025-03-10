import numpy as np
import osmnx as ox
import json5
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import geopandas as gpd
from shapely.geometry import LineString
from .simplify_OSM_network import merge_two_edge_nodes

ox.settings.log_console = True
ox.settings.max_query_area_size = 25000000000


def calculate_sw_coords(ne_lat, ne_lng, aspect_ratio, width_m):
    """
    Calculate the southwest (SW) latitude and longitude from the given northeast (NE) point,
    aspect ratio, and width in meters using accurate geodesic calculations.

    Parameters:
        ne_lat (float): Latitude of the northeast point.
        ne_lng (float): Longitude of the northeast point.
        aspect_ratio (float): Width / Height ratio.
        width_m (float): Width of the region in meters.

    Returns:
        (float, float): Southwest latitude and longitude.
    """
    # Calculate height from aspect ratio
    height_m = width_m / aspect_ratio

    # Move south by height_m (latitude change)
    sw_lat_lng = geodesic(meters=height_m).destination((ne_lat, ne_lng), 180)  # 180° = due south
    sw_lat = sw_lat_lng.latitude  # Extract latitude

    # Move west by width_m (longitude change)
    sw_lat_lng = geodesic(meters=width_m).destination((sw_lat, ne_lng), 270)  # 270° = due west
    sw_lng = sw_lat_lng.longitude  # Extract longitude

    return sw_lat, sw_lng


# Mapbox API credentials
with open("keys.json5") as f:
    keys = json5.load(f)
    access_token = keys["mapbox"]["token"]
    map_id = keys["mapbox"]["style"]

# screen_resolution = (3840, 2160)
screen_resolution = (2560, 1440)
dpi = 300
fig_size = (screen_resolution[0] / dpi, screen_resolution[1] / dpi)

aspect_ratio = screen_resolution[0] / screen_resolution[1]

# image_width = 74  # bricks
# image_height = int(image_width / aspect_ratio)
image_width = screen_resolution[0]
image_height = screen_resolution[1]

corners = {
    "ne": {"lat": -33.575081595647845, "lng": 151.3686975828967},
    "sw": {"lat": -34.107634411327636, "lng": 150.10678868286178},  # dummy values
}

width_m = 90000  # 90 km
sw_lat, sw_lng = calculate_sw_coords(corners["ne"]["lat"], corners["ne"]["lng"], aspect_ratio, width_m)
# print(f"SW Latitude: {sw_lat}, SW Longitude: {sw_lng}")
corners["sw"]["lat"] = sw_lat
corners["sw"]["lng"] = sw_lng

print(corners)

bbox = (
    corners["sw"]["lng"],
    corners["sw"]["lat"],
    corners["ne"]["lng"],
    corners["ne"]["lat"],
)

custom_filter = '["highway"~"motorway|trunk"]'

# Download the road network from OSM
print("Downloading the road network from OSM...")
graph = ox.graph_from_bbox(
    bbox,
    custom_filter=custom_filter,
    simplify=False,
)
G_proj = ox.projection.project_graph(graph)

# graph = ox.project_graph(graph, to_crs="EPSG:3857")  # Web Mercator projection
graph = ox.simplification.consolidate_intersections(G_proj, rebuild_graph=True, tolerance=20, dead_ends=True)
print(len(graph))
graph = ox.simplification.simplify_graph(graph)
print(len(graph))
for i in range(5):
    graph = merge_two_edge_nodes(graph)
    print(len(graph))

edges = ox.graph_to_gdfs(graph, nodes=False, edges=True)
# Convert to Web Mercator (needed for Mapbox tiles)
edges = edges.to_crs(epsg=3857)


# Load SA3 boundaries for Sydney using an open dataset
# Downloaded from: https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files

sa3_areas = gpd.read_file("/Users/bmar5496/Downloads/SA3_2021_AUST_SHP_GDA2020/SA3_2021_AUST_GDA2020.shp")

# Ensure both layers have the same CRS
sa3_areas = sa3_areas.to_crs(edges.crs)

# Find intersections of SA3 areas with the road network
sa3_intersections = gpd.overlay(sa3_areas, edges, how="intersection", keep_geom_type=False)

print(len(sa3_intersections))
# sa3_intersections.to_file("sa3_road_intersections.geojson", driver="GeoJSON")

# Plot each intersection as a random color
fig, ax = plt.subplots(figsize=fig_size, dpi=dpi)

# for i in range(len(sa3_intersections)):
#     sa3_intersections.iloc[[i]].plot(ax=ax, color=np.random.rand(3), linewidth=1)
for i in range(len(edges)):
    edges.iloc[[i]].plot(ax=ax, color=np.random.rand(3), linewidth=1)

plt.savefig("sa3_road_intersections.png", dpi=dpi)
