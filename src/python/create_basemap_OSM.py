import numpy as np
import osmnx as ox
import json5
import matplotlib.pyplot as plt
import contextily as ctx
from geopy.distance import geodesic
import scipy.ndimage
from simplify_OSM_network import buffer_to_centerline, merge_two_edge_nodes
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
import scipy.signal

ox.settings.log_console = True
ox.settings.max_query_area_size = 25000000000


def calculate_defaults(p):
    p["fig_size"] = (p["screen_resolution"][0] / p["dpi"], p["screen_resolution"][1] / p["dpi"])

    p["aspect_ratio"] = p["screen_resolution"][0] / p["screen_resolution"][1]

    sw_lat, sw_lng = calculate_sw_coords(
        p["map"]["ne"]["lat"],
        p["map"]["ne"]["lng"],
        p["aspect_ratio"],
        p["map"]["width_m"],
    )

    # print(f"SW Latitude: {sw_lat}, SW Longitude: {sw_lng}")
    p["map"]["sw"]["lat"] = sw_lat
    p["map"]["sw"]["lng"] = sw_lng

    return p


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


def draw_image(keys, p, edges):

    MAPBOX_STYLE = f"https://api.mapbox.com/styles/v1/{keys['mapbox']['style']}/tiles/{{z}}/{{x}}/{{y}}{{r}}?access_token={keys['mapbox']['token']}"

    # edges.plot(ax=ax, edgecolor="white", linewidth=p["line_width"])
    colours = ["red", "green", "orange"]
    for i in range(len(edges)):
        edges.iloc[[i]].plot(ax=ax, color=colours[np.random.randint(3)], linewidth=1)

    ctx.add_basemap(ax, source=MAPBOX_STYLE, alpha=1, zoom=p["map"]["zoom"])

    # Remove axis labels for a clean look
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    # ax.set_aspect("equal")
    # ax.set_aspect(np.cos(np.radians(p["map"]["sw"]["lat"])))  # Fix latitude distortion
    ax.set_aspect(0.974)  # HACK: Fix latitude distortion

    # fig.savefig("OSM.png")
    canvas.draw()  # Update the figure

    # Repeat update every 1000 ms (1 second)
    root.after(1000, draw_image, keys, p, edges)


def gaussian_kernel(size: int, sigma: float) -> np.ndarray:
    """Generate a 2D Gaussian kernel using only NumPy."""
    ax = np.arange(-(size // 2), size // 2 + 1)
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx**2 + yy**2) / (2 * sigma**2))
    kernel /= kernel.sum()  # Normalize so sum equals 1
    return kernel


def draw_with_convolved_traffic(keys, p, edges):
    plt.figure(1)
    fg = plt.imread("fg_mask.png")
    fg = fg[:, :, 0]  # Extract one channel
    fg = 1-fg  # Invert mask
    fg[fg == 0] = np.nan
    bg = plt.imread("bg_mask.png")
    try:
        heights = requests.get("http://localhost:5000/get_depths_from_server").json()
        heights = np.array(heights).reshape((p["H"],p["W"])).T
        print('GOT HEIGHTS FROM SERVER')
        print(heights.min(), heights.max())

        #lego = heights > 0

        kernel = gaussian_kernel(5, 1)

        #traffic = scipy.signal.convolve2d(heights, kernel, mode="same", boundary="wrap")
        # zoom to same size as fg
        size_ratio = fg.shape[0]/p["W"], fg.shape[1]/p["H"]
        #traffic_scaled = scipy.ndimage.zoom(traffic, size_ratio)
        #fg = traffic_scaled*fg  # Apply mask

        heights_scaled = scipy.ndimage.zoom(heights, size_ratio)
        fg *= heights_scaled

        plt.imshow(bg)
        plt.imshow(fg, cmap="hot", alpha=0.5)
       # plt.imshow(heights_scaled)

        # Remove axis labels for a clean look
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        # ax.set_aspect("equal")
        # ax.set_aspect(np.cos(np.radians(p["map"]["sw"]["lat"])))  # Fix latitude distortion
        ax.set_aspect(0.974)  # HACK: Fix latitude distortion

        canvas.draw()  # Update the figure
    except Exception as e:
        print('Got an exception when receiving heights from server:')
        print(e)
    # Repeat update every 1000 ms (1 second)
    root.after(1000, draw_with_convolved_traffic, keys, p, edges)


