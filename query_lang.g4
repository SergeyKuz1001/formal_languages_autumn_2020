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
script : SEP? (command SEP_PROG | COMMENT_BLOCK)+ ;
command : CONNECT dir_name # ConnectC
        | SELECT obj_expr FROM graph_expr_si # SimpleSISelectC
        | SELECT obj_expr FROM graph_expr_io # SimpleIOSelectC
        | SELECT obj_expr FROM graph_expr_si WHERE EACH_EDGE bool_expr_si # FilterSISelectC
        | SELECT obj_expr FROM graph_expr_io WHERE EACH_EDGE bool_expr_io # FilterIOSelectC
        | var ARROW pattern # NamedPatternC
        | ASK_STRING var # AskStringC
        | ASK_NUMBER var # AskNumberC
        | STRING # TellC
        ;
dir_name : STRING ;
obj_expr : o_1 ;
o_1 : COUNT o_2 # CountO
    | o_2 # SetO
    ;
o_2 : EDGES # EdgesO
    | PAIRS # PairsO
    | START_VERTICES # StartVsO
    | FINAL_VERTICES # FinalVsO
    ;
bool_expr_si : b_3_si ;
b_1_si : (b_2_si OR)* b_2_si # OrSIB ;
b_2_si : (b_3_si AND)* b_3_si # AndSIB ;
b_3_si : b_4_si # ConstructSIB
       | (
             LP b_1_si RP
           | LB b_1_si RB
         ) # ParenthesisSIB
       | (
             NOT LP b_1_si RP
           | NOT LB b_1_si RB
         ) # NotParenthesisSIB
       ;
b_4_si : IS LABELED_AS symbol # LblIsB
       | IS_NOT LABELED_AS symbol # LblIsNotB
       | IS LOOP # LoopB
       | IS_NOT LOOP # NotLoopB
       ;
bool_expr_io : b_3_io ;
b_1_io : (b_2_io OR)* b_2_io # OrIOB ;
b_2_io : (b_3_io AND)* b_3_io # AndIOB ;
b_3_io : b_4_io # ConstructIOB
       | (
             LP b_1_io RP
           | LB b_1_io RB
         ) # ParenthesisIOB
       | (
             NOT LP b_1_io RP
           | NOT LB b_1_io RB
         ) # NotParenthesisIOB
       ;
b_4_io : b_4_si # SIB
       | IS STARTED IN START_VERTICES # IsStartSB
       | IS STARTED IN FINAL_VERTICES # IsStartFB
       | IS FINISHED IN START_VERTICES # IsFinalSB
       | IS FINISHED IN FINAL_VERTICES # IsFinalFB
       | IS_NOT STARTED IN START_VERTICES # IsNotStartSB
       | IS_NOT STARTED IN FINAL_VERTICES # IsNotStartFB
       | IS_NOT FINISHED IN START_VERTICES # IsNotFinalSB
       | IS_NOT FINISHED IN FINAL_VERTICES # IsNotFinalFB
       ;
symbol : term # TermS
       | var # NontermS
       ;
graph_expr_si : g_1_si ;
g_1_si : g_1_g # GG
       | g_1_l # LG
       ;
graph_expr_io : g_1_io ;
g_1_io : g_1_h # HG
       | g_1_j # JG
       ;
g_1_g : g_1_g INTERSECT g_2_g # IntersectGGGG
      | g_1_g INTERSECT g_2_h # IntersectGGHG
      | g_1_h INTERSECT g_2_h # IntersectGHGG
      | g_1_h INTERSECT g_2_h # IntersectGHHG
      | g_2_g # JustGG
      ;
g_2_g : g_3_g # SIGG ;
g_3_g : g_4_g # ConstructGG
      | (
            LP g_1_g RP
          | LB g_1_g RB
        ) # ParenthesisGG
      ;
g_4_g : GRAPH graph_name # GraphG ;
g_1_q : g_2_q # JustQG ;
g_2_q : g_3_q # SIQG ;
g_3_q : g_4_q # ConstructQG
      | (
            LP g_1_q RP
          | LB g_1_q RB
        ) # ParenthesisQG
      ;
g_4_q : QUERY var # SimpleQueryG
      | QUERY closed_pattern NAMED_AS var # ComplexQueryG
      ;
