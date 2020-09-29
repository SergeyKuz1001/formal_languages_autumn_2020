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
        self._cnf: Optional[CFG] = None
        self._start_V: Variable = Variable('S')
        self._generate_eps: Optional[bool] = None
        self._simple_APs: Optional[Dict[Terminal, Set[Variable]]] = None
        self._complex_APs: \
                Optional[Dict[Tuple[Variable, Variable], Set[Variable]]] = None
        self._complex_Ps: \
                Optional[Dict[Variable, Set[Tuple[Variable, Variable]]]] = None

    @property
    def start_symbol(self) -> Variable:
        return self._start_V

    @property
    def variables(self) -> Set[Variable]:
        return self._cnf.variables

    @property
    def terminals(self) -> Set[Terminal]:
        return self._cnf.terminals

    @property
    def generate_epsilon(self) -> Optional[bool]:
        return self._generate_eps

    @property
    def simple_antiproductions(self) -> Dict[Terminal, Set[Variable]]:
        if self._simple_APs is None:
            self._eval_APs()
        return self._simple_APs

    @property
    def complex_antiproductions(self) -> Dict[
                                                 Tuple[Variable, Variable],
                                                 Set[Variable]
                                             ]:
        if self._complex_APs is None:
            self._eval_APs()
        return self._complex_APs

    @property
    def complex_productions(self) -> Dict[
                                             Variable,
                                             Set[Tuple[Variable, Variable]]
                                         ]:
        if self._complex_Ps is None:
            self._eval_Ps()
        return self._complex_Ps

    @classmethod
    def from_text(cls, text: str) -> "ContextFreeQuery":
        res = cls()
        cfg = CFG.from_text(text)
        cnf = cfg.to_normal_form()
        res._cnf = cnf
        res._generate_eps = cfg.generate_epsilon()
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

    def _eval_APs(self) -> None:
        self._simple_APs = dict()
        self._complex_APs = dict()
        for production in self._cnf.productions:
            var = production.head
            if len(production.body) == 1:
                term = production.body[0]
                self._simple_APs.setdefault(term, set())
                self._simple_APs[term].add(var)
            elif len(production.body) == 2:
                var1, var2 = production.body
                self._complex_APs.setdefault((var1, var2), set())
                self._complex_APs[(var1, var2)].add(var)

    def _eval_Ps(self) -> None:
        self._complex_Ps = dict()
        for production in self._cnf.productions:
            var = production.head
            if len(production.body) == 2:
                var1, var2 = production.body
                self._complex_Ps.setdefault(var, set())
                self._complex_Ps[var].add((var1, var2))
