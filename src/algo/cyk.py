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

from src.config import Config

from pyformlang.cfg import Terminal, Variable
from pygraphblas import Matrix, types
from typing import List, Set, Any, Tuple, Dict

Vertex = int

class MyMatrix:
    def __init__(self, _dict: Dict[Any, Matrix]) -> None:
        self._dict = _dict

    def __getitem__(self, key: Tuple[int, int, Any]) -> bool:
        i, j, k = key
        return self._dict[k].get(i, j, False)

    def __setitem__(self, key: Tuple[int, int, Any], value: bool) -> None:
        i, j, k = key
        self._dict[k][i, j] = True

def cyk(config: Config) -> bool:
    word = config['word']
    query = config['cnf_query']
    if word == '':
        return query.generate_epsilon
    for char in word:
        if Terminal(char) not in query.terminals:
            return False
    len_word = len(word)
    dp: MyMatrix = MyMatrix({
            V: Matrix.sparse(types.BOOL, len_word, len_word)
            for V in query.variables
        })
    for i, char in enumerate(word):
        term = Terminal(char)
        for V in query.simple_antiproductions[term]:
            dp[i, i, V] = True
    for m in range(1, len_word):
        for i in range(len_word - m):
            j = i + m
            for A in query.variables:
                flag = False
                for B, C in query.complex_productions.get(A, set()):
                    for k in range(i, j):
                        if dp[i, k, B] and dp[k+1, j, C]:
                            dp[i, j, A] = True
                            flag = True
                            break
                    if flag:
                        break
    return dp[0, len_word-1, query.start_symbol]
