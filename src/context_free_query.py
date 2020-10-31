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

from pyformlang.regular_expression import Regex, regex_objects
from pyformlang.cfg import CFG, Terminal, Variable
from typing import Dict, Set, Optional, Tuple, List

class ContextFreeQuery(Query):
    def __init__(self) -> None:
        super().__init__()
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
    def _from_head_and_regex(cls, head, regex) -> Tuple[bool, List[str]]:
        def without_union(line):
            return '|' not in line

        if isinstance(regex.head, regex_objects.Concatenation):
            head_C0 = head + "_C0"
            head_C1 = head + "_C1"
            rec_0, lines_0 = cls._from_head_and_regex(head_C0, regex.sons[0])
            rec_1, lines_1 = cls._from_head_and_regex(head_C1, regex.sons[1])
            if without_union(lines_0[0]) and not rec_0:
                head_C0 = lines_0[0].split("->")[1].strip()
                lines_0 = lines_0[1:]
            if without_union(lines_1[0]) and not rec_1:
                head_C1 = lines_1[0].split("->")[1].strip()
                lines_1 = lines_1[1:]
            return (False,
                [head + " -> " + head_C0 + " " + head_C1] +
                lines_0 + lines_1)
        if isinstance(regex.head, regex_objects.Union):
            head_U0 = head + "_U0"
            head_U1 = head + "_U1"
            rec_0, lines_0 = cls._from_head_and_regex(head_U0, regex.sons[0])
            rec_1, lines_1 = cls._from_head_and_regex(head_U1, regex.sons[1])
            if not rec_0:
                head_U0 = lines_0[0].split("->")[1].strip()
                lines_0 = lines_0[1:]
            if not rec_1:
                head_U1 = lines_1[0].split("->")[1].strip()
                lines_1 = lines_1[1:]
            return (False,
                [head + " -> " + head_U0 + " | " + head_U1] +
                lines_0 + lines_1)
        if isinstance(regex.head, regex_objects.KleeneStar):
            head_KS = head + "_KS"
            rec, lines = cls._from_head_and_regex(head_KS, regex.sons[0])
            if without_union(lines[0]) and not rec:
                head_KS = lines[0].split("->")[1].strip()
                lines = lines[1:]
            return (True,
                [head + " -> | " + head_KS + " " + head] +
                lines)
        if isinstance(regex.head, regex_objects.Epsilon):
            return (False, [head + " -> "])
        if isinstance(regex.head, regex_objects.Symbol):
            return (False, [head + " -> " + str(regex)])

    @classmethod
    def _from_heads_and_regexes(cls, heads_and_regexes) -> str:
        result = ""
        for head, regex in heads_and_regexes:
            #result += '\n'.join(cls._from_head_and_regex(head, regex)[1]) + '\n'
            _, r = cls._from_head_and_regex(head, regex)
            for l in r:
                print(l)
            result += '\n'.join(r) + '\n'
        return result

    @classmethod
    def from_text(cls, text: str) -> "ContextFreeQuery":
        res = cls()
        text = text.replace("eps", "$")
        lines = text.splitlines()
        heads  = list(map(lambda line: line.split("->")[0].strip(), lines))
        bodies = list(map(lambda line: line.split("->")[1].strip(), lines))
        heads_and_bodies = dict()
        for i in range(len(lines)):
            if heads[i] in heads_and_bodies.keys():
                heads_and_bodies[heads[i]] += " | " + bodies[i]
            else:
                heads_and_bodies[heads[i]] = bodies[i]
        for head, body in heads_and_bodies.items():
            heads_and_bodies[head] = Regex(body)
        text = cls._from_heads_and_regexes(heads_and_bodies.items())
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
