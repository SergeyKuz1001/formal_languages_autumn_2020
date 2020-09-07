from sys import exit
from pygraphblas import *

def matrix_read():
    I = list(map(int, input().split()))
    J = list(map(int, input().split()))
    V = list(map(int, input().split()))
    return Matrix.from_lists(I, J, V)

def matrix_check(A, B):
    return A.to_lists() == B.to_lists()


A = matrix_read()
B = matrix_read()
C = matrix_read()

if matrix_check(A @ B, C):
    exit(0)
else:
    exit(1)
