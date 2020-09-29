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

from pyformlang.cfg import Terminal, Variable
from typing import Dict, Set, Optional, Tuple, Union

Vertex = int

def cfpq(self,return_only_number_of_pairs: bool = False
        ) -> Union[bool, Set[Tuple[Vertex, Vertex]]]:
    r: Set[Tuple[Variable, Vertex, Vertex]] = \
        {
            (N, v, u)
            for v, S, u in self.data_base.edges()
            for N in self.query._simple_APs[Terminal(S.value)]
        } + \
        {
            (self.start_symbol, v, v)
            for v in self.data_base.count_vertexes
        } if self.generate_epsilon else {}
    m = r.copy()
    while m != set():
        N_i, v, u = m.pop()
        for N_j, w, v_ in r:
            if v == v_:
                for N_k in self.query._complex_APs.get((N_j, N_i), set()):
                    if (N_k, w, u) not in r:
                        m.add((N_k, w, u))
                        r.add((N_k, w, u))
        for N_j, u_, w in r:
            if u_ == u:
                for N_k in self.query._complex_APs.get((N_i, N_j), set()):
                    if (N_k, v, w) not in r:
                        m.add((N_k, v, w))
                        r.add((N_k, v, w))
    ans = filter(lambda t: t[0] == self.query.start_symbol, r)
    if return_only_number_of_pairs:
        return len(ans)
    else:
        return set(ans)

Request.cfpq = cfpq
