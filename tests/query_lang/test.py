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

from interpret import interpret

import os
import json
import pytest
from typing import List, Tuple, Any, Callable

MAIN_TEST_DIR = \
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
TEST_DIRS = list(map(
        lambda dir_name: os.path.join(MAIN_TEST_DIR, dir_name),
        os.listdir(MAIN_TEST_DIR)
    ))

def list_to_set(l):
    if isinstance(l, list):
        return set(map(tuple, l))
    return l

@pytest.mark.parametrize('test_dir', TEST_DIRS)
def test(test_dir):
    result = interpret(os.path.join(test_dir, 'script.txt'))
    with open(os.path.join(test_dir, 'answer.json'), 'r') as answer_file:
        answer = list(map(list_to_set, json.load(answer_file)))
    assert result == answer
