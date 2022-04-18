# Copyright (c) 2019-2022, NVIDIA CORPORATION.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from cugraph.community import (
    ecg,
    ktruss_subgraph,
    k_truss,
    louvain,
    leiden,
    spectralBalancedCutClustering,
    spectralModularityMaximizationClustering,
    analyzeClustering_modularity,
    analyzeClustering_edge_cut,
    analyzeClustering_ratio_cut,
    subgraph,
    triangles,
    ego_graph,
    batched_ego_graphs,
)

from cugraph.structure import (
    Graph,
    DiGraph,
    MultiGraph,
    MultiDiGraph,
    BiPartiteGraph,
    BiPartiteDiGraph,
    from_edgelist,
    from_cudf_edgelist,
    from_pandas_edgelist,
    to_pandas_edgelist,
    from_pandas_adjacency,
    to_pandas_adjacency,
    from_numpy_array,
    to_numpy_array,
    from_numpy_matrix,
    to_numpy_matrix,
    from_adjlist,
    hypergraph,
    symmetrize,
    symmetrize_df,
    symmetrize_ddf,
    is_weighted,
    is_directed,
    is_multigraph,
    is_bipartite,
    is_multipartite)

"""
from cugraph.structure.graph_implementation.simpleGraph import (
    simpleGraphImpl.AdjList,
    simpleGraphImpl.degree,
    simpleGraphImpl.degrees,
    simpleGraphImpl.delete_adj_list,
    simpleGraphImpl.delete_edge_list,
    simpleGraphImpl.EdgeList,
    simpleGraphImpl.edges,
    simpleGraphImpl.enable_batch,
    simpleGraphImpl.get_two_hop_neighbors,
    simpleGraphImpl.has_edge,
    simpleGraphImpl.has_node,
    simpleGraphImpl.has_self_loop,
    simpleGraphImpl.in_degree,
    simpleGraphImpl.mro,
    simpleGraphImpl.neighbors,
    simpleGraphImpl.nodes,
    simpleGraphImpl.number_of_edges,
    simpleGraphImpl.number_of_nodes,
    simpleGraphImpl.number_of_vertices,
    simpleGraphImpl.out_degree,
    simpleGraphImpl.Properties,
    simpleGraphImpl.to_directed,
    simpleGraphImpl.to_numpy_array,
    simpleGraphImpl.to_numpy_matrix,
    simpleGraphImpl.to_pandas_adjacency,
    simpleGraphImpl.to_pandas_edgelist,
    simpleGraphImpl.to_undirected,
    simpleGraphImpl.transposedAdjList,
    simpleGraphImpl.vertex_column_size,
    simpleGraphImpl.view_adj_list,
    simpleGraphImpl.view_edge_list,
    simpleGraphImpl.view_transposed_adj_list
)
"""
"""
from cugraph.structure.graph_implementation.simpleGraph.simpleGraphImpl import (
    AdjList,
    degree,
    degrees,
    delete_adj_list,
    delete_edge_list,
    EdgeList,
    edges,
    enable_batch,
    get_two_hop_neighbors,
    has_edge,
    has_node,
    has_self_loop,
    in_degree,
    mro,
    neighbors,
    nodes,
    number_of_edges,
    number_of_nodes,
    number_of_vertices,
    out_degree,
    Properties,
    to_directed,
    to_numpy_array,
    to_numpy_matrix,
    to_pandas_adjacency,
    to_pandas_edgelist,
    to_undirected,
    transposedAdjList,
    vertex_column_size,
    view_adj_list,
    view_edge_list,
    view_transposed_adj_list
)
"""

from cugraph.centrality import (
    betweenness_centrality,
    edge_betweenness_centrality,
    katz_centrality,
)

from cugraph.cores import core_number, k_core

from cugraph.components import (
    connected_components,
    weakly_connected_components,
    strongly_connected_components,
)

from cugraph.link_analysis import pagerank, hits

from cugraph.link_prediction import (
    jaccard,
    jaccard_coefficient,
    overlap,
    overlap_coefficient,
    sorensen,
    sorensen_coefficient,
    jaccard_w,
    overlap_w,
    sorensen_w,
)

from cugraph.traversal import (
    bfs,
    bfs_edges,
    sssp,
    shortest_path,
    filter_unreachable,
    shortest_path_length,
    concurrent_bfs,
    multi_source_bfs,
)

from cugraph.tree import minimum_spanning_tree, maximum_spanning_tree

from cugraph.utilities import utils

from cugraph.proto.components import strong_connected_component
from cugraph.proto.structure import find_bicliques

from cugraph.linear_assignment import hungarian, dense_hungarian
from cugraph.layout import force_atlas2
from raft import raft_include_test
from cugraph.comms import comms

from cugraph.sampling import random_walks, rw_path, node2vec

from cugraph import experimental

from cugraph import gnn


# Versioneer
from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
