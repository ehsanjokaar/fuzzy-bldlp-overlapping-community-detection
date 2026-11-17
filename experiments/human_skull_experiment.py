from pathlib import Path
import sys
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import networkx as nx

from src.bldlp import bldlp, compute_weights
from src.data import load_edge_list_csv, load_node_metadata_csv
from src.fuzzy import (
    fuzzy_memberships, overlapping_nodes, partition_from_labels,
    threshold_memberships,
)
from src.lpa import lpa
from src.visualization import plot_fuzzy_partition


def report(graph, metadata, name, partition, memberships, cutoff):
    cover = threshold_memberships(memberships, cutoff)
    overlaps = overlapping_nodes(memberships, cutoff)
    assigned = set().union(*cover.values()) if cover else set()

    print(f"\n{name}")
    print("-" * len(name))
    print(f"Disjoint communities (phase 2): {len(partition)}")
    print(f"Fuzzy communities after cutoff {cutoff:.2f}: {len(cover)}")
    named_overlaps = [
        f"{node} ({metadata.get(node, {}).get('node_name', 'unknown')})"
        for node in overlaps
    ]
    print(f"Overlapping nodes: {named_overlaps}")
    print(f"Nodes not assigned after cutoff: {sorted(set(graph.nodes) - assigned)}")
    print(f"Membership sums valid: {all(abs(sum(v.values()) - 1.0) < 1e-9 for v in memberships.values())}")


if __name__ == "__main__":
    edge_file = ROOT / "data" / "human_skull_edges.csv"
    node_file = ROOT / "data" / "human_skull_nodes.csv"

    G = load_edge_list_csv(edge_file)
    metadata = load_node_metadata_csv(node_file, G)

    print("Human Skull network")
    print(f"Nodes: {G.number_of_nodes()} | Edges: {G.number_of_edges()}")
    print("Node names and anatomical types are in data/human_skull_nodes.csv")

    ALPHA = 6
    CUTOFF = 0.4
    SEED = 42

    # Phase 1: compute directional BLDLP weights once and reuse them.
    weights = compute_weights(G, alpha=ALPHA)
    zero_weight_nodes = [
        node for node in G
        if sum(weights[(node, neighbor)] for neighbor in G.neighbors(node)) == 0
    ]
    print(f"Nodes requiring the documented uniform-membership fallback: {zero_weight_nodes}")

    # Phase 2: any disjoint detector can provide a partition.
    bldlp_partition = partition_from_labels(
        bldlp(G, alpha=ALPHA, seed=SEED, weights=weights)
    )
    lpa_partition = partition_from_labels(lpa(G, seed=SEED))
    louvain_partition = list(
        nx.community.louvain_communities(G, seed=SEED)
    )

    # Phase 3: apply exactly the same fuzzy postprocessing to each partition.
    results = {
        "Fuzzy BLDLP": (bldlp_partition, fuzzy_memberships(G, bldlp_partition, weights)),
        "Fuzzy LPA": (lpa_partition, fuzzy_memberships(G, lpa_partition, weights)),
        "Fuzzy Louvain": (louvain_partition, fuzzy_memberships(G, louvain_partition, weights)),
    }

    for name, (partition, memberships) in results.items():
        report(G, metadata, name, partition, memberships, CUTOFF)

    # Native NetworkX overlapping detector: K-clique percolation.
    # This is a separate overlapping baseline, not a disjoint phase-two method.
    k = 4
    k_clique_cover = list(nx.community.k_clique_communities(G, k=k))
    clique_counts = Counter(node for community in k_clique_cover for node in community)
    native_overlaps = sorted(node for node, count in clique_counts.items() if count > 1)
    covered = set(clique_counts)
    print(f"\nNetworkX native k-clique percolation (k={k})")
    print(f"Overlapping communities: {len(k_clique_cover)}")
    print(f"Overlapping nodes: {native_overlaps}")
    print(f"Nodes not covered by any k-clique community: {sorted(set(G.nodes) - covered)}")

    # Same layout across the three fuzzy methods for visual comparison.
    pos = nx.spring_layout(G, seed=10)
    plt.figure(figsize=(15, 5))
    for index, (name, (_, memberships)) in enumerate(results.items(), start=1):
        plt.subplot(1, 3, index)
        plot_fuzzy_partition(G, memberships, name, pos, cutoff=CUTOFF)
    plt.tight_layout()
    plt.show()
