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
from pygraphblas import Matrix, types
from typing import Any, Dict, Set, Tuple, Optional, Iterable
from functools import reduce
from math import log2
import operator

Config = Dict[str, Any]
Vertex = int

class Request:
    def __init__(self):
        self._data_base: Optional[DataBase] = None
        self._db_Vs_from: Set[Vertex] = set()
        self._db_Vs_to: Set[Vertex] = set()
        self._query: Optional[Query] = None

    def result(self) -> Set[Tuple[Vertex, Vertex]]:
        data_base = self._data_base
        query = self._query
        # tensor product
        intersection_matrices: Dict[Symbol, Matrix] = {
                S: data_base.matrices[S].kronecker(query.matrices[S])
                for S in data_base.symbols & query.symbols
            }
        # reachability matrix for one step
        reachability_matrix_for_one_step: Matrix = \
                reduce(operator.or_, intersection_matrices.values())
        # reachability matrix for count_vertexes step
        reachability_matrix: Matrix = reachability_matrix_for_one_step
        for _ in range(int(log2(reachability_matrix.ncols)) + 1):
            reachability_matrix += reachability_matrix @ reachability_matrix
        # input/output vertexes for reachability matrix
        Vs_from: Iterable[Vertex] = map(
                lambda x: x * query.size + query.start_vertex,
                self._db_Vs_from
            )
        Vs_to: Iterable[Vertex] = [
                data_base_V_to * query.size + query_final_V
                for data_base_V_to in self._db_Vs_to
                for query_final_V in query.final_vertexes
            ]
        # construcing result
        res = set()
        for V_from in Vs_from:
            for V_to in Vs_to:
                if reachability_matrix.get(V_from, V_to, False):
                    res.add((V_from, V_to))
        # input/output vertexes for data base
        res = set(map(lambda pair: tuple(map(lambda V: V // query.size, pair)), res))
        return res

    @classmethod
    def from_config(cls, config: Config) -> "Request":
        res = cls()
        if 'data_base_lists' in config:
            Vs_from, _Ss, Vs_to = config['data_base_lists']
            Ss = list(map(Symbol, _Ss))
            res._data_base = DataBase.from_lists(Vs_from, Vs_to, Ss)
        elif 'data_base_file' in config:
            res._data_base = DataBase.from_file(config['data_base_file'])
        else:
            raise KeyError('config hasn\'t data base definition')
        if 'query_regex' in config:
            res._query = Query.from_regex(config['query_regex'])
        elif 'query_file' in config:
            res._query = Query.from_file(config['query_file'])
        else:
            raise KeyError('config hasn\'t query definition')
        if 'input_vertexes' in config:
            res._db_Vs_from = set(config['input_vertexes'])
        else:
            res._db_Vs_from = set(range(res._data_base.count_vertexes))
        if 'output_vertexes' in config:
            res._db_Vs_to = set(config['output_vertexes'])
        else:
            res._db_Vs_to = set(range(res._data_base.count_vertexes))
        return res
