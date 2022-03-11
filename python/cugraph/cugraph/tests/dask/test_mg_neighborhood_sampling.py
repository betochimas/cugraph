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
 * @brief Multi-GPU Uniform Neighborhood Sampling.
 * @tparam graph_view_t Type of graph view.
 * @tparam index_t Type used for indexing; typically edge_t
 * @param handle RAFT handle object to encapsulate resources (e.g. CUDA stream, communicator, and
 * handles to various CUDA libraries) to run graph algorithms.
 * @param graph_view Graph View object to generate NBR Sampling on.
 * @param ptr_d_start Device array of pairs: (starting_vertex_index, rank) for the NBR Sampling.
 * @param num_starting_vs size of starting vertex set
 * @param h_fan_out vector of branching out (fan-out) degree per source vertex for each level
 * parameter used for obtaining local out-degree information
 * @param flag_replacement boolean flag specifying if random sampling is done without replacement
 * (true); or, with replacement (false); default = true;
 * @return tuple of tuple of device vectors and counts:
 * ((vertex_t source_vertex, vertex_t destination_vertex, int rank, edge_t index), rx_counts)
 */
template <typename graph_view_t,
          typename gpu_t,
          typename index_t = typename graph_view_t::edge_type>
std::tuple<std::tuple<rmm::device_uvector<typename graph_view_t::vertex_type>,
                      rmm::device_uvector<typename graph_view_t::vertex_type>,
                      rmm::device_uvector<gpu_t>,
                      rmm::device_uvector<index_t>>,
           std::vector<size_t>>
uniform_nbr_sample(raft::handle_t const& handle,
                   graph_view_t const& graph_view,
                   typename graph_view_t::vertex_type const* ptr_d_start,
                   gpu_t const* ptr_d_ranks,
                   size_t num_starting_vs,
                   std::vector<int> const& h_fan_out,
                   bool flag_replacement = true);

template <typename vertex_t, typename edge_t, typename weight_t, typename result_t, bool multi_gpu>
void katz_centrality(raft::handle_t const& handle,
                     graph_view_t<vertex_t, edge_t, weight_t, true, multi_gpu> const& graph_view,
                     result_t const* betas,
                     result_t* katz_centralities,
                     result_t alpha,
                     result_t beta,
                     result_t epsilon,
                     size_t max_iterations   = 500,
                     bool has_initial_guess  = false,
                     bool normalize          = false,
                     bool do_expensive_check = false);
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
def test_dask_neighborhood_sampling(dask_client):
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

    # Test to ensure that df and ddf graphs have same sampling
    # expected_nbr_sample = cugraph.neighb
    result_nbr_sample = dcg.neighborhood_sampling(dg)