g_1_l : g_1_g INTERSECT g_2_q # IntersectLGQG
      | g_1_g INTERSECT g_2_l # IntersectLGLG
      | g_1_g INTERSECT g_2_j # IntersectLGJG
      | g_1_q INTERSECT g_2_g # IntersectLQGG
      | g_1_q INTERSECT g_2_l # IntersectLQLG
      | g_1_l INTERSECT g_2_g # IntersectLLGG
      | g_1_l INTERSECT g_2_q # IntersectLLQG
      | g_1_l INTERSECT g_2_l # IntersectLLLG
      | g_1_l INTERSECT g_2_h # IntersectLLHG
      | g_1_l INTERSECT g_2_j # IntersectLLJG
      | g_1_h INTERSECT g_2_l # IntersectLHLG
      | g_1_h INTERSECT g_2_j # IntersectLHJG
      | g_1_j INTERSECT g_2_g # IntersectLJGG
      | g_1_j INTERSECT g_2_l # IntersectLJLG
      | g_1_j INTERSECT g_2_h # IntersectLJHG
      | g_1_j INTERSECT g_2_j # IntersectLJJG
      | g_2_l # JustLG
      ;
g_2_l : g_3_l # SILG ;
g_3_l : (LP g_1_l RP | LB g_1_l RB) # ParenthesisLG ;
g_1_h : g_2_h # JustHG ;
g_2_h : g_3_g WHERE io_vertices # IOHG
      | g_3_h # SIHG
      ;
g_3_h : (LP g_1_h RP | LB g_1_h RB) # ParenthesisHG ;
g_1_j : g_1_q INTERSECT g_2_h # IntersectJQHG
      | g_1_q INTERSECT g_2_j # IntersectJQJG
      | g_1_h INTERSECT g_2_q # IntersectJHQG
      | g_1_j INTERSECT g_2_q # IntersectJJQG
      | g_2_j # JustJG
      ;
g_2_j : g_3_l WHERE io_vertices # IOJG
      | g_3_j # SIJG
      ;
g_3_j : (LP g_1_j RP | LB g_1_j RB) # ParenthesisJG ;
graph_name : STRING ;
io_vertices : start_vertices ARE START_VERTICES # StartIOV
            | final_vertices ARE FINAL_VERTICES # FinalIOV
            | (
                  start_vertices ARE START_VERTICES AND
                  final_vertices ARE FINAL_VERTICES
                | final_vertices ARE FINAL_VERTICES AND
                  start_vertices ARE START_VERTICES
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
vertex : NUM # NumV
       | var # VarV
       ;
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
    | var # NontermP
    | EPS # EpsilonP
    | (
          LP p_1 RP
        | LB p_1 RB
      ) # ParenthesisP
    ;
term : STRING ;
var : NAME ;
SEP_PROG : ';' SEP? ;
CONNECT : 'connect' SEP 'to' SEP ;
SELECT : 'select' SEP ;
FROM : SEP 'from' SEP ;
WHERE : SEP 'where' SEP ;
EACH_EDGE : 'each' SEP 'edge' SEP ;
ARROW : SEP? '->' SEP? ;
ASK_STRING : 'ask' SEP 'string' SEP ;
ASK_NUMBER : 'ask' SEP 'number' SEP ;
COUNT : 'count' SEP 'of' SEP ;
EDGES : 'edges' ;
PAIRS : 'pairs' ;
OR : SEP 'or' SEP | SEP? '||' SEP? ;
AND : SEP 'and' SEP | SEP? '&&' SEP? ;
IS : 'is' SEP ;
IS_NOT : 'is' SEP 'not' SEP | 'isn\'t' SEP ;
LABELED_AS : 'labeled' SEP 'as' SEP ;
LOOP : 'loop' ;
STARTED : 'started' SEP ;
FINISHED : 'finished' SEP ;
IN : 'in' SEP ;
ARE : SEP 'are' SEP ;
START_VERTICES : 'start' SEP 'vertices' ;
FINAL_VERTICES : 'final' SEP 'vertices' ;
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
CON : SEP | SEP? '.' SEP? ;
STAR : SEP? '*' ;
PLUS : SEP? '+' ;
OPT : SEP? '?' ;
EPS : '$' ;
SEP : [ \n]+ ;
COMMENT_BLOCK : '\'' COM_CHAR* '`' SEP? ;
STRING : '"' CHAR* '"' ;
NUM : NUM_CHAR_NOT_ZERO NUM_CHAR* | NUM_CHAR_ZERO ;
NAME : NAME_CHAR+ ;
COM_CHAR : CHAR | '"' ;
CHAR : NAME_CHAR | [-.;,: +/(){}\n!@#$%^&*?\\[\]'<>~|] ;
NAME_CHAR : 'a'..'z' | 'A'..'Z' | '_' | NUM_CHAR ;
NUM_CHAR : NUM_CHAR_NOT_ZERO | NUM_CHAR_ZERO ;
NUM_CHAR_NOT_ZERO : '1'..'9' ;
NUM_CHAR_ZERO : '0' ;
