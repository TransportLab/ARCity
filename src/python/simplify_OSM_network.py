# import osmnx as ox
import geopandas as gpd
from centerline.geometry import Centerline


def buffer_to_centerline(edges, buffer_width=10):
    edges["buffer"] = edges.geometry.buffer(buffer_width)
    buffer_gdf = edges.set_geometry("buffer")
    merged_buffers = buffer_gdf.dissolve().explode(index_parts=False)

    # Extract centerlines without negative buffer
    centerlines = merged_buffers.geometry.apply(lambda geom: Centerline(geom))

    # Convert result to GeoDataFrame
    centerlines_gdf = gpd.GeoDataFrame(geometry=centerlines.explode(index_parts=False))

    return centerlines_gdf


# def buffer_to_centerline(edges, buffer_width=10):
#     # Convert graph edges to GeoDataFrame
#     # edges = ox.graph_to_gdfs(G, nodes=False)

#     # Buffer edges slightly (adjust width as needed)
#     edges["buffer"] = edges.geometry.buffer(buffer_width)  # buffer ~10 m each side

#     # Create GeoDataFrame explicitly using the buffered geometries
#     buffer_gdf = edges.set_geometry("buffer")

#     # Now dissolve
#     merged_buffers = buffer_gdf.dissolve()

#     # Get simplified centerlines
#     centerlines = merged_buffers.buffer(-1).simplify(5).explode(ignore_index=True)
#     centerlines_gdf = gpd.GeoDataFrame(geometry=centerlines)

#     return centerlines_gdf


def merge_two_edge_nodes(G):
    """
    Merges edges where exactly two edges meet at a node.

    Returns:
        A new NetworkX MultiDiGraph with merged edges.
    """
    G = G.copy()
    nodes_to_remove = []

    for node in list(G.nodes):
        predecessors = list(G.predecessors(node))
        successors = list(G.successors(node))

        # Only merge if exactly one predecessor and one successor
        if len(predecessors) == 1 and len(successors) == 1:
            u = predecessors[0]
            v = successors[0]

            # Ensure both edges exist
            if G.has_edge(u, node) and G.has_edge(node, v):
                edge1 = G[u][node][0]
                edge2 = G[node][v][0]

                # Merge geometries
                new_geometry = LineString(list(edge1["geometry"].coords) + list(edge2["geometry"].coords)[1:])

                # Merge attributes, preserving road name and highway type
                new_attrs = {
                    "name": edge1.get("name", edge2.get("name", None)),
                    "highway": edge1.get("highway", edge2.get("highway", None)),
                    "geometry": new_geometry,
                }

                # Add the new merged edge
                G.add_edge(u, v, **new_attrs)

                # Mark node and old edges for removal
                nodes_to_remove.append(node)

    # Remove merged nodes
    for node in nodes_to_remove:
        G.remove_node(node)

    return G