def get_map(p):
    bbox = (
        p["map"]["sw"]["lng"],
        p["map"]["sw"]["lat"],
        p["map"]["ne"]["lng"],
        p["map"]["ne"]["lat"],
    )

    # Download the road network from OSM
    print("Downloading the road network from OSM...")
    graph = ox.graph_from_bbox(
        bbox,
        custom_filter=p["osm_filter"],
        simplify=True,
    )

    edges = ox.graph_to_gdfs(graph, nodes=False, edges=True)
    # Convert to Web Mercator (needed for Mapbox tiles)
    edges = edges.to_crs(epsg=3857)

    # Remove ramps
    edges = edges[~edges["name"].astype(str).str.contains("ramp", case=False, na=False)]

    # Buffer edges slightly (adjust width as needed)
    # edges = buffer_to_centerline(edges, buffer_width=10)

    return edges

def make_mask(p, edges):
    fig = plt.figure(2, figsize=p["fig_size"], dpi=p["dpi"])
    ax = plt.subplot(111)
    MAPBOX_STYLE = f"https://api.mapbox.com/styles/v1/{keys['mapbox']['style']}/tiles/{{z}}/{{x}}/{{y}}{{r}}?access_token={keys['mapbox']['token']}"

    edges.plot(ax=ax, edgecolor="white", linewidth=p["line_width"])
    #colours = ["red", "green", "orange"]
    #for i in range(len(edges)):
    #    edges.iloc[[i]].plot(ax=ax, color=colours[np.random.randint(3)], linewidth=1)

    ctx.add_basemap(ax, source=MAPBOX_STYLE, alpha=1, zoom=p["map"]["zoom"])

    # Remove axis labels for a clean look
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    # ax.set_aspect("equal")
    # ax.set_aspect(np.cos(np.radians(p["map"]["sw"]["lat"])))  # Fix latitude distortion
    ax.set_aspect(0.974)  # HACK: Fix latitude distortion

    # fig.savefig("OSM.png")
    
    plt.savefig("bg_mask.png", transparent=False)

    plt.clf()
    ax = plt.subplot(111)

    #ctx.add_basemap(ax, source=MAPBOX_STYLE, alpha=0, zoom=p["map"]["zoom"])
    edges.plot(ax=ax, edgecolor="black", linewidth=p["line_width"])

    # Remove axis labels for a clean look
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_frame_on(False)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    # ax.set_aspect("equal")
    # ax.set_aspect(np.cos(np.radians(p["map"]["sw"]["lat"])))  # Fix latitude distortion
    ax.set_aspect(0.974)  # HACK: Fix latitude distortion

    # fig.savefig("OSM.png")
    
    plt.savefig("fg_mask.png", transparent=False)





if __name__ == "__main__":
    # Mapbox API credentials
    with open("keys.json5") as f:
        keys = json5.load(f)

    with open("params.json5") as f:
        p = json5.load(f)

    p = calculate_defaults(p)

    edges = get_map(p)

    # Create root window
    root = tk.Tk()
    root.attributes("-fullscreen", True)  # Fullscreen mode
    root.configure(bg="black")
    root.bind("<Escape>", lambda e: root.destroy())  # Exit on ESC

    # Create Matplotlib figure
    fig = plt.figure(1, figsize=p["fig_size"], dpi=p["dpi"])
    ax = plt.subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Pack canvas and set background
    widget = canvas.get_tk_widget()
    widget.pack(fill=tk.BOTH, expand=True)
    widget.configure(bg="black", highlightthickness=0)

    make_mask(p, edges)

    # draw_image(keys, p, edges)

    draw_with_convolved_traffic(keys, p, edges)
    root.mainloop()
