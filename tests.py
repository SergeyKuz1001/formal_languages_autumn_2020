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

from pyformlang.finite_automaton import *
from pygraphblas import *

def test_pygraphblas():
    A = Matrix.from_lists(
        [1,  0,  0,  1,  2],
        [0,  1,  2,  2,  2],
        [2,  3, -1,  1,  5])
    B = Matrix.from_lists(
        [0,  1,  0,  1,  2],
        [0,  1,  2,  2,  2],
        [1,  3,  6, -1,  2])
    C = Matrix.from_lists(
        [1,  0,  0,  1,  2],
        [0,  1,  2,  2,  2],
        [2,  9, -5, 14, 10])
    assert (A @ B).to_lists() == C.to_lists()

def test_pyformlang():
    q = [State(i) for i in range(6)]
    c = [Symbol(chr(ord('a') + i)) for i in range(3)]

    dfa_fst = DeterministicFiniteAutomaton()
    dfa_fst.add_start_state(q[0])
    dfa_fst.add_final_state(q[5])
    dfa_fst.add_transition(q[0], c[0], q[1])
    dfa_fst.add_transition(q[0], c[1], q[5])
    dfa_fst.add_transition(q[1], c[1], q[2])
    dfa_fst.add_transition(q[1], c[2], q[3])
    dfa_fst.add_transition(q[1], c[0], q[4])
    dfa_fst.add_transition(q[2], c[0], q[5])
    dfa_fst.add_transition(q[2], c[2], q[3])
    dfa_fst.add_transition(q[3], c[0], q[5])
    dfa_fst.add_transition(q[4], c[0], q[0])
    dfa_fst.add_transition(q[4], c[1], q[5])

    dfa_snd = DeterministicFiniteAutomaton()
    dfa_snd.add_start_state(q[0])
    dfa_snd.add_final_state(q[0])
    dfa_snd.add_transition(q[0], c[0], q[0])
    dfa_snd.add_transition(q[0], c[1], q[0])
    dfa_snd.add_transition(q[0], c[2], q[1])
    dfa_snd.add_transition(q[1], c[0], q[0])
    dfa_snd.add_transition(q[1], c[1], q[1])
    dfa_snd.add_transition(q[1], c[2], q[0])

    dfa_int = dfa_fst & dfa_snd

    assert not dfa_int.accepts('')
    assert not dfa_int.accepts('a')
    assert dfa_int.accepts('b')
    assert not dfa_int.accepts('c')
    assert not dfa_int.accepts('ab')
    assert dfa_int.accepts('aab')
    assert dfa_int.accepts('aaab')
    assert not dfa_int.accepts('aaaab')
    assert dfa_int.accepts('aaaaba')
    assert dfa_int.accepts('aaaaca')
    assert dfa_int.accepts('aba')
    assert not dfa_int.accepts('abc')
    assert not dfa_int.accepts('babc')
    assert not dfa_int.accepts('acbcc')
    assert not dfa_int.accepts('cbb')
