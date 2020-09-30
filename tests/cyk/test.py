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

from src import ContextFreeQuery, cyk

import json
import pytest
import os

TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')

@pytest.mark.parametrize('dir_name', os.listdir(TEST_DIR))
def test(dir_name):
    test_dir_name = os.path.join(TEST_DIR, dir_name)
    with open(os.path.join(test_dir_name, 'word.txt'), 'r') as word_file:
        word = word_file.readline().strip()
    cfq = ContextFreeQuery.from_file(os.path.join(test_dir_name, 'cfq.txt'))
    result = cyk(word, cfq)
    with open(os.path.join(test_dir_name, 'answer.txt'), 'r') as answer_file:
        answer = answer_file.readline().strip() == 't'
    assert result == answer
