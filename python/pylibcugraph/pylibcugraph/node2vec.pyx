# Copyright (c) 2022, NVIDIA CORPORATION.
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

# Have cython use python 3 syntax
# cython: language_level = 3

from pylibcugraph._cugraph_c.cugraph_api cimport (
    bool_t,
    data_type_id_t,
    cugraph_resource_handle_t,
)
from pylibcugraph._cugraph_c.error cimport (
    cugraph_error_code_t,
    cugraph_error_t,
)
from pylibcugraph._cugraph_c.array cimport (
    cugraph_type_erased_device_array_view_t,
)
from pylibcugraph._cugraph_c.graph cimport (
    cugraph_graph_t,
)
from pylibcugraph._cugraph_c.algorithms cimport (
    cugraph_sssp,
    cugraph_paths_result_t,
    cugraph_paths_result_get_vertices,
    cugraph_paths_result_get_distances,
    cugraph_paths_result_get_predecessors,
    cugraph_paths_result_free,
)

from pylibcugraph.resource_handle cimport (
    EXPERIMENTAL__ResourceHandle,
)
from pylibcugraph.graphs cimport (
    EXPERIMENTAL__Graph,
)
from pylibcugraph.utils cimport (
    assert_success,
    get_numpy_type_from_c_type,
)


def EXPERIMENTAL__node2vec(EXPERIMENTAL__ResourceHandle resource_handle,
                           EXPERIMENTAL__Graph graph,
                           sources,
                           size_t max_depth,
                           bool_t flag_use_padding,
                           double p,
                           double q):
    """
    FIXME: Add description after

    Parameters
    ----------
    resource_handle : ResourceHandle
        Handle to the underlying device resources needed for referencing data
        and running algorithms.

    graph : SGGraph
        The input graph.

    max_depth : size_t

    flag_use_padding : bool_t

    p : double

    q : double

    Returns
    -------
    # NOTE: Currently not implemented and always returns None

    Examples
    --------
    >>> import pylibcugraph, cupy, numpy
    >>> srcs = cupy.asarray([0, 1, 2], dtype=numpy.int32)
    >>> dsts = cupy.asarray([1, 2, 3], dtype=numpy.int32)
    >>> weights = cupy.asarray([1.0, 1.0, 1.0], dtype=numpy.float32)
    >>> resource_handle = pylibcugraph.experimental.EXPERIMENTAL__ResourceHandle()
    >>> graph_props = pylibcugraph.experimental.GraphProperties(
    ...     is_symmetric=False, is_multigraph=False)
    >>> G = pylibcugraph.experimental.SGGraph(
    ...     resource_handle, graph_props, srcs, dsts, weights,
    ...     store_transposed=False, renumber=False, do_expensive_check=False)
    >>> dfr = pylibcugraph.experimental.node2vec(
    ...     resource_handle, G, source=1, cutoff=999,
    ...     compute_predecessors=True, do_expensive_check=False)
    >>> dfr

    """

    # FIXME: import these modules here for now until a better pattern can be
    # used for optional imports (perhaps 'import_optional()' from cugraph), or
    # these are made hard dependencies.
    try:
        import cupy
    except ModuleNotFoundError:
        raise RuntimeError("node2vec requires the cupy package, which could not "
                           "be imported")
    try:
        import numpy
    except ModuleNotFoundError:
        raise RuntimeError("node2vec requires the numpy package, which could not "
                           "be imported")

    cdef cugraph_resource_handle_t* c_resource_handle_ptr = \
        resource_handle.c_resource_handle_ptr
    cdef cugraph_graph_t* c_graph_ptr = graph.c_graph_ptr

    cdef cugraph_paths_result_t* result_ptr
    cdef cugraph_error_code_t error_code
    cdef cugraph_error_t* error_ptr

    error_code = cugraph_node2vec(c_resource_handle_ptr,
                                  c_graph_ptr,
                                  max_depth,
                                  flag_use_padding,
                                  p,
                                  q,
                                  &result_ptr,
                                  &error_ptr)
    assert_success(error_code, error_ptr, "cugraph_node2vec")

    # Extract individual device array pointers from result and copy to cupy
    # arrays for returning.
    cdef cugraph_type_erased_device_array_view_t* vertices_ptr = \
        cugraph_paths_result_get_vertices(result_ptr)
    # cdef cugraph_type_erased_device_array_view_t* distances_ptr = \
    #    cugraph_paths_result_get_distances(result_ptr)
    cdef cugraph_type_erased_device_array_view_t* predecessors_ptr = \
        cugraph_paths_result_get_predecessors(result_ptr)

    cupy_vertices = copy_to_cupy_array(c_resource_handle_ptr, vertices_ptr)
    # cupy_distances = copy_to_cupy_array(c_resource_handle_ptr, distances_ptr)
    cupy_predecessors = copy_to_cupy_array(c_resource_handle_ptr,
                                           predecessors_ptr)

    return None
