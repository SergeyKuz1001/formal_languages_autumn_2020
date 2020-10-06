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
from .io_graph import IOGraph

from pyformlang.cfg import CFG, Terminal, Variable
from pyformlang.cfg.cfg_object import CFGObject
from pyformlang.finite_automaton import Symbol
from pygraphblas import Matrix, types
from typing import Dict, Set, Optional, Tuple, Union, List, Any

Vertex = int

class RAQuery(ContextFreeQuery, IOGraph):
    class Bor:
        def __init__(self) -> None:
            self.links: List[Dict[Any, Vertex]] = [dict()]
            self.parents: List[Optional[Tuple[Vertex, Any]]] = [None]
            self.in_tail: List[bool] = [False]
            self.amount_vertexes: int = 1
            self.final_vertexes: List[Vertex] = []

        def add_path(self, path: List[Any]) -> None:
            vertex: Vertex = 0
            for elem in path:
                if self.in_tail[vertex] and self.links[vertex] != dict():
                    self.in_tail[vertex] = False
                if elem not in self.links[vertex]:
                    self.links.append(dict())
                    self.parents.append((vertex, elem))
                    self.in_tail.append(True)
                    self.links[vertex][elem] = self.amount_vertexes
                    self.amount_vertexes += 1
                else:
                    self.in_tail[self.links[vertex][elem]] = False
                vertex = self.links[vertex][elem]
            self.final_vertexes.append(vertex)

        def glue_tail(self) -> Tuple[
                                        List[Dict[Any, Vertex]],
                                        Tuple[Vertex, List[Vertex]]
                                    ]:
            res: List[Dict[Any, Vertex]] = [dict()]
            as_new_vertex: Dict[Vertex, Vertex] = dict()
            for vertex in range(self.amount_vertexes-1, -1, -1):
                if not self.in_tail[vertex]:
                    as_new_vertex[vertex] = len(res)
                    res.append(dict())
                    for elem, son in self.links[vertex].items():
                        if not self.in_tail[son]:
                            res[as_new_vertex[vertex]][elem] = \
                                    as_new_vertex[son]
            start_vertex: Vertex = as_new_vertex[0]
            tail_vertexes: List[Tuple[Vertex, List[Vertex]]] = [
                    (
                        0,
                        list(filter(
                                lambda vertex: self.in_tail[vertex],
                                self.final_vertexes
                            ))
                    )
                ]
            while tail_vertexes != []:
                gluing_vertex, glued_vertexes = tail_vertexes.pop()
                parents_glued_vertexes: Dict[Any, List[Vertex]] = dict()
                for vertex in glued_vertexes:
                    parent_vertex, elem = self.parents[vertex]
                    if not self.in_tail[parent_vertex]:
                        res[as_new_vertex[parent_vertex]][elem] = gluing_vertex
                    else:
                        parents_glued_vertexes.setdefault(elem, [])
                        parents_glued_vertexes[elem].append(parent_vertex)
                for elem, parents_vertexes in parents_glued_vertexes.items():
                    new_vertex: Vertex = len(res)
                    res.append(dict())
                    res[new_vertex][elem] = gluing_vertex
                    tail_vertexes.append((new_vertex, parents_vertexes))
            final_vertexes: List[Vertex] = [0] + \
                    list(map(as_new_vertex.get, filter(
                            lambda vertex: not self.in_tail[vertex],
                            self.final_vertexes
                        )))
            return (res, (start_vertex, final_vertexes))

    def __init__(self) -> None:
        super().__init__()
        self._Ps: Dict[Variable, Set[List[CFGObject]]] = dict()
        self._V_of_path_from: Dict[Vertex, Variable] = dict()

    @property
    def productions(self
            ) -> Dict[Variable, Set[List[CFGObject]]]:
        return self._Ps

    def variable_of_path_from(self, vertex: Vertex) -> Variable:
        return self._V_of_path_from[vertex]

    @classmethod
    def from_context_free_query(cls, cfq: ContextFreeQuery) -> "RAQuery":
        res = cls()
        res._cfg = cfq._cfg
        for production in res._cfg.productions:
            res._Ps.setdefault(production.head, set())
            res._Ps[production.head].add(tuple(production.body))
        bors: Dict[Variable, Bor] = dict()
        for head, bodies in res._Ps.items():
            bors[head] = cls.Bor()
            for body in bodies:
                bors[head].add_path(body)
        glued_bors = {
                variable: bor.glue_tail()
                for variable, bor in bors.items()
            }
        res._count_Vs = sum(map(lambda t: len(t[0]), glued_bors.values()))
        symbols = map(
                lambda x: Symbol(x.value),
                res._cfg.variables | res._cfg.terminals)
        res._matrices: Dict[Symbol, Matrix] = {
                symbol: Matrix.sparse(
                        types.BOOL,
                        res._count_Vs,
                        res._count_Vs
                    )
                for symbol in symbols
            }
        m: int = 0
        for variable, glued_bor in glued_bors.items():
            graph, (start_vertex, final_vertexes) = glued_bor
            for i, links in enumerate(graph):
                for elem, j in links.items():
                    symbol = Symbol(elem.value)
                    res._matrices[symbol][i + m, j + m] = True
            res._start_Vs.add(start_vertex + m)
            res._V_of_path_from[start_vertex + m] = variable
            for final_vertex in final_vertexes:
                res._final_Vs.add(final_vertex + m)
            m += len(graph)
        return res

    @classmethod
    def from_text(cls, text: str) -> "RAQuery":
        return cls.from_context_free_query(ContextFreeQuery.from_text(text))
