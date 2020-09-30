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

from src import Request, Config

from argparse import Namespace
import json
import pytest
import os

TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')

@pytest.mark.parametrize('dir_name', os.listdir(TEST_DIR))
def test(dir_name):
    test_dir_name = os.path.join(TEST_DIR, dir_name)
    args = dict()
    for file_name, dest_name in [
                    ('config.json', 'config'),
                    ('data_base.txt', 'data_base'),
                    ('context_free_query.txt', 'context_free_query')]:
        full_file_name = os.path.join(test_dir_name, file_name)
        if os.path.exists(full_file_name):
            args[dest_name] = full_file_name
    config = Config.from_args(args)
    request = Request.from_config(config)
    result = request.execute()
    with open(os.path.join(test_dir_name, 'answer.json'), 'r') as answer_file:
        answer = set(map(tuple, json.load(answer_file)))
    assert result == answer
