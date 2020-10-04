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

from pyformlang.finite_automaton import Symbol
from pygraphblas import Matrix, types
from typing import Dict, List, Iterable, Tuple, Optional

Vertex = int

class Graph:
    def __init__(self) -> None:
        self._matrices: Dict[Symbol, Matrix] = dict()
        self._count_Vs: int = 0
        self._edges: Optional[List[Tuple[Vertex, Symbol, Vertex]]] = None

    @property
    def count_vertexes(self) -> int:
        return self._count_Vs

    @property
    def symbols(self) -> Iterable[Symbol]:
        return set(self._matrices.keys())

    @property
    def matrices(self) -> Dict[Symbol, Matrix]:
        return self._matrices

    @property
    def edges(self) -> List[Tuple[Vertex, Symbol, Vertex]]:
        if self._edges is None:
            self._edges = [
                    (i, S, j)
                    for S in self.symbols
                    for i, j, _ in self.matrices[S]
                ]
        return self._edges

    @classmethod
    def from_matrices(cls, matrices: Dict[Symbol, Matrix]) -> "Graph":
        res = cls()
        res._matrices = matrices
        res._count_Vs = max([max(matrix.nrows, matrix.ncols)
                            for matrix in matrices.values()])
        return res
