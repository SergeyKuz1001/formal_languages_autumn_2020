#  Copyright 2020 Sergey Kuzivanov
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from .request import Request

from pyformlang.finite_automaton import Symbol
from pygraphblas import Matrix
from typing import Dict, List, Set, Tuple, Optional, Union
from functools import reduce
import operator

Vertex = int

def rpq(self, return_only_number_of_pairs: bool = False
       ) -> Union[bool, Set[Tuple[Vertex, Vertex]]]:
    # tensor product of data base and query
    intersection_matrices: Dict[Symbol, Matrix] = {
        S: self.data_base.matrices[S].kronecker(self.query.matrices[S])
        for S in self.data_base.symbols & self.query.symbols
      }
    # reachability matrix for one step
    reachability_matrix_for_one_step: Matrix = \
            reduce(operator.add, intersection_matrices.values())
    # reachability matrix
    prev_nvals = 0
    reachability_matrix: Matrix = reachability_matrix_for_one_step
    while reachability_matrix.nvals != prev_nvals:
        prev_nvals = reachability_matrix.nvals
        reachability_matrix += \
                reachability_matrix @ reachability_matrix
    # ... or ...
    #           reachability_matrix @ reachability_matrix_for_one_step
    # number of reachable pairs
    if return_only_number_of_pairs:
        return reachability_matrix.nvals
    # input vertexes
    if self.input_vertexes is None:
        Vs_from = list(range(self.data_base.count_vertexes))
    else:
        Vs_from = self.input_vertexes
    tensor_product_input_vertexes, data_base_input_vertexes = ( \
        list(map(
            lambda x:
                x * self.query.count_vertexes + self.query.start_vertex,
            Vs_from)),
        Vs_from
      )
    # output vertexes
    if self.output_vertexes is None:
        Vs_to = list(range(self.data_base.count_vertexes))
    else:
        Vs_to = self.output_vertexes
    tensor_product_output_vertexes, data_base_output_vertexes = \
        list(map(list, zip(*[
            (
                data_base_V_to * self.query.count_vertexes + query_final_V,
                data_base_V_to
            )
            for data_base_V_to in Vs_to
            for query_final_V in self.query.final_vertexes
        ])))
    # reachable pairs
    return {
               (data_base_input_vertexes[i], data_base_output_vertexes[j])
               for i, j, _ in reachability_matrix.extract_matrix(
                   tensor_product_input_vertexes,
                   tensor_product_output_vertexes)
           }

Request.rpq = rpq
