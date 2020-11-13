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

pretty_dict = {
        ' ': 'space',
        '_': 'underscore',
        '.': 'dot',
        ',': 'comma',
        '+': 'plus',
        '-': 'minus',
        '*': 'multiply',
        '/': 'division',
        '"': 'double_quotes',
        '(': 'opening_parenthesis',
        ')': 'closing_parenthesis',
        '[': 'opening_square_bracket',
        ']': 'closing_square_bracket',
        '{': 'opening_brace',
        '}': 'closing_brace',
        '?': 'question_mark',
        ':': 'colon',
        '&': 'logical_and',
        '|': 'logical_or'
    }

anti_pretty_dict = {s: c for c, s in pretty_dict.items()}

class PrettyContextFreeQuery(ContextFreeQuery):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def _to_pretty_term(cls, char: str) -> str:
        if char in pretty_dict.keys():
            return 't_' + pretty_dict[char]
        return 't_' + char

    @classmethod
    def _from_pretty_term(cls, term: str) -> str:
        if term[2:] in anti_pretty_dict.keys():
            return anti_pretty_dict[term[2:]]
        return term[2:]

    @classmethod
    def _from_pretty(cls, text: str) -> str:
        new_text = ""
        i = 0
        while i < len(text):
            if text[i].isalpha() or text[i] == '_' or text[i].isdigit():
                j = i + 1
                while j < len(text) and (text[j].isalpha() or text[j] == '_' or text[j].isdigit()):
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
                        if c == '\\':
                            escape = True
                        else:
                            new_text += cls._to_pretty_term(c) + ' '
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
            elif text[i] == '|' and text[i-1] != '\'':
                new_text += ') | ('
                i += 1
            elif text[i] == '(':
                new_text += '(('
                i += 1
            elif text[i] == ')':
                new_text += '))'
                i += 1
            elif text[i] == '>' and text[i-1] == '-':
                new_text += '> ('
                i += 1
            elif text[i] == '\n':
                new_text += ')\n'
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
                if cfg_obj.value == 't_newline':
                    return Terminal('\n')
                if cfg_obj.value == 't_escape':
                    return Terminal('\\')
                return Terminal(cls._from_pretty_term(cfg_obj.value))
        def production_to_pretty(production: Production):
            new_production = Production(
                    cfg_obj_to_pretty(production.head),
                    list(map(cfg_obj_to_pretty, production.body)),
                    False
                )
            return new_production

        pretty_productions = list(map(str, cfq._cfg.productions))
        pretty_productions.sort()
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
            text = input_file.read()
        return cls.from_text(text)
