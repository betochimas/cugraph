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

import pylibcugraph
import cudf
from cugraph.utilities import ensure_cugraph_obj_for_nx


def call_hits(SID,
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
    return 0

def hits(input_graph, max_iter=100, tol=1.0e-5, nstart=None, normalized=True):
    """
    Compute HITS hubs and authorities values for each vertex using multiple GPUs.

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