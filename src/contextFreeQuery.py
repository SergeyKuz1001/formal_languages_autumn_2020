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

from .query import Query

from pyformlang.cfg import CFG, Terminal, Variable
from typing import Dict, Set, Optional, Tuple

class ContextFreeQuery(Query):
    def __init__(self) -> None:
        self._start_V: Variable = Variable('S')
        self._generate_eps: Optional[bool] = None
        self._simple_APs: Dict[Terminal, Set[Variable]] = dict()
        self._complex_APs: Dict[Tuple[Variable, Variable], Set[Variable]] = \
                dict()

    @property
    def start_symbol(self):
        return self._start_V

    @property
    def generate_epsilon(self) -> Optional[bool]:
        return self._generate_eps

    @property
    def simple_antiproductions(self) -> Dict[Terminal, Set[Variable]]:
        return self._simple_APs

    @property
    def complex_antiproductions(self) -> Dict[
                                                 Tuple[Variable, Variable],
                                                 Set[Variable]
                                             ]:
        return self._complex_APs

    @classmethod
    def from_text(cls, text: str) -> "ContextFreeQuery":
        res = cls()
        cfg = CFG.from_text(text)
        cnf = cfg.to_normal_form()
        res._generate_eps = cfg.generate_epsilon()
        for production in cnf.productions:
            var = production.head
            if len(production.body) == 1:
                term = production.body[0]
                res._simple_APs.setdefault(term, set())
                res._simple_APs[term].add(var)
            elif len(production.body) == 2:
                var1, var2 = production.body
                res._complex_APs.setdefault((var1, var2), set())
                res._complex_APs[(var1, var2)].add(var)
        return res

    @classmethod
    def from_file(cls, path: str) -> "ContextFreeQuery":
        with open(path, 'r') as input_file:
            lines = input_file.readlines()
        text = '\n'.join(map(
            lambda line: ' '.join(line.split().insert(1, '->')),
            lines
          ))
        return cls.from_text(text)
