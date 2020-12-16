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

from .graph import Graph

from pygraphblas import Matrix, types
from typing import Dict, List, Iterable, Tuple, Optional, Set

Vertex = int

class IOGraph(Graph):
    def __init__(self) -> None:
        super().__init__()
        self._start_Vs: Set[Vertex] = set()
        self._final_Vs: Set[Vertex] = set()
        self._other_N: Optional[int] = None

    def copy(self) -> "IOGraph":
        res = super().copy()
        res._start_Vs = self._start_Vs.copy()
        res._final_Vs = self._final_Vs.copy()
        res._other_N = self._other_N
        return res

    @property
    def start_vertexes(self) -> Set[Vertex]:
        return self._start_Vs

    @property
    def final_vertexes(self) -> Set[Vertex]:
        return self._final_Vs

    def __matmul__(self, other: "IOGraph") -> "IOGraph":
        res = super().__matmul__(other)
        res._start_Vs = {
                self_start_V * other.count_vertexes + other_start_V
                for  self_start_V in  self.start_vertexes
                for other_start_V in other.start_vertexes
            }
        res._final_Vs = {
                self_final_V * other.count_vertexes + other_final_V
                for  self_final_V in  self.final_vertexes
                for other_final_V in other.final_vertexes
            }
        res._other_N = other.count_vertexes
        return res

    def vertex_to_pair(self, vertex: Vertex) -> Tuple[Vertex, Vertex]:
        return (vertex // self._other_N, vertex % self._other_N)
