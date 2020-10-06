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

from src.config import Config

from pyformlang.cfg import Terminal, Variable
from pyformlang.finite_automaton import Symbol
from pygraphblas import Matrix, types
from typing import Dict, Set, Optional, Tuple, Union

Vertex = int

def cfpq_tp(config: Config) -> Union[bool, Set[Tuple[Vertex, Vertex]]]:
    data_base = config['io_data_base'].copy()
    query = config['ra_query']
    for start_vertex in query.start_vertexes:
        if start_vertex in query.final_vertexes:
            N_i = query.variable_of_path_from(start_vertex)
            for j in range(data_base.count_vertexes):
                data_base[j, N_i, j] = True
    changing = True
    while changing:
        changing = False
        M = data_base @ query
        tC = M.transitive_closure()
        for i, j, _ in tC:
            x, s = M.vertex_to_pair(i)
            y, f = M.vertex_to_pair(j)
            if s in query.start_vertexes and f in query.final_vertexes:
                N = query.variable_of_path_from(s)
                if not data_base[x, N, y]:
                    changing = True
                    data_base[x, N, y] = True
    ans = {
            (i, j)
            for i, j, _ in data_base.matrices[Symbol('S')] \
                    if i in data_base.start_vertexes and \
                       j in data_base.final_vertexes
        }
    if 'return_number_of_pairs' in config and config['return_number_of_pairs']:
        return len(ans)
    else:
        return ans
