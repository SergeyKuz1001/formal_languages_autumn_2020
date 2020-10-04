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

from src import rpq, Config
from tests.simple_test import simple_test

import json
import pytest
import os
import random

MAIN_TEST_DIR = \
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
TEST_DIRS = list(map(
        lambda dir_name: os.path.join(MAIN_TEST_DIR, dir_name),
        os.listdir(MAIN_TEST_DIR)
    ))

@pytest.mark.parametrize('test_dir', TEST_DIRS)
def test_small_test(test_dir):
    assert simple_test(
            test_dir,
            [
                ('config.json', 'config'),
                ('data_base.txt', 'data_base'),
                ('query.txt', 'regular_query')
            ],
            rpq,
            lambda j: set(map(tuple, j))
        )

@pytest.mark.parametrize(('max_count_vertexes', 'regex'),
            [
                (max_count_vertexes, regex)
                for max_count_vertexes in [10, 40, 160]
                for regex in ['a | b', 'a* (b | $)', '(a | b) . (b* | a b)']
            ])
                #for regex in ['a | b']])
def test_big_test(max_count_vertexes, regex):
    count_edges = random.randint(1, max_count_vertexes ** 2)
    I = [random.randint(0, max_count_vertexes - 1) for _ in range(count_edges)]
    J = [random.randint(0, max_count_vertexes - 1) for _ in range(count_edges)]
    V = [random.choice(['a', 'b', 'c']) for _ in range(count_edges)]
    count_vertexes = max(I + J) + 1
    max_count_input_vertexes = random.randint(1, count_vertexes)
    max_count_output_vertexes = random.randint(1, count_vertexes)
    input_vertexes = list({random.randint(0, count_vertexes - 1)
        for _ in range(max_count_input_vertexes)})
    output_vertexes = list({random.randint(0, count_vertexes - 1)
        for _ in range(max_count_output_vertexes)})
    config = Config.from_dict(
        {
            'data_base_lists': [I, J, V],
            'regular_query_regex': regex,
            'input_vertexes': input_vertexes,
            'output_vertexes': output_vertexes
        }
      )
    result = rpq(config)
    for V_from, _ in result:
        assert V_from in input_vertexes
    for _, V_to in result:
        assert V_to in output_vertexes
