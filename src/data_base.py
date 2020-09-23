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
from typing import Dict, List, Iterable

Vertex = int

class DataBase:
    def __init__(self) -> None:
        self._matrices: Dict[Symbol, Matrix] = dict()
        self._count_Vs: int = 0

    def __str__(self) -> str:
        return 'DataBase[' + str(self._count_Vs) + ']'

    @property
    def count_vertexes(self) -> int:
        return self._count_Vs

    @property
    def symbols(self) -> Iterable[Symbol]:
        return set(self._matrices.keys())

    @property
    def matrices(self) -> Dict[Symbol, Matrix]:
        return self._matrices

    @classmethod
    def from_matrices(cls, matrices: Dict[Symbol, Matrix]) -> "DataBase":
        res = cls()
        res._matrices = matrices
        res._count_Vs = max([max(matrix.nrows, matrix.ncols)
                            for matrix in matrices.values()])
        return res

    @classmethod
    def from_lists(cls,
                   Vs_from: List[Vertex],
                   Vs_to: List[Vertex],
                   Ss: List[Symbol]
                  ) -> "DataBase":
        res = cls()
        res._count_Vs = max(Vs_from + Vs_to) + 1
        for V_from, V_to, S in zip(Vs_from, Vs_to, Ss):
            res._matrices.setdefault(S,
                    Matrix.sparse(types.BOOL, res._count_Vs, res._count_Vs))
            res._matrices[S][V_from, V_to] = True
        return res

    @classmethod
    def from_file(cls, path: str) -> "DataBase":
        with open(path, 'r') as input_file:
            lines = input_file.readlines()
        Vs_from, Ss, Vs_to = zip(*map(lambda line: line.split(), lines))
        return cls.from_lists(list(map(int, Vs_from)),
                              list(map(int, Vs_to)),
                              list(map(Symbol, Ss))
                             )
