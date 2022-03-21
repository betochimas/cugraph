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
from pylibcugraph.experimental import ResourceHandle, GraphProperties, SGGraph


# =============================================================================
# Test data
# =============================================================================
# The result names correspond to the datasets defined in conftest.py
# Note: the only deterministic path(s) in the following datasets
# are contained in Simple_1
_test_data = {"karate.csv": {
                  "seeds": cp.asarray([0, 0], dtype=np.int32),
                  "paths": cp.asarray([0, 8, 33, 29, 26, 0, 1, 3, 13, 33],
                                      dtype=np.int32),
                  "weights": cp.asarray([1., 1., 1., 1., 1., 1., 1., 1.],
                                        dtype=np.float32),
                  "path_sizes": cp.asarray([5, 5], dtype=np.int32),
                  "max_depth": 5
                  },
              "dolphins.csv": {
                  "seeds": cp.asarray([11], dtype=np.int32),
                  "paths": cp.asarray([11, 51, 11, 51],
                                      dtype=np.int32),
                  "weights": cp.asarray([1., 1., 1.],
                                        dtype=np.float32),
                  "path_sizes": cp.asarray([4], dtype=np.int32),
                  "max_depth": 4
                  },
              "Simple_1": {
                  "seeds": cp.asarray([0, 3], dtype=np.int32),
                  "paths": cp.asarray([0, 1, 2, 3],
                                      dtype=np.int32),
                  "weights": cp.asarray([1., 1.],
                                        dtype=np.float32),
                  "path_sizes": cp.asarray([3, 1], dtype=np.int32),
                  "max_depth": 3
                  },
              "Simple_2": {
                  "seeds": cp.asarray([0, 3], dtype=np.int32),
                  "paths": cp.asarray([0, 1, 3, 5, 3, 5],
                                      dtype=np.int32),
                  "weights": cp.asarray([0.1, 2.1, 7.2, 7.2],
                                        dtype=np.float32),
                  "path_sizes": cp.asarray([4, 2], dtype=np.int32),
                  "max_depth": 4
                  },
              }
_test_data_2 = {"karate.csv": {
                    "seeds": cp.asarray([], dtype=np.int32),
                    "path_sizes": cp.asarray([], dtype=np.int32),
                    "max_depth": 0
                    },
                "dolphins.csv": {
                    "seeds": cp.asarray([], dtype=np.int32),
                    "path_sizes": cp.asarray([], dtype=np.int32),
                    "max_depth": 0
                    },
                }

# =============================================================================
# Pytest fixtures
# =============================================================================
# fixtures used in this test module are defined in conftest.py


# =============================================================================
# Tests
# =============================================================================

@pytest.mark.parametrize("compress_result", [True, False])
def test_node2vec(sg_graph_objs, compress_result):
    from pylibcugraph.experimental import node2vec

    (g, resource_handle, ds_name) = sg_graph_objs

    (seeds, expected_paths, expected_weights, expected_path_sizes, max_depth) \
        = _test_data[ds_name].values()

    p = 0.8
    q = 0.5

    result = node2vec(resource_handle, g, seeds, max_depth,
                      compress_result, p, q)

    (actual_paths, actual_weights, actual_path_sizes) = result
    num_paths = len(seeds)

    if compress_result:
        assert actual_paths.dtype == expected_paths.dtype
        assert actual_weights.dtype == expected_weights.dtype
        assert actual_path_sizes.dtype == expected_path_sizes.dtype
        actual_paths = actual_paths.tolist()
        actual_weights = actual_weights.tolist()
        actual_path_sizes = actual_path_sizes.tolist()
        exp_paths = expected_paths.tolist()
        exp_weights = expected_weights.tolist()
        exp_path_sizes = expected_path_sizes.tolist()
        # If compress_results is True, then also verify path lengths match
        # up with weights array
        assert len(actual_path_sizes) == num_paths
        expected_walks = sum(exp_path_sizes) - num_paths
        # Verify the number of walks was equal to path sizes - num paths
        assert len(actual_weights) == expected_walks
    else:
        assert actual_paths.dtype == expected_paths.dtype
        assert actual_weights.dtype == expected_weights.dtype
        actual_paths = actual_paths.tolist()
        actual_weights = actual_weights.tolist()
        exp_paths = expected_paths.tolist()
        exp_weights = expected_weights.tolist()

    # Verify exact walks chosen for linear graph Simple_1
    if ds_name == 'Simple_1':
        for i in range(len(exp_paths)):
            assert pytest.approx(actual_paths[i], 1e-4) == exp_paths[i]
        for i in range(len(exp_weights)):
            assert pytest.approx(actual_weights[i], 1e-4) == exp_weights[i]

    # Verify starting vertex of each path is the corresponding seed
    if compress_result:
        path_start = 0
        for i in range(num_paths):
            assert actual_path_sizes[i] == exp_path_sizes[i]
            assert actual_paths[path_start] == seeds[i]
            path_start += actual_path_sizes[i]


