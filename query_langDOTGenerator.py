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

from antlr4 import ParserRuleContext
from query_langVisitor import query_langVisitor
from query_langParser import query_langParser
from graphviz import Digraph

class query_langDOTGenerator(query_langVisitor):
    def __init__(self, parser:query_langParser):
        self.dot = None
        self.nodes = 0
        self.curPath = []
        self.parser = parser

    def generateDOT(self, title:str):
        self.dot = Digraph(title)
        self.visit(self.parser.script())
        self.dot.render(title.lower().replace(' ', '_'), format='ps')

    def add_node(self, title:str) -> int:
        self.nodes += 1
        ad_new_node = self.nodes
        self.curPath.append(ad_new_node)
        self.dot.node(str(ad_new_node), title)
        return ad_new_node

    def add_edge(self, from_node, to_node):
        if from_node == None or to_node == None:
            return None
        self.dot.edge(str(from_node), str(to_node))
        return from_node

    def obj_to_node(self, obj):
        if isinstance(obj, int):
            return obj
        if isinstance(obj, str):
            return self.add_node(obj)
        if isinstance(obj, ParserRuleContext):
            return self.visit(obj)
        text = obj.getText()
        if text == '':
            return self.add_node('')
        if text[0] == '"':
            return self.add_node(text[1:-1])
        return self.add_node(text)

    def gen_edge(self, title, obj):
        return self.add_edge(self.add_node(title), self.obj_to_node(obj))

    def gen_edges(self, title, objs):
        ad_root = self.add_node(title)
        for obj in objs:
            self.add_edge(ad_root, self.obj_to_node(obj))
        return ad_root

    def gen_edges_optional(self, title, objs):
        if len(objs) == 1:
            return self.obj_to_node(objs[0])
        return self.gen_edges(title, objs)

    def gen_stairs(self, title, objs):
        ad_children = list(map(self.obj_to_node, objs))
        ad_root = ad_children[-1]
        for ad_child in ad_children[-2::-1]:
            ad_new_root = self.add_node(title)
            self.add_edge(ad_new_root, ad_child)
            self.add_edge(ad_new_root, ad_root)
            ad_root = ad_new_root
        return ad_root

    def visitScript(self, ctx:query_langParser.ScriptContext):
        return self.gen_edges('Script', ctx.command())

    def visitConnectC(self, ctx:query_langParser.ConnectCContext):
        return self.gen_edge('Connect', ctx.STRING())

    def visitSelectC(self, ctx:query_langParser.SelectCContext):
        return self.gen_edges('Select', [ctx.obj_expr(), ctx.graph_expr()])

    def visitNamedPatternC(self, ctx:query_langParser.NamedPatternCContext):
        return self.gen_edges('NamedPattern', [ctx.NAME(), ctx.pattern()])

    def visitCommentC(self, ctx:query_langParser.CommentCContext):
        return None

    def visitObj_expr(self, ctx:query_langParser.Obj_exprContext):
        return self.visit(ctx.o_1())

    def visitCountO(self, ctx:query_langParser.CountOContext):
        return self.gen_edge('Count', ctx.o_2())

    def visitSetO(self, ctx:query_langParser.SetOContext):
        return self.visit(ctx.o_2())

    def visitEdgesO(self, ctx:query_langParser.EdgesOContext):
        return self.add_node('Edges')

    def visitFilterO(self, ctx:query_langParser.FilterOContext):
        return self.gen_edges('Filter', [
                self.gen_edges('Cond', [
                    'u',
                    'w',
                    'v',
                    ctx.bool_expr()
                ]),
                'Edges'
            ])

    def visitBool_expr(self, ctx:query_langParser.Bool_exprContext):
        return self.visit(ctx.b_3())

    def visitOrB(self, ctx:query_langParser.OrBContext):
        return self.gen_stairs('Or', ctx.b_2())

    def visitAndB(self, ctx:query_langParser.AndBContext):
        return self.gen_stairs('And', ctx.b_3())

    def visitLblIsB(self, ctx:query_langParser.LblIsBContext):
        return self.gen_edges('LblIs', ['w', ctx.STRING()])

    def visitLblIsNotB(self, ctx:query_langParser.LblIsNotBContext):
        return self.gen_edge('Not',
                self.gen_edges('LblIs', ['w', ctx.STRING()])
            )

    def visitIsStartSB(self, ctx:query_langParser.IsStartSBContext):
        return self.gen_edge('IsStart', 'u')

    def visitIsStartFB(self, ctx:query_langParser.IsStartFBContext):
        return self.gen_edge('IsFinal', 'u')

    def visitIsFinalSB(self, ctx:query_langParser.IsFinalSBContext):
        return self.gen_edge('IsStart', 'v')

    def visitIsFinalFB(self, ctx:query_langParser.IsFinalFBContext):
        return self.gen_edge('IsFinal', 'v')

    def visitIsNotStartSB(self, ctx:query_langParser.IsNotStartSBContext):
        return self.gen_edge('Not',
                self.gen_edge('IsStart', 'u')
            )

    def visitIsNotStartFB(self, ctx:query_langParser.IsNotStartFBContext):
        return self.gen_edge('Not',
                self.gen_edge('IsFinal', 'u')
            )

    def visitIsNotFinalSB(self, ctx:query_langParser.IsNotFinalSBContext):
        return self.gen_edge('Not',
                self.gen_edge('IsStart', 'v')
            )

    def visitIsNotFinalFB(self, ctx:query_langParser.IsNotFinalFBContext):
        return self.gen_edge('Not',
                self.gen_edge('IsFinal', 'v')
            )

    def visitParenthesisB(self, ctx:query_langParser.ParenthesisBContext):
        return self.visit(ctx.b_1())

    def visitNotParenthesisB(self, ctx:query_langParser.NotParenthesisBContext):
        return self.gen_edge('Not', ctx.b_1())

    def visitGraph_expr(self, ctx:query_langParser.Graph_exprContext):
        return self.visit(ctx.g_1())

    def visitDFAG(self, ctx:query_langParser.DFAGContext):
        return self.visit(ctx.g_1_g())

    def visitNoDFAG(self, ctx:query_langParser.NoDFAGContext):
        return self.visit(ctx.g_1_q())

    def visitIntersectDG(self, ctx:query_langParser.IntersectDGContext):
        return self.gen_stairs('Intersect', ctx.g_2_g())

    def visitSetStartAndFinalDG(self, ctx:query_langParser.SetStartAndFinalDGContext):
        return self.gen_edges('SetStartAndFinal',
                self.obj_to_node(ctx.io_vertices()) + [ctx.g_3_g()]
            )

    def visitJustDG(self, ctx:query_langParser.JustDGContext):
        return self.visit(ctx.g_3_g())

    def visitGraphDG(self, ctx:query_langParser.GraphDGContext):
        return self.gen_edge('GraphName', ctx.STRING())

    def visitQueryDG(self, ctx:query_langParser.QueryDGContext):
        return self.gen_edge('Query', ctx.regex())

    def visitParenthesisDG(self, ctx:query_langParser.ParenthesisDGContext):
        return self.visit(ctx.g_1_g())

    def visitIntersectDNG(self, ctx:query_langParser.IntersectDNGContext):
        return self.gen_edges('Intersect', [ctx.g_2_g(), ctx.g_1_q()])

    def visitIntersectNNG(self, ctx:query_langParser.IntersectNNGContext):
        return self.gen_edges('Intersect', [ctx.g_2_q(), ctx.g_1_g()])

    def visitJustDNG(self, ctx:query_langParser.JustDNGContext):
        return self.visit(ctx.g_2_g())

    def visitJustNNG(self, ctx:query_langParser.JustNNGContext):
        return self.visit(ctx.g_2_q())

    def visitSetStartAndFinalNG(self, ctx:query_langParser.SetStartAndFinalNGContext):
        return self.gen_edges('SetStartAndFinal',
                self.obj_to_node(ctx.io_vertices()) + [ctx.g_3_q()]
            )

    def visitJustNG(self, ctx:query_langParser.JustNGContext):
        return self.visit(ctx.g_3_q())

    def visitQueryNG(self, ctx:query_langParser.QueryNGContext):
        return self.gen_edge('Query', ctx.closed_pattern())

    def visitParenthesisNG(self, ctx:query_langParser.ParenthesisNGContext):
        return self.visit(ctx.g_1())

    def visitStartIOV(self, ctx:query_langParser.StartIOVContext):
        return [ctx.vertices(), 'None']

    def visitFinalIOV(self, ctx:query_langParser.FinalIOVContext):
        return ['None', ctx.vertices()]

    def visitStartAndFinalIOV(self, ctx:query_langParser.StartAndFinalIOVContext):
        return ctx.vertices()

    def visitFinalAndStartIOV(self, ctx:query_langParser.FinalAndStartIOVContext):
        return ctx.vertices()[::-1]

    def visitVertices(self, ctx:query_langParser.VerticesContext):
        return self.visit(ctx.v_2())

    def visitUniteV(self, ctx:query_langParser.UniteVContext):
        return self.gen_stairs('Union', ctx.v_2())

    def visitIntersectV(self, ctx:query_langParser.IntersectVContext):
        return self.gen_stairs('Intersection', ctx.v_2())

    def visitSetV(self, ctx:query_langParser.SetVContext):
        return self.gen_edges('Set', ctx.NUM())

    def visitRangeV(self, ctx:query_langParser.RangeVContext):
        return self.gen_edges('Range', ctx.NUM())

    def visitParenthesisV(self, ctx:query_langParser.ParenthesisVContext):
        return self.visit(ctx.v_1())

    def visitPattern(self, ctx:query_langParser.PatternContext):
        return self.visit(ctx.p_1())

    def visitClosed_pattern(self, ctx:query_langParser.Closed_patternContext):
        return self.visit(ctx.p_3())

    def visitAlternativeP(self, ctx:query_langParser.AlternativePContext):
        return self.gen_stairs('Alt', ctx.p_2())

    def visitConcatenationP(self, ctx:query_langParser.ConcatenationPContext):
        return self.gen_edges_optional('Seq', ctx.p_3())

    def visitKleeneStarP(self, ctx:query_langParser.KleeneStarPContext):
        return self.gen_edge('Star', ctx.p_4())

    def visitKleenePlusP(self, ctx:query_langParser.KleenePlusPContext):
        return self.gen_edge('Plus', ctx.p_4())

    def visitOptionP(self, ctx:query_langParser.OptionPContext):
        return self.gen_edge('Option', ctx.p_4())

    def visitJustP(self, ctx:query_langParser.JustPContext):
        return self.visit(ctx.p_4())

    def visitTermP(self, ctx:query_langParser.TermPContext):
        return self.gen_edge('Term', ctx.STRING())

    def visitNontermP(self, ctx:query_langParser.NontermPContext):
        return self.gen_edge('Nonterm', ctx.NAME())

    def visitParenthesisP(self, ctx:query_langParser.ParenthesisPContext):
        return self.visit(ctx.p_1())

    def visitRegex(self, ctx:query_langParser.RegexContext):
        return self.visit(ctx.r_3())

    def visitAlternativeR(self, ctx:query_langParser.AlternativeRContext):
        return self.gen_stairs('Alt', ctx.r_2())

    def visitConcatenationR(self, ctx:query_langParser.ConcatenationRContext):
        return self.gen_edges_optional('Seq', ctx.r_3())

    def visitKleeneStarR(self, ctx:query_langParser.KleeneStarRContext):
        return self.gen_edge('Star', ctx.r_4())

    def visitKleenePlusR(self, ctx:query_langParser.KleenePlusRContext):
        return self.gen_edge('Plus', ctx.r_4())

    def visitOptionR(self, ctx:query_langParser.OptionRContext):
        return self.gen_edge('Option', ctx.r_4())

    def visitJustR(self, ctx:query_langParser.JustRContext):
        return self.visit(ctx.r_4())

    def visitLiteralR(self, ctx:query_langParser.LiteralRContext):
        return self.gen_edge('Term', ctx.STRING())

    def visitParenthesisR(self, ctx:query_langParser.ParenthesisRContext):
        return self.visit(ctx.r_1())
