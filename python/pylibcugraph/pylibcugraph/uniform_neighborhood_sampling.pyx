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

def EXPERIMENTAL__uniform_neighborhood_sampling(input_graph,
                                                start_info_list,
                                                fanout_vals,
                                                bool_t with_replacement):
    """
    Does uniform neighborhood sampling.

    Parameters
    ----------
    input_graph: _MGGraph???

    start_info_list: ???

    fanout_vals: ???

    with_replacement: ???
    """
    print("Hello from uniform_neighborhood_sampling.pyx!")

    c_api_implemented = False
    if c_api_implemented:
        error_code = uniform_nbr_sample(c_resource_handle_ptr,
                           c_graph_ptr,
                           d_start,
                           d_ranks,
                           num_starting_vs,
                           h_fan_out,
                           flag_replacement)
        assert_success(error_code, error_ptr, "uniform_nbr_sample")
        """
        uniform_nbr_sample(raft::handle_t const& handle,
                   graph_view_t const& graph_view,
                   typename graph_view_t::vertex_type const* ptr_d_start,
                   gpu_t const* ptr_d_ranks,
                   size_t num_starting_vs,
                   std::vector<int> const& h_fan_out,
                   bool flag_replacement = true);
        """
    return 0
