# Suggested documentation changes for cugraph/python/cugraph/cugraph

This markdown file serves to suggest changes in the documentation for the python implementation of cugraph.
These notes are split up by the organization of the modules in the repository.

Key functions should have a complete documentation, which includes: 
- a specific description of the function's purpose
- a list of all arguments the function accepts with information about what types are allowed and how the function changes as the argument changes
- a description of the return value(s) with their corresponding type(s)
- at least 1 example, with an example output if possible
Helper functions need not have a complete documentation, though some sort of description is still necessary

## centrality, comms, community, components, cores, dask, internals, structure

## generators

### rmat.py

- In general, the method signatures all have one argument per line
- `rmat` return value description is incomplete

## layout

### force_atlas2.py

- `force_atlas2` missing example(s)

## linear_assignment

### lap.py

- `hungarian` example fails because dataset bipartite is not included within datasets/, and workers is not defined
- `dense_hungarian` missing example, this is what the FIXME is referring to

## link_analysis

### hits.py

### pagerank.py

## link_prediction

### jaccard.py

- `jaccard_coefficient` could use more detailed description

### overlap.py

- `overlap_coefficient` could use more detailed description

### sorensen.py

- `sorensen_coefficient` missing description

### wjaccard.py

### woverlap.py

### wsorensen.py

## sampling

### random_walks.py

- `random_walks` description is incomplete, parameter description includes deprecated class (DiGraph), FIXME w.r.t. Nx return types
- `rw_path` missing example(s)

## traversal

### bfs.py

- `bfs` has no description of return_predecessors argument

### ms_bfs.py

- `_get_feasibility` has detailed documentation yet isn't featured on docs.rapids.ai
- `concurrent_bfs` missing example(s), multi-line comments present that look like notes
- `multi_source_bfs` WIP; missing example(s), commented-out code present, FIXME present

### sssp.py

- `sssp` FIXME before function signature, incomplete description of arguments, FIXME regarding nx_weight_attr
- `filter_unreachable` could benefit from example(s)
- `shortest_path_length` could benefit from example(s)

## tree

### minimum_spanning_tree.py

- `maximum_spanning_tree` has failing doctest, though related to a bug


This example results in cugraph.maximum_spanning_tree outputting a MaxST (haven't verified its correctness)
- import cudf, cugraph
- M = cudf.read_csv('datasets/karate_undirected.csv',
                     delimiter='\t', dtype=['int32', 'int32'],
                     header=None)
- G = cugraph.Graph()
- G.from_cudf_edgelist(M, source='0', destination='1')
- cugraph.minimum_spanning_tree(G)
- cugraph.maximum_spanning_tree(G, weight=None)

This examples results in cugraph.maximum_spanning_tree erroring with message:
AttributeError: 'NoneType' object has no attribute 'weights'
- import cudf, cugraph
- M = cudf.read_csv('datasets/karate_undirected.csv',
                     delimiter='\t', dtype=['int32', 'int32'],
                     header=None)
- G = cugraph.Graph()
- G.from_cudf_edgelist(M, source='0', destination='1')
- cugraph.maximum_spanning_tree(G, weight=None)

This examples results in cugraph.maximum_spanning_tree erroring with message:
RuntimeError: RAFT failure at file=/opt/conda/envs/rapids/include/raft/sparse/mst/detail/mst_solver_inl.cuh line=173: Number of edges found by MST is invalid. This may be due to loss in precision. Try increasing precision of weights.
Obtained 28 stack frames
- import cudf, cugraph
- M = cudf.read_csv('datasets/karate_undirected.csv',
                     delimiter='\t', dtype=['int32', 'int32'],
                     header=None)
- G = cugraph.Graph()
- G.from_cudf_edgelist(M, source='0', destination='1')
- cugraph.minimum_spanning_tree(G)
- cugraph.maximum_spanning_tree(G)


## utilities - these methods do not show up on docs.rapids.ai

### grmat.py

- `grmat_gen` missing documentation, although possibly not necessary

### nx_factory.py

- `convert_unweighted_to_gdf` missing documentation
- `convert_weighted_named_to_gdf` missing documentation
- `convert_weighted_unnamed_to_gdf` missing documentation
- `convert_from_nx` has incomplete argument descriptions. Missing overall description and info about returns and examples
- `df_score_to_dictionary` could elaborate on overall descriptions. Could add an example, although not necessary
- `df_edge_score_to_dictionary` could elaborate on overall descriptions, e.g. how it's different from df_score_to_dictionary
- `cugraph_to_nx` missing documentation, although possibly not necessary

### path_retrieval.py

- `get_traversed_cost` missing example(s)

### utils.py

- `ensure_cugraph_obj` missing argument, returns descriptions, and examples, FIXME present
- `ensure_cugraph_obj_for_nx` description is incomplete, and is missing argument, returns descriptions, and examples
- `is_cp_matrix_type`, `is_sp_matrix_type`, `is_matrix_type`, `is_nx_graph_type`, and `is_cugraph_graph_type` could do with one-liner description
- `renumber_vertex_pair` missing documentation
- `import_optional` missing argument and returns descriptions