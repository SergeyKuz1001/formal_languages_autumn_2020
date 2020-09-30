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

from src import Config, Request

import pytest
import os
import json
import random

TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')

@pytest.mark.parametrize('dir_name', os.listdir(TEST_DIR))
def test_small_test(dir_name):
    test_dir_name = os.path.join(TEST_DIR, dir_name)
    args = dict()
    for file_name, dest_name in [('config.json', 'config'),
                                 ('data_base.txt', 'data_base'),
                                 ('query.txt', 'regular_query')]:
        full_file_name = os.path.join(test_dir_name, file_name)
        if os.path.exists(full_file_name):
            args[dest_name] = full_file_name
    config = Config.from_args(args)
    request = Request.from_config(config)
    result = request.execute()
    with open(os.path.join(test_dir_name, 'answer.json'), 'r') as answer_file:
        answer = set(map(tuple, json.load(answer_file)))
    assert result == answer

@pytest.mark.parametrize(('count_vertexes', 'regex'), [(count_vertexes, regex)
                for count_vertexes in [10, 40, 160]
                for regex in ['a | b', 'a* (b | $)', '(a | b) . (b* | a b)']])
def test_big_test(count_vertexes, regex):
    count_edges = random.randint(0, count_vertexes ** 2)
    I = [random.randint(0, count_vertexes) for _ in range(count_edges)]
    J = [random.randint(0, count_vertexes) for _ in range(count_edges)]
    V = [random.choice(['a', 'b', 'c']) for _ in range(count_edges)]
    max_count_input_vertexes = random.randint(0, count_vertexes)
    max_count_output_vertexes = random.randint(0, count_vertexes)
    input_vertexes = list({random.randint(0, count_vertexes)
        for _ in range(max_count_input_vertexes)})
    output_vertexes = list({random.randint(0, count_vertexes)
        for _ in range(max_count_output_vertexes)})
    config = Config.from_dict(
        {
            'data_base_lists': [I, J, V],
            'regular_query_regex': regex,
            'input_vertexes': input_vertexes,
            'output_vertexes': output_vertexes
        }
      )
    request = Request.from_config(config)
    result = request.execute()
    for V_from, _ in result:
        assert V_from in input_vertexes
    for _, V_to in result:
        assert V_to in output_vertexes
