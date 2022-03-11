# Copyright (c) 2022, NVIDIA CORPORATION.:
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


"""
/**
 * @brief Compute HITS scores.
 *
 * This function computes HITS scores for the vertices of a graph
 *
 * @throws cugraph::logic_error on erroneous input arguments
 *
 * @tparam vertex_t Type of vertex identifiers. Needs to be an integral type.
 * @tparam edge_t Type of edge identifiers. Needs to be an integral type.
 * @tparam weight_t Type of edge weights. Needs to be a floating point type.
 * @tparam multi_gpu Flag indicating whether template instantiation should target single-GPU (false)
 * or multi-GPU (true).
 * @param handle RAFT handle object to encapsulate resources (e.g. CUDA stream, communicator, and
 * handles to various CUDA libraries) to run graph algorithms.
 * @param graph_view Graph view object.
 * @param hubs Pointer to the input/output hub score array.
 * @param authorities Pointer to the output authorities score array.
 * @param epsilon Error tolerance to check convergence. Convergence is assumed if the sum of the
 * differences in hub values between two consecutive iterations is less than @p epsilon
 * @param max_iterations Maximum number of HITS iterations.
 * @param has_initial_guess If set to `true`, values in the hubs output array (pointed by @p
 * hubs) is used as initial hub values. If false, initial hub values are set to 1.0
 * divided by the number of vertices in the graph.
 * @param normalize If set to `true`, final hub and authority scores are normalized (the L1-norm of
 * the returned hub and authority score arrays is 1.0) before returning.
 * @param do_expensive_check A flag to run expensive checks for input arguments (if set to `true`).
 * @return std::tuple<weight_t, size_t> A tuple of sum of the differences of hub scores of the last
 * two iterations and the total number of iterations taken to reach the final result
 */
template <typename vertex_t, typename edge_t, typename weight_t, bool multi_gpu>
std::tuple<weight_t, size_t> hits(
  raft::handle_t const& handle,
  graph_view_t<vertex_t, edge_t, weight_t, true, multi_gpu> const& graph_view,
  weight_t* hubs,
  weight_t* authorities,
  weight_t epsilon,
  size_t max_iterations,
  bool has_initial_hubs_guess,
  bool normalize,
  bool do_expensive_check);
"""

import cugraph.dask as dcg
import gc
import pytest
import cugraph
import dask_cudf
import cudf
from cugraph.dask.common.mg_utils import is_single_gpu
from cugraph.tests.utils import RAPIDS_DATASET_ROOT_DIR_PATH

@pytest.mark.skipif(
    is_single_gpu(), reason="skipping MG testing on Single GPU system"
)
def test_dask_hits(dask_client):
    gc.collect()

    input_data_path = (RAPIDS_DATASET_ROOT_DIR_PATH /
                       "karate.csv").as_posix()
    print(f"dataset={input_data_path}")
    chunksize = dcg.get_chunksize(input_data_path)

    ddf = dask_cudf.read_csv(
        input_data_path,
        chunksize=chunksize,
        delimiter=" ",
        names=["src", "dst", "value"],
        dtype=["int32", "int32", "float32"],
    )

    df = cudf.read_csv(
        input_data_path,
        delimiter=" ",
        names=["src", "dst", "value"],
        dtype=["int32", "int32", "float32"],
    )

    g = cugraph.DiGraph()
    g.from_cudf_edgelist(df, "src", "dst")

    dg = cugraph.DiGraph()
    dg.from_dask_cudf_edgelist(ddf, "src", "dst")

    expected_hits = cugraph.hits(g)
    result_hits = dcg.hits(dg)