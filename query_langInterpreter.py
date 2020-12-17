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

import os
from antlr4 import ParserRuleContext
from query_langVisitor import query_langVisitor
from query_langParser import query_langParser
from pygraphblas import Matrix, types
from src.cnf_query import CNFQuery
from src.data_base import DataBase
from src.io_data_base import IODataBase
from functools import reduce
import operator

class VisitException(Exception):
    pass

def cfpq(graph, query):
    n = graph.count_vertexes
    T = graph.copy()
    for A in query.variables:
        T._matrices[A.value] = Matrix.sparse(types.BOOL, n, n)
    for terminal, variables in query.simple_antiproductions.items():
        for i, j, _ in graph.matrices[terminal.value]:
            for variable in variables:
                T[i, variable.value, j] = True
    if query.generate_epsilon:
        for i in range(n):
            T[i, query.start_symbol.value, i] = True
    changing = True
    while changing:
        changing = False
        for (A_j, A_k), As_i in query.complex_antiproductions.items():
            for A_i in As_i:
                prev_nvals = T._matrices[A_i.value].nvals
                T._matrices[A_i.value] += \
                    T._matrices[A_j.value] @ T._matrices[A_k.value]
                if T._matrices[A_i.value].nvals != prev_nvals:
                    changing = True
    return T

def text(ctx):
    if hasattr(ctx, 'STRING'):
        return ctx.STRING().getText()[1:-1]
    if hasattr(ctx, 'NAME'):
        return ctx.NAME().getText()

def as_term(text):
    return 't_' + text

def as_nonterm(text):
    return 'N_' + text

def from_symbol(text):
    return text[2:]

def term_to_text(ctx):
    return as_term(text(ctx))

def nonterm_to_text(ctx):
    return as_nonterm(text(ctx))

def symbol_to_text(ctx):
    if hasattr(ctx, 'nonterm'):
        return nonterm_to_text(ctx.nonterm())
    if hasattr(ctx, 'term'):
        return term_to_text(ctx.term())

def vertex_to_num(ctx):
    return int(ctx.NUM().getText())

def grammar_to_text(grammar):
    res = ''
    for head, body in grammar.items():
        res += head + ' -> ' + body + '\n'
    return res

