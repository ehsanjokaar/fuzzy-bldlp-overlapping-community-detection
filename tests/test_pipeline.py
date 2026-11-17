import unittest

import networkx as nx

from src.bldlp import compute_weights, strength
from src.fuzzy import fuzzy_memberships, partition_from_labels
from src.lpa import lpa


class TestFuzzyPipeline(unittest.TestCase):
    def test_bldlp_strength_example(self):
        graph = nx.Graph()
        graph.add_edges_from([(0, 1), (0, 3), (1, 2), (1, 3), (2, 3)])
        self.assertEqual(strength(graph, 0, 1), 4)
        self.assertEqual(strength(graph, 1, 0), 2)
        self.assertEqual(strength(graph, 1, 3), 3)

    def test_memberships_sum_to_one_even_for_zero_weights(self):
        graph = nx.path_graph(4)
        labels = lpa(graph, seed=1)
        partition = partition_from_labels(labels)
        weights = {(u, v): 0 for u, v in graph.edges}
        weights.update({(v, u): 0 for u, v in graph.edges})
        memberships = fuzzy_memberships(graph, partition, weights)
        for scores in memberships.values():
            self.assertAlmostEqual(sum(scores.values()), 1.0)


if __name__ == "__main__":
    unittest.main()
