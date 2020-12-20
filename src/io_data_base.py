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
from .io_graph import IOGraph
from .data_base import DataBase

from pygraphblas import Matrix, types
from typing import List, Optional

Vertex = int

class IODataBase(IOGraph, DataBase):
    def __and__(self, other: "IODataBase") -> "DataBase":
        res = self @ other
        count_v = res.count_vertexes
        start_vertices = list(res.start_vertexes)
        count_sv = len(start_vertices)
        start_vertices.sort()
        A = Matrix.from_lists(
                list(range(count_sv)),
                start_vertices,
                [True] * count_sv,
                count_sv,
                count_v
            )
        final_vertices = list(res.final_vertexes)
        count_fv = len(final_vertices)
        final_vertices.sort()
        B = Matrix.from_lists(
                final_vertices,
                list(range(count_fv)),
                [True] * count_fv,
                count_v,
                count_fv
            )
        matrices = res.matrices
        for S in matrices.keys():
            matrices[S] = A @ matrices[S] @ B
        return DataBase.from_graph(Graph.from_matrices(matrices))

    @classmethod
    def from_db_and_io_vertexes(
                                cls,
                                db: DataBase,
                                input_vertexes: Optional[List[Vertex]],
                                output_vertexes: Optional[List[Vertex]]
                               ) -> "IODataBase":
        res = cls()
        res._matrices = db._matrices
        res._count_Vs = db._count_Vs
        if input_vertexes is None:
            res._start_Vs = set(range(db._count_Vs))
        else:
            res._start_Vs = set(input_vertexes)
        if output_vertexes is None:
            res._final_Vs = set(range(db._count_Vs))
        else:
            res._final_Vs = set(output_vertexes)
        return res
