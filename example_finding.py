import doctest
import inspect
import os

import numpy as np
#import pytest  GOAL is to find all examples w/o pytest

import cugraph
import cudf


__all__ = [
        "analyzeClustering_edge_cut", 
        "analyzeClustering_modularity",
        "analyzeClustering_ratio_cut"
        "batched_ego_graphs",
        "betweenness_centrality",
        "bfs",
        "bfs_edges",
        "BiPartiteDiGraph",
        "BiPartiteGraph",
        "centrality",
        "comms",
        "community",
        "components",
        "concurrent_bfs",
        "connected_components",
        "core_number",
        "cores",
        "dask",
        "dense_hungarian",
        "DiGraph",
        "ecg",
        "edge_betweenness_centrality",
        "ego_graph",
        "filter_unreachable",
        "find_bicliques",
        "force_atlas2",
        "from_adjlist",
        "from_cudf_edgelist",
        "from_edgelist",
        "from_numpy_array",
        "from_numpy_matrix",
        "from_pandas_adjacency",
        "from_pandas_edgelist",
        "Graph",
        "hits",
        "hungarian",
        "hypergraph",
        "is_bipartite",
        "is_directed",
        "is_multigraph",
        "is_multipartite",
        "is_weighted",
        "jaccard",
        "jaccard_coefficient",
        "jaccard_w",
        "katz_centrality",
        "k_core",
        "k_truss",
        "ktruss_subgraph",
        "layout",
        "leiden",
        "linear_assignment",
        "link_analysis",
        "link_prediction",
        "louvain",
        "maximum_spanning_tree",
        "minimum_spanning_tree",
        "MultiDiGraph",
        "MultiGraph",
        "multi_source_bfs",
        "overlap",
        "overlap_coefficient",
        "overlap_w",
        "pagerank",
        "proto", 
        "raft",
        "raft_include_test",
        "random_walks",
        "rw_path",
        "sampling",
        "shortest_path",
        "shortest_path_length",
        "sorensen",
        "sorensen_coefficient",
        "sorensen_w",
        "spectralBalancedCutClustering",
        "spectralModularityMaximizationClustering",
        "sssp",
        "strong_connected_component",
        "strongly_connected_components",
        "structure",
        "subgraph",
        "symmetrize",
        "symmetrize_ddf",
        "symmetrize_df",
        "to_numpy_array",
        "to_numpy_matrix",
        "to_pandas_adjacency",
        "to_pandas_edgelist",
        "traversal",
        "tree",
        "triangles",
        "utilities",
        "utils",
        "weakly_connected_components",
]


def name_in_all(parent, name, member):
    # member not necessary in sig
    return name in __all__

def is_public_name(parent, name, member):
    # member not necessary in sig
    return not name.startswith("_")


def find_docstrings_in_module(finder, obj, criteria=None):
    #for docstring in finder.find(obj):
    #   if docstring.examples:
    #        print("found example")
    #        yield obj

    for name, member in inspect.getmembers(obj):
        if criteria is not None and not criteria(obj, name, member):
            continue
        #breakpoint()
        if inspect.ismodule(member):
            #print(name + "... is a module")
            if name_in_all(obj, name, member):     # can think of this as 2nd criteria
                yield from find_docstrings_in_module(finder, member, criteria)
        elif inspect.isfunction(member):
            #print(name + "... is a function")
            for docstring in finder.find(member):
                if docstring.examples:
                    #print("... and found examples")
                    yield docstring
        yield name

def find_docstrings_in_obj(finder, obj, criteria=None):
    for name, member in inspect.getmembers(obj):
        if criteria is not None and not criteria(obj, name, member):
            continue
        if inspect.ismodule(member):
            yield from find_docstrings_in_module(finder, member, criteria=is_public_name)


def fetch_doctests():
    finder = doctest.DocTestFinder()
    #yield from find_docstrings_in_module(finder, cugraph, criteria=is_public_name)
    yield from find_docstrings_in_module(finder, cugraph, criteria=is_public_name)

iter = 497
num_tests_found = 0
fetcher = fetch_doctests()
while iter > 0:
    try:
        fetched = next(fetcher)
    except StopIteration:
        break
    if isinstance(fetched, doctest.DocTest):
        print(fetched)
        num_tests_found += len(fetched.examples)
    iter -= 1
print("Total # of tests found: " + str(num_tests_found))