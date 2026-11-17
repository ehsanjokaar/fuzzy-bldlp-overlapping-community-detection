import csv
from pathlib import Path
import networkx as nx


def _parse_node(value):
    value = value.strip()
    try:
        return int(value)
    except ValueError:
        return value


def load_edge_list_csv(path, source_col="source", target_col="target"):
    """Load an undirected edge list CSV with source and target columns."""
    graph = nx.Graph()
    with Path(path).open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None or source_col not in reader.fieldnames or target_col not in reader.fieldnames:
            raise ValueError(
                f"CSV must contain columns {source_col!r} and {target_col!r}."
            )
        for row in reader:
            source, target = row[source_col], row[target_col]
            if source is None or target is None or not source.strip() or not target.strip():
                continue
            graph.add_edge(_parse_node(source), _parse_node(target))
    return graph


def load_node_metadata_csv(path, graph=None):
    """Read node metadata and optionally attach it to a NetworkX graph."""
    metadata = {}
    with Path(path).open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            node = _parse_node(row["node_id"])
            metadata[node] = {key: value for key, value in row.items() if key != "node_id"}
            if graph is not None:
                graph.add_node(node, **metadata[node])
    return metadata
