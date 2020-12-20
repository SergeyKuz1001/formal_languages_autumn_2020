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

class AskNumberException(Exception):
    pass

class FormatTextException(Exception):
    pass

class FindVariableException(Exception):
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

class query_langInterpreter(query_langVisitor):
    def __init__(self, parser:query_langParser):
        self.db_dir = None
        self.graph = None
        self.edges = None
        self.grammar = dict()
        self.vars_str = dict()
        self.vars_num = dict()
        self.online = True
        self.inputs = []
        self.result = []
        self.parser = parser

    def interpret(self, online = True, inputs = []):
        script = self.parser.script()
        self.online = online
        self.inputs = inputs
        return self.visit(script)

    def input(self):
        if self.online or self.inputs == []:
            return input()
        else:
            return self.inputs.pop(0)

    def print(self, text):
        if self.online:
            print(text)
        else:
            self.result.append(text)

    def get_edges(self, predicate):
        return set(filter(predicate, self.edges))

    def text(self, ctx):
        if hasattr(ctx, 'STRING'):
            def has_format_block(string):
                nonlocal lc, rc
                while '{' in string[rc : ]:
                    lc = string.index('{', rc)
                    if string[lc - 1] == '\\':
                        rc = lc + 1
                    elif '}' in string[lc : ]:
                        rc = string.index('}', lc)
                        return True
                    else:
                        raise FormatTextException(f'"{string}" hasn\'t ' + '"}"')
                return False
            string = ctx.STRING().getText()
            lc, rc = 0, 0
            while has_format_block(string):
                var_name = string[lc + 1 : rc]
                if not var_name in self.vars_str:
                    raise FindVariableException(
                            f'String variable "{var_name}" wasn\'t found'
                        )
                string = string[:lc] + self.vars_str[var_name] + string[rc+1:]
            return string[1:-1]
        elif hasattr(ctx, 'NAME'):
            return ctx.NAME().getText()

    def as_term(self, text):
        return 't_' + text

    def as_nonterm(self, text):
        return 'N_' + text

    def from_symbol(self, text):
        return text[2:]

    def term_to_text(self, ctx):
        return self.as_term(self.text(ctx))

    def nonterm_to_text(self, ctx):
        return self.as_nonterm(self.text(ctx))

    def symbol_to_text(self, ctx):
        if hasattr(ctx, 'var'):
            return self.nonterm_to_text(ctx.var())
        elif hasattr(ctx, 'term'):
            return self.term_to_text(ctx.term())

    def vertex_to_num(self, ctx):
        if hasattr(ctx, 'NUM'):
            return int(ctx.NUM().getText())
        elif hasattr(ctx, 'var'):
            var_name = self.text(ctx.var())
            if var_name in self.vars_num:
                return self.vars_num[var_name]
            else:
                raise FindVariableException(
                        f'Number variable "{var_name}" wasn\'t found'
                    )

    def grammar_to_text(self, grammar):
        res = ''
        for head, body in grammar.items():
            res += head + ' -> ' + body + '\n'
        return res

    def visible_edge(self, edge):
        x, s, y = edge
        return s[-1] != '_' and not '#' in s

    def ioing(self, graph):
        all_vs = set(range(graph.count_vertexes))
        return IODataBase.from_db_and_io_vertexes(graph, all_vs, all_vs)

    def intersect(self, obj1, obj2):
        if isinstance(obj1, IODataBase):
            if isinstance(obj2, IODataBase):
                return obj1 & obj2
            elif isinstance(obj2, DataBase):
                return obj1 & self.ioing(obj2)
            elif isinstance(obj2, CNFQuery):
                return cfpq(obj1, obj2)
            else:
                raise Exception('Unknown type ' + str(type(obj2)))
        elif isinstance(obj1, DataBase):
            if isinstance(obj2, IODataBase):
                return self.ioing(obj1) & obj2
            elif isinstance(obj2, DataBase):
                return obj1 & obj2
            elif isinstance(obj2, CNFQuery):
                return cfpq(obj1, obj2)
            else:
                raise Exception('Unknown type ' + str(type(obj2)))
        elif isinstance(obj1, CNFQuery):
            if isinstance(obj2, IODataBase):
                return cfpq(obj2, obj1)
            elif isinstance(obj2, DataBase):
                return cfpq(obj2, obj1)
            elif isinstance(obj2, CNFQuery):
                raise Exception('Can\'t intersect two CNFQuery')
            else:
                raise Exception('Unknown type ' + str(type(obj2)))
        else:
            raise Exception('Unknown type ' + str(type(obj1)))

    def visitScript(self, ctx:query_langParser.ScriptContext):
        for command in ctx.command():
            self.visit(command)
        if not self.online:
            return self.result

    def visitConnectC(self, ctx:query_langParser.ConnectCContext):
        self.db_dir = self.text(ctx.dir_name())

    def visitSimpleSISelectC(self, ctx:query_langParser.SimpleSISelectCContext):
        self.visit(ctx.graph_expr_si())
        self.visit(ctx.obj_expr())

    def visitSimpleIOSelectC(self, ctx:query_langParser.SimpleIOSelectCContext):
        self.visit(ctx.graph_expr_io())
        self.visit(ctx.obj_expr())

    def visitFilterSISelectC(self, ctx:query_langParser.FilterSISelectCContext):
        self.visit(ctx.graph_expr_si())
        self.visit(ctx.bool_expr_si())
        self.visit(ctx.obj_expr())

    def visitFilterIOSelectC(self, ctx:query_langParser.FilterIOSelectCContext):
        self.visit(ctx.graph_expr_io())
        self.visit(ctx.bool_expr_io())
        self.visit(ctx.obj_expr())

    def visitNamedPatternC(self, ctx:query_langParser.NamedPatternCContext):
        self.grammar[self.nonterm_to_text(ctx.var())] = self.visit(ctx.pattern())

    def visitAskStringC(self, ctx:query_langParser.AskStringCContext):
        value = self.input()
        var_name = self.text(ctx.var())
        self.vars_str[var_name] = value

    def visitAskNumberC(self, ctx:query_langParser.AskNumberCContext):
        value = self.input()
        try:
            value = int(value)
        except ValueError:
            raise AskNumberException(f'"{value}" isn\'t number')
        var_name = self.text(ctx.var())
        self.vars_num[var_name] = value

    def visitTellC(self, ctx:query_langParser.TellCContext):
        self.print(self.text(ctx))

    def visitDir_name(self, ctx:query_langParser.Dir_nameContext):
        raise VisitException('Dir_name')

    def visitObj_expr(self, ctx:query_langParser.Obj_exprContext):
        self.print(self.visit(ctx.o_1()))

    def visitCountO(self, ctx:query_langParser.CountOContext):
        return len(self.visit(ctx.o_2()))

    def visitSetO(self, ctx:query_langParser.SetOContext):
        return self.visit(ctx.o_2())

    def visitEdgesO(self, ctx:query_langParser.EdgesOContext):
        def pretty_edge(edge):
            x, s, y = edge
            return (x, self.from_symbol(s), y)
        return set(map(pretty_edge, self.edges))

    def visitPairsO(self, ctx:query_langParser.PairsOContext):
        def edge_to_pair(edge):
            x, s, y = edge
            return (x, y)
        return set(map(edge_to_pair, self.edges))

    def visitStartVsO(self, ctx:query_langParser.StartVsOContext):
        return set(map(lambda edge: edge[0], self.edges))

    def visitFinalVsO(self, ctx:query_langParser.FinalVsOContext):
        return set(map(lambda edge: edge[2], self.edges))

    def visitBool_expr_si(self, ctx:query_langParser.Bool_expr_siContext):
        self.edges = self.visit(ctx.b_3_si())

    def visitOrSIB(self, ctx:query_langParser.OrSIBContext):
        return reduce(operator.or_, map(self.visit, ctx.b_2_si()))

    def visitAndSIB(self, ctx:query_langParser.AndSIBContext):
        return reduce(operator.and_, map(self.visit, ctx.b_3_si()))

    def visitConstructSIB(self, ctx:query_langParser.ConstructSIBContext):
        return self.visit(ctx.b_4_si())

    def visitParenthesisSIB(self, ctx:query_langParser.ParenthesisSIBContext):
        return self.visit(ctx.b_1_si())

    def visitNotParenthesisSIB(self, ctx:query_langParser.NotParenthesisSIBContext):
        return self.edges - self.visit(ctx.b_1_si())

    def visitLblIsB(self, ctx:query_langParser.LblIsBContext):
        symbol = self.symbol_to_text(ctx.symbol())
        return self.get_edges(
                lambda edge: edge[1] == symbol
            )

    def visitLblIsNotB(self, ctx:query_langParser.LblIsNotBContext):
        symbol = self.symbol_to_text(ctx.symbol())
        return self.get_edges(
                lambda edge: edge[1] != symbol
            )

    def visitLoopB(self, ctx:query_langParser.LoopBContext):
        return self.get_edges(
                lambda edge: edge[0] == edge[2]
            )

    def visitNotLoopB(self, ctx:query_langParser.NotLoopBContext):
        return self.get_edges(
                lambda edge: edge[0] != edge[2]
            )

    def visitBool_expr_io(self, ctx:query_langParser.Bool_expr_ioContext):
        self.edges = self.visit(ctx.b_3_io())

    def visitOrIOB(self, ctx:query_langParser.OrIOBContext):
        return reduce(operator.or_, map(self.visit, ctx.b_2_io()))

    def visitAndIOB(self, ctx:query_langParser.AndIOBContext):
        return reduce(operator.and_, map(self.visit, ctx.b_3_io()))

    def visitConstructIOB(self, ctx:query_langParser.ConstructIOBContext):
        return self.visit(ctx.b_4_io())

    def visitParenthesisIOB(self, ctx:query_langParser.ParenthesisIOBContext):
        return self.visit(ctx.b_1_io())

    def visitNotParenthesisIOB(self, ctx:query_langParser.NotParenthesisIOBContext):
        return self.edges - self.visit(ctx.b_1_io())

    def visitSIB(self, ctx:query_langParser.SIBContext):
        return self.visit(ctx.b_4_si())

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

    def visitTermS(self, ctx:query_langParser.TermSContext):
        raise VisitException('Symbol')

    def visitNontermS(self, ctx:query_langParser.NontermSContext):
        raise VisitException('Symbol')

    def visitGraph_expr_si(self, ctx:query_langParser.Graph_expr_siContext):
        self.graph = self.visit(ctx.g_1_si())
        self.edges = set(filter(self.visible_edge, self.graph.edges))

    def visitGG(self, ctx:query_langParser.GGContext):
        return self.visit(ctx.g_1_g())

    def visitLG(self, ctx:query_langParser.LGContext):
        return self.visit(ctx.g_1_l())

    def visitGraph_expr_io(self, ctx:query_langParser.Graph_expr_ioContext):
        self.graph = self.visit(ctx.g_1_io())
        self.edges = set(filter(self.visible_edge, self.graph.edges))

    def visitHG(self, ctx:query_langParser.HGContext):
        return self.visit(ctx.g_1_h())

    def visitJG(self, ctx:query_langParser.JGContext):
        return self.visit(ctx.g_1_j())

    def visitJustGG(self, ctx:query_langParser.JustGGContext):
        return self.visit(ctx.g_2_g())

    def visitIntersectGHGG(self, ctx:query_langParser.IntersectGHGGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_h(), ctx.g_2_g()]))

    def visitIntersectGGHG(self, ctx:query_langParser.IntersectGGHGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_g(), ctx.g_2_h()]))

    def visitIntersectGHHG(self, ctx:query_langParser.IntersectGHHGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_h(), ctx.g_2_h()]))

    def visitIntersectGGGG(self, ctx:query_langParser.IntersectGGGGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_g(), ctx.g_2_g()]))

    def visitSIGG(self, ctx:query_langParser.SIGGContext):
        return self.visit(ctx.g_3_g())

    def visitConstructGG(self, ctx:query_langParser.ConstructGGContext):
        return self.visit(ctx.g_4_g())

    def visitParenthesisGG(self, ctx:query_langParser.ParenthesisGGContext):
        return self.visit(ctx.g_1_g())

    def visitGraphG(self, ctx:query_langParser.GraphGContext):
        path = os.path.join(self.db_dir, self.text(ctx.graph_name()))
        with open(path, 'r') as input_file:
            lines = input_file.readlines()
        Vs_from, Ss, Vs_to = zip(*map(lambda line: line.split(), lines))
        return DataBase.from_lists(
                list(map(int, Vs_from)),
                list(map(int, Vs_to)),
                list(map(self.as_term, Ss))
            )

    def visitJustQG(self, ctx:query_langParser.JustQGContext):
        return self.visit(ctx.g_2_q())

    def visitSIQG(self, ctx:query_langParser.SIQGContext):
        return self.visit(ctx.g_3_q())

    def visitConstructQG(self, ctx:query_langParser.ConstructQGContext):
        return self.visit(ctx.g_4_q())

    def visitParenthesisQG(self, ctx:query_langParser.ParenthesisQGContext):
        return self.visit(ctx.g_1_q())

    def visitSimpleQueryG(self, ctx:query_langParser.SimpleQueryGContext):
        return CNFQuery.from_text(
                self.grammar_to_text(self.grammar),
                self.nonterm_to_text(ctx.var())
            )

    def visitComplexQueryG(self, ctx:query_langParser.ComplexQueryGContext):
        temp_grammar = self.grammar.copy()
        var_name = self.nonterm_to_text(ctx.var())
        temp_grammar[var_name] = self.visit(ctx.closed_pattern())
        return CNFQuery.from_text(
                self.grammar_to_text(temp_grammar),
                var_name
            )

    def visitIntersectLHJG(self, ctx:query_langParser.IntersectLHJGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_h(), ctx.g_2_j()]))

    def visitIntersectLJLG(self, ctx:query_langParser.IntersectLJLGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_j(), ctx.g_2_l()]))

    def visitIntersectLJJG(self, ctx:query_langParser.IntersectLJJGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_j(), ctx.g_2_j()]))

    def visitIntersectLLLG(self, ctx:query_langParser.IntersectLLLGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_l(), ctx.g_2_l()]))

    def visitIntersectLJHG(self, ctx:query_langParser.IntersectLJHGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_j(), ctx.g_2_h()]))

    def visitIntersectLLJG(self, ctx:query_langParser.IntersectLLJGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_l(), ctx.g_2_j()]))

    def visitIntersectLJGG(self, ctx:query_langParser.IntersectLJGGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_j(), ctx.g_2_g()]))

    def visitIntersectLQLG(self, ctx:query_langParser.IntersectLQLGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_q(), ctx.g_2_l()]))

    def visitIntersectLLQG(self, ctx:query_langParser.IntersectLLQGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_l(), ctx.g_2_q()]))

    def visitIntersectJQJG(self, ctx:query_langParser.IntersectJQJGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_q(), ctx.g_2_j()]))

    def visitIntersectJJQG(self, ctx:query_langParser.IntersectJJQGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_j(), ctx.g_2_q()]))

    def visitIntersectLLHG(self, ctx:query_langParser.IntersectLLHGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_l(), ctx.g_2_h()]))

    def visitIntersectLLGG(self, ctx:query_langParser.IntersectLLGGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_l(), ctx.g_2_g()]))

    def visitIntersectLGQG(self, ctx:query_langParser.IntersectLGQGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_g(), ctx.g_2_q()]))

    def visitIntersectJHQG(self, ctx:query_langParser.IntersectJHQGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_h(), ctx.g_2_q()]))

    def visitJustLG(self, ctx:query_langParser.JustLGContext):
        return self.visit(ctx.g_2_l())

    def visitIntersectLGLG(self, ctx:query_langParser.IntersectLGLGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_g(), ctx.g_2_l()]))

    def visitIntersectLHLG(self, ctx:query_langParser.IntersectLHLGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_h(), ctx.g_2_l()]))

    def visitIntersectLGJG(self, ctx:query_langParser.IntersectLGJGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_g(), ctx.g_2_j()]))

    def visitIntersectJQHG(self, ctx:query_langParser.IntersectJQHGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_q(), ctx.g_2_h()]))

    def visitIntersectLQGG(self, ctx:query_langParser.IntersectLQGGContext):
        return self.intersect(*map(self.visit, [ctx.g_1_q(), ctx.g_2_g()]))

    def visitSILG(self, ctx:query_langParser.SILGContext):
        return self.visit(ctx.g_3_l())

    def visitParenthesisLG(self, ctx:query_langParser.ParenthesisLGContext):
        return self.visit(ctx.g_1_l())

    def visitJustHG(self, ctx:query_langParser.JustHGContext):
        return self.visit(ctx.g_2_h())

    def visitIOHG(self, ctx:query_langParser.IOHGContext):
        return IODataBase.from_db_and_io_vertexes(
                self.visit(ctx.g_3_g()),
                *self.visit(ctx.io_vertices())
            )

    def visitSIHG(self, ctx:query_langParser.SIHGContext):
        return self.visit(ctx.g_3_h())

    def visitParenthesisHG(self, ctx:query_langParser.ParenthesisHGContext):
        return self.visit(ctx.g_1_h())

    def visitJustJG(self, ctx:query_langParser.JustJGContext):
        return self.visit(ctx.g_2_j())

    def visitIOJG(self, ctx:query_langParser.IOJGContext):
        return IODataBase.from_db_and_io_vertexes(
                self.visit(ctx.g_3_l()),
                *self.visit(ctx.io_vertices())
            )

    def visitSIJG(self, ctx:query_langParser.SIJGContext):
        return self.visit(ctx.g_3_j())

    def visitParenthesisJG(self, ctx:query_langParser.ParenthesisJGContext):
        return self.visit(ctx.g_1_j())

    def visitGraph_name(self, ctx:query_langParser.Graph_nameContext):
        raise VisitException('Graph_name')

    def visitStartIOV(self, ctx:query_langParser.StartIOVContext):
        return (
                self.visit(ctx.start_vertices()),
                None
            )

    def visitFinalIOV(self, ctx:query_langParser.FinalIOVContext):
        return (
                None,
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
        return set(map(self.vertex_to_num, ctx.vertex()))

    def visitRangeV(self, ctx:query_langParser.RangeVContext):
        return set(range(
                self.vertex_to_num(ctx.vertexFrom().vertex()),
                self.vertex_to_num(ctx.vertexTo().vertex()) + 1
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
        return '(' + ') | ('.join(map(self.visit, ctx.p_2())) + ')'

    def visitConcatenationP(self, ctx:query_langParser.ConcatenationPContext):
        return '(' + ') ('.join(map(self.visit, ctx.p_3())) + ')'

    def visitKleeneStarP(self, ctx:query_langParser.KleeneStarPContext):
        return '(' + self.visit(ctx.p_4()) + ')*'

    def visitKleenePlusP(self, ctx:query_langParser.KleenePlusPContext):
        reg = self.visit(ctx.p_4())
        return '((' + reg + ') (' + reg + ')*)'

    def visitOptionP(self, ctx:query_langParser.OptionPContext):
        return '(' + self.visit(ctx.p_4()) + ' | eps)'

    def visitJustP(self, ctx:query_langParser.JustPContext):
        return self.visit(ctx.p_4())

    def visitTermP(self, ctx:query_langParser.TermPContext):
        return self.symbol_to_text(ctx)

    def visitNontermP(self, ctx:query_langParser.NontermPContext):
        return self.symbol_to_text(ctx)

    def visitEpsilonP(self, ctx:query_langParser.EpsilonPContext):
        return 'eps'

    def visitParenthesisP(self, ctx:query_langParser.ParenthesisPContext):
        return self.visit(ctx.p_1())

    def visitTerm(self, ctx:query_langParser.TermContext):
        raise VisitException('Term')

    def visitVar(self, ctx:query_langParser.VarContext):
        raise VisitException('Var')

del query_langParser
