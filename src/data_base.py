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
from typing import List

Symbol = str
Vertex = int

class DataBase(Graph):
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
