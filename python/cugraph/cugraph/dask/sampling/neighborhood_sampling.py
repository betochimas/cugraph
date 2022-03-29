# Copyright (c) 2022, NVIDIA CORPORATION.
#
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

from dask.distributed import wait, default_client
from cugraph.dask.common.input_utils import get_distributed_data
import cugraph.comms.comms as Comms
import dask_cudf
import pylibcugraph.experimental as pylibcugraph
import cudf


def call_nbr_sampling(sID,
                      data,
                      src_col_name,
                      dst_col_name,
                      num_edges,
                      do_expensive_check,
                      start_list,
                      info_list,
                      h_fan_out,
                      with_replacement):

    # Preparation for graph creation
    handle = Comms.get_handle(sID)
    handle = pylibcugraph.ResourceHandle(handle.getHandle())
    graph_properties = pylibcugraph.GraphProperties(
        is_multigraph=False)
    srcs = data[0][src_col_name]
    dsts = data[0][dst_col_name]
    weights = None
    if "value" in data[0].columns:
        weights = data[0]['value']

    mg = pylibcugraph.MGGraph(handle,
                              graph_properties,
                              srcs,
                              dsts,
                              weights,
                              False,
                              num_edges,
                              do_expensive_check)

    return pylibcugraph.uniform_neighborhood_sampling(handle,
                                                      mg,
                                                      start_list,
                                                      info_list,
                                                      h_fan_out,
                                                      with_replacement,
                                                      do_expensive_check)


def convert_to_cudf(cp_arrays):
    """
    Creates a cudf DataFrame from cupy arrays from pylibcugraph wrapper
    """
    cupy_sources, cupy_destinations, cupy_labels, cupy_indices = cp_arrays
    # cupy_sources, cupy_destinations, cupy_labels, cupy_indices,
    #    cupy_counts = cp_arrays
    df = cudf.DataFrame()
    df["sources"] = cupy_sources
    df["destinations"] = cupy_destinations
    df["labels"] = cupy_labels
    df["indices"] = cupy_indices
    # df["counts"] = cupy_counts
    return df


def EXPERIMENTAL__uniform_neighborhood(input_graph,
                                       start_info_list,
                                       fanout_vals,
                                       with_replacement=True):
    """
    Does neighborhood sampling, which samples nodes from a graph based on the
    current node's neighbors, with a corresponding fanout value at each hop.

    Parameters
    ----------
    input_graph : cugraph.DiGraph
        cuGraph graph, which contains connectivity information as dask cudf
        edge list dataframe

    start_info_list : tuple of list or cudf.Series
        Tuple of a list of starting vertices for sampling, along with a
        corresponding list of label for reorganizing results after sending
        the input to different callers.

    fanout_vals : list or cudf.Series
        List of branching out (fan-out) degrees per starting vertex for each
        hop level.

    with_replacement: bool, optional (default=True)
        Flag to specify if the random sampling is done with replacement

    Returns
    -------
    result : dask_cudf.DataFrame
        GPU data frame containing two dask_cudf.Series

        ddf['srcs']: dask_cudf.Series
            Contains the source vertices from the sampling result
        ddf['dsts']: dask_cudf.Series
            Contains the destination vertices from the sampling result
        ddf['labels']: dask_cudf.Series
            Contains the start labels from the sampling result
        ddf['index']: dask_cudf.Series
            Contains the indices from the sampling result
        ddf['counts']: dask_cudf.Series
            Contains the transaction counts from the sampling result,
            not implemented
    """
    # Initialize dask client
    client = default_client()
    # Important for handling renumbering
    input_graph.compute_renumber_edge_list(transposed=True)

    start_list, info_list = start_info_list

    if isinstance(start_list, list):
        start_list = cudf.Series(start_list)
    if isinstance(info_list, list):
        info_list = cudf.Series(info_list)
    if isinstance(fanout_vals, list):
        fanout_vals = cudf.Series(fanout_vals)

    ddf = input_graph.edgelist.edgelist_df
    num_edges = len(ddf)
    data = get_distributed_data(ddf)

    src_col_name = input_graph.renumber_map.renumbered_src_col_name
    dst_col_name = input_graph.renumber_map.renumbered_dst_col_name

    result = [client.submit(call_nbr_sampling,
                            Comms.get_session_id(),
                            wf[1],
                            src_col_name,
                            dst_col_name,
                            num_edges,
                            False,
                            start_list,
                            info_list,
                            fanout_vals,
                            with_replacement,
                            workers=[wf[0]])
              for idx, wf in enumerate(data.worker_to_parts.items())]

    wait(result)

    cudf_result = [client.submit(convert_to_cudf,
                                 cp_arrays)
                   for cp_arrays in result]

    wait(cudf_result)

    ddf = dask_cudf.from_delayed(cudf_result)
    if input_graph.renumbered:
        return input_graph.unrenumber(ddf, 'vertex')

    return ddf
