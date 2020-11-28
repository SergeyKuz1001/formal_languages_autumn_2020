/**
   Copyright 2020 Sergey Kuzivanov

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
grammar query_lang;
script : SEP? (command ',' SEP?)* command '.' SEP? ;
command : 'connect' SEP 'to' SEP file_name=STRING # ConnectC
        | 'select' SEP obj_expr SEP 'from' SEP graph_expr # SelectC
        | (
              'define' SEP nonterm=NAME SEP 'as' SEP pattern
            | nonterm=NAME SEP? '->' SEP? pattern
          ) # NamedPatternC
        | comment=STRING # CommentC
        ;
obj_expr : o_1 ;
o_1 : 'count' SEP 'of' SEP o_2 # CountO
    | o_2 # SetO
    ;
o_2 : 'edges' # EdgesO
    | 'edges' SEP 'which' SEP bool_expr # FilterO
    ;
bool_expr : b_3 ;
b_1 : (b_2 (SEP? '|' SEP? | SEP 'or'  SEP))* b_2 # OrB ;
b_2 : (b_3 (SEP? '&' SEP? | SEP 'and' SEP))* b_3 # AndB ;
b_3 : 'are' SEP 'labeled' SEP 'as' SEP term=STRING # LblIsB
    | 'aren\'t' SEP 'labeled' SEP 'as' SEP term=STRING # LblIsNotB
    | 'are' SEP 'started' SEP 'in' SEP 'start' SEP 'vertices' # IsStartSB
    | 'are' SEP 'started' SEP 'in' SEP 'final' SEP 'vertices' # IsStartFB
    | 'are' SEP 'finished' SEP 'in' SEP 'start' SEP 'vertices' # IsFinalSB
    | 'are' SEP 'finished' SEP 'in' SEP 'final' SEP 'vertices' # IsFinalFB
    | ('aren\'t' | 'are' SEP 'not') SEP 'started' SEP 'in' SEP 'start' SEP 'vertices' # IsNotStartSB
    | ('aren\'t' | 'are' SEP 'not') SEP 'started' SEP 'in' SEP 'final' SEP 'vertices' # IsNotStartFB
    | ('aren\'t' | 'are' SEP 'not') SEP 'finished' SEP 'in' SEP 'start' SEP 'vertices' # IsNotFinalSB
    | ('aren\'t' | 'are' SEP 'not') SEP 'finished' SEP 'in' SEP 'final' SEP 'vertices' # IsNotFinalFB
    | (
          '(' SEP? b_1 SEP? ')'
        | '[' SEP? b_1 SEP? ']'
      ) # ParenthesisB
    | (
          ('not' SEP | '!' SEP?) '(' SEP? b_1 SEP? ')'
        | ('not' SEP | '!' SEP?) '[' SEP? b_1 SEP? ']'
      ) # NotParenthesisB
    ;
graph_expr : g_1 ;
g_1 : g_1_g # DFAG
    | g_1_q # NoDFAG
    ;
g_1_g : (g_2_g SEP 'intersect' SEP 'with' SEP)* g_2_g # IntersectDG ;
g_2_g : g_3_g SEP 'with' SEP io_vertices # SetStartAndFinalDG
      | g_3_g # JustDG
      ;
g_3_g : 'graph' SEP graph_name=STRING # GraphDG
      | 'query' SEP regex # QueryDG
      | (
            '(' SEP? g_1_g SEP? ')'
          | '[' SEP? g_1_g SEP? ']'
        ) # ParenthesisDG
      ;
g_1_q :   dfa=g_2_g SEP 'intersect' SEP 'with' SEP g_1_q # IntersectDNG
      | nodfa=g_2_q SEP 'intersect' SEP 'with' SEP g_1_g # IntersectNNG
      | g_2_g # JustDNG
      | g_2_q # JustNNG
      ;
g_2_q : g_3_q SEP 'with' SEP io_vertices # SetStartAndFinalNG
      | g_3_q # JustNG
      ;
g_3_q : 'query' SEP closed_pattern # QueryNG
      | (
            '(' SEP? g_1 SEP? ')'
          | '[' SEP? g_1 SEP? ']'
        ) # ParenthesisNG
      ;
io_vertices : start_vs=vertices SEP 'start' SEP 'vertices' # StartIOV
            | final_vs=vertices SEP 'final' SEP 'vertices' # FinalIOV
            | (
                  start_vs=vertices SEP 'start' SEP 'vertices' SEP 'and' SEP
                  final_vs=vertices SEP 'final' SEP 'vertices'
                | final_vs=vertices SEP 'final' SEP 'vertices' SEP 'and' SEP
                  start_vs=vertices SEP 'start' SEP 'vertices'
              ) # StartAndFinalIOV
            ;
vertices : v_2 ;
v_1 : (v_2 SEP 'union' SEP 'with' SEP)* v_2 # UnionV
    | (v_2 SEP 'intersect' SEP 'with' SEP)* v_2 # IntersectV
    ;
v_2 : '{' SEP? (vertex+=NUM ',' SEP?)* vertex+=NUM SEP? '}' # SetV
    | vertexFrom=NUM SEP? '..' SEP? vertexTo=NUM # RangeV
    | (
          '(' SEP? v_1 SEP? ')'
        | '[' SEP? v_1 SEP? ']'
      ) # ParenthesisV
    ;
pattern : p_1 ;
closed_pattern : p_3 ;
p_1 : (p_2 (SEP? '|' SEP? | SEP 'or' SEP))* p_2 # AlternativeP ;
p_2 : (p_3 (SEP | SEP? '.' SEP?))* p_3 # ConcatenationP ;
p_3 : p_4 SEP? '*' # KleeneStarP
    | p_4 SEP? '+' # KleenePlusP
    | p_4 SEP? '?' # OptionP
    | p_4 # JustP
    ;
p_4 : term=STRING # TermP
    | nonterm=NAME # NontermP
    | (
          '(' SEP? p_1 SEP? ')'
        | '[' SEP? p_1 SEP? ']'
      ) # ParenthesisP
    ;
regex : r_3 ;
r_1 : (r_2 (SEP? '|' SEP? | SEP 'or' SEP))* r_2 # AlternativeR ;
r_2 : (r_3 (SEP | SEP? '.' SEP?))* r_3 # ConcatenationR ;
r_3 : r_4 SEP? '*' # KleeneStarR
    | r_4 SEP? '+' # KleenePlusR
    | r_4 SEP? '?' # OptionR
    | r_4 # JustR
    ;
r_4 : term=STRING # LiteralR
    | (
          '(' SEP? r_1 SEP? ')'
        | '[' SEP? r_1 SEP? ']'
      ) # ParenthesisR
    ;
SEP : [ \n]+ ;
STRING : '"' CHAR* '"' ;
NUM : NUM_CHAR_NOT_ZERO NUM_CHAR* ;
NAME : NAME_CHAR+ ;
CHAR : NAME_CHAR | [-., +/()\n] ;
NAME_CHAR : 'a'..'z' | 'A'..'Z' | '_' | NUM_CHAR ;
NUM_CHAR : NUM_CHAR_NOT_ZERO | '0' ;
NUM_CHAR_NOT_ZERO : '1'..'9' ;
