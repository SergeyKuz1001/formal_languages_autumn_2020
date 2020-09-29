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

from pyformlang.finite_automaton import DeterministicFiniteAutomaton, \
                                        State, Symbol
from pyformlang.regular_expression import Regex
from pygraphblas import Matrix, types
from typing import Dict, Set, Optional

DFA = DeterministicFiniteAutomaton
Vertex = int

class Query:
    def __init__(self) -> None:
        self._matrices: Dict[Symbol, Matrix] = dict()
        self._start_V: Optional[Vertex] = None
        self._final_Vs: Set[Vertex] = set()

    @property
    def size(self) -> int:
        return list(self._matrices.values())[0].ncols

    @property
    def start_vertex(self) -> Vertex:
        if self._start_V is None:
            raise ValueError
        return self._start_V

    @property
    def final_vertexes(self) -> Set[Vertex]:
        return self._final_Vs

    @property
    def symbols(self) -> Set[Symbol]:
        return set(self._matrices.keys())

    @property
    def matrices(self) -> Dict[Symbol, Matrix]:
        return self._matrices

    @classmethod
    def from_regex(cls, regex: str) -> "Query":
        return cls.from_dfa(Regex(regex.strip()).to_epsilon_nfa().minimize())

    @classmethod
    def from_dfa(cls, dfa: DFA) -> "Query":
        Q_to_V = { Q: V for V, Q in enumerate(dfa.states) }
        res = cls()
        res._matrices = cls._dfa_dict_to_matrices(dfa.to_dict(), Q_to_V)
        res._start_V = Q_to_V[dfa.start_state]
        res._final_Vs = set(map(Q_to_V.get, dfa.final_states))
        return res

    @classmethod
    def from_file(cls, path: str) -> "Query":
        with open(path, 'r') as input_file:
            line = input_file.readline()
        return cls.from_regex(line)

    @staticmethod
    def _dfa_dict_to_matrices(Q_and_S_to_Q: Dict[State, Dict[Symbol, State]],
                              Q_to_V: Dict[State, Vertex]
                             ) -> Dict[Symbol, Matrix]:
        size = len(Q_to_V)
        matrices: Dict[Symbol, Matrix] = dict()
        for Q_from, S_to_Q in Q_and_S_to_Q.items():
            V_from = Q_to_V[Q_from]
            for S, Q_to in S_to_Q.items():
                V_to = Q_to_V[Q_to]
                matrices.setdefault(S,
                        Matrix.sparse(types.BOOL, size, size))
                matrices[S][V_from, V_to] = True
        return matrices
