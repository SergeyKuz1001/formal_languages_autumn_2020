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
import pytest
import os

TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + '/tests'

states = dict()
symbols = dict()

def set_state(state):
    if state not in states.keys():
        states[state] = State(state)

def set_symbol(symbol):
    if symbol not in symbols.keys():
        symbols[symbol] = Symbol(symbol)

def dfa_read_from_file(file_input):
    dfa = DeterministicFiniteAutomaton()
    start_state = file_input.readline()
    set_state(start_state)
    dfa.add_start_state(states[start_state])
    for final_state in file_input.readline().split():
        set_state(final_state)
        dfa.add_final_state(states[final_state])
    n_transitions = int(file_input.readline())
    for i in range(n_transitions):
        (state_from, symbol, state_to) = file_input.readline().split()
        set_state(state_from)
        set_symbol(symbol)
        set_state(state_to)
        dfa.add_transition(
                states[state_from],
                symbols[symbol],
                states[state_to])
    return dfa

@pytest.mark.parametrize('file_name', os.listdir(TEST_DIR))
def test(file_name):
    with open(f'{TEST_DIR}/{file_name}', 'r') as file_input:
        dfa_fst = dfa_read_from_file(file_input)
        dfa_snd = dfa_read_from_file(file_input)
        dfa_int = dfa_fst & dfa_snd

        n_tests = int(file_input.readline())
        for i in range(n_tests):
            word = file_input.readline()
            ans = file_input.readline() == 't'
            assert dfa_int.accepts(word) == ans
