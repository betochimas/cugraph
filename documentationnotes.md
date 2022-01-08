# Suggested documentation changes for cugraph/python/cugraph/cugraph

This markdown file serves to suggest changes in the documentation for the python implementation of cugraph.
These notes are split up by the organization of the modules in the repository.

Key functions should have a complete documentation, which includes: 
- a specific description of the function's purpose
- a list of all arguments the function accepts with information about what types are allowed and how the function changes as the argument changes
- a description of the return value(s) with their corresponding type(s)
- at least 1 example 
Helper functions need not have a complete documentation, though some sort of description is still necessary

## centrality

## comms

## community

## components

## cores

## dask

## generators

## internals

## layout

## layout

## linear_assignment

## link_analysis

## proto

## sampling

## structure

## traversal

## tree

## utilities

### grmat.py

- `grmat_gen` missing documentation, although possibly not necessary

### nx_factory.py

- `convert_unweighted_to_gdf` missing documentation
- `convert_weighted_named_to_gdf` missing documentation
- `convert_weighted_unnamed_to_gdf` missing documentation
- `convert_from_nx` has incomplete argument descriptions. Missing overall description and info about returns and examples
- `df_score_to_dictionary` could elaborate on overall descriptions. Could add an example, although not necessary
- `df_edge_score_to_dictionary` could elaborate on overall descriptions. Could add an example, although not necessary
- `cugraph_to_nx` missing documentation, although possibly not necessary

### path_retrieval.py

- `get_traversed_cost` missing example(s)

### utils.py

- `get_traversed_path` doctest fails
- `get_traversed_path_list` doctest fails
- `ensure_cugraph_obj` missing argument, returns descriptions, and examples
- `ensure_cugraph_obj_for_nx` description is incomplete, and is missing argument, returns descriptions, and examples
- `is_cp_matrix_type`, `is_sp_matrix_type`, `is_matrix_type`, `is_nx_graph_type`, and `is_cugraph_graph_type` could do with one-liner description
- `renumber_vertex_pair` missing documentation
- `import_optional` missing argument and returns descriptions