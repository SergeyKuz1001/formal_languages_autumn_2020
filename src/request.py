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

from .data_base import DataBase
from .query import Query
from .regularQuery import RegularQuery
from .config import Config

from typing import List, Optional, Set, Tuple, Union
import os

Vertex = int

class Request:
    def __init__(self,
                 data_base: Optional[DataBase] = None,
                 query: Optional[Query] = None
                ) -> None:
        self._data_base: Optional[DataBase] = data_base
        self._db_Vs_from: Optional[List[Vertex]] = None
        self._db_Vs_to: Optional[List[Vertex]] = None
        self._query: Optional[Query] = query

    def execute(self, return_only_number_of_pairs: bool = False
               ) -> Union[bool, Set[Tuple[Vertex, Vertex]]]:
        if isinstance(self.query, RegularQuery):
            return self.rpq(return_only_number_of_pairs)

    @property
    def data_base(self) -> Optional[DataBase]:
        return self._data_base

    @data_base.setter
    def data_base(self, value: DataBase) -> None:
        self._data_base = value

    @property
    def input_vertexes(self) -> Optional[List[Vertex]]:
        return self._db_Vs_from

    @input_vertexes.setter
    def input_vertexes(self, value: List[Vertex]) -> None:
        self._db_Vs_from = value

    @property
    def output_vertexes(self) -> Optional[List[Vertex]]:
        return self._db_Vs_to

    @output_vertexes.setter
    def output_vertexes(self, value: List[Vertex]) -> None:
        self._db_Vs_to = value

    @property
    def query(self) -> Optional[Query]:
        return self._query

    @query.setter
    def query(self, value: Query) -> None:
        self._query = value

    @classmethod
    def from_config(cls, config: Config) -> "Request":
        res = cls()
        if 'data_base_lists' in config:
            Vs_from, _Ss, Vs_to = config['data_base_lists']
            Ss = list(map(Symbol, _Ss))
            res._data_base = DataBase.from_lists(Vs_from, Vs_to, Ss)
        elif 'data_base_file' in config:
            data_base_file = config['data_base_file'] \
                if config.path is None \
                else os.path.join(config.path, config['data_base_file'])
            res._data_base = DataBase.from_file(data_base_file)
        else:
            raise KeyError('config hasn\'t data base definition')
        if 'query_regex' in config:
            res._query = Query.from_regex(config['query_regex'])
        elif 'query_file' in config:
            query_file = config['query_file'] \
                if config.path is None \
                else os.path.join(config.path, config['query_file'])
            res._query = Query.from_file(query_file)
        else:
            raise KeyError('config hasn\'t query definition')
        if 'input_vertexes' in config:
            res._db_Vs_from = list(config['input_vertexes'])
        else:
            res._db_Vs_from = None
        if 'output_vertexes' in config:
            res._db_Vs_to = list(config['output_vertexes'])
        else:
            res._db_Vs_to = None
        return res
