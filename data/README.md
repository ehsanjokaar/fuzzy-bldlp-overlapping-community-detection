# Human Skull network data

`human_skull_edges.csv` is the 35-node, 79-edge Human Skull network used in the Fuzzy BLDLP article (Jokar, Mosleh, & Kheyrandish, 2021). The edge list was supplied with the project materials and converted to a CSV with `source` and `target` columns. The accompanying text file used 1-based IDs; the supplied spreadsheet used 0-based IDs, and the edge pairs match after adding one to the spreadsheet IDs. Node IDs are kept 1-based.

`human_skull_nodes.csv` maps IDs 1-35 to anatomical names using the node-label list in Esteve-Altava et al. (2015). Nodes 30-33 are cartilages; the remaining nodes in this 35-node subset are bones.

The 2015 source paper describes a larger skeletal network (45 bones/cartilages and 86 articulation contacts). This repository does not claim that the supplied 35-node edge list is the full 2015 network; it preserves the 35-node, 79-edge version reported in the 2021 Fuzzy BLDLP paper.

## References

- Jokar, E., Mosleh, M., & Kheyrandish, M. (2021). Overlapping community detection in complex networks using fuzzy theory, balanced link density, and label propagation. *Expert Systems*. https://doi.org/10.1111/exsy.12921
- Esteve-Altava, B., Diogo, R., Smith, C., Boughner, J. C., & Rasskin-Gutman, D. (2015). Anatomical networks reveal the musculoskeletal modularity of the human head. *Scientific Reports, 5*, 8298. https://doi.org/10.1038/srep08298

The node-name mapping is based on the source article's published label list. It is not a ground-truth community assignment.