class query_langInterpreter(query_langVisitor):
    def __init__(self, parser:query_langParser):
        self.db_dir = None
        self.grammar = dict()
        self.graph = None
        self.result = []
        self.parser = parser

    def interpret(self):
        return self.visit(self.parser.script())

    def get_edges(self, predicate):
        def nontemp_edge(edge):
            x, s, y = edge
            return s[-1] != '_'
        return set(filter(predicate, filter(nontemp_edge, self.graph.edges)))

    def intersectGraph(self, graph):
        if graph is None:
            return
        if isinstance(graph, IODataBase):
            if isinstance(self.graph, IODataBase):
                self.graph = graph @ self.graph
            elif isinstance(self.graph, CNFQuery):
                self.graph = cfpq(graph, self.graph)
            else:
                raise Exception('Unknown type ' + str(type(self.graph)))
        elif isinstance(graph, CNFQuery):
            if isinstance(self.graph, IODataBase):
                self.graph = cfpq(self.graph, graph)
            elif isinstance(self.graph, CNFQuery):
                raise Exception('Can\'t intersect two CNFQuery')
            else:
                raise Exception('Unknown type ' + str(type(self.graph)))
        else:
            raise Exception('Unknown type ' + str(type(graph)))

    def visitScript(self, ctx:query_langParser.ScriptContext):
        for command in ctx.command():
            self.visit(command)
        return self.result

    def visitConnectC(self, ctx:query_langParser.ConnectCContext):
        self.db_dir = text(ctx.dir_name())

    def visitSelectC(self, ctx:query_langParser.SelectCContext):
        self.visit(ctx.graph_expr())
        self.visit(ctx.obj_expr())

    def visitNamedPatternC(self, ctx:query_langParser.NamedPatternCContext):
        self.grammar[nonterm_to_text(ctx.nonterm())] = self.visit(ctx.pattern())

    def visitCommentC(self, ctx:query_langParser.CommentCContext):
        self.result.append(text(ctx.comment()))

    def visitDir_name(self, ctx:query_langParser.Dir_nameContext):
        raise VisitException('Dir_name')

    def visitComment(self, ctx:query_langParser.CommentContext):
        raise VisitException('Comment')

    def visitObj_expr(self, ctx:query_langParser.Obj_exprContext):
        self.result.append(self.visit(ctx.o_1()))

    def visitCountO(self, ctx:query_langParser.CountOContext):
        return len(self.visit(ctx.o_2()))

    def visitSetO(self, ctx:query_langParser.SetOContext):
        def pretty_edge(edge):
            x, s, y = edge
            s = from_symbol(s)
            if s[-5:] == '#CNF#':
                s = s[:-5]
            return (x, s, y)
        return set(map(pretty_edge, self.visit(ctx.o_2())))

    def visitEdgesO(self, ctx:query_langParser.EdgesOContext):
        return self.get_edges(lambda edge: True)

    def visitFilterO(self, ctx:query_langParser.FilterOContext):
        return self.visit(ctx.bool_expr())

    def visitBool_expr(self, ctx:query_langParser.Bool_exprContext):
        return self.visit(ctx.b_3())

    def visitOrB(self, ctx:query_langParser.OrBContext):
        return reduce(operator.or_, map(self.visit, ctx.b_2()))

    def visitAndB(self, ctx:query_langParser.AndBContext):
        return reduce(operator.and_, map(self.visit, ctx.b_3()))

    def visitLblIsB(self, ctx:query_langParser.LblIsBContext):
        return self.get_edges(
                lambda edge: edge[1] == symbol_to_text(ctx.symbol())
            )

    def visitLblIsNotB(self, ctx:query_langParser.LblIsNotBContext):
        return self.get_edges(
                lambda edge: edge[1] != symbol_to_text(ctx.symbol())
            )

    def visitIsStartSB(self, ctx:query_langParser.IsStartSBContext):
        return self.get_edges(
                lambda edge: edge[0] in self.graph.start_vertexes
            )

    def visitIsStartFB(self, ctx:query_langParser.IsStartFBContext):
        return self.get_edges(
                lambda edge: edge[0] in self.graph.final_vertexes
            )

    def visitIsFinalSB(self, ctx:query_langParser.IsFinalSBContext):
        return self.get_edges(
                lambda edge: edge[2] in self.graph.start_vertexes
            )

    def visitIsFinalFB(self, ctx:query_langParser.IsFinalFBContext):
        return self.get_edges(
                lambda edge: edge[2] in self.graph.final_vertexes
            )

    def visitIsNotStartSB(self, ctx:query_langParser.IsNotStartSBContext):
        return self.get_edges(
                lambda edge: not edge[0] in self.graph.start_vertexes
            )

    def visitIsNotStartFB(self, ctx:query_langParser.IsNotStartFBContext):
        return self.get_edges(
                lambda edge: not edge[0] in self.graph.final_vertexes
            )

    def visitIsNotFinalSB(self, ctx:query_langParser.IsNotFinalSBContext):
        return self.get_edges(
                lambda edge: not edge[2] in self.graph.start_vertexes
            )

    def visitIsNotFinalFB(self, ctx:query_langParser.IsNotFinalFBContext):
        return self.get_edges(
                lambda edge: not edge[2] in self.graph.final_vertexes
            )

    def visitParenthesisB(self, ctx:query_langParser.ParenthesisBContext):
        return self.visit(ctx.b_1())

    def visitNotParenthesisB(self, ctx:query_langParser.NotParenthesisBContext):
        return self.get_edges(lambda edge: True) - self.visit(ctx.b_1())

    def visitTermS(self, ctx:query_langParser.TermSContext):
        raise VisitException('Symbol')

    def visitNontermS(self, ctx:query_langParser.NontermSContext):
        raise VisitException('Symbol')

    def visitGraph_expr(self, ctx:query_langParser.Graph_exprContext):
        self.graph = None
        self.visit(ctx.g_1())

    def visitGG(self, ctx:query_langParser.GGContext):
        self.visit(ctx.g_1_g())

    def visitQG(self, ctx:query_langParser.QGContext):
        self.visit(ctx.g_1_q())

    def visitIntersectGG(self, ctx:query_langParser.IntersectGGContext):
        res_graph = self.graph
        for g_2_g in ctx.g_2_g():
            self.graph = None
            self.visit(g_2_g)
            self.intersectGraph(res_graph)

    def visitSetStartAndFinalGG(self, ctx:query_langParser.SetStartAndFinalGGContext):
        self.visit(ctx.g_3_g())
        self.graph = IODataBase.from_db_and_io_vertexes(
                self.graph,
                *self.visit(ctx.io_vertices())
            )

    def visitJustGG(self, ctx:query_langParser.JustGGContext):
        self.visit(ctx.g_3_g())
        self.graph = IODataBase.from_db_and_io_vertexes(
                self.graph,
                set(range(self.graph.count_vertexes)),
                set(range(self.graph.count_vertexes))
            )

    def visitGraphG(self, ctx:query_langParser.GraphGContext):
        path = os.path.join(self.db_dir, text(ctx.graph_name()))
        with open(path, 'r') as input_file:
            lines = input_file.readlines()
        Vs_from, Ss, Vs_to = zip(*map(lambda line: line.split(), lines))
        self.graph = DataBase.from_lists(list(map(int, Vs_from)),
                                         list(map(int, Vs_to)),
                                         list(map(as_term, Ss))
                                        )

    def visitParenthesisGG(self, ctx:query_langParser.ParenthesisGGContext):
        self.graph = None
        self.visit(ctx.g_1_g())

    def visitIntersectGQG(self, ctx:query_langParser.IntersectGQGContext):
        res_graph = self.graph
        self.visit(ctx.g_2_g())
        self.intersectGraph(res_graph)
        self.visit(ctx.g_1_q())

    def visitIntersectQQG(self, ctx:query_langParser.IntersectQQGContext):
        res_graph = self.graph
        self.visit(ctx.g_2_q())
        self.intersectGraph(res_graph)
        self.visit(ctx.g_1_g())

    def visitJustGQG(self, ctx:query_langParser.JustGQGContext):
        res_graph = self.graph
        self.visit(ctx.g_2_g())
        self.intersectGraph(res_graph)

    def visitJustQQG(self, ctx:query_langParser.JustQQGContext):
        res_graph = self.graph
        self.visit(ctx.g_2_q())
        self.intersectGraph(res_graph)

    def visitJustQG(self, ctx:query_langParser.JustQGContext):
        self.visit(ctx.g_3_q())

    def visitSimpleQueryG(self, ctx:query_langParser.SimpleQueryGContext):
        self.graph = CNFQuery.from_text(
                grammar_to_text(self.grammar),
                nonterm_to_text(ctx.nonterm())
            )

    def visitComplexQueryG(self, ctx:query_langParser.ComplexQueryGContext):
        temp_grammar = self.grammar.copy()
        temp_grammar[nonterm_to_text(ctx.nonterm())] = \
            self.visit(ctx.closed_pattern())
        self.graph = CNFQuery.from_text(
                grammar_to_text(temp_grammar),
                nonterm_to_text(ctx.nonterm())
            )

    def visitParenthesisQG(self, ctx:query_langParser.ParenthesisQGContext):
        self.graph = None
        self.visit(ctx.g_1())

    def visitGraph_name(self, ctx:query_langParser.Graph_nameContext):
        raise VisitException('Graph_name')

    def visitStartIOV(self, ctx:query_langParser.StartIOVContext):
        return (
                self.visit(ctx.start_vertices()),
                set(range(self.graph.count_vertexes))
            )

    def visitFinalIOV(self, ctx:query_langParser.FinalIOVContext):
        return (
                set(range(self.graph.count_vertexes)),
                self.visit(ctx.final_vertices())
            )

    def visitStartAndFinalIOV(self, ctx:query_langParser.StartAndFinalIOVContext):
        return (
                self.visit(ctx.start_vertices()),
                self.visit(ctx.final_vertices())
            )

    def visitStart_vertices(self, ctx:query_langParser.Start_verticesContext):
        return self.visit(ctx.vertices())

    def visitFinal_vertices(self, ctx:query_langParser.Final_verticesContext):
        return self.visit(ctx.vertices())

    def visitVertices(self, ctx:query_langParser.VerticesContext):
        return self.visit(ctx.v_2())

    def visitUniteV(self, ctx:query_langParser.UniteVContext):
        return reduce(operator.or_, map(self.visit, ctx.v_2()))

    def visitIntersectV(self, ctx:query_langParser.IntersectVContext):
        return reduce(operator.and_, map(self.visit, ctx.v_2()))

    def visitSetV(self, ctx:query_langParser.SetVContext):
        return set(map(vertex_to_num, ctx.vertex()))

    def visitRangeV(self, ctx:query_langParser.RangeVContext):
        return set(range(
                vertex_to_num(ctx.vertexFrom().vertex()),
                vertex_to_num(ctx.vertexTo().vertex()) + 1
            ))

    def visitParenthesisV(self, ctx:query_langParser.ParenthesisVContext):
        return self.visit(ctx.v_1())

    def visitVertexFrom(self, ctx:query_langParser.VertexFromContext):
        raise VisitException('VertexFrom')

    def visitVertexTo(self, ctx:query_langParser.VertexToContext):
        raise VisitException('VertexTo')

    def visitVertex(self, ctx:query_langParser.VertexContext):
        raise VisitException('Vertex')

    def visitPattern(self, ctx:query_langParser.PatternContext):
        return self.visit(ctx.p_1())

    def visitClosed_pattern(self, ctx:query_langParser.Closed_patternContext):
        return self.visit(ctx.p_3())

    def visitAlternativeP(self, ctx:query_langParser.AlternativePContext):
        return ' | '.join(map(self.visit, ctx.p_2()))

    def visitConcatenationP(self, ctx:query_langParser.ConcatenationPContext):
        return ' '.join(map(self.visit, ctx.p_3()))

    def visitKleeneStarP(self, ctx:query_langParser.KleeneStarPContext):
        return self.visit(ctx.p_4()) + '*'

    def visitKleenePlusP(self, ctx:query_langParser.KleenePlusPContext):
        reg = self.visit(ctx.p_4())
        return '(' + reg + ' ' + reg + '*)'

    def visitOptionP(self, ctx:query_langParser.OptionPContext):
        return '(' + self.visit(ctx.p_4()) + ' | eps)'

    def visitJustP(self, ctx:query_langParser.JustPContext):
        return self.visit(ctx.p_4())

    def visitTermP(self, ctx:query_langParser.TermPContext):
        return symbol_to_text(ctx)

    def visitNontermP(self, ctx:query_langParser.NontermPContext):
        return symbol_to_text(ctx)

    def visitParenthesisP(self, ctx:query_langParser.ParenthesisPContext):
        return self.visit(ctx.p_1())

    def visitTerm(self, ctx:query_langParser.TermContext):
        raise VisitException('Term')

    def visitNonterm(self, ctx:query_langParser.NontermContext):
        raise VisitException('Nonterm')

del query_langParser
