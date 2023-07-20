# Copyright (c) 2019-2023, NVIDIA CORPORATION.
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

import sys
from tempfile import NamedTemporaryFile
import math

import cudf
from cupyx.scipy.sparse import coo_matrix as cupy_coo_matrix
import cupy

from cugraph.testing import ResultSet, ResultSet2
import pytest

import cugraph


CONNECTED_GRAPH = """1,5,3
1,4,1
1,2,1
1,6,2
1,7,2
4,5,1
2,3,1
7,6,2
"""

DISCONNECTED_GRAPH = CONNECTED_GRAPH + "8,9,4"

paths_results = ResultSet(local_result_file="paths_results.pkl")

"""paths_results2 = {'1,1,connected,nx': 0, '1,1,connected,cu': 0.0,
                  '1,5,connected,nx': 2.0, '1,5,connected,cu': 2.0,
                  '1,3,connected,nx': 2.0, '1,3,connected,cu': 2.0,
                  '1,6,connected,nx': 2.0, '1,6,connected,cu': 2.0,
                  '-1,1,connected,invalid': 'ValueError',
                  '0,42,connected,invalid': 'ValueError',
                  '1,10,disconnected,invalid': 'ValueError',
                  '1,8,disconnected,invalid': 3.4028235e+38}"""
connected_test_data = [
    ["1", "1", "nx", 0],
    ["1", "1", "cu", 0.0],
    ["1", "5", "nx", 2.0],
    ["1", "5", "cu", 2.0],
    ["1", "3", "nx", 2.0],
    ["1", "3", "cu", 2.0],
    ["1", "6", "nx", 2.0],
    ["1", "6", "cu", 2.0],
    ["-1", "1", "invalid", ValueError],
    ["0", "42", "invalid", ValueError]
]
disconnected_test_data = [
    ["1", "10", "invalid", ValueError],
    ["1", "8", "invalid", 3.4028235e+38]
]

# The above can be saved as a result within the same file, however dicts and dataframes can't
# We would create results files within
# '1,notarget,nx': {'1': 0, '4': 1.0, '2': 1.0, '6': 2.0, '7': 2.0, '5': 2.0, '3': 2.0}
# '1,notarget,cu': {'1': 0, '4': 1.0, '2': 1.0, '6': 2.0, '7': 2.0, '5': 2.0, '3': 2.0}

@pytest.fixture
def graphs(request):
    with NamedTemporaryFile(mode="w+", suffix=".csv") as graph_tf:
        graph_tf.writelines(request.param)
        graph_tf.seek(0)

        cudf_df = cudf.read_csv(
            graph_tf.name,
            names=["src", "dst", "data"],
            delimiter=",",
            dtype=["int32", "int32", "float64"],
        )
        cugraph_G = cugraph.Graph()
        cugraph_G.from_cudf_edgelist(
            cudf_df, source="src", destination="dst", edge_attr="data"
        )

        # construct cupy coo_matrix graph
        i = []
        j = []
        weights = []
        for index in range(cudf_df.shape[0]):
            vertex1 = cudf_df.iloc[index]["src"]
            vertex2 = cudf_df.iloc[index]["dst"]
            weight = cudf_df.iloc[index]["data"]
            i += [vertex1, vertex2]
            j += [vertex2, vertex1]
            weights += [weight, weight]
        i = cupy.array(i)
        j = cupy.array(j)
        weights = cupy.array(weights)
        largest_vertex = max(cupy.amax(i), cupy.amax(j))
        cupy_df = cupy_coo_matrix(
            (weights, (i, j)), shape=(largest_vertex + 1, largest_vertex + 1)
        )

        yield cugraph_G, cupy_df


@pytest.mark.sg
@pytest.mark.parametrize("graphs", [CONNECTED_GRAPH], indirect=True)
def test_connected_graph_shortest_path_length(graphs):
    cugraph_G, cupy_df = graphs

    path_1_to_1_length = cugraph.shortest_path_length(cugraph_G, 1, 1)
    assert path_1_to_1_length == 0.0
    assert path_1_to_1_length == paths_results.results["1,1,connected,nx"]
    assert path_1_to_1_length == paths_results.results["1,1,connected,cu"]
    assert path_1_to_1_length == cugraph.shortest_path_length(cupy_df, 1, 1)

    path_1_to_5_length = cugraph.shortest_path_length(cugraph_G, 1, 5)
    assert path_1_to_5_length == 2.0
    assert path_1_to_5_length == paths_results.results["1,5,connected,nx"]
    assert path_1_to_5_length == paths_results.results["1,5,connected,cu"]
    assert path_1_to_5_length == cugraph.shortest_path_length(cupy_df, 1, 5)

    path_1_to_3_length = cugraph.shortest_path_length(cugraph_G, 1, 3)
    assert path_1_to_3_length == 2.0
    assert path_1_to_3_length == paths_results.results["1,3,connected,nx"]
    assert path_1_to_3_length == paths_results.results["1,3,connected,cu"]
    assert path_1_to_3_length == cugraph.shortest_path_length(cupy_df, 1, 3)

    path_1_to_6_length = cugraph.shortest_path_length(cugraph_G, 1, 6)
    assert path_1_to_6_length == 2.0
    assert path_1_to_6_length == paths_results.results["1,6,connected,nx"]
    assert path_1_to_6_length == paths_results.results["1,6,connected,cu"]
    assert path_1_to_6_length == cugraph.shortest_path_length(cupy_df, 1, 6)


