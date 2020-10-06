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
        self._cfg: Optional[CFG] = None
        self._generate_eps: Optional[bool] = None

    @property
    def start_symbol(self) -> Variable:
        return self._cfg.start_symbol

    @property
    def variables(self) -> Set[Variable]:
        return self._cfg.variables

    @property
    def terminals(self) -> Set[Terminal]:
        return self._cfg.terminals

    @property
    def generate_epsilon(self) -> Optional[bool]:
        if self._generate_eps is None:
            self._generate_eps = self._cfg.generate_epsilon()
        return self._generate_eps

    @classmethod
    def from_text(cls, text: str) -> "ContextFreeQuery":
        res = cls()
        res._cfg = CFG.from_text(text)
        return res

    @classmethod
    def from_file(cls, path: str) -> "ContextFreeQuery":
        def my_insert(l, i, el):
            l_ = l.copy()
            l_.insert(i, el)
            return l_

        with open(path, 'r') as input_file:
            lines = input_file.readlines()
        text = '\n'.join(map(
            lambda line: ' '.join(my_insert(line.split(), 1, '->')),
            lines
          ))
        return cls.from_text(text)
