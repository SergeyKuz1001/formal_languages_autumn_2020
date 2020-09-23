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

from .data_base import DataBase
from .query import Query
from .config import Config

from pyformlang.finite_automaton import Symbol
from pygraphblas import Matrix, types, semiring
from typing import Any, Dict, List, Set, Tuple, Optional, Iterable
from functools import reduce
from math import log2
import operator
import os

Vertex = int

class Request:
    def __init__(self):
        self._data_base: Optional[DataBase] = None
        self._db_Vs_from: Optional[List[Vertex]] = list()
        self._db_Vs_to: Optional[List[Vertex]] = list()
        self._query: Optional[Query] = None

    @property
    def data_base(self) -> Optional[DataBase]:
        return self._data_base

    @data_base.setter
    def data_base(self, value: DataBase) -> None:
        self._data_base = value

    @property
    def query(self) -> Optional[Query]:
        return self._query

    @query.setter
    def query(self, value: Query) -> None:
        self._query = value

    def tensor_product_of_data_base_and_query(self) -> Dict[Symbol, Matrix]:
        intersection_matrices: Dict[Symbol, Matrix] = {
              S: self.data_base.matrices[S].kronecker(self.query.matrices[S])
              for S in self.data_base.symbols & self.query.symbols
            }
        return intersection_matrices

    def reachability_matrix_for_one_step(self) -> Matrix:
        intersection_matrices = self.tensor_product_of_data_base_and_query()
        reachability_matrix_for_one_step: Matrix = \
                reduce(operator.add, intersection_matrices.values())
        return reachability_matrix_for_one_step

    def reachability_matrix(self) -> Matrix:
        reachability_matrix_for_one_step = \
                self.reachability_matrix_for_one_step()
        prev_nvals = 0
        reachability_matrix: Matrix = reachability_matrix_for_one_step
        while reachability_matrix.nvals != prev_nvals:
            prev_nvals = reachability_matrix.nvals
            reachability_matrix += \
                    reachability_matrix @ reachability_matrix
# ... or ...
#                   reachability_matrix @ reachability_matrix_for_one_step
        return reachability_matrix

    def count_reachable_pairs(self) -> int:
        return self.reachability_matrix().nvals

    def input_vertexes(self) -> Tuple[List[Vertex], List[Vertex]]:
        if self._db_Vs_from is None:
            Vs_from = list(range(self.data_base.count_vertexes))
        else:
            Vs_from = self._db_Vs_from
        return (
            list(map(
                lambda x:
                    x * self.query.count_vertexes + self.query.start_vertex,
                Vs_from)),
            Vs_from
          )

    def output_vertexes(self) -> Tuple[List[Vertex], List[Vertex]]:
        if self._db_Vs_to is None:
            Vs_to = list(range(self.data_base.count_vertexes))
        else:
            Vs_to = self._db_Vs_to
        return list(map(list, zip(*[
                (
                    data_base_V_to * self.query.count_vertexes + query_final_V,
                    data_base_V_to
                )
                for data_base_V_to in Vs_to
                for query_final_V in self.query.final_vertexes
            ])))

    def reachable_pairs(self) -> Set[Tuple[Vertex, Vertex]]:
        reachability_matrix = self.reachability_matrix()
        tensor_product_input_vertexes, data_base_input_vertexes = \
                self.input_vertexes()
        tensor_product_output_vertexes, data_base_output_vertexes = \
                self.output_vertexes()
        return {
                   (data_base_input_vertexes[i], data_base_output_vertexes[j])
                   for i, j, _ in reachability_matrix.extract_matrix(
                       tensor_product_input_vertexes,
                       tensor_product_output_vertexes)
               }

    @classmethod
    def from_config(cls, config: Config) -> "Request":
        res = cls()
        if 'data_base_lists' in config:
            Vs_from, _Ss, Vs_to = config['data_base_lists']
            Ss = list(map(Symbol, _Ss))
            res._data_base = DataBase.from_lists(Vs_from, Vs_to, Ss)
        elif 'data_base_file' in config:
            data_base_file = config['data_base_file'] \
                if config.path is None \
                else os.path.join(config.path, config['data_base_file'])
            res._data_base = DataBase.from_file(data_base_file)
        else:
            raise KeyError('config hasn\'t data base definition')
        if 'query_regex' in config:
            res._query = Query.from_regex(config['query_regex'])
        elif 'query_file' in config:
            query_file = config['query_file'] \
                if config.path is None \
                else os.path.join(config.path, config['query_file'])
            res._query = Query.from_file(query_file)
        else:
            raise KeyError('config hasn\'t query definition')
        if 'input_vertexes' in config:
            res._db_Vs_from = list(config['input_vertexes'])
        else:
            res._db_Vs_from = None
        if 'output_vertexes' in config:
            res._db_Vs_to = list(config['output_vertexes'])
        else:
            res._db_Vs_to = None
        return res

    @classmethod
    def from_dict(cls, _dict: Dict[str, Any]) -> "Request":
        return cls.from_config(_dict)
