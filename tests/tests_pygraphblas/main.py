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
