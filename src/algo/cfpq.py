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
from typing import Dict, Set, Optional, Tuple, Union

Vertex = int

def cfpq(config: Config) -> Union[bool, Set[Tuple[Vertex, Vertex]]]:
    data_base = config['data_base']
    query = config['context_free_query']
    r: Set[Tuple[Variable, Vertex, Vertex]] = \
        {
            (N, v, u)
            for v, S, u in data_base.edges()
            for N in query.simple_antiproductions[Terminal(S.value)]
        } | \
        ({
            (query.start_symbol, v, v)
            for v in range(data_base.count_vertexes)
        } if query.generate_epsilon else set())
    m = r.copy()
    r_new = r.copy()
    query_complex_antiproductions = query.complex_antiproductions
    while m != set():
        N_i, v, u = m.pop()
        for N_j, w, v_ in r:
            if v == v_:
                for N_k in query_complex_antiproductions.get((N_j, N_i), set()):
                    if (N_k, w, u) not in r:
                        m.add((N_k, w, u))
                        r_new.add((N_k, w, u))
        for N_j, u_, w in r:
            if u_ == u:
                for N_k in query_complex_antiproductions.get((N_i, N_j), set()):
                    if (N_k, v, w) not in r:
                        m.add((N_k, v, w))
                        r_new.add((N_k, v, w))
        r = r_new.copy()
    ans = map(
            lambda t: (t[1], t[2]),
            filter(
                    lambda t: t[0] == query.start_symbol,
                    r
                )
        )
    if 'input_vertexes' in config:
        ans = filter(lambda t: t[0] in config['input_vertexes'], ans)
    if 'output_vertexes' in config:
        ans = filter(lambda t: t[1] in config['output_vertexes'], ans)
    if 'return_number_of_pairs' in config and config['return_number_of_pairs']:
        return len(ans)
    else:
        return set(ans)
