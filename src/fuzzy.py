from collections import defaultdict


def partition_from_labels(labels):
    """Convert a node-to-label dictionary into a disjoint partition."""
    groups = defaultdict(set)
    for node, label in labels.items():
        groups[label].add(node)
    return list(groups.values())


def validate_partition(graph, partition):
    """Check that a disjoint partition covers every graph node exactly once."""
    partition = [set(community) for community in partition if community]
    assigned = [node for community in partition for node in community]
    if len(assigned) != len(set(assigned)):
        raise ValueError("The phase-two method returned overlapping communities; a disjoint partition is required.")
    if set(assigned) != set(graph.nodes):
        missing = set(graph.nodes) - set(assigned)
        extra = set(assigned) - set(graph.nodes)
        raise ValueError(f"Partition must cover every graph node exactly once (missing={missing}, extra={extra}).")
    return partition


def fuzzy_memberships(graph, partition, weights, zero_weight_fallback="uniform"):
    """Compute fuzzy memberships from directional edge weights and a disjoint partition.

    For node i, membership in community C is the sum of weights(i,j) over
    neighbors j in C, divided by the sum over all neighbors of i.

    If all outgoing integer weights of a node are zero, the paper's ratio has
    a zero denominator. By default, that node's incident edges are treated
    equally for this postprocessing step only. The BLDLP weights themselves
    are not modified. Set zero_weight_fallback='raise' to reject this case.
    """
    partition = validate_partition(graph, partition)
    node_to_community = {node: index for index, community in enumerate(partition) for node in community}
    memberships = {}

    for node in graph.nodes:
        neighbors = list(graph.neighbors(node))
        if not neighbors:
            memberships[node] = {node_to_community[node]: 1.0}
            continue

        node_weights = {neighbor: weights[(node, neighbor)] for neighbor in neighbors}
        total_weight = sum(node_weights.values())

        if total_weight == 0:
            if zero_weight_fallback == "raise":
                raise ZeroDivisionError(
                    f"All directional weights from node {node!r} are zero; fuzzy membership is undefined."
                )
            if zero_weight_fallback != "uniform":
                raise ValueError("zero_weight_fallback must be 'uniform' or 'raise'.")
            node_weights = {neighbor: 1.0 for neighbor in neighbors}
            total_weight = float(len(neighbors))

        node_memberships = {}
        for community_id, community in enumerate(partition):
            weight_to_community = sum(
                node_weights[neighbor] for neighbor in neighbors if neighbor in community
            )
            if weight_to_community > 0:
                node_memberships[community_id] = weight_to_community / total_weight

        memberships[node] = node_memberships

    return memberships


def threshold_memberships(memberships, cutoff=0.4):
    """Convert fuzzy memberships to a crisp cover using a membership cutoff."""
    cover = defaultdict(set)
    for node, scores in memberships.items():
        for community_id, score in scores.items():
            if score >= cutoff:
                cover[community_id].add(node)
    return dict(cover)


def overlapping_nodes(memberships, cutoff=0.4):
    """Return nodes assigned to at least two communities after thresholding."""
    return sorted(
        node for node, scores in memberships.items()
        if sum(score >= cutoff for score in scores.values()) > 1
    )