def test_generic_node2vec(src_arr,
                          dst_arr,
                          wgt_arr,
                          seeds,
                          num_vertices,
                          num_edges,
                          num_seeds,
                          max_depth,
                          compressed_result,
                          p,
                          q,
                          renumbered):
    from pylibcugraph.experimental import node2vec

    resource_handle = ResourceHandle()
    graph_props = GraphProperties(is_symmetric=False, is_multigraph=False)
    G = SGGraph(resource_handle, graph_props, src_arr, dst_arr, wgt_arr,
                store_transposed=False, renumber=renumbered,
                do_expensive_check=False)
    (paths, weights, sizes) = node2vec(resource_handle, G, seeds, max_depth,
                                       compressed_result, p, q)
    paths = paths.get()
    weights = weights.get()
    # if max_depth == 5:
    #     breakpoint()

    # Validating results of node2vec by checking each path
    M = np.zeros((num_vertices, num_vertices), dtype=np.float64)
    # breakpoint()
    for i in range(num_edges):
        M[src_arr.get()[i]][dst_arr.get()[i]] = wgt_arr.get()[i]

    if compressed_result:
        path_offsets = np.zeros(num_seeds + 1, dtype=np.int32)
        path_offsets[0] = 0
        for i in range(num_seeds):
            path_offsets[i + 1] = path_offsets[i] + sizes.get()[i]

        for i in range(num_seeds):
            for j in range(path_offsets[i], path_offsets[i + 1]):
                actual_wgt = weights[j - i]
                expected_wgt = M[paths[j]][paths[j + 1]]
                if pytest.approx(expected_wgt, 1e-4) != actual_wgt:
                    raise ValueError("Edge ({},{}) has wgt {}, should \
                                     have been {}".format(paths[j],
                                                          paths[j+1],
                                                          actual_wgt,
                                                          expected_wgt))
    else:
        for i in range(num_seeds):
            for j in range(max_depth - 1):
                curr_idx = i * max_depth + j
                if paths[curr_idx] != num_vertices:
                    actual_wgt = weights[i * (max_depth - 1) + j]
                    expected_wgt = M[paths[curr_idx]][paths[curr_idx + 1]]
                    if pytest.approx(expected_wgt, 1e-4) != actual_wgt:
                        raise ValueError("Edge ({},{}) has wgt {}, should \
                                        have been {}".format(paths[j],
                                                             paths[j+1],
                                                             actual_wgt,
                                                             expected_wgt))


def test_node2vec_short():
    num_edges = 8
    num_vertices = 6
    src = cp.asarray([0, 1, 1, 2, 2, 2, 3, 4])
    dst = cp.asarray([1, 3, 4, 0, 1, 3, 5, 5])
    wgt = cp.asarray([0.1, 2.1, 1.1, 5.1, 3.1, 4.1, 7.2, 3.2])
    seeds = cp.asarray([0, 0])
    max_depth = 4

    test_generic_node2vec(src, dst, wgt, seeds, num_vertices, num_edges,
                          2, max_depth, False, 0.8, 0.5, False)


