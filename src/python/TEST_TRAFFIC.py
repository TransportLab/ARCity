import networkx as nx
import random
import matplotlib.pyplot as plt
from collections import defaultdict

"""
This script generates a traffic flow simulation on a 2D Cartesian grid where buildings (nodes) are connected by roads (edges).
The goal is to visualize the traffic flow between these buildings, with the width of the roads proportional to the amount of traffic they carry.

### Explanation of the Code

1. **Grid Setup:**
   - We begin by defining a grid of a specified size (e.g., 50x50) and randomly placing a set number of points (buildings) on this grid. Each point represents a building in the simulation.

2. **Graph Construction:**
   - A graph `G` is constructed where each node corresponds to a building on the grid.
   - Edges between nodes represent roads that can be either horizontal, vertical, or discretized diagonal paths. 
   - Diagonal connections between buildings are not allowed directly. Instead, they are decomposed into a combination of horizontal and vertical segments. For instance, a diagonal move from `(x1, y1)` to `(x2, y2)` is broken down into horizontal and vertical moves through intermediate points.

3. **Weights and Their Meaning:**
   - The `weight` attribute assigned to each edge represents the Manhattan distance (also known as L1 norm or taxicab geometry) between the two nodes it connects. For purely horizontal or vertical connections, this is simply the absolute difference in either the x-coordinates or the y-coordinates of the two nodes.
   - For discretized diagonal paths, the weight of each segment of the path is set to 1. This means that the total weight of a diagonal connection is the sum of its horizontal and vertical components.

4. **Minimum Spanning Tree (MST):**
   - The graph `G` may contain redundant connections, so we extract a Minimum Spanning Tree (MST) `T` from it. The MST is a subgraph that connects all the buildings with the minimum total distance (weight) and no cycles.
   - The MST ensures that all buildings are connected with the least amount of road construction, avoiding any unnecessary paths.

5. **Traffic Demand:**
   - Traffic demand represents the number of trips between pairs of buildings. It is randomly generated for each pair of buildings.
   - The demand is modeled as a random integer between 1 and 10 for each pair, simulating different levels of traffic between different buildings.

6. **Traffic Flow Assignment:**
   - For each pair of buildings, the shortest path in terms of road distance (weight) is calculated using the MST `T`.
   - The traffic demand between each pair is assigned to this shortest path, with the traffic accumulated on each edge (road segment) it traverses.

7. **Visualization:**
   - The visualization uses `matplotlib` to plot the grid, buildings, roads, and traffic flow.
   - Buildings are plotted as green dots, representing the original positions of the nodes on the grid.
   - Roads (edges) with non-zero traffic are drawn, with their widths proportional to the amount of traffic they carry. This width scaling helps to visually represent the intensity of traffic on each road.
   - Roads and nodes with zero traffic are hidden from the plot to focus on the active parts of the network.
   - The network visualization clearly shows how traffic is distributed among the roads, giving insights into which routes are most heavily used.

### Key Concepts:
- **Nodes:** Represent buildings on a grid. Each node corresponds to a coordinate on the grid.
- **Edges:** Represent roads between buildings. These roads can be horizontal, vertical, or discretized diagonal paths.
- **Weights:** Represent the distance between connected nodes. Horizontal and vertical connections use the Manhattan distance, while diagonal paths are discretized.
- **Traffic Demand:** Represents the number of trips between pairs of buildings. This demand is distributed across the network based on the shortest path in the MST.
- **Traffic Flow:** The cumulative amount of traffic on each road (edge), visualized by the width of the edge.

This script can be used to model and visualize traffic patterns in a simplified city grid, providing insights into road usage and potential bottlenecks.
"""


# Define the grid size and number of points
grid_size = 50
N = 30

# Generate random points on the grid
while True:
    points = [
        (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))
        for _ in range(N)
    ]
    points = list(set(points))  # Ensure unique points

    # Create a graph and add edges including discretized diagonal paths
    G = nx.Graph()
    original_pos = {
        point: point for point in points
    }  # Save original positions of points
    pos = original_pos.copy()  # Position nodes by their coordinates

    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            p1, p2 = points[i], points[j]
            if p1[0] == p2[0] or p1[1] == p2[1]:  # Horizontal or vertical connections
                weight = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
                G.add_edge(p1, p2, weight=weight)
            else:  # Diagonal connections, break into horizontal and vertical segments
                x_path = [
                    (p1[0] + k if p1[0] < p2[0] else p1[0] - k, p1[1])
                    for k in range(1, abs(p1[0] - p2[0]) + 1)
                ]
                y_path = [
                    (x_path[-1][0], p1[1] + k if p1[1] < p2[1] else p1[1] - k)
                    for k in range(1, abs(p1[1] - p2[1]) + 1)
                ]

                full_path = [p1] + x_path + y_path
                for k in range(len(full_path) - 1):
                    G.add_edge(full_path[k], full_path[k + 1], weight=1)

                # Add all intermediate nodes to pos
                for node in full_path:
                    pos[node] = node

    # Check if the graph is connected
    if nx.is_connected(G):
        break  # Exit the loop if the graph is connected

# Compute the minimum spanning tree
T = nx.minimum_spanning_tree(G)

# Initialize traffic demand (uniform random for simplicity)
demand = {
    (i, j): random.randint(1, 10)
    for i in range(len(points))
    for j in range(i + 1, len(points))
}

# Calculate shortest paths and assign traffic
traffic = defaultdict(int)

for (i, j), d in demand.items():
    p1, p2 = points[i], points[j]
    # Find shortest path in the spanning tree
    path = nx.shortest_path(T, source=p1, target=p2, weight="weight")
    # Assign the demand to the path edges
    for k in range(len(path) - 1):
        edge = (path[k], path[k + 1])
        traffic[edge] += d

# Plotting the network
plt.figure(figsize=(8, 8))

# Plot original positions using matplotlib
original_x, original_y = zip(*original_pos.values())
plt.scatter(original_x, original_y, color="green", s=100, label="Original Buildings")

# Draw edges with widths proportional to traffic, hiding those with zero traffic
edges, widths = zip(*[(edge, traffic[edge]) for edge in T.edges() if traffic[edge] > 0])

nx.draw_networkx_edges(
    T, pos, edgelist=edges, width=[w * 0.1 for w in widths], edge_color="gray"
)

# Plot only the nodes that have traffic
active_nodes = {node for edge in edges for node in edge}
nx.draw_networkx_nodes(
    T, pos, nodelist=list(active_nodes), node_size=20, node_color="blue"
)

# Add labels and title
plt.title("Buildings, Roads, and Traffic Flow with Discretized Diagonal Paths")
plt.axis("equal")
plt.grid(True)
plt.legend()

plt.show()
