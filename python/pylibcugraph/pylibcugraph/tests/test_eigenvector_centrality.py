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

import pytest
import cupy as cp
import numpy as np
from pylibcugraph.experimental import (ResourceHandle,
                                       GraphProperties,
                                       SGGraph,
                                       eigenvector_centrality)


# =============================================================================
# Test helpers
# =============================================================================
def _get_param_args(param_name, param_values):
    """
    Returns a tuple of (<param_name>, <pytest.param list>) which can be applied
    as the args to pytest.mark.parametrize(). The pytest.param list also
    contains param id string formed from the param name and values.
    """
    return (param_name,
            [pytest.param(v, id=f"{param_name}={v}") for v in param_values])


def _generic_eigenvector_test(src_arr,
                              dst_arr,
                              wgt_arr,
                              result_arr,
                              num_vertices,
                              num_edges,
                              store_transposed,
                              epsilon,
                              max_iterations):
    """
    Builds a graph from the input arrays and runs eigen using the other args,
    similar to how eigen is tested in libcugraph.
    """
    resource_handle = ResourceHandle()
    graph_props = GraphProperties(is_symmetric=False, is_multigraph=False)
    G = SGGraph(resource_handle, graph_props, src_arr, dst_arr, wgt_arr,
                store_transposed=False, renumber=False,
                do_expensive_check=True)

    (vertices, centralities) = eigenvector_centrality(resource_handle, G, None,
                                                      epsilon, max_iterations,
                                                      do_expensive_check=False)

    result_arr = result_arr.get()
    vertices = vertices.get()
    centralities = centralities.get()

    for idx in range(num_vertices):
        vertex_id = vertices[idx]
        expected_result = result_arr[vertex_id]
        actual_result = centralities[idx]
        if pytest.approx(expected_result, 1e-4) != actual_result:
            raise ValueError(f"Vertex {idx} has centrality {actual_result}"
                             f", should have been {expected_result}")


def test_eigenvector():
    num_edges = 8
    num_vertices = 6
    src = cp.asarray([0, 1, 1, 2, 2, 2, 3, 4], dtype=np.int32)
    dst = cp.asarray([1, 3, 4, 0, 1, 3, 5, 5], dtype=np.int32)
    wgt = cp.asarray([0.1, 2.1, 1.1, 5.1, 3.1, 4.1, 7.2, 3.2],
                     dtype=np.float32)
    result = cp.asarray([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32)

    epsilon = 0.000001
    max_iterations = 1000

    # Eigenvector requires store_transposed to be True
    _generic_eigenvector_test(src, dst, wgt, result, num_vertices, num_edges,
                              True, epsilon, max_iterations)
