# Fuzzy BLDLP: Reusable Overlapping Community Detection Pipeline

A concise Python reproduction of the three-stage method described in **Jokar, Mosleh, and Kheyrandish (2021)**. It combines BLDLP-style directional link weights, a selectable disjoint community detector, and a fuzzy membership postprocessing step.

The goal is also to make the fuzzy postprocessing reusable: researchers can plug in their own disjoint community-detection algorithms without changing the weight preprocessing or membership calculation.

## Three-stage pipeline

1. **Preprocessing:** compute directional BLDLP link weights using the same strength and integer weight calculation as the companion BLDLP repository.
2. **Disjoint detection:** obtain a partition using BLDLP, standard LPA, Louvain, or another disjoint detector.
3. **Fuzzy postprocessing:** compute each node's membership in the communities represented among its neighbors, using the link weights.

The 2021 paper explains that the membership calculation is independent of the disjoint detector used in stage 2. The implementation uses the following node-to-community membership ratio:

`M(i, C) = sum(weight(i, j) for j in N(i) intersect C) / sum(weight(i, j) for j in N(i))`

## Included methods

- **Fuzzy BLDLP** — BLDLP partition + fuzzy membership postprocessing.
- **Fuzzy LPA** — standard LPA partition + the same fuzzy postprocessing. In this repository, this means standard LPA followed by the 2021 paper's membership formula; it is not a separate reproduction of the earlier Poaka et al. fuzzy-LPA algorithm.
- **Fuzzy Louvain** — NetworkX Louvain partition + the same fuzzy postprocessing.
- **NetworkX k-clique percolation** — included as an optional native overlapping baseline, not as a disjoint phase-two detector.

## Human Skull dataset

The repository includes the 35-node, 79-edge edge list used in the 2021 Fuzzy BLDLP article and an accompanying node metadata file with anatomical names and bone/cartilage type. The ID-to-name mapping comes from the label list in Esteve-Altava et al. (2015). It is not a ground-truth community labeling. See [`data/README.md`](data/README.md) for provenance and the distinction between the supplied 35/79 graph and the larger 45/86 skeletal network described by the 2015 source article.

## Requirements and run

Python 3.9 or later, NetworkX 3.2 or later, and Matplotlib 3.7 or later.

```bash
pip install -r requirements.txt
python experiments/human_skull_experiment.py
```

The script loads the CSV edge list, attaches node metadata, computes weights once, runs the three fuzzy variants, reports the number of communities and overlapping nodes at the paper's default cutoff (0.4), and visualizes the results. It also reports NetworkX's native k-clique percolation result for `k=4`.

## CSV format for your own graphs

The default edge-list loader expects a header row with two columns, `source,target`:

```csv
source,target
A,B
A,C
B,C
```

Use `load_edge_list_csv(path, source_col="source", target_col="target")` for a different pair of column names. Node identifiers are read as integers when possible; otherwise, they remain strings.

## Plug in another disjoint detector

A contributed method only needs to return a disjoint partition: a list (or iterable) of node sets that covers every graph node exactly once. For example:

```python
from src.fuzzy import fuzzy_memberships

partition = my_community_detector(G)  # list[set[node]]
memberships = fuzzy_memberships(G, partition, weights)
```

The partition is validated before postprocessing. Overlapping detectors should not be passed here; the third stage expects a disjoint partition.

## Important numerical note: zero-weight nodes

The BLDLP weight calculation is retained from the BLDLP community detection repository. Because the paper's integer-valued weights can be zero, some nodes in the supplied Human Skull graph have zero total outgoing weight at `alpha=6`. The membership ratio would then have a zero denominator. To keep the pipeline defined, the implementation uses a documented fallback **only in the fuzzy postprocessing**: if all outgoing weights of a node are zero, its adjacent edges are treated as equally weighted for that node's membership calculation. The original BLDLP weights and phase-two tie-breaking are not changed. Set `zero_weight_fallback="raise"` to instead raise an error when this case occurs.

For the supplied Human Skull graph at `alpha=6`, 12 nodes have zero total outgoing integer weight and use this fallback. This fallback is a pragmatic resolution of an undefined denominator; it is not claimed to be an additional equation from the published paper. The published article reports five overlapping skull nodes, whereas this single-seed Python run may produce a different set. That difference should be interpreted in light of the explicit zero-weight fallback, stochastic node order/residual ties, and the distinction between this one-run demonstration and the paper's 100-run experiments.

## NetworkX native overlapping detection

NetworkX provides [`k_clique_communities`](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.kclique.k_clique_communities.html), which implements k-clique percolation. It directly returns overlapping communities. The parameter `k` controls the smallest clique size; nodes that do not belong to any qualifying clique may not appear in its output. It is a useful additional comparison, but it is a different approach from this repository's fuzzy weighting pipeline.

## Scope and interpretation

The Human Skull data do not include independent ground-truth overlapping community labels. The five complexes and overlapping node IDs reported in the Fuzzy BLDLP article are results reported by that method, not independent ground truth. This repository therefore reports detected memberships and structural summaries rather than precision/recall or ONMI against unavailable labels.

## References

1. Jokar, E., Mosleh, M., & Kheyrandish, M. (2021). Overlapping community detection in complex networks using fuzzy theory, balanced link density, and label propagation. *Expert Systems*. https://doi.org/10.1111/exsy.12921
2. Jokar, E., & Mosleh, M. (2019). Community detection in social networks based on improved label propagation algorithm and balanced link density. *Physics Letters A, 383*(8), 718-727. https://doi.org/10.1016/j.physleta.2018.11.033
3. Esteve-Altava, B., Diogo, R., Smith, C., Boughner, J. C., & Rasskin-Gutman, D. (2015). Anatomical networks reveal the musculoskeletal modularity of the human head. *Scientific Reports, 5*, 8298. https://doi.org/10.1038/srep08298

## Invitation to researchers

Researchers are welcome to test their own **disjoint** community-detection methods in this pipeline. If your algorithm returns a complete non-overlapping partition, you can pass that partition to the shared fuzzy-membership function and compare the resulting overlapping cover under the same preprocessing and postprocessing rules. Please cite the relevant papers and document any adaptations.
