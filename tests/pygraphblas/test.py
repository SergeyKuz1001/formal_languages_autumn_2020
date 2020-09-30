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

from pygraphblas import *
import pytest
import os

TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + '/tests'

def matrix_read_from_file(file_input):
    I = list(map(int, file_input.readline().split()))
    J = list(map(int, file_input.readline().split()))
    V = list(map(int, file_input.readline().split()))
    return Matrix.from_lists(I, J, V)

def matrix_check(A, B):
    return A.to_lists() == B.to_lists()

@pytest.mark.parametrize('file_name', os.listdir(TEST_DIR))
def test(file_name):
    with open(f'{TEST_DIR}/{file_name}', 'r') as file_input:
        A = matrix_read_from_file(file_input)
        B = matrix_read_from_file(file_input)
        C = matrix_read_from_file(file_input)
        assert matrix_check(A @ B, C)