def test_node2vec_short_dense():
    num_edges = 8
    num_vertices = 6
    src = cp.asarray([0, 1, 1, 2, 2, 2, 3, 4])
    dst = cp.asarray([1, 3, 4, 0, 1, 3, 5, 5])
    wgt = cp.asarray([0.1, 2.1, 1.1, 5.1, 3.1, 4.1, 7.2, 3.2])
    seeds = cp.asarray([2, 3])
    max_depth = 4

    test_generic_node2vec(src, dst, wgt, seeds, num_vertices, num_edges,
                          2, max_depth, False, 0.8, 0.5, False)


def test_node2vec_short_sparse():
    num_edges = 8
    num_vertices = 6
    src = cp.asarray([0, 1, 1, 2, 2, 2, 3, 4])
    dst = cp.asarray([1, 3, 4, 0, 1, 3, 5, 5])
    wgt = cp.asarray([0.1, 2.1, 1.1, 5.1, 3.1, 4.1, 7.2, 3.2])
    seeds = cp.asarray([2, 3])
    max_depth = 4

    test_generic_node2vec(src, dst, wgt, seeds, num_vertices, num_edges,
                          2, max_depth, True, 0.8, 0.5, False)


@pytest.mark.parametrize("compress_result", [True, False])
@pytest.mark.parametrize("renumbered", [True, False])
def test_node2vec_karate(compress_result, renumbered):
    num_edges = 156
    num_vertices = 34
    src = cp.asarray([1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 17, 19, 21, 31,
                      2, 3, 7, 13, 17, 19, 21, 30, 3, 7, 8, 9, 13, 27, 28,
                      32, 7, 12, 13, 6, 10, 6, 10, 16, 16, 30, 32, 33, 33,
                      33, 32, 33, 32, 33, 32, 33, 33, 32, 33, 32, 33, 25, 27,
                      29, 32, 33, 25, 27, 31, 31, 29, 33, 33, 31, 33, 32, 33,
                      32, 33, 32, 33, 33, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2,
                      2, 2, 3, 3, 3, 4, 4, 5, 5, 5, 6, 8, 8, 8, 9, 13, 14,
                      14, 15, 15, 18, 18, 19, 20, 20, 22, 22, 23, 23, 23, 23,
                      23, 24, 24, 24, 25, 26, 26, 27, 28, 28, 29, 29, 30, 30,
                      31, 31, 32])
    dst = cp.asarray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1,
                      1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 4,
                      4, 5, 5, 5, 6, 8, 8, 8, 9, 13, 14, 14, 15, 15, 18, 18,
                      19, 20, 20, 22, 22, 23, 23, 23, 23, 23, 24, 24, 24, 25,
                      26, 26, 27, 28, 28, 29, 29, 30, 30, 31, 31, 32, 1, 2,
                      3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 17, 19, 21, 31, 2, 3,
                      7, 13, 17, 19, 21, 30, 3, 7, 8, 9, 13, 27, 28, 32, 7,
                      12, 13, 6, 10, 6, 10, 16, 16, 30, 32, 33, 33, 33, 32,
                      33, 32, 33, 32, 33, 33, 32, 33, 32, 33, 25, 27, 29, 32,
                      33, 25, 27, 31, 31, 29, 33, 33, 31, 33, 32, 33, 32, 33,
                      32, 33, 33])
    wgt = cp.asarray([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      1.0, 1.0])
    seeds = cp.asarray([12, 28, 20, 23, 15, 26])
    max_depth = 5

    test_generic_node2vec(src, dst, wgt, seeds, num_vertices, num_edges,
                          2, max_depth, compress_result, 0.8, 0.5, renumbered)
