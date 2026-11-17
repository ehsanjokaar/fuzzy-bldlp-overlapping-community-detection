import random
from collections import Counter


def lpa(graph, seed=None, max_iter=1000):
    """Standard asynchronous Label Propagation Algorithm."""
    rng = random.Random(seed)
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
            candidates = [label for label, count in counts.items() if count == maximum]
            new_label = rng.choice(candidates)

            if labels[node] != new_label:
                labels[node] = new_label
                changed = True

        if not changed:
            break

    return labels
