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
script : SEP? (command SEP_PROG)* command END_PROG SEP? ;
command : CONNECT dir_name # ConnectC
        | SELECT obj_expr FROM graph_expr # SelectC
        | nonterm ARROW pattern # NamedPatternC
        | comment # CommentC
        ;
dir_name : STRING ;
comment : STRING ;
obj_expr : o_1 ;
o_1 : COUNT o_2 # CountO
    | o_2 # SetO
    ;
o_2 : EDGES # EdgesO
    | EDGES WHICH bool_expr # FilterO
    ;
bool_expr : b_3 ;
b_1 : (b_2 OR)* b_2 # OrB ;
b_2 : (b_3 AND)* b_3 # AndB ;
b_3 : ARE LABELED_AS symbol # LblIsB
    | ARE_NOT LABELED_AS symbol # LblIsNotB
    | ARE STARTED IN START_VERTICES # IsStartSB
    | ARE STARTED IN FINAL_VERTICES # IsStartFB
    | ARE FINISHED IN START_VERTICES # IsFinalSB
    | ARE FINISHED IN FINAL_VERTICES # IsFinalFB
    | ARE_NOT STARTED IN START_VERTICES # IsNotStartSB
    | ARE_NOT STARTED IN FINAL_VERTICES # IsNotStartFB
    | ARE_NOT FINISHED IN START_VERTICES # IsNotFinalSB
    | ARE_NOT FINISHED IN FINAL_VERTICES # IsNotFinalFB
    | (
          LP b_1 RP
        | LB b_1 RB
      ) # ParenthesisB
    | (
          NOT LP b_1 RP
        | NOT LB b_1 RB
      ) # NotParenthesisB
    ;
symbol : term # TermS
       | nonterm # NontermS
       ;
graph_expr : g_1 ;
g_1 : g_1_g # GG
    | g_1_q # QG
    ;
g_1_g : (g_2_g INTERSECT)* g_2_g # IntersectGG ;
g_2_g : g_3_g WITH io_vertices # SetStartAndFinalGG
      | g_3_g # JustGG
      ;
g_3_g : GRAPH graph_name # GraphG
      | (
            LP g_1_g RP
          | LB g_1_g RB
        ) # ParenthesisGG
      ;
g_1_q : g_2_g INTERSECT g_1_q # IntersectGQG
      | g_2_q INTERSECT g_1_g # IntersectQQG
      | g_2_g # JustGQG
      | g_2_q # JustQQG
      ;
g_2_q : g_3_q # JustQG ;
g_3_q : QUERY nonterm # SimpleQueryG
      | QUERY closed_pattern NAMED_AS nonterm # ComplexQueryG
      | (
            LP g_1 RP
          | LB g_1 RB
        ) # ParenthesisQG
      ;
graph_name : STRING ;
io_vertices : start_vertices START_VERTICES # StartIOV
            | final_vertices FINAL_VERTICES # FinalIOV
            | (
                  start_vertices START_VERTICES AND
                  final_vertices FINAL_VERTICES
                | final_vertices FINAL_VERTICES AND
                  start_vertices START_VERTICES
              ) # StartAndFinalIOV
            ;
start_vertices : vertices ;
final_vertices : vertices ;
vertices : v_2 ;
v_1 : (v_2 UNITE)* v_2 # UniteV
    | (v_2 INTER)* v_2 # IntersectV
    ;
v_2 : LC (vertex COMMA)* vertex RC # SetV
    | vertexFrom RANGE vertexTo # RangeV
    | (
          LP v_1 RP
        | LB v_1 RB
      ) # ParenthesisV
    ;
vertexFrom : vertex ;
vertexTo : vertex ;
vertex : NUM ;
pattern : p_1 ;
closed_pattern : p_3 ;
p_1 : (p_2 ALT)* p_2 # AlternativeP ;
p_2 : (p_3 CON)* p_3 # ConcatenationP ;
p_3 : p_4 STAR # KleeneStarP
    | p_4 PLUS # KleenePlusP
    | p_4 OPT # OptionP
    | p_4 # JustP
    ;
p_4 : term # TermP
    | nonterm # NontermP
    | (
          LP p_1 RP
        | LB p_1 RB
      ) # ParenthesisP
    ;
term : STRING ;
nonterm : NAME ;
SEP_PROG : ';' SEP? ;
END_PROG : '.' ;
CONNECT : 'connect' SEP 'to' SEP ;
SELECT : 'select' SEP ;
FROM : SEP 'from' SEP ;
ARROW : SEP? '->' SEP? | SEP 'is' SEP ;
COUNT : 'count' SEP 'of' SEP ;
EDGES : 'edges' ;
WHICH : SEP 'which' SEP ;
OR : SEP 'or' SEP | SEP? '||' SEP? ;
AND : SEP 'and' SEP | SEP? '&&' SEP? ;
ARE : 'are' SEP ;
ARE_NOT : 'are' SEP 'not' SEP | 'aren\'t' SEP ;
LABELED_AS : 'labeled' SEP 'as' SEP ;
STARTED : 'started' SEP ;
FINISHED : 'finished' SEP ;
IN : 'in' ;
START_VERTICES : SEP 'start' SEP 'vertices' ;
FINAL_VERTICES : SEP 'final' SEP 'vertices' ;
LP : '(' SEP? ;
RP : SEP? ')' ;
LB : '[' SEP? ;
RB : SEP? ']' ;
LC : '{' SEP? ;
RC : SEP? '}' ;
NOT : 'not' SEP | '!' SEP? ;
INTERSECT : SEP 'intersect' SEP 'with' SEP ;
WITH : SEP 'with' SEP ;
GRAPH : 'graph' SEP ;
QUERY : 'query' SEP ;
NAMED_AS : (SEP 'named')? SEP 'as' SEP ;
UNITE : SEP ('unite' | 'U') SEP ;
INTER : SEP ('intersect' | 'I') SEP ;
COMMA : ',' SEP? ;
RANGE : SEP? '..' SEP? ;
ALT : SEP? '|' SEP? ;
CON : SEP | SEP? '++' SEP? ;
STAR : SEP? '*' ;
PLUS : SEP? '+' ;
OPT : SEP? '?' ;
SEP : [ \n]+ ;
STRING : '"' CHAR* '"' ;
NUM : NUM_CHAR_NOT_ZERO NUM_CHAR* | NUM_CHAR_ZERO ;
NAME : NAME_CHAR+ ;
CHAR : NAME_CHAR | [-., +/()\n] ;
NAME_CHAR : 'a'..'z' | 'A'..'Z' | '_' | NUM_CHAR ;
NUM_CHAR : NUM_CHAR_NOT_ZERO | NUM_CHAR_ZERO ;
NUM_CHAR_NOT_ZERO : '1'..'9' ;
NUM_CHAR_ZERO : '0' ;
