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

from pylibcugraph._cugraph_c.resource_handle cimport (
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
    cugraph_type_erased_device_array_view_create,
    cugraph_type_erased_device_array_free,
    cugraph_type_erased_host_array_view_t,
)
from pylibcugraph._cugraph_c.graph cimport (
    cugraph_graph_t,
)
from pylibcugraph._cugraph_c.algorithms cimport (
    uniform_nbr_sample,
    cugraph_sample_result_t,
    cugraph_sample_result_get_sources,
    cugraph_sample_result_get_destinations,
    cugraph_sample_result_get_start_labels,
    cugraph_sample_result_get_index,
    cugraph_sample_result_get_counts,
    cugraph_sample_result_free,
)
from pylibcugraph.resource_handle cimport (
    EXPERIMENTAL__ResourceHandle,
)
from pylibcugraph.graphs cimport (
    _GPUGraph
)
from pylibcugraph.utils cimport (
    assert_success,
    copy_to_cupy_array,
    assert_CAI_type,
    get_c_type_from_numpy_type,
)

def EXPERIMENTAL__uniform_neighborhood_sampling(EXPERIMENTAL__ResourceHandle resource_handle,
                               _GPUGraph input_graph,
                               start_info_list,
                               h_fan_out,
                               bool_t without_replacement,
                               bool_t do_expensive_check):
    """
    Does uniform neighborhood sampling.

    Parameters
    ----------
    input_graph: ???
    start_info_list: ???
    fanout_vals: ???
    without_replacement: ???
    do_expensive_check: ???

    Examples
    --------
    >>> import pylibcugraph, cupy, numpy
    >>> srcs = cupy.asarray([0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4],
    ...                     dtype=numpy.int32)
    >>> dsts = cupy.asarray([1, 2, 3, 4, 5, 6, 7, 5, 6, 7, 5, 6, 7],
    ...                     dtype=numpy.int32)
    >>> weights = cupy.asarray([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
    ...                         1.0, 1.0, 1.0, 1.0], dtype=numpy.float32)
    >>> resource_handle = pylibcugraph.experimental.ResourceHandle()
    >>> graph_props = pylibcugraph.experimental.GraphProperties(
    ...     is_symmetric=False, is_multigraph=False)
    >>> G = pylibcugraph.experimental.MGGraph(
    ...     resource_handle, graph_props)

    """
    print("Hello from uniform_neighborhood_sampling.pyx!")
    
    cdef cugraph_resource_handle_t* c_resource_handle_ptr = \
        resource_handle.c_resource_handle_ptr
    cdef cugraph_graph_t* c_graph_ptr = input_graph.c_graph_ptr

    cdef cugraph_sample_result_t* result_ptr
    cdef cugraph_error_code_t error_code
    cdef cugraph_error_t* error_ptr

    cdef uintptr cai_start_ptr = \
        start_info_list.__cuda_array_interface__["data"][0]
    cdef uintptr cai_labels_ptr = \
        start_info_list.__cuda_array_interface__["data"][1]
    cdef uintptr cai_fan_out_ptr = \
        h_fan_out.__cuda_array_interface__["data"][0]

    cdef cugraph_type_erased_device_array_view_t* start_ptr = \
        cugraph_type_erased_device_array_view_create(
            <void*>cai_start_ptr,
            len(start_info_list),
            get_c_type_from_numpy_type(start_info_list.dtype))
    cdef cugraph_type_erased_device_array_view_t* start_labels_ptr = \
        cugraph_type_erased_device_array_view_create(
            <void*>cai_labels_ptr,
            len(start_info_list),
            get_c_type_from_numpy_type(start_info_list.dtype))
    cdef cugraph_type_erased_host_array_view_t* fan_out_ptr = \
        cugraph_type_erased_host_array_view_create(
            <void*>cai_fan_out_ptr,
            len(h_fan_out),
            get_c_type_from_numpy_type(h_fan_out.dtype))

    error_code = uniform_nbr_sample(c_resource_handle_ptr,
                                    c_graph_ptr,
                                    start_ptr,
                                    start_labels_ptr,
                                    fan_out_ptr,
                                    without_replacement,
                                    do_expensive_check,
                                    &result_ptr,
                                    &error_ptr)
    assert_success(error_code, error_ptr, "uniform_nbr_sample")

    cdef cugraph_type_erased_device_array_view_t* src_ptr = \
        cugraph_sample_result_get_sources(result_ptr)
    cdef cugraph_type_erased_device_array_view_t* dst_ptr = \
        cugraph_sample_result_get_destinations(result_ptr)
    cdef cugraph_type_erased_device_array_view_t* start_labels_ptr = \
        cugraph_sample_result_get_start_labels(result_ptr)
    cdef cugraph_type_erased_device_array_view_t* index_ptr = \
        cugraph_sample_result_get_index(result_ptr)
    cdef cugraph_type_erased_device_array_view_t* counts_ptr = \
        cugraph_sample_result_get_counts(result_ptr)

    cupy_sources = copy_to_cupy_array(c_resource_handle_ptr, src_ptr)
    cupy_destinations = copy_to_cupy_array(c_resource_handle_ptr, dst_ptr)
    cupy_labels = copy_to_cupy_array(c_resource_handle_ptr, start_labels_ptr)
    cupy_indices = copy_to_cupy_array(c_resource_handle_ptr, index_ptr)
    cupy_counts = copy_to_cupy_array(c_resource_handle_ptr, counts_ptr)

    cugraph_sample_result_free(result_ptr)

    return (cupy_sources, cupy_destinations, cupy_labels, cupy_indices, cupy_counts)
