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
from .io_data_base import IODataBase
from .regular_query import RegularQuery
from .context_free_query import ContextFreeQuery
from .pretty_context_free_query import PrettyContextFreeQuery
from .cnf_query import CNFQuery
from .ra_query import RAQuery

from pyformlang.finite_automaton import Symbol
from typing import Any, Dict, Optional
import json
import os

class Config:
    def __init__(self):
        self._args: Dict[str, Any] = dict()
        self._objs: Dict[str, Any] = dict()
        self._path: Optional[str] = None

    def __contains__(self, item: str) -> bool:
        if item == 'data_base' or item == 'io_data_base':
            return 'data_base_lists' in self._args or \
                    'data_base_file' in self._args
        elif item == 'regular_query':
            return 'regular_query_regex' in self._args or \
                    'regular_query_file' in self._args
        elif item == 'context_free_query' or \
                item == 'cnf_query' or item == 'ra_query':
            return 'context_free_query_text' in self._args or \
                    'context_free_query_file' in self._args
        elif item == 'pretty_context_free_query' or \
                item == 'pretty_cnf_query':
            return 'pretty_context_free_query_text' in self._args or \
                    'pretty_context_free_query_file' in self._args
        elif item == 'input_vertexes':
            return 'input_vertexes' in self._args
        elif item == 'output_vertexes':
            return 'output_vertexes' in self._args
        elif item == 'word':
            return 'word_file' in self._args or \
                    'word' in self._args
        elif item == 'return_number_of_pairs':
            return 'return_number_of_pairs' in self._args
        return False

    def __getitem__(self, key: str) -> Any:
        if key not in self._objs:
            if key == 'data_base':
                if 'data_base_lists' in self._args:
                    Vs_from, Vs_to, _Ss = self._args['data_base_lists']
                    Ss = list(map(Symbol, _Ss))
                    self._objs[key] = DataBase.from_lists(Vs_from, Vs_to, Ss)
                elif 'data_base_file' in self._args:
                    if self._path is None:
                        data_base_file = self._args['data_base_file']
                    else:
                        data_base_file = os.path.join(
                                self._path, 
                                self._args['data_base_file'])
                    self._objs[key] = DataBase.from_file(data_base_file)
                else:
                    raise KeyError('Config hasn\'t data base definition')
            elif key == 'io_data_base':
                data_base = self['data_base']
                if 'input_vertexes' in self:
                    input_vertexes = self['input_vertexes']
                else:
                    input_vertexes = list(range(data_base.count_vertexes))
                if 'output_vertexes' in self:
                    output_vertexes = self['output_vertexes']
                else:
                    output_vertexes = list(range(data_base.count_vertexes))
                self._objs[key] = IODataBase.from_db_and_io_vertexes(
                        data_base,
                        input_vertexes,
                        output_vertexes
                    )
            elif key == 'regular_query':
                if 'regular_query_regex' in self._args:
                    self._objs[key] = RegularQuery.from_regex(
                            self._args['regular_query_regex'])
                elif 'regular_query_file' in self._args:
                    if self._path is None:
                        regular_query_file = self._args['regular_query_file']
                    else:
                        regular_query_file = os.path.join(
                                self._path,
                                self._args['regular_query_file'])
                    self._objs[key] = RegularQuery.from_file(regular_query_file)
                else:
                    raise KeyError('Config hasn\'t regular query definition')
            elif key == 'context_free_query':
                if 'context_free_query_text' in self._args:
                    self._objs[key] = ContextFreeQuery.from_text(
                            self._args['context_free_query_text'])
                elif 'context_free_query_file' in self._args:
                    if self._path is None:
                        context_free_query_file = \
                                self._args['context_free_query_file']
                    else:
                        context_free_query_file = os.path.join(
                                self._path,
                                self._args['context_free_query_file'])
                    self._objs[key] = ContextFreeQuery.from_file(
                            context_free_query_file)
                else:
                    raise KeyError(
                            'Config hasn\'t context free query definition')
            elif key == 'cnf_query':
                self._objs[key] = CNFQuery.from_context_free_query(
                        self['context_free_query'])
            elif key == 'ra_query':
                self._objs[key] = RAQuery.from_context_free_query(
                        self['context_free_query'])
            elif key == 'pretty_context_free_query':
                if 'pretty_context_free_query_text' in self._args:
                    self._objs[key] = PrettyContextFreeQuery.from_text(
                            self._args['pretty_context_free_query_text'])
                elif 'pretty_context_free_query_file' in self._args:
                    if self._path is None:
                        context_free_query_file = \
                                self._args['pretty_context_free_query_file']
                    else:
                        context_free_query_file = os.path.join(
                                self._path,
                                self._args['pretty_context_free_query_file'])
                    self._objs[key] = PrettyContextFreeQuery.from_file(
                            context_free_query_file)
                else:
                    raise KeyError(
                            'Config hasn\'t pretty context free query definition')
            elif key == 'pretty_cnf_query':
                self._objs[key] = CNFQuery.from_context_free_query(
                        self['pretty_context_free_query'])
            elif key == 'input_vertexes':
                if 'input_vertexes' in self._args:
                    self._objs[key] = list(self._args['input_vertexes'])
                else:
                    raise KeyError('Config hasn\'t input vertexes definition')
            elif key == 'output_vertexes':
                if 'output_vertexes' in self._args:
                    self._objs[key] = list(self._args['output_vertexes'])
                else:
                    raise KeyError('Config hasn\'t output vertexes definition')
            elif key == 'word':
                if 'word' in self._args:
                    self._objs[key] = self._args['word']
                elif 'word_file' in self._args:
                    if self._path is None:
                        word_file = self._args['word_file']
                    else:
                        word_file = os.path.join(
                                self._path,
                                self._args['word_file'])
                    with open(word_file, 'r') as input_file:
                        self._objs[key] = input_file.read()[:-1]
                else:
                    raise KeyError('Config hasn\'t word definition')
            elif key == 'return_number_of_pairs':
                if 'return_number_of_pairs' in self._args:
                    self._objs[key] = self._args['return_number_of_pairs']
                else:
                    raise KeyError(
                            'Config don\'t know if return only number of pairs')
            else:
                raise KeyError('Config don\'t contain [' + key + '] key')
        return self._objs[key]

    def copy(self) -> "Config":
        res = type(self)()
        res._args = self._args.copy()
        res._objs = self._objs.copy()
        res._path = self._path
        return res

    @classmethod
    def from_dict(cls, args: Dict[str, Any]) -> "Config":
        res = Config()
        res._args = args
        return res

    @classmethod
    def from_args(cls, args: Dict[str, Any]) -> "Config":
        res = Config()
        if 'config' in args:
            res = cls.from_file(args['config'])
        for arg_name in [
                        'data_base',
                        'regular_query',
                        'context_free_query',
                        'pretty_context_free_query',
                        'word'
                        ]:
            if arg_name in args:
                res._args[arg_name + '_file'] = args[arg_name]
        return res

    @classmethod
    def from_file(cls, path: str) -> "Config":
        res = Config()
        res._path = os.path.dirname(os.path.abspath(path))
        with open(path, 'r') as config_file:
            res._args = json.load(config_file)
        return res
