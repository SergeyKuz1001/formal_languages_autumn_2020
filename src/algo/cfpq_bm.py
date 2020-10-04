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

def cfpq_bm(config: Config) -> Union[bool, Set[Tuple[Vertex, Vertex]]]:
    data_base = config['data_base']
    query = config['context_free_query']
    n = data_base.count_vertexes
    T: Dict[Variable, Matrix] = {
            A: Matrix.sparse(types.BOOL, n, n)
            for A in query.variables
        }
    for terminal, variables in query.simple_antiproductions.items():
        for i, j, _ in data_base.matrices[Symbol(terminal.value)]:
            for variable in variables:
                T[variable][i, j] = True
    if query.generate_epsilon:
        for i in range(n):
            T[query.start_symbol][i, i] = True
    changing = True
    while changing:
        changing = False
        for (A_j, A_k), As_i in query.complex_antiproductions.items():
            for A_i in As_i:
                prev_nvals = T[A_i].nvals
                T[A_i] += T[A_j] @ T[A_k]
                if T[A_i].nvals != prev_nvals:
                    changing = True
    ans = { (i, j) for i, j, _ in T[query.start_symbol] }
    if 'input_vertexes' in config:
        ans = filter(lambda t: t[0] in config['input_vertexes'], ans)
    if 'output_vertexes' in config:
        ans = filter(lambda t: t[1] in config['output_vertexes'], ans)
    if 'return_number_of_pairs' in config and config['return_number_of_pairs']:
        return len(ans)
    else:
        return set(ans)
