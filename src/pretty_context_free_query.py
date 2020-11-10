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

from pyformlang.regular_expression import Regex, regex_objects
from pyformlang.cfg import CFG, Terminal, Variable, Production
from typing import Union

class PrettyContextFreeQuery(ContextFreeQuery):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def _from_pretty(cls, text: str) -> str:
        new_text = ""
        i = 0
        while i < len(text):
            if text[i].isalpha():
                j = i + 1
                while j < len(text) and text[j].isalpha():
                    j += 1
                new_text += 'V_' + text[i:j]
                i = j
            elif text[i] == '\'':
                i += 1
                new_text += '('
                j = i
                while text[j] != '\'':
                    j += 1
                escape = False
                for c in text[i:j]:
                    if not escape:
                        if c == ' ':
                            new_text += 't_space '
                        elif c == '\\':
                            escape = True
                        else:
                            new_text += 't_' + c + ' '
                    else:
                        if c == 'n':
                            new_text += 't_newline '
                        if c == '\\':
                            new_text += 't_escape '
                        escape = False
                new_text += ')'
                i = j + 1
            elif text[i] == '$':
                new_text += 'eps'
                i += 1
            else:
                new_text += text[i]
                i += 1
        return new_text

    @classmethod
    def _to_pretty(cls, cfq: ContextFreeQuery) -> "PrettyContextFreeQuery":
        def cfg_obj_to_pretty(cfg_obj: Union[Variable, Terminal]):
            if isinstance(cfg_obj, Variable):
                return Variable(cfg_obj.value[2:])
            elif isinstance(cfg_obj, Terminal):
                if cfg_obj.value == 't_space':
                    return Terminal(' ')
                if cfg_obj.value == 't_newline':
                    return Terminal('\n')
                if cfg_obj.value == 't_escape':
                    return Terminal('\\')
                return Terminal(cfg_obj.value[2:])
        def production_to_pretty(production: Production):
            new_production = Production(
                    cfg_obj_to_pretty(production.head),
                    list(map(cfg_obj_to_pretty, production.body)),
                    False
                )
            return new_production

        new_productions = set(map(production_to_pretty, cfq._cfg.productions))
        new_cfg = CFG(productions = new_productions, start_symbol = Variable('S'))
        res = cls()
        res._generate_eps = cfq._generate_eps
        res._cfg = new_cfg
        return res

    @classmethod
    def from_text(cls, text: str) -> "PrettyContextFreeQuery":
        return cls._to_pretty(super().from_text(cls._from_pretty(text)))

    @classmethod
    def from_file(cls, path: str) -> "PrettyContextFreeQuery":
        with open(path, 'r') as input_file:
            lines = input_file.readlines()
        text = '\n'.join(lines)
        return cls.from_text(text)
