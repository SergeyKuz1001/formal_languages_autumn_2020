from sys import exit
from pyformlang.finite_automaton import *

states = dict()
symbols = dict()

def set_state(state):
    if state not in states.keys():
        states[state] = State(state)

def set_symbol(symbol):
    if symbol not in symbols.keys():
        symbols[symbol] = Symbol(symbol)

def dfa_read():
    dfa = DeterministicFiniteAutomaton()
    start_state = input()
    set_state(start_state)
    dfa.add_start_state(states[start_state])
    for final_state in input().split():
        set_state(final_state)
        dfa.add_final_state(states[final_state])
    n_transitions = int(input())
    for i in range(n_transitions):
        (state_from, symbol, state_to) = input().split()
        set_state(state_from)
        set_symbol(symbol)
        set_state(state_to)
        dfa.add_transition(
                states[state_from],
                symbols[symbol],
                states[state_to])
    return dfa


dfa_fst = dfa_read()
dfa_snd = dfa_read()
dfa_int = dfa_fst & dfa_snd

n_tests = int(input())
for i in range(n_tests):
    word = input()
    ans = input() == 't'
    if dfa_int.accepts(word) != ans:
        exit(1)
