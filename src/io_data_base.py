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

from .io_graph import IOGraph
from .data_base import DataBase

from typing import List

Vertex = int

class IODataBase(IOGraph, DataBase):
    @classmethod
    def from_db_and_io_vertexes(
                                cls,
                                db: DataBase,
                                input_vertexes: List[Vertex],
                                output_vertexes: List[Vertex]
                               ) -> "IODataBase":
        res = cls()
        res._matrices = db._matrices
        res._count_Vs = db._count_Vs
        res._start_Vs = set(input_vertexes)
        res._final_Vs = set(output_vertexes)
        return res
