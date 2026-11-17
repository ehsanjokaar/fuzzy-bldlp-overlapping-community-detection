import matplotlib.pyplot as plt
import networkx as nx

from src.fuzzy import overlapping_nodes


def plot_fuzzy_partition(graph, memberships, title, pos, cutoff=0.4):
    """Show each node in its strongest membership; outline overlapping nodes."""
    dominant = {
        node: max(scores, key=scores.get)
        for node, scores in memberships.items() if scores
    }
    overlap = set(overlapping_nodes(memberships, cutoff))
    node_colors = [dominant[node] for node in graph.nodes]
    edge_colors = ["crimson" if node in overlap else "#555555" for node in graph.nodes]
    line_widths = [2.8 if node in overlap else 0.7 for node in graph.nodes]

    nx.draw_networkx(
        graph, pos=pos, node_color=node_colors, cmap=plt.cm.tab10,
        edgecolors=edge_colors, linewidths=line_widths, with_labels=True,
        node_size=430, font_size=8, edge_color="#bbbbbb",
    )
    plt.title(title)
    plt.axis("off")
