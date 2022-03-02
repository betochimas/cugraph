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

from dask.distributed import wait, default_client
from cugraph.dask.common.input_utils import (get_distributed_data,
                                             get_vertex_partition_offsets)
from pylibcugraph.experimental import hits as mg_hits
import cugraph.comms.comms as Comms
import dask_cudf
# from cugraph.utilities import ensure_cugraph_obj_for_nx


def call_hits(sID,
              data,
              src_col_name,
              dst_col_name,
              num_verts,
              num_edges,
              vertex_partition_offsets,
              aggregate_segment_offsets,
              max_iter,
              tol,
              nstart,
              normalized):
    wid = Comms.get_worker_id(sID)
    handle = Comms.get_handle(sID)
    local_size = len(aggregate_segment_offsets) // Comms.get_n_workers(sID)
    segment_offsets = \
        aggregate_segment_offsets[local_size * wid: local_size * (wid + 1)]
    # NOTE: This will require updating once the C HITS api is ready
    return mg_hits(data[0],
                   src_col_name,
                   dst_col_name,
                   num_verts,
                   num_edges,
                   vertex_partition_offsets,
                   wid,
                   handle,
                   segment_offsets,
                   max_iter,
                   tol,
                   nstart,
                   normalized)
    """
    return mg_hits(handle,
                graph,
                max_iter,
                tol,
                nstart,
                normalized,
                do_expensive_check)
    """


def hits(input_graph, max_iter=100, tol=1.0e-5, nstart=None, normalized=True):
    """
    Compute HITS hubs and authorities values for each vertex using multiple
    GPUs.

    Parameters
    ----------
    input_graph : cugraph.Graph
        cuGraph graph descriptor, should contain the connectivity information
        as an edge list (edge weights are not used for this algorithm). The
        adjacency list will be computed if not already present.

    max_iter : int, optional (default=100)

    tol : float, optional (default=1.0e-5)

    nstart : cudf.Dataframe, optional (default=None)

    normalized : bool, optional (default=True)

    Returns
    -------
    HubsAndAuthorities : dask_cudf.DataFrame
        GPU data frame containing three dask_cudf.Series of size V: the vertex
        identifiers and the corresponding hubs values and the corresponding
        authorities values.

        ddf['vertex'] : dask_cudf.Series
            Contains the vertex identifiers
        ddf['hubs'] : dask_cudf.Series
            Contains the hubs score
        ddf['authorities'] : dask_cudf.Series
            Contains the authorities score
    """
    # note: signature for pylib HITS is
    # hits(handle, graph, max_iter, tol, nstart, normalized, do_exp_check),
    # compared to node2vec's, which is/was
    # node2vec(handle, graph, src_array, max_depth, compress_result, p, q)
    nstart = None

    client = default_client()

    input_graph.compute_renumber_edge_list(transposed=True)
    ddf = input_graph.edgelist.edgelist_df
    vertex_partition_offsets = get_vertex_partition_offsets(input_graph)
    num_verts = vertex_partition_offsets.iloc[-1]
    num_edges = len(ddf)
    data = get_distributed_data(ddf)

    src_col_name = input_graph.renumber_map.renumbered_src_col_name
    dst_col_name = input_graph.renumber_map.renumbered_dst_col_name

    result = [client.submit(call_hits,
                            Comms.get_session_id(),
                            wf[1],
                            src_col_name,
                            dst_col_name,
                            num_verts,
                            num_edges,
                            vertex_partition_offsets,
                            input_graph.aggregate_segment_offsets,
                            max_iter,
                            tol,
                            nstart,
                            normalized,
                            workers=[wf[0]])
              for idx, wf in enumerate(data.worker_to_parts.items())]
    wait(result)
    ddf = dask_cudf.from_delayed(result)
    if input_graph.renumbered:
        return input_graph.unrenumber(ddf, 'vertex')

    return ddf
