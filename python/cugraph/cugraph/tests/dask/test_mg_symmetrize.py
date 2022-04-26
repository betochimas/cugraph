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

import gc

import pytest

import pandas as pd
import cudf
import cugraph
from cugraph.tests import utils
from cugraph.dask.common.mg_utils import (is_single_gpu,
                                          setup_local_dask_cluster,
                                          teardown_local_dask_cluster)


def test_version():
    gc.collect()
    cugraph.__version__


@pytest.fixture(scope="module")
def client_connection():
    (cluster, client) = setup_local_dask_cluster(p2p=True)
    yield client
    teardown_local_dask_cluster(cluster, client)


@pytest.mark.skipif(
    is_single_gpu(), reason="skipping MG testing on Single GPU system"
)
@pytest.mark.parametrize("graph_file", utils.DATASETS_UNDIRECTED)
def test_mg_symmetrize(graph_file, client_connection):
    gc.collect()

    ddf = utils.read_dask_cudf_csv_file(graph_file)
    sym_src, sym_dst = cugraph.symmetrize(ddf["src"], ddf["dst"])

    # convert to regular cudf to facilitate comparison
    df = ddf.compute()

    compare(
        df["src"], df["dst"], None, sym_src.compute(), sym_dst.compute(), None
    )


@pytest.mark.skipif(
    is_single_gpu(), reason="skipping MG testing on Single GPU system"
)
@pytest.mark.parametrize("graph_file", utils.DATASETS_UNDIRECTED)
def test_mg_symmetrize_df(graph_file, client_connection):
    gc.collect()

    pd.set_option('display.max_rows', 500)

    ddf = utils.read_dask_cudf_csv_file(graph_file)
    sym_ddf = cugraph.symmetrize_ddf(ddf, "src", "dst", "weight")

    # convert to regular cudf to facilitate comparison
    df = ddf.compute()
    sym_df = sym_ddf.compute()

    compare(
        df["src"],
        df["dst"],
        df["weight"],
        sym_df["src"],
        sym_df["dst"],
        sym_df["weight"],
    )