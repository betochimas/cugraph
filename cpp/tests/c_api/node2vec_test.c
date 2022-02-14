/*
 * Copyright (c) 2022, NVIDIA CORPORATION.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "c_test_utils.h" /* RUN_TEST */

#include <cugraph_c/algorithms.h>
#include <cugraph_c/graph.h>

#include <math.h>

typedef int32_t vertex_t;
typedef int32_t edge_t;
typedef float weight_t;

const weight_t EPSILON = 0.001;

int generic_node2vec_test(vertex_t* h_src,
                          vertex_t* h_dst,
                          weight_t* h_wgt,
                          vertex_t* h_seeds,
                          size_t num_edges,
                          size_t num_seeds,
                          size_t max_depth,
                          double p,
                          double q,
                          bool_t store_transposed)
{
  int test_ret_value = 0;

  cugraph_error_code_t ret_code = CUGRAPH_SUCCESS;
  cugraph_error_t* ret_error    = NULL;

  cugraph_resource_handle_t* p_handle                    = NULL;
  cugraph_graph_t* p_graph                               = NULL;
  cugraph_random_walk_result_t* p_result                 = NULL;
  cugraph_type_erased_device_array_t* p_sources          = NULL;
  cugraph_type_erased_device_array_view_t* p_source_view = NULL;

  p_handle = cugraph_create_resource_handle();
  TEST_ASSERT(test_ret_value, p_handle != NULL, "resource handle creation failed.");

  ret_code = create_test_graph(
    p_handle, h_src, h_dst, h_wgt, num_edges, store_transposed, &p_graph, &ret_error);
  TEST_ASSERT(test_ret_value, ret_code == CUGRAPH_SUCCESS, "graph creation failed.");

  ret_code =
    cugraph_type_erased_device_array_create(p_handle, num_seeds, INT32, &p_sources, &ret_error);
  TEST_ASSERT(test_ret_value, ret_code == CUGRAPH_SUCCESS, "p_sources create failed.");

  p_source_view = cugraph_type_erased_device_array_view(p_sources);

  ret_code = cugraph_type_erased_device_array_view_copy_from_host(
    p_handle, p_source_view, (byte_t*)h_seeds, &ret_error);
  TEST_ASSERT(test_ret_value, ret_code == CUGRAPH_SUCCESS, "src copy_from_host failed.");

  ret_code = cugraph_node2vec(
    p_handle, p_graph, p_source_view, max_depth, FALSE, p, q, &p_result, &ret_error);
  TEST_ASSERT(test_ret_value, ret_code == CUGRAPH_SUCCESS, "node2vec failed failed.");

  cugraph_type_erased_device_array_view_t* paths;
  cugraph_type_erased_device_array_view_t* weights;
  size_t max_path_length;

  max_path_length = cugraph_random_walk_result_get_max_path_length(p_result);
  paths           = cugraph_random_walk_result_get_paths(p_result);
  weights         = cugraph_random_walk_result_get_weights(p_result);

  vertex_t h_paths[max_path_length * num_seeds];
  weight_t h_weights[max_path_length * num_seeds];

  ret_code = cugraph_type_erased_device_array_view_copy_to_host(
    p_handle, (byte_t*)h_paths, paths, &ret_error);
  TEST_ASSERT(test_ret_value, ret_code == CUGRAPH_SUCCESS, "copy_to_host failed.");

  ret_code = cugraph_type_erased_device_array_view_copy_to_host(
    p_handle, (byte_t*)h_weights, weights, &ret_error);
  TEST_ASSERT(test_ret_value, ret_code == CUGRAPH_SUCCESS, "copy_to_host failed.");

  //  We can easily validate that the results of node2vec
  //  are feasible by converting the sparse (h_src,h_dst,h_wgt)
  //  into a dense host matrix and check each path.
  int num_vertices = 5;
  weight_t M[num_vertices][num_vertices];

  for (int i = 0; i < num_vertices; ++i)
    for (int j = 0; j < num_vertices; ++j)
      M[i][j] = 0.0;

  for (int i = 0; i < num_edges; ++i)
    M[h_src[i]][h_dst[i]] = h_wgt[i];

  for (int i = 0; (i < num_seeds) && (test_ret_value == 0); ++i) {
    for (int j = 0; (j < (max_path_length-1)) && (test_ret_value == 0); ++j) {
      TEST_ASSERT(test_ret_value,
                  nearlyEqual(h_weights[i * (max_path_length - 1)],
                              M[h_paths[i * max_path_length]][h_paths[i * max_path_length + 1]],
                              EPSILON),
                  "node2vec weights don't match");
    }
  }

  return test_ret_value;
}

int test_node2vec()
{
  size_t num_edges    = 8;
  size_t num_vertices = 6;

  vertex_t src[]   = {0, 1, 1, 2, 2, 2, 3, 4};
  vertex_t dst[]   = {1, 3, 4, 0, 1, 3, 5, 5};
  weight_t wgt[]   = {0.1f, 2.1f, 1.1f, 5.1f, 3.1f, 4.1f, 7.2f, 3.2f};
  vertex_t seeds[] = {0, 0};
  size_t max_depth = 4;

  return generic_node2vec_test(src, dst, wgt, seeds, num_edges, 2, max_depth, 0.8, 0.5, FALSE);
}

int main(int argc, char** argv)
{
  int result = 0;
  result |= RUN_TEST(test_node2vec);
  return result;
}