@pytest.mark.sg
@pytest.mark.parametrize("graphs", [CONNECTED_GRAPH], indirect=True)
def test_shortest_path_length_invalid_source(graphs):
    cugraph_G, cupy_df = graphs

    with pytest.raises(ValueError):
        cugraph.shortest_path_length(cugraph_G, -1, 1)

    assert "ValueError" == paths_results.results["-1,1,connected,invalid"]

    with pytest.raises(ValueError):
        cugraph.shortest_path_length(cupy_df, -1, 1)


@pytest.mark.sg
@pytest.mark.parametrize("graphs", [DISCONNECTED_GRAPH], indirect=True)
def test_shortest_path_length_invalid_target(graphs):
    cugraph_G, cupy_df = graphs

    with pytest.raises(ValueError):
        cugraph.shortest_path_length(cugraph_G, 1, 10)

    assert "ValueError" == paths_results.results["1,10,disconnected,invalid"]

    with pytest.raises(ValueError):
        cugraph.shortest_path_length(cupy_df, 1, 10)


@pytest.mark.sg
@pytest.mark.parametrize("graphs", [CONNECTED_GRAPH], indirect=True)
def test_shortest_path_length_invalid_vertexes(graphs):
    cugraph_G, cupy_df = graphs

    with pytest.raises(ValueError):
        cugraph.shortest_path_length(cugraph_G, 0, 42)

    assert "ValueError" == paths_results.results["0,42,connected,invalid"]

    with pytest.raises(ValueError):
        cugraph.shortest_path_length(cupy_df, 0, 42)


@pytest.mark.sg
@pytest.mark.parametrize("graphs", [DISCONNECTED_GRAPH], indirect=True)
def test_shortest_path_length_no_path(graphs):
    cugraph_G, cupy_df = graphs

    # FIXME: In case there is no path between two vertices, the
    # result can be either the max of float32 or float64
    max_float_32 = (2 - math.pow(2, -23)) * math.pow(2, 127)

    path_1_to_8 = cugraph.shortest_path_length(cugraph_G, 1, 8)
    assert path_1_to_8 == sys.float_info.max
    assert paths_results.results["1,8,disconnected,invalid"] in [
        max_float_32,
        path_1_to_8,
    ]
    assert path_1_to_8 == cugraph.shortest_path_length(cupy_df, 1, 8)


@pytest.mark.sg
@pytest.mark.parametrize("graphs", [DISCONNECTED_GRAPH], indirect=True)
def test_shortest_path_length_no_target(graphs):
    cugraph_G, cupy_df = graphs

    cugraph_path_1_to_all = cugraph.shortest_path_length(cugraph_G, 1)
    #nx_path_1_to_all = paths_results.results["1,notarget,nx"]
    #nx_gpu_path_1_to_all = cudf.DataFrame.from_dict(
    #    paths_results.results["1,notarget,cu"]
    #)
    nx_path_1_to_all = ResultSet2(
        lib="nx", alg="shortest_path_length", graph="DISCONNECTEDnx", param="1"
    ).results
    nx_path_1_to_all = nx_path_1_to_all.rename(columns={"Unnamed: 0": "vertex", "0": "distance"})
    nx_path_1_to_all = nx_path_1_to_all.reset_index("vertex").to_dict()["distance"]

    nx_gpu_path_1_to_all = ResultSet2(
        lib="cugraph", alg="shortest_path_length", graph="DISCONNECTEDnx", param="1"
    ).results
    cupy_path_1_to_all = cugraph.shortest_path_length(cupy_df, 1)
    #breakpoint()

    # Cast networkx graph on cugraph vertex column type from str to int.
    # SSSP preserves vertex type, convert for comparison
    nx_gpu_path_1_to_all["vertex"] = nx_gpu_path_1_to_all["vertex"].astype("int32")
    assert cugraph_path_1_to_all == nx_gpu_path_1_to_all
    assert cugraph_path_1_to_all == cupy_path_1_to_all
    #breakpoint()
    # results for vertex 8 and 9 are not returned
    assert cugraph_path_1_to_all.shape[0] == len(nx_path_1_to_all) + 2

    for index in range(cugraph_path_1_to_all.shape[0]):

        vertex = str(cugraph_path_1_to_all["vertex"][index].item())
        distance = cugraph_path_1_to_all["distance"][index].item()
        breakpoint()
        # verify cugraph against networkx
        if vertex in {"8", "9"}:
            # Networkx does not return distances for these vertexes.
            assert distance == sys.float_info.max
        else:
            assert distance == nx_path_1_to_all[vertex]
