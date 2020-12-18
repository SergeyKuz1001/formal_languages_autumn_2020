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

from .context_free_query import ContextFreeQuery

from pyformlang.cfg import Terminal, Variable
from typing import Dict, Set, Optional, Tuple

class CNFQuery(ContextFreeQuery):
    def __init__(self) -> None:
        super().__init__()
        self._simple_APs: Optional[Dict[Terminal, Set[Variable]]] = None
        self._complex_APs: \
                Optional[Dict[Tuple[Variable, Variable], Set[Variable]]] = None
        self._complex_Ps: \
                Optional[Dict[Variable, Set[Tuple[Variable, Variable]]]] = None

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
    def from_context_free_query(cls, cfq: ContextFreeQuery) -> "CNFQuery":
        res = cls()
        res._generate_eps = cfq._cfg.generate_epsilon()
        res._cfg = cfq._cfg.to_normal_form()
        return res

    @classmethod
    def from_text(cls, text: str, start_symbol = "S") -> "CNFQuery":
        return cls.from_context_free_query(
                ContextFreeQuery.from_text(text, start_symbol)
            )

    def _eval_APs(self) -> None:
        self._simple_APs = dict()
        self._complex_APs = dict()
        for production in self._cfg.productions:
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
        for production in self._cfg.productions:
            var = production.head
            if len(production.body) == 2:
                var1, var2 = production.body
                self._complex_Ps.setdefault(var, set())
                self._complex_Ps[var].add((var1, var2))
