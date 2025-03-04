import numpy as np
import osmnx as ox
import json5
import matplotlib.pyplot as plt
import contextily as ctx
from geopy.distance import geodesic

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
    sw_lat_lng = geodesic(meters=height_m).destination(
        (ne_lat, ne_lng), 180
    )  # 180° = due south
    sw_lat = sw_lat_lng.latitude  # Extract latitude

    # Move west by width_m (longitude change)
    sw_lat_lng = geodesic(meters=width_m).destination(
        (sw_lat, ne_lng), 270
    )  # 270° = due west
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
sw_lat, sw_lng = calculate_sw_coords(
    corners["ne"]["lat"], corners["ne"]["lng"], aspect_ratio, width_m
)
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

custom_filter = '["highway"~"motorway|motorway_link|trunk"]'

# Download the road network from OSM
print("Downloading the road network from OSM...")
graph = ox.graph_from_bbox(
    bbox,
    custom_filter=custom_filter,
    simplify=True,
)
edges = ox.graph_to_gdfs(graph, nodes=False, edges=True)
# Convert to Web Mercator (needed for Mapbox tiles)
edges = edges.to_crs(epsg=3857)

# Create a figure
fig, ax = plt.subplots(figsize=fig_size, dpi=dpi)

MAPBOX_STYLE = f"https://api.mapbox.com/styles/v1/{map_id}/tiles/{{z}}/{{x}}/{{y}}{{r}}?access_token={access_token}"

edges.plot(ax=ax, edgecolor="white", linewidth=1)
ctx.add_basemap(ax, source=MAPBOX_STYLE, alpha=1, zoom=10)

# Remove axis labels for a clean look
ax.set_xticks([])
ax.set_yticks([])
ax.set_frame_on(False)
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
# ax.set_aspect("equal")
# ax.set_aspect(np.cos(np.radians(corners["sw"]["lat"])))  # Fix latitude distortion
ax.set_aspect(0.974)

fig.savefig("OSM_graph.png")
