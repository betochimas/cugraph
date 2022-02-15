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


# =============================================================================
# Test data
# =============================================================================
# _alpha = 0.85
# _epsilon = 1.0e-6
# _max_iterations = 500

"""
_test_data = {"karate.csv": {

                  },
              "dolphins.csv": {

                  },
              "Simple_1": {

                  },
              "Simple_2": {

                  },
              }

# The result names correspond to the datasets defined in conftest.py
_test_data = {"karate.csv": {
                  "start_vertex": 1,
                  "vertex": cp.asarray(range(34), dtype=np.int32),
                  "distance": cp.asarray(
                      [1., 0., 1., 1., 2., 2., 2., 1., 2., 2., 2., 2., 2., 1.,
                       3., 3., 3., 1., 3., 1., 3., 1., 3., 3., 3., 3., 3., 2.,
                       2., 3., 1., 2., 2., 2.,
                       ],
                      dtype=np.float32),
                  "predecessor": cp.asarray(
                      [1, -1, 1, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 1, 32,
                       32, 5, 1, 32, 1, 32, 1, 32, 32, 27, 31, 33, 2, 2, 32,
                       1, 0, 2, 13,
                       ],
                      dtype=np.int32),
                  },
              "dolphins.csv": {
                  "start_vertex": 1,
                  "vertex": cp.asarray(range(62), dtype=np.int32),
                  "distance": cp.asarray(
                      [3., 0., 4., 3., 4., 3., 2., 2., 2., 2., 3., 4., 4., 2.,
                       3., 3., 3., 1., 3., 1., 2., 3., 2., 2., 4., 2., 1., 1.,
                       1., 4., 2., 2., 3., 3., 3., 5., 1., 2., 3., 2., 2., 1.,
                       3., 3., 3., 3., 4., 2., 3., 4., 3., 3., 3., 4., 1., 4.,
                       3., 2., 4., 2., 4., 3.,
                       ],
                      dtype=np.float32),
                  "predecessor": cp.asarray(
                      [40, -1, 10, 59, 51, 13, 54, 54, 28, 41, 47, 51, 33, 41,
                       37, 40, 37, 1, 20, 1, 28, 37, 17, 36, 45, 17, 1, 1,
                       1, 10, 19, 17, 9, 37, 37, 29, 1, 36, 20, 36, 36, 1,
                       30, 37, 20, 23, 43, 28, 57, 34, 20, 23, 40, 43, 1, 51,
                       6, 41, 38, 36, 32, 37,
                       ],
                      dtype=np.int32),
                   },
              "Simple_1": {
                  "start_vertex": 1,
                  "vertex": cp.asarray(range(4), dtype=np.int32),
                  "distance": cp.asarray(
                      [3.4028235e+38, 0.0000000e+00, 1.0000000e+00,
                       2.0000000e+00,
                       ],
                      dtype=np.float32),
                  "predecessor": cp.asarray(
                      [-1, -1,  1,  2,
                       ],
                      dtype=np.int32),
                   },
              "Simple_2": {
                  "start_vertex": 1,
                  "vertex": cp.asarray(range(6), dtype=np.int32),
                  "distance": cp.asarray(
                      [3.4028235e+38, 0.0000000e+00, 3.4028235e+38,
                       2.0999999e+00, 1.1000000e+00, 4.3000002e+00
                       ],
                      dtype=np.float32),
                  "predecessor": cp.asarray(
                      [-1, -1, -1,  1,  1,  4,
                       ],
                      dtype=np.int32),
                   },
              }
"""
# =============================================================================
# Pytest fixtures
# =============================================================================
# fixtures used in this test module are defined in conftest.py


# =============================================================================
# Tests
# =============================================================================
def test_node2vec(sg_graph_objs):
    from pylibcugraph.experimental import node2vec

    (g, resource_handle, ds_name) = sg_graph_objs

    (seeds,
    expected_paths,
    expected_weights,
    expected_offsets) = _test_data[ds_name].values()

    max_depth = 4
    compress_result = False
    p = 0.8
    q = 0.5

    result = node2vec(resource_handle,
                      g,
                      seeds,
                      max_depth,
                      compress_result,
                      p,
                      q)


    (actual_paths, actual_weights, actual_offsets) = result

    # NOTE: This is not the actual check, but regardless should be expected to
    # fail at current moment
    num_walks = len(actual_paths)
    for i in range(num_walks):
        assert actual_paths[i] == expected_paths[i]
        assert actual_weights[i] == expected_weights[i]
