import random
from collections import Counter


def strength(graph, u, v):
    """Directional link strength used by the LDPA/BLDLP papers."""
    closed_neighborhood = set(graph.neighbors(v))
    closed_neighborhood.add(v)
    closed_neighborhood.discard(u)
    return graph.subgraph(closed_neighborhood).number_of_edges() + 1


def compute_weights(graph, alpha=6):
    """Compute the two directional integer weights for every undirected edge."""
    weights = {}
    for u, v in graph.edges:
        weights[(u, v)] = alpha // strength(graph, u, v)
        weights[(v, u)] = alpha // strength(graph, v, u)
    return weights


def bldlp(graph, alpha=6, seed=None, max_iter=1000, weights=None):
    """Balanced Link Density-based Label Propagation (BLDLP).

    `weights` may be supplied when the preprocessing has already been done,
    allowing the same weights to be reused by fuzzy postprocessing.
    """
    rng = random.Random(seed)
    if weights is None:
        weights = compute_weights(graph, alpha)

    labels = {node: node for node in graph}

    for _ in range(max_iter):
        nodes = list(graph.nodes)
        rng.shuffle(nodes)
        changed = False

        for node in nodes:
            neighbors = list(graph.neighbors(node))
            if not neighbors:
                continue

            counts = Counter(labels[neighbor] for neighbor in neighbors)
            maximum = max(counts.values())
            candidate_labels = {label for label, count in counts.items() if count == maximum}
            candidate_neighbors = [n for n in neighbors if labels[n] in candidate_labels]

            max_weight = max(weights[(node, neighbor)] for neighbor in candidate_neighbors)
            best_neighbors = [
                neighbor for neighbor in candidate_neighbors
                if weights[(node, neighbor)] == max_weight
            ]

            # The paper does not define a second tie-break rule for equal weights.
            new_label = labels[rng.choice(best_neighbors)]
            if labels[node] != new_label:
                labels[node] = new_label
                changed = True

        if not changed:
            break

    return labels